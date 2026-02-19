"""
Configuration module for Data Chat Bot backend.
Loads environment variables and provides typed settings.
"""
import os
from dotenv import load_dotenv

# Load .env from the backend directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


class Settings:
    """Application settings loaded from environment variables."""

    # PostgreSQL
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "postgres")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # App
    APP_NAME: str = os.getenv("APP_NAME", "DataChatBot")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    def get_db_url(self, db_name: str | None = None) -> str:
        """Build a PostgreSQL connection URL, optionally overriding the DB name."""
        import urllib.parse
        encoded_password = urllib.parse.quote_plus(self.DB_PASSWORD)
        name = db_name or self.DB_NAME
        return f"postgresql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{name}"


settings = Settings()
