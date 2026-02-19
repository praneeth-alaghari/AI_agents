"""
API client for communicating with the FastAPI backend.
Uses @st.cache_data to avoid redundant network calls on Streamlit reruns.
"""
import requests
import streamlit as st

BASE_URL = "http://localhost:8000"


def _get(path: str, params: dict | None = None) -> dict:
    resp = requests.get(f"{BASE_URL}{path}", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _post(path: str, json_body: dict) -> dict:
    resp = requests.post(f"{BASE_URL}{path}", json=json_body, timeout=120)
    resp.raise_for_status()
    return resp.json()


# ─── Database endpoints (cached — these rarely change) ───────────────────────

@st.cache_data(ttl=300, show_spinner=False)  # cache for 5 minutes
def fetch_databases() -> list[str]:
    data = _get("/api/db/databases")
    return data.get("databases", [])


@st.cache_data(ttl=300, show_spinner=False)  # cache for 5 minutes
def fetch_tables(db_name: str) -> list[str]:
    data = _get(f"/api/db/tables/{db_name}")
    return [t["table_name"] for t in data.get("tables", [])]


@st.cache_data(ttl=60, show_spinner=False)  # cache for 1 minute
def fetch_table_data(db_name: str, table_name: str, page: int = 1, page_size: int = 10) -> dict:
    return _get(
        f"/api/db/data/{db_name}/{table_name}",
        params={"page": page, "page_size": page_size},
    )


# ─── Chat endpoint (never cached — each question is unique) ─────────────────

def ask_question(question: str, db_name: str, table_name: str) -> dict:
    return _post("/api/chat/ask", {
        "question": question,
        "db_name": db_name,
        "table_name": table_name,
    })
