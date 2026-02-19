"""
WhatsApp-style chat interface component.
User messages on the right, agent responses on the left, scrollable history.
Uses @st.fragment so sending a message only re-renders the chat section —
the header, dropdowns, and data viewer stay untouched (no dimming/reload).
"""
import streamlit as st
import pandas as pd
from services.api_client import ask_question


def _init_chat_state():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []


@st.fragment
def render_chat_interface():
    """Render the chat panel below the data viewer."""
    db = st.session_state.get("selected_db")
    table = st.session_state.get("selected_table")

    if not db or not table:
        return

    _init_chat_state()

    st.markdown("---")
    st.markdown("### 💬 Chat with your Data")
    st.caption(f"Ask questions about **{table}** in **{db}** — powered by AI")

    # ── Chat history (scrollable container via CSS) ──────────────────────
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-window">', unsafe_allow_html=True)
        for msg in st.session_state["chat_history"]:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-row user-row">'
                    f'<div class="chat-bubble user-bubble">{msg["content"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                # Agent message
                content = msg["content"]
                sql = msg.get("sql")

                bubble_html = f'<div class="chat-row agent-row"><div class="chat-bubble agent-bubble">'
                if sql:
                    bubble_html += f'<div class="sql-badge">SQL</div><code class="sql-code">{sql}</code><br/>'
                bubble_html += f'{content}</div></div>'
                st.markdown(bubble_html, unsafe_allow_html=True)

                # If there are tabular results, render them as a DataFrame
                raw = msg.get("raw_results")
                if raw and isinstance(raw, dict) and raw.get("rows"):
                    df = pd.DataFrame(raw["rows"], columns=raw.get("columns", []))
                    st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Input ────────────────────────────────────────────────────────────
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_input = st.text_input(
                "Message",
                placeholder="Ask a question about your data…",
                label_visibility="collapsed",
            )
        with col_btn:
            submitted = st.form_submit_button("Send ➤", use_container_width=True)

    if submitted and user_input.strip():
        # Append user message
        st.session_state["chat_history"].append({
            "role": "user",
            "content": user_input.strip(),
        })

        # Call backend
        with st.spinner("🤖 Thinking…"):
            try:
                resp = ask_question(user_input.strip(), db, table)
                st.session_state["chat_history"].append({
                    "role": "agent",
                    "content": resp.get("summary", "No response."),
                    "sql": resp.get("sql"),
                    "raw_results": resp.get("raw_results"),
                })
            except Exception as e:
                st.session_state["chat_history"].append({
                    "role": "agent",
                    "content": f"⚠️ Error: {e}",
                })

        # Fragment reruns only this section — no full page reload!
        st.rerun(scope="fragment")
