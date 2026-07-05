from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    APPWRITE_ENDPOINT: str
    APPWRITE_PROJECT_ID: str
    APPWRITE_API_KEY: str
    APPWRITE_BUCKET_ID: str
    
    MAX_FILE_SIZE_MB: int = 10
    SUPPORTED_FORMATS: list[str] = ["image/jpeg", "image/png", "image/webp"]

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()