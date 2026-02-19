"""
Database connection & utility module.
Handles all direct PostgreSQL interactions: listing databases, tables,
fetching rows with pagination, executing arbitrary SQL, and schema introspection.
"""
from typing import Any
from sqlalchemy import create_engine, text, inspect
from core.config import settings


def _engine(db_name: str | None = None):
    """Create a SQLAlchemy engine for the given database."""
    return create_engine(settings.get_db_url(db_name))


# ─── Database listing ───────────────────────────────────────────────────────

def list_databases() -> list[str]:
    """Return the list of non-template databases the user can connect to."""
    engine = _engine()
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;")
        )
        return [row[0] for row in result.fetchall()]


# ─── Table listing ──────────────────────────────────────────────────────────

def list_tables(db_name: str) -> list[str]:
    """Return table names in the *public* schema of the given database."""
    engine = _engine(db_name)
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' "
            "ORDER BY table_name;"
        ))
        return [row[0] for row in result.fetchall()]


# ─── Table row count ────────────────────────────────────────────────────────

def get_table_row_count(db_name: str, table_name: str) -> int:
    """Return the total number of rows in a table."""
    engine = _engine(db_name)
    with engine.connect() as conn:
        result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}";'))
        return result.scalar()


# ─── Paginated data fetch ───────────────────────────────────────────────────

def get_table_data(
    db_name: str,
    table_name: str,
    page: int = 1,
    page_size: int = 10,
) -> dict[str, Any]:
    """
    Return paginated rows from a table.

    Returns dict with: columns, rows, total_rows, page, page_size, total_pages
    """
    engine = _engine(db_name)
    total_rows = get_table_row_count(db_name, table_name)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    offset = (page - 1) * page_size

    with engine.connect() as conn:
        result = conn.execute(
            text(f'SELECT * FROM "{table_name}" LIMIT :limit OFFSET :offset'),
            {"limit": page_size, "offset": offset},
        )
        columns = list(result.keys())
        rows = [_serialize_row(dict(zip(columns, row))) for row in result.fetchall()]

    return {
        "columns": columns,
        "rows": rows,
        "total_rows": total_rows,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ─── Schema introspection ──────────────────────────────────────────────────

def get_table_schema(db_name: str, table_name: str) -> str:
    """Return a human-readable schema description for the LLM prompt."""
    engine = _engine(db_name)
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    lines = [f'Table: {table_name}', 'Columns:']
    for col in columns:
        lines.append(f'  - "{col["name"]}" ({col["type"]})')
    return "\n".join(lines)


# ─── Arbitrary SQL execution ───────────────────────────────────────────────

def execute_raw_sql(db_name: str, sql: str) -> dict[str, Any]:
    """Execute a raw SQL query and return results."""
    engine = _engine(db_name)
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        if result.returns_rows:
            columns = list(result.keys())
            rows = [_serialize_row(dict(zip(columns, row))) for row in result.fetchall()]
            return {"columns": columns, "rows": rows, "row_count": len(rows)}
        else:
            return {"message": "Query executed successfully (no rows returned)."}


# ─── Date range helper ──────────────────────────────────────────────────────

def get_date_range(db_name: str, table_name: str) -> str | None:
    """Try to find date columns and return their min/max values for LLM context."""
    engine = _engine(db_name)
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    date_cols = [
        col["name"]
        for col in columns
        if "date" in str(col["type"]).lower() or "timestamp" in str(col["type"]).lower()
    ]
    if not date_cols:
        return None

    parts = []
    with engine.connect() as conn:
        for dc in date_cols:
            try:
                result = conn.execute(
                    text(f'SELECT MIN("{dc}"), MAX("{dc}") FROM "{table_name}";')
                )
                min_val, max_val = result.fetchone()
                if min_val and max_val:
                    parts.append(f'Column "{dc}" ranges from {min_val} to {max_val}.')
            except Exception:
                pass
    return " ".join(parts) if parts else None


# ─── Helpers ────────────────────────────────────────────────────────────────

def _serialize_row(row: dict) -> dict:
    """Make every value JSON-serializable."""
    out = {}
    for k, v in row.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        elif isinstance(v, (bytes, bytearray)):
            out[k] = v.hex()
        else:
            out[k] = v
    return out
