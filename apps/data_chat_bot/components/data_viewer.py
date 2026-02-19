"""
Paginated data viewer component.
Calls core.database directly. Uses @st.fragment so pagination clicks only
re-render this section.
"""
import streamlit as st
import pandas as pd
from core.database import get_table_data


@st.cache_data(ttl=60, show_spinner=False)
def _cached_table_data(db: str, table: str, page: int, page_size: int) -> dict:
    return get_table_data(db, table, page, page_size)


@st.fragment
def render_data_viewer():
    """Render paginated table data for the currently selected database + table."""
    db = st.session_state.get("selected_db")
    table = st.session_state.get("selected_table")

    if not db or not table:
        return

    st.markdown("---")
    st.markdown(f"### 📊 Data Preview — `{table}`")

    # ── Page size control ────────────────────────────────────────────────
    col_size, col_spacer = st.columns([1, 3])
    with col_size:
        page_size = st.number_input(
            "Rows per page",
            min_value=1,
            max_value=500,
            value=st.session_state.get("page_size", 10),
            step=5,
            key="page_size_input",
        )
        st.session_state["page_size"] = page_size

    # Track per-table page
    page_key = f"page_{db}_{table}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 1

    current_page = st.session_state[page_key]

    # ── Fetch data (cached) ──────────────────────────────────────────────
    try:
        data = _cached_table_data(db, table, page=current_page, page_size=page_size)
    except Exception as e:
        st.error(f"⚠️ Error loading data: {e}")
        return

    total_rows = data["total_rows"]
    total_pages = data["total_pages"]
    rows = data["rows"]
    columns = data["columns"]

    # ── Display table ────────────────────────────────────────────────────
    if rows:
        df = pd.DataFrame(rows, columns=columns)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("This table is empty.")

    # ── Pagination controls ──────────────────────────────────────────────
    pcol1, pcol2, pcol3, pcol4, pcol5 = st.columns([1, 1, 2, 1, 1])

    with pcol1:
        if st.button("⏮ First", disabled=(current_page <= 1), use_container_width=True):
            st.session_state[page_key] = 1

    with pcol2:
        if st.button("◀ Prev", disabled=(current_page <= 1), use_container_width=True):
            st.session_state[page_key] = max(1, current_page - 1)

    with pcol3:
        st.markdown(
            f"<div style='text-align:center; padding:8px 0; font-weight:600;'>"
            f"Page {current_page} of {total_pages} &nbsp;·&nbsp; {total_rows:,} rows"
            f"</div>",
            unsafe_allow_html=True,
        )

    with pcol4:
        if st.button("Next ▶", disabled=(current_page >= total_pages), use_container_width=True):
            st.session_state[page_key] = min(total_pages, current_page + 1)

    with pcol5:
        if st.button("Last ⏭", disabled=(current_page >= total_pages), use_container_width=True):
            st.session_state[page_key] = total_pages
