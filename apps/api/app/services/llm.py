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
            )
            raw = response.choices[0].message.content.strip()
            return json.loads(raw)
        except Exception as e:
            print(f"[LLM-JSON] Nvidia failed: {e}")

    raise RuntimeError("All LLM JSON providers failed or are unconfigured")


def _fallback_explanation(phone_item: dict, persona: str, budget: float) -> str:
    """Generate high-quality rule-based explanation when LLM is offline."""
    phone = phone_item["phone"]
    brand = phone.brand or "This device"
    model = phone.model or phone.name or "smartphone"
    specs = phone.specs
    reasons = phone_item.get("match_reasons", [])

    processor_str = specs.processor if specs and specs.processor and specs.processor != "Unknown" else ""
    battery_str = specs.battery if specs and specs.battery and specs.battery != "Unknown" else ""
    camera_str = specs.mainCamera if specs and specs.mainCamera and specs.mainCamera != "Unknown" else ""

    p_lower = persona.lower()
    if "student" in p_lower:
        first = f"The {brand} {model} delivers exceptional battery stamina and responsive daily performance within your ₹{budget:,.0f} budget."
        second = f"Equipped with {processor_str or 'a balanced chipset'} and {battery_str or 'long-lasting battery'}, it comfortably handles study apps, media, and multitasking."
    elif "gamer" in p_lower:
        first = f"The {brand} {model} stands out with high compute power and thermal stability for heavy gaming sessions."
        second = f"Driven by {processor_str or 'high-performance silicon'}, it sustains high framerates without severe thermal throttling."
    elif "content" in p_lower or "creator" in p_lower or "photo" in p_lower:
        first = f"The {brand} {model} features a standout camera configuration with natural color science and sharp video recording."
        second = f"With its {camera_str or 'advanced camera array'}, it gives you flagship-grade capture capabilities under ₹{budget:,.0f}."
    elif "professional" in p_lower:
        first = f"The {brand} {model} offers a refined design, clean software longevity, and swift multitasking for business workflows."
        second = f"Backed by {processor_str or 'fast hardware'} and dependable battery life, it keeps you productive throughout demanding workdays."
    else:
        strength_summary = reasons[0] if reasons else "well-rounded hardware balance"
        first = f"The {brand} {model} offers an outstanding price-to-performance ratio in the Indian market."
        second = f"It excels in {strength_summary}, making it a reliable and verified choice under ₹{budget:,.0f}."

    return f"{first} {second}"


def generate_explanations(phones: list, persona: str, budget: float) -> dict:
    """
    Generates a personalized 2-sentence explanation for why each phone fits the persona and budget.
    Returns a dict mapping phone name -> explanation.
    """
    if not phones:
        return {}

    # Fast check for Groq
    if _get_groq_client():
        phone_names = [f'{i+1}. {p["phone"].brand} {p["phone"].model}' for i, p in enumerate(phones)]
        phones_str = "\n".join(phone_names)

        prompt = f"""You are a smartphone expert. For each of these phones, write 2 concise sentences explaining why it fits a '{persona}' user with budget Rs. {budget}.
PHONES:
{phones_str}

Return valid JSON:
{{
  "explanations": {{
    "Phone Brand Model": "2-sentence explanation..."
  }}
}}"""
        try:
            response = generate_json(prompt, max_tokens=4096)
            exps = response.get("explanations", {})
            if exps:
                return exps
        except Exception as e:
            print(f"[LLM] Explanation generation skipped ({e}), using instant fallback.")

    # Rule-based fallback (instant)
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
