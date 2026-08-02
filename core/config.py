from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    APPWRITE_ENDPOINT: str
    APPWRITE_PROJECT_ID: str
    APPWRITE_API_KEY: str
    APPWRITE_BUCKET_ID: str
    
    MAX_FILE_SIZE_MB: int = 10
    SUPPORTED_FORMATS: list[str] = ["image/jpeg", "image/png", "image/webp"]

    # No timeout was previously set on any Gemini API call — in production,
    # if that call (or the network path to Google's API) is slow or hangs,
    # this service would just wait indefinitely and never respond at all.
    # That's indistinguishable from a dead service to anything calling this
    # API (e.g. it's what produces an ETIMEDOUT with zero response on the
    # Node backend's side, which is much less diagnosable than a clean
    # 504-style failure from here).
    GEMINI_TIMEOUT_SECONDS: int = 50

    # Same reasoning, for Appwrite Storage uploads (see services/appwrite_service.py).
    APPWRITE_TIMEOUT_SECONDS: int = 20

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()