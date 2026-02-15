"""
myAgentAI - Authentication Router
====================================
Handles user registration and login with JWT tokens.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import hash_password, verify_password, create_access_token
from app.core.response import success_response, error_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""

    # Check existing email
    existing = await db.execute(select(User).where(User.email == user_data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_response(message="An account with this email already exists"),
        )

    # Check existing username
    existing_usr = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if existing_usr.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_response(message="This username is already taken"),
        )

    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )
    db.add(user)
    await db.flush()

    token = create_access_token(data={"sub": str(user.id)})

    return success_response(
        message="Account created successfully",
        data={
            "user": UserResponse.model_validate(user).model_dump(),
            "token": TokenResponse(access_token=token).model_dump(),
        },
    )


@router.post("/login")
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login with email and password. Returns JWT token."""

    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response(message="Invalid email or password"),
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response(message="Account is deactivated"),
        )

    token = create_access_token(data={"sub": str(user.id)})

    return success_response(
        message="Login successful",
        data={
            "user": UserResponse.model_validate(user).model_dump(),
            "token": TokenResponse(access_token=token).model_dump(),
        },
    )
