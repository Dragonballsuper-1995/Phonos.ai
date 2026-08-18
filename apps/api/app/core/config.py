import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Phonos.ai API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS — set CORS_ORIGINS env var to a comma-separated list of allowed origins.
    # Defaults to "*" (open). After Vercel deploy, set to: https://phonos-ai.vercel.app
    CORS_ORIGINS: str = "*"

    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # PostHog analytics
    POSTHOG_API_KEY: Optional[str] = None
    POSTHOG_HOST: str = "https://eu.i.posthog.com"

    # AI APIs — Nvidia NIM → Gemini → Groq (priority order)
    NVIDIA_API_KEY: Optional[str] = None
    NVIDIA_MODEL: str = "meta/llama-3.3-70b-instruct"
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    # Live Data & Pricing APIs
    MOBILEAPI_KEY: Optional[str] = None
    TECHSPECS_API_ID: Optional[str] = None
    TECHSPECS_API_KEY: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None
    APIFY_TOKEN: Optional[str] = None
    PRICE_CACHE_TTL_HOURS: int = 24

    _ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
    model_config = SettingsConfigDict(
        env_file=_ENV_PATH if os.path.exists(_ENV_PATH) else ".env",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
