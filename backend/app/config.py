from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    google_api_key: str
    llm_model: str = "gemini-2.5-flash"
    max_file_size_mb: int = 10
    max_correction_retries: int = 2
    ocr_confidence_threshold: float = 0.6
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_port: int = 3000
    log_level: str = "INFO"


settings = Settings()
