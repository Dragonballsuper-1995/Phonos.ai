import posthog as _posthog_lib
from app.core.config import settings

posthog = _posthog_lib

def init_posthog() -> None:
    if not settings.POSTHOG_API_KEY:
        return
    posthog.project_api_key = settings.POSTHOG_API_KEY
    posthog.host = settings.POSTHOG_HOST
    posthog.disabled = False

def shutdown_posthog() -> None:
    try:
        posthog.shutdown()
    except Exception:
        pass
