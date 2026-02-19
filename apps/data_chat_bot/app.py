"""
Data Chat Bot — Main Streamlit Application
=============================================
Run locally:
    cd apps/data_chat_bot
    streamlit run app.py

Deploy to Streamlit Cloud:
    Main file path: apps/data_chat_bot/app.py
"""
import os
import streamlit as st

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Data ChatBot — Talk to your Database",
    page_icon="🗃️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Load custom CSS ─────────────────────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Additional inline styles for Streamlit overrides ────────────────────────
st.markdown(
    """
    <style>
    /* Hide default Streamlit header & footer for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Give the main block some breathing room */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 1100px;
    }

    /* Selectbox & number input styling */
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        border-radius: 10px !important;
    }

    /* Button styling */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(99,102,241,0.3) !important;
    }

    /* Dataframe tweaks */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden;
    }

    /* Form submit button */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }
    .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #4F46E5, #7C3AED) !important;
        transform: translateY(-1px) !important;
    }

    /* Text input */
    .stTextInput > div > div > input {
        border-radius: 10px !important;
        padding: 10px 14px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Import & render components ──────────────────────────────────────────────
from components.header import render_header
from components.db_explorer import render_db_explorer
from components.data_viewer import render_data_viewer
from components.chat_interface import render_chat_interface

render_header()
render_db_explorer()
render_data_viewer()
render_chat_interface()
