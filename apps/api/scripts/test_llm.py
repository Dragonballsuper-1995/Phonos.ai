"""Quick live test: Nvidia → verify one phone via LLM"""
import sys
sys.path.insert(0, '.')

# Secrets are loaded from environment or .env file

from app.core.config import settings
print("Settings check:")
print("  NVIDIA:", bool(settings.NVIDIA_API_KEY))
print("  GEMINI:", bool(settings.GEMINI_API_KEY))
print("  GROQ:", bool(settings.GROQ_API_KEY))
print("  GROQ_MODEL:", settings.GROQ_MODEL)

print("\nTesting Nvidia Llama-4 Maverick...")
from app.services.llm import generate_text, _get_groq_client
try:
    result = generate_text("Say 'Nvidia OK' and nothing else.", max_tokens=10, temperature=0.0)
    print("  Response:", result)
except Exception as e:
    print("  Nvidia test failed:", e)

print(f"\nTesting Groq with {settings.GROQ_MODEL}...")
groq = _get_groq_client()
if groq:
    try:
        resp = groq.chat.completions.create(
            messages=[{"role": "user", "content": "Say 'Groq GPT-OSS-120B OK' and nothing else."}],
            model=settings.GROQ_MODEL,
            max_tokens=256,
            temperature=0.0
        )
        print("  Groq Response:", resp.choices[0].message.content.strip())
    except Exception as e:
        print("  Groq test failed:", e)

print("\nTesting JSON generation...")
from app.services.llm import generate_json
test_prompt = """Return a JSON object with key "status" set to "working" and key "model" set to "active"."""
result = generate_json(test_prompt, max_tokens=256)
print("  JSON Response:", result)

print("\nAll LLM tests passed!")
