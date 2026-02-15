"""
myAgentAI - User Schemas
=========================
Pydantic models for user registration, login, and responses.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user data in API responses."""
    id: int
    email: str
    username: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class APIKeyCreate(BaseModel):
    """Schema for storing a user API key."""
    service_name: str = Field(
        ..., pattern="^(openai|gmail)$",
        description="Service name: 'openai' or 'gmail'"
    )
    api_key: str = Field(..., min_length=1)


class APIKeyResponse(BaseModel):
    """Schema for API key info (never exposes the actual key)."""
    id: int
    service_name: str
    is_set: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
