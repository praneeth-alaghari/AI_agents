"""
myAgentAI - Application Entry Point
======================================
FastAPI application with modular router registration.

Sections are organized like PhonePe-style categories:
  └── Personal Management
      └── Email Housekeeper

To add a new utility:
  1. Create a folder under the appropriate section in app/sections/
  2. Add models, schemas, service, router inside that folder
  3. Import and include the router below
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.response import error_response

# ── Core Routers ─────────────────────────────────────────
from app.routers.auth import router as auth_router
from app.routers.api_keys import router as api_keys_router

# ── Section Routers ──────────────────────────────────────
# Personal Management
from app.sections.personal_management.email_housekeeper.router import (
    router as email_housekeeper_router,
)

settings = get_settings()

# ── App Initialization ───────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "myAgentAI — A scalable, modular Multi-Utility AI SaaS platform. "
        "Personal AI assistant with pluggable utilities, reinforcement memory, "
        "and profile-based API key management."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── App Initialization ───────────────────────────────────

from app.db.init_db import init_models

@app.on_event("startup")
async def startup_event():
    """Run startup tasks."""
    print("🚀 App Starting Up...")
    await init_models()

# ── CORS Middleware ──────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler — no raw stack traces leak to the client."""
    return JSONResponse(
        status_code=500,
        content=error_response(
            message="Something went wrong. Please try again later."
        ),
    )


# ── Register Routers ────────────────────────────────────

# Core
app.include_router(auth_router)
app.include_router(api_keys_router)

# Personal Management section
app.include_router(email_housekeeper_router)

# Future sections — just add more include_router() calls here:
# app.include_router(resume_master_router)
# app.include_router(insurance_assistant_router)


# ── Health Check ─────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "success": True,
        "message": f"{settings.APP_NAME} is running",
        "data": {
            "version": settings.APP_VERSION,
            "sections": {
                "personal_management": {
                    "name": "Personal Management",
                    "utilities": ["email_housekeeper"],
                },
            },
        },
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "success": True,
        "message": "All systems operational",
        "data": {"status": "healthy", "version": settings.APP_VERSION},
    }
