"""
Central configuration for the whole backend.

Every other module reads settings from HERE, not from os.environ directly.
That way, if we ever change how config is loaded (e.g. add a secrets manager),
only this one file changes.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Which LLM provider is active: "gemini" | "openai" | "claude"
    llm_provider: str = "gemini"

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Claude
    anthropic_api_key: str = ""
    claude_model: str = "claude-3-5-sonnet-20241022"

    # App
    app_env: str = "development"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    database_url: str = "sqlite:///./study_buddy.db"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


# Import this singleton everywhere: `from app.config import settings`
settings = Settings()
