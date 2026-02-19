"""
Database exploration API router.
Endpoints for listing databases, tables, and fetching paginated data.
"""
from fastapi import APIRouter, HTTPException, Query

from app.database import (
    list_databases,
    list_tables,
    get_table_data,
    get_table_row_count,
)

router = APIRouter(prefix="/api/db", tags=["Database"])


@router.get("/databases")
def get_databases():
    """List all available PostgreSQL databases."""
    try:
        dbs = list_databases()
        return {"databases": dbs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables/{db_name}")
def get_tables(db_name: str):
    """List all tables in the public schema of the given database."""
    try:
        tables = list_tables(db_name)
        return {"database": db_name, "tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/{db_name}/{table_name}")
def get_data(
    db_name: str,
    table_name: str,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=1000, description="Rows per page"),
):
    """Fetch paginated rows from a table."""
    try:
        data = get_table_data(db_name, table_name, page, page_size)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/count/{db_name}/{table_name}")
def get_count(db_name: str, table_name: str):
    """Get total row count for a table."""
    try:
        count = get_table_row_count(db_name, table_name)
        return {"table": table_name, "total_rows": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
