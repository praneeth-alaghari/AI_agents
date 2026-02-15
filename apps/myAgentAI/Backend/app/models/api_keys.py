"""
myAgentAI - User API Keys Model
==================================
Stores per-user API keys for external services (OpenAI, Gmail, etc.).
Rules:
  - OpenAI: Falls back to system default if user key not provided
  - Gmail:  MUST be user-provided (no fallback)
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserAPIKey(Base):
    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_name = Column(String(50), nullable=False)   # "openai" | "gmail"
    encrypted_key = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ── Constraints ──────────────────────────────────────
    __table_args__ = (
        UniqueConstraint("user_id", "service_name", name="uq_user_service"),
    )

    # ── Relationships ────────────────────────────────────
    user = relationship("User", back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<UserAPIKey(user_id={self.user_id}, service={self.service_name})>"
