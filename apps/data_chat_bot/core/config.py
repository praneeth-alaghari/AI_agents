"""
Configuration module for Data Chat Bot.
Uses st.secrets on Streamlit Cloud, falls back to .env for local development.
"""
import os
import urllib.parse

try:
    import streamlit as st
    _secrets = dict(st.secrets.get("postgres", {}))
    _ai_secrets = dict(st.secrets.get("openai", {}))
except Exception:
    _secrets = {}
    _ai_secrets = {}


class Settings:
    """Application settings — reads from st.secrets (cloud) or env vars (local)."""

    # PostgreSQL
    DB_USER: str = _secrets.get("DB_USER") or os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = _secrets.get("DB_PASSWORD") or os.getenv("DB_PASSWORD", "")
    DB_HOST: str = _secrets.get("DB_HOST") or os.getenv("DB_HOST", "localhost")
    DB_PORT: str = _secrets.get("DB_PORT") or os.getenv("DB_PORT", "5432")
    DB_NAME: str = _secrets.get("DB_NAME") or os.getenv("DB_NAME", "postgres")

    # OpenAI
    OPENAI_API_KEY: str = _ai_secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = _ai_secrets.get("OPENAI_MODEL") or os.getenv("OPENAI_MODEL", "gpt-4o")

    def get_db_url(self, db_name: str | None = None) -> str:
        """Build a PostgreSQL connection URL, optionally overriding the DB name."""
        encoded_password = urllib.parse.quote_plus(self.DB_PASSWORD)
        name = db_name or self.DB_NAME
        return f"postgresql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{name}"


settings = Settings()
