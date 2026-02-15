"""
myAgentAI - Application Configuration
======================================
Centralized settings loaded from environment variables.
Uses pydantic-settings for validation and type safety.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "myAgentAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/myagentai"

    # ── JWT Authentication ───────────────────────────────
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── OpenAI (System Default) ──────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ── Qdrant Vector DB ─────────────────────────────────
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # ── Reinforcement Thresholds ─────────────────────────
    AUTO_EXECUTE_THRESHOLD: float = 0.85
    SIMILARITY_BOOST_THRESHOLD: float = 0.9

    # ── Scoring Weights ──────────────────────────────────
    LLM_CONFIDENCE_WEIGHT: float = 0.6
    VECTOR_SIMILARITY_WEIGHT: float = 0.3
    RULE_WEIGHT: float = 0.1

    # ── Google OAuth ─────────────────────────────────────
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    DEFAULT_GMAIL_TOKEN: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — loaded once, reused everywhere."""
    return Settings()
