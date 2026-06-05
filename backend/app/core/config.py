from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Zuppa"
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"
    DEFAULT_USER: str = "zuppa"

    # Base de datos
    DATABASE_URL: str
    # LLM
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str = "openai/gpt-4o-mini"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"


settings = Settings()
