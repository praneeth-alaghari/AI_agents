# myAgentAI — Backend

> A scalable, modular Multi-Utility AI SaaS platform.

## 🏗 Architecture

```
app/
├── main.py                          # FastAPI entry point
├── core/                            # Shared infrastructure
│   ├── config.py                    # Environment settings (pydantic-settings)
│   ├── security.py                  # JWT auth, password hashing
│   └── response.py                  # Standard { success, message, data } wrapper
├── db/
│   ├── base.py                      # SQLAlchemy declarative base
│   └── session.py                   # Async engine + session factory
├── models/                          # Shared ORM models
│   ├── user.py                      # User model
│   └── api_keys.py                  # Per-user API key storage
├── schemas/                         # Shared Pydantic schemas
│   ├── user.py                      # Auth request/response schemas
│   └── response.py                  # Standard response schema
├── services/                        # Shared services
│   └── openai_service.py            # Async OpenAI client
├── routers/                         # Core API routers
│   ├── auth.py                      # POST /auth/register, /auth/login
│   └── api_keys.py                  # CRUD /api-keys
├── sections/                        # 📱 PhonePe-style app sections
│   └── personal_management/
│       └── email_housekeeper/       # Self-contained utility module
│           ├── models.py            # EmailRecord, FeedbackRecord
│           ├── schemas.py           # Request/response schemas
│           ├── router.py            # POST /email/run, GET /email/stats, etc.
│           ├── service.py           # Business logic pipeline
│           ├── classifier.py        # LLM-based email classifier
│           ├── reinforcement.py     # Memory-augmented reinforcement
│           └── vector_service.py    # Qdrant vector memory (user-scoped)
└── utils/
    ├── scoring.py                   # Hybrid scoring formula
    └── constants.py                 # App constants & section registry
```

## 🚀 Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and configure environment
copy .env.example .env

# 4. Run the server
uvicorn app.main:app --reload --port 8000
```

## 📡 API Endpoints

| Method | Endpoint          | Description                          |
|--------|-------------------|--------------------------------------|
| POST   | /auth/register    | Create a new user account            |
| POST   | /auth/login       | Login and get JWT token              |
| POST   | /api-keys/        | Store an API key (openai/gmail)      |
| GET    | /api-keys/        | List stored API keys                 |
| DELETE | /api-keys/{name}  | Delete an API key                    |
| POST   | /email/run        | Process emails through AI pipeline   |
| GET    | /email/stats      | 24h processing statistics            |
| GET    | /email/review     | Low-confidence emails for review     |
| POST   | /email/feedback   | Submit feedback for reinforcement    |

## 🧠 Reinforcement Scoring

```
final_score = (LLM confidence × 0.6)
            + (vector similarity × 0.3)
            + (rule weight × 0.1)

If final_score > 0.85 → Auto-execute
Else → Mark as needs_review
```

## 🔌 Adding a New Utility

1. Create a folder: `app/sections/<section_name>/<utility_name>/`
2. Add: `models.py`, `schemas.py`, `service.py`, `router.py`
3. Import router in `app/main.py`
4. Done! No core code changes needed.

## ⚙ Tech Stack

- **FastAPI** — Async web framework
- **PostgreSQL** + **SQLAlchemy** — Relational database
- **Qdrant** — Vector similarity database
- **OpenAI** — LLM classification + embeddings
- **JWT** — Authentication
- **Pydantic** — Validation
