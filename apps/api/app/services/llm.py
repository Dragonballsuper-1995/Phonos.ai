"""
Intelligent LLM Service for Phonos.ai
=======================================
Priority chain: Nvidia NIM (Llama-4 Maverick) → Gemini 2.5 Flash → Groq (GPT OSS 120B)
All models accessed via OpenAI-compatible API or native SDK.
"""

import json
import warnings
from typing import Optional
from openai import OpenAI
from groq import Groq
from app.core.config import settings

# Suppress any deprecation noise
warnings.filterwarnings("ignore", category=FutureWarning)

# ─── Client initialization ────────────────────────────────────────────────────

_nvidia_client: Optional[OpenAI] = None
_groq_client: Optional[Groq] = None
_gemini_client = None


def _get_nvidia_client() -> Optional[OpenAI]:
    global _nvidia_client
    if _nvidia_client is None and settings.NVIDIA_API_KEY:
        _nvidia_client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=settings.NVIDIA_API_KEY,
            timeout=2.0,
        )
    return _nvidia_client


def _get_groq_client() -> Optional[Groq]:
    global _groq_client
    if _groq_client is None and settings.GROQ_API_KEY:
        _groq_client = Groq(api_key=settings.GROQ_API_KEY, timeout=10.0)
    return _groq_client


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is None and settings.GEMINI_API_KEY:
        try:
            from google import genai
            _gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        except Exception as e:
            print(f"[LLM] Gemini client init failed: {e}")
    return _gemini_client


# ─── Core text generation ─────────────────────────────────────────────────────

def generate_text(prompt: str, max_tokens: int = 1024, temperature: float = 0.1) -> str:
    """
    Try Groq (Fastest) → Gemini → Nvidia in order.
    Returns the generated text or raises RuntimeError if all fail.
    """
    # 1. Groq (Fastest, Sub-200ms)
    groq = _get_groq_client()
    if groq:
        try:
            resp = groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=settings.GROQ_MODEL,
                max_tokens=max(max_tokens, 512),
                temperature=temperature,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[LLM] Groq failed ({settings.GROQ_MODEL}): {e}")

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
                top_p=1.0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[LLM] Nvidia failed ({settings.NVIDIA_MODEL}): {e}")

    raise RuntimeError("All LLM providers failed")


def generate_json(prompt: str, max_tokens: int = 2048) -> dict:
    """
    Generate a structured JSON response. Tries Groq → Gemini → Nvidia.
    """
    system_msg = "You are a JSON-only responder. Return valid JSON and nothing else. No markdown, no code blocks."

    # 1. Groq with JSON mode (Fastest, Sub-300ms)
    groq = _get_groq_client()
    if groq:
        try:
            resp = groq.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": f"{prompt}\nPlease output valid JSON."}
                ],
                model=settings.GROQ_MODEL,
                max_tokens=max(max_tokens, 4096),
                temperature=0.05,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content.strip()
            return json.loads(raw)
        except Exception as e:
            print(f"[LLM-JSON] Groq failed ({settings.GROQ_MODEL}): {e}")

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

    # 3. Nvidia with JSON response format
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
            print(f"[LLM-JSON] Nvidia failed ({settings.NVIDIA_MODEL}): {e}")

    raise RuntimeError("All LLM JSON providers failed")


def generate_explanations(phones: list, persona: str, budget: float) -> dict:
    """
    Generates a personalized 2-sentence explanation for why each phone fits the persona and budget.
    Returns a dict mapping phone name -> explanation.
    """
    if not phones:
        return {}
        
    phone_names = [f'{i+1}. {p["phone"].brand} {p["phone"].model}' for i, p in enumerate(phones)]
    phones_str = "\n".join(phone_names)
    
    prompt = f"""You are a smartphone expert advising a '{persona}' user with a budget of Rs. {budget}.
For each of the following phones, write exactly 2 sentences explaining specifically why it is a great choice for this persona.
Be specific about real features (e.g. "Snapdragon 8 Gen 3 for gaming", "6000mAh for long study sessions"). Do NOT make up specs.

PHONES:
{phones_str}

Return JSON ONLY in this format:
{{
  "explanations": {{
    "exact phone name (e.g. Samsung Galaxy S26)": "2-sentence explanation...",
    ...
  }}
}}
"""
    try:
        response = generate_json(prompt, max_tokens=2048)
        return response.get("explanations", {})
    except Exception as e:
        print(f"[LLM] Explanation generation failed: {e}")
        return {}


# ─── Persona detection ────────────────────────────────────────────────────────

async def detect_persona(query: str) -> str:
    """Classify query into one of the standard personas."""
    prompt = (
        "Analyze this phone buyer query and classify the user into exactly ONE persona. "
        "Valid personas: Student, Gamer, Content Creator, Professional, Senior/Basic, Photography, General. "
        f"Query: '{query}'. "
        "Return ONLY the persona name, nothing else."
    )
    try:
        return generate_text(prompt, max_tokens=20, temperature=0.0)
    except Exception:
        return "General"
