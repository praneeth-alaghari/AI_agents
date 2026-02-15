"""
Email Housekeeper - ORM Models
================================
Database models for email records and user feedback.
"""

import enum
from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, Text, ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


# ── Enums ─────────────────────────────────────────────────

class EmailPriority(enum.IntEnum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    SPAM = 5


class EmailAction(str, enum.Enum):
    KEEP = "keep"
    DELETE = "delete"
    REVIEW = "needs_review"


# ── Email Record ─────────────────────────────────────────

class EmailRecord(Base):
    __tablename__ = "email_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email_id = Column(String(255), nullable=False)
    subject = Column(String(500))
    sender = Column(String(255))
    snippet = Column(Text)

    # Classification results
    priority = Column(Integer, default=3)
    action = Column(String(20), default=EmailAction.REVIEW.value)

    # Scoring breakdown
    llm_confidence = Column(Float, default=0.0)
    vector_similarity = Column(Float, default=0.0)
    rule_weight = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0)

    auto_executed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="email_records")

    def __repr__(self) -> str:
        return f"<EmailRecord(id={self.id}, subject={self.subject[:30]})>"


# ── Feedback Record ──────────────────────────────────────

class FeedbackRecord(Base):
    __tablename__ = "feedback_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email_record_id = Column(
        Integer,
        ForeignKey("email_records.id", ondelete="CASCADE"),
        nullable=False,
    )
    original_action = Column(String(20), nullable=False)
    user_action = Column(String(20), nullable=False)
    is_override = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="feedback_records")
    email_record = relationship("EmailRecord")

    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, override={self.is_override})>"
