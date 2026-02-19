"""
Database explorer component — database & table selection dropdowns.
Calls core.database directly (no HTTP API layer).
"""
import streamlit as st
from core.database import list_databases, list_tables


@st.cache_data(ttl=300, show_spinner=False)
def _cached_databases() -> list[str]:
    return list_databases()


@st.cache_data(ttl=300, show_spinner=False)
def _cached_tables(db_name: str) -> list[str]:
    return list_tables(db_name)


def render_db_explorer():
    """
    Render the database and table selector.
    Stores selected db/table in ``st.session_state``.
    """
    col1, col2 = st.columns(2)

    # ── Database selector ────────────────────────────────────────────────
    with col1:
        try:
            databases = _cached_databases()
        except Exception as e:
            st.error(f"⚠️ Cannot connect to database: {e}")
            return

        if not databases:
            st.warning("No databases found.")
            return

        selected_db = st.selectbox(
            "🗄️ Select Database",
            options=databases,
            index=databases.index(st.session_state.get("selected_db", databases[0]))
            if st.session_state.get("selected_db") in databases
            else 0,
            key="db_selector",
        )
        st.session_state["selected_db"] = selected_db

    # ── Table selector ───────────────────────────────────────────────────
    with col2:
        if selected_db:
            try:
                tables = _cached_tables(selected_db)
            except Exception as e:
                st.error(f"⚠️ Error listing tables: {e}")
                return

            if not tables:
                st.info("No tables found in this database.")
                return

            selected_table = st.selectbox(
                "📋 Select Table",
                options=tables,
                index=tables.index(st.session_state.get("selected_table", tables[0]))
                if st.session_state.get("selected_table") in tables
                else 0,
                key="table_selector",
            )
            st.session_state["selected_table"] = selected_table
