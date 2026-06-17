import google.generativeai as genai
from groq import Groq
from typing import Optional, Dict, Any
from app.core.config import settings

# Initialize clients
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

groq_client = None
if settings.GROQ_API_KEY:
    groq_client = Groq(api_key=settings.GROQ_API_KEY)

async def detect_persona(query: str) -> str:
    prompt = f"Analyze this query and map it to a persona: Student, Gamer, Content Creator, Professional, Senior/Basic, Photography, General. Query: '{query}'. Return ONLY the persona name."
    
    if settings.GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini failed: {e}")
            
    if groq_client:
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq failed: {e}")
            
    return "General"
