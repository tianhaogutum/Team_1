from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Runtime configuration for the FastAPI service.
    """

    app_name: str = Field(default="Rec Lab API")
    version: str = Field(default="0.1.0")

    # Database configuration (Supabase PostgreSQL)
    # Format: postgresql+asyncpg://postgres:[password]@[host]:[port]/postgres
    # Get this from Supabase: Settings -> Database -> Connection string (URI format)
    database_url: SecretStr | None = Field(
        default=None,
        env="DATABASE_URL",
        description="PostgreSQL connection string for Supabase. Format: postgresql+asyncpg://postgres:[password]@[host]:5432/postgres"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Allow extra fields (like old SUPABASE_URL) without errors
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: SecretStr | None) -> SecretStr:
        if v is None:
            raise ValueError(
                "DATABASE_URL is required. "
                "Please set it in your .env file. "
                "Get it from Supabase: Settings -> Database -> Connection string (URI format). "
                "Then change 'postgresql://' to 'postgresql+asyncpg://'"
            )
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Cached accessor for application settings.
    """
    return Settings()

