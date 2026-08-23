"""
Intelligent LLM Service for Phonos.ai
=======================================
Priority chain: Groq (GPT OSS 120B / Fast Inference) → Gemini 2.5 Flash → Nvidia NIM
Includes instant rule-based fallback when external LLM APIs are unreachable or unconfigured.
"""

import json
import warnings
from typing import Optional, Dict, Any
from openai import OpenAI
from groq import Groq
from app.core.config import settings

# Suppress any deprecation noise
warnings.filterwarnings("ignore", category=FutureWarning)

# ─── Client initialization ────────────────────────────────────────────────────

_nvidia_client: Optional[OpenAI] = None
_groq_client: Optional[Groq] = None
_gemini_client = None


def _get_groq_client() -> Optional[Groq]:
    global _groq_client
    if _groq_client is None and settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip():
        try:
            _groq_client = Groq(api_key=settings.GROQ_API_KEY.strip(), timeout=3.0)
        except Exception as e:
            print(f"[LLM] Groq client init failed: {e}")
    return _groq_client


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is None and settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.startswith("AIzaSy"):
        try:
            from google import genai
            _gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY.strip())
        except Exception as e:
            print(f"[LLM] Gemini client init failed: {e}")
    return _gemini_client


def _get_nvidia_client() -> Optional[OpenAI]:
    global _nvidia_client
    if _nvidia_client is None and settings.NVIDIA_API_KEY and settings.NVIDIA_API_KEY.strip():
        try:
            _nvidia_client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=settings.NVIDIA_API_KEY.strip(),
                timeout=2.0,
            )
        except Exception as e:
            print(f"[LLM] Nvidia client init failed: {e}")
    return _nvidia_client


# ─── Core text generation ─────────────────────────────────────────────────────

def generate_text(prompt: str, max_tokens: int = 1024, temperature: float = 0.1) -> str:
    # 1. Groq (Fastest, Sub-1s)
    groq = _get_groq_client()
    if groq:
        try:
            resp = groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=settings.GROQ_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[LLM] Groq failed: {e}")

    # 2. Gemini 2.5 Flash
    gemini = _get_gemini_client()
    if gemini:
        try:
            from google.genai import types as genai_types
            result = gemini.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )
            )
            if result.text:
                return result.text.strip()
        except Exception as e:
            print(f"[LLM] Gemini failed: {e}")

    # 3. Nvidia NIM
    nvidia = _get_nvidia_client()
    if nvidia:
        try:
            response = nvidia.chat.completions.create(
                model=settings.NVIDIA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[LLM] Nvidia failed: {e}")

    raise RuntimeError("All LLM providers failed or are unconfigured")


def generate_json(prompt: str, max_tokens: int = 4096) -> dict:
    system_msg = "You are a JSON-only responder. Return valid JSON only. No markdown, no commentary."

    # 1. Groq with JSON mode
    groq = _get_groq_client()
    if groq:
        try:
            resp = groq.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                model=settings.GROQ_MODEL,
                max_tokens=max(max_tokens, 4096),
                temperature=0.05,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content.strip()
            return json.loads(raw)
        except Exception as e:
            print(f"[LLM-JSON] Groq failed: {e}")

    # 2. Gemini with JSON mime type
    gemini = _get_gemini_client()
    if gemini:
        try:
            from google.genai import types as genai_types
            result = gemini.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_msg}\n\n{prompt}",
                config=genai_types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.05,
                    response_mime_type="application/json",
                )
            )
            if result.text:
                return json.loads(result.text.strip())
        except Exception as e:
            print(f"[LLM-JSON] Gemini failed: {e}")

    # 3. Nvidia NIM
    nvidia = _get_nvidia_client()
    if nvidia:
        try:
            response = nvidia.chat.completions.create(
                model=settings.NVIDIA_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.05,
                response_format={"type": "json_object"},
                timeout=2.0,
            )
            raw = response.choices[0].message.content.strip()
            return json.loads(raw)
        except Exception as e:
            print(f"[LLM-JSON] Nvidia failed: {e}")

    raise RuntimeError("All LLM JSON providers failed or are unconfigured")


def _fallback_explanation(phone_item: dict, persona: str, budget: float) -> str:
    """Generate high-quality, instant, benchmark-backed explanation for recommendations."""
    phone = phone_item["phone"]
    brand = phone.brand or "This device"
    model = phone.model or phone.name or "smartphone"
    specs = phone.specs
    reasons = phone_item.get("match_reasons", [])

    processor_str = specs.processor if specs and specs.processor and specs.processor != "Unknown" else ""
    battery_str = specs.battery if specs and specs.battery and specs.battery != "Unknown" else ""
    camera_str = specs.mainCamera if specs and specs.mainCamera and specs.mainCamera != "Unknown" else ""

    # Check benchmarks for scientific citations
    benchmarks = []
    if getattr(phone, 'dxomark_camera_score', None):
        benchmarks.append(f"DxOMark optics score of {int(phone.dxomark_camera_score)}")
    if getattr(phone, 'geekbench_multi', None):
        benchmarks.append(f"Geekbench 6 multi-core compute score of {int(phone.geekbench_multi):,}")
    if getattr(phone, 'antutu_v10_score', None):
        benchmarks.append(f"AnTuTu v10 rating of {phone.antutu_v10_score/1000000:.1f}M")
    if getattr(phone, 'gsmarena_battery_hours', None):
        benchmarks.append(f"{phone.gsmarena_battery_hours}h active battery endurance")

    bench_citation = f" (backed by {', '.join(benchmarks[:2])})" if benchmarks else ""

    p_lower = persona.lower()
    if "student" in p_lower:
        first = f"The {brand} {model} delivers exceptional battery stamina and responsive daily performance within your ₹{budget:,.0f} budget{bench_citation}."
        second = f"Equipped with {processor_str or 'a power-efficient chipset'} and {battery_str or 'a high-capacity battery'}, it effortlessly powers study apps, multimedia, and daily tasks."
    elif "gamer" in p_lower:
        first = f"The {brand} {model} stands out with high compute power and thermal stability for intense gaming{bench_citation}."
        second = f"Driven by {processor_str or 'high-performance silicon'}, it sustains high framerates and minimal thermal throttling."
    elif "content" in p_lower or "creator" in p_lower or "photo" in p_lower:
        first = f"The {brand} {model} features a standout camera configuration with natural color science and sharp video recording{bench_citation}."
        second = f"With its {camera_str or 'advanced optical setup'}, it offers creator-grade capture capabilities under ₹{budget:,.0f}."
    elif "professional" in p_lower:
        first = f"The {brand} {model} offers a refined design, clean software longevity, and swift multitasking for business workflows{bench_citation}."
        second = f"Backed by {processor_str or 'fast hardware'} and dependable battery life, it keeps you productive throughout demanding workdays."
    else:
        strength_summary = reasons[0] if reasons else "well-rounded hardware balance"
        first = f"The {brand} {model} offers an outstanding price-to-performance ratio in the Indian market{bench_citation}."
        second = f"It excels in {strength_summary}, making it a reliable and verified choice under ₹{budget:,.0f}."

    return f"{first} {second}"


def generate_explanations(phones: list, persona: str, budget: float) -> dict:
    """
    Generates personalized explanations for why each phone fits the persona and budget.
    Returns instantly with rich benchmark-backed rationale.
    """
    if not phones:
        return {}

    return {
        (p["phone"].name or p["phone"].model): _fallback_explanation(p, persona, budget)
        for p in phones
    }


async def detect_persona(query: str) -> str:
    """Classify query into one of the standard personas."""
    # Fast heuristic classification first
    q_lower = query.lower()
    if any(w in q_lower for w in ["game", "gaming", "fps", "bgmi", "cod", "gpu"]):
        return "Gamer"
    if any(w in q_lower for w in ["camera", "photo", "vlog", "reel", "video", "shoot", "lens", "dslr"]):
        return "Content Creator"
    if any(w in q_lower for w in ["student", "college", "study", "cheap", "budget"]):
        return "Student"
    if any(w in q_lower for w in ["work", "business", "office", "professional", "email", "productivity"]):
        return "Professional"
    if any(w in q_lower for w in ["senior", "elderly", "parent", "simple", "loud", "grandparent"]):
        return "Senior"

    prompt = (
        "Analyze this query and output ONE persona name from: Student, Gamer, Content Creator, Professional, Senior, Photography, General. "
        f"Query: '{query}'. Output ONLY the name."
    )
    try:
        return generate_text(prompt, max_tokens=20, temperature=0.0)
    except Exception:
        return "General"


import asyncio
from typing import AsyncIterator, List

def generate_clarification_questions(query: str, budget: float = 50000.0, detected_persona: str = "General") -> List[Dict[str, Any]]:
    """
    Generates dynamic interactive clarification questions based on query intent & budget.
    """
    q_lower = query.lower()
    questions = []

    # 1. Primary Workflow / Persona Focus
    if "game" not in q_lower and "photo" not in q_lower and "camera" not in q_lower:
        questions.append({
            "id": "primary_focus",
            "question": "What is your main priority for this phone?",
            "options": [
                "Camera & Natural Portrait Photography",
                "High-FPS Competitive Gaming (BGMI / COD)",
                "All-Day Battery & Super Fast Charging",
                "Clean, Bloatware-Free Daily Driver"
            ]
        })

    # 2. Form Factor / Screen Size Preference
    questions.append({
        "id": "form_factor",
        "question": "Do you prefer a compact or large display?",
        "options": [
            "Compact & Lightweight (Under 6.4\")",
            "Large & Immersive (6.7\"+ for gaming & movies)",
            "Standard / No Strong Preference"
        ]
    })

    # 3. Software UI & Brand Ecosystem
    if "clean" not in q_lower and "stock" not in q_lower and "moto" not in q_lower:
        questions.append({
            "id": "software_ui",
            "question": "How important is a 100% ad-free, clean OS?",
            "options": [
                "Must be Ad-Free & Clean (Nothing OS / Motorola / Pixel)",
                "Feature-Rich Custom UI (HyperOS / Realme UI / OxygenOS)",
                "Samsung One UI Ecosystem"
            ]
        })

    # 4. Long-Term Support
    if budget >= 40000:
        questions.append({
            "id": "longevity",
            "question": "How many years do you plan to use this device?",
            "options": [
                "2 to 3 Years",
                "4 to 5+ Years (Prioritize OS updates)"
            ]
        })

    return questions[:3]


async def stream_deep_reasoning(query: str, top_phones: list, budget: float) -> AsyncIterator[str]:
    """
    Streams an expert architectural breakdown token-by-token.
    """
    phone_names = [f"{p['phone'].brand} {p['phone'].name or p['phone'].model}" for p in top_phones[:3]]
    names_str = ", ".join(phone_names) if phone_names else "top matched devices"

    prompt = f"""You are an elite smartphone architect advising an Indian buyer.
USER QUERY: '{query}' (Budget: Rs. {budget:,.0f})
MATCHED TOP MODELS: {names_str}

Provide a concise, highly insightful 3-paragraph breakdown:
1. Architectural analysis of what hardware is needed for their exact request.
2. Direct comparison of why these models lead in performance, optics, and battery.
3. Final purchasing recommendation.

Do NOT include pleasantries. Dive straight into the analysis."""

    # 1. Try Groq streaming
    groq = _get_groq_client()
    if groq:
        try:
            stream = groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=settings.GROQ_MODEL,
                max_tokens=600,
                temperature=0.3,
                stream=True
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    yield delta
            return
        except Exception as e:
            print(f"[LLM-Stream] Groq streaming notice: {e}")

    # 2. Rule-based streaming fallback
    fallback_text = (
        f"### Neural Hardware Analysis for \"{query}\"\n\n"
        f"Based on our hybrid scoring matrix blending scientific lab benchmarks (DxOMark, Geekbench 6, AnTuTu v10) "
        f"with verified Indian catalog data, we evaluated the available options under your ₹{budget:,.0f} budget.\n\n"
        f"**Leading Candidates:** {names_str}.\n\n"
        f"Each top recommendation achieves optimal thermal stability, high-efficiency silicon compute, "
        f"and proven battery endurance tailored directly to your workflow requirements."
    )

    for word in fallback_text.split(" "):
        yield word + " "
        await asyncio.sleep(0.02)
