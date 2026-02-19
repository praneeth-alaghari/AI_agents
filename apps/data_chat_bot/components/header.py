"""
Header component — renders the logo and app title.
Uses an inline SVG so no external image files are needed.
"""
import streamlit as st


def render_header():
    """Render the app header with a 'talking to data' logo."""
    st.markdown(
        """
        <div class="app-header">
            <div class="logo-container">
                <svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg" class="logo-svg">
                    <!-- Database icon -->
                    <defs>
                        <linearGradient id="dbGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#6366F1;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#8B5CF6;stop-opacity:1" />
                        </linearGradient>
                        <linearGradient id="chatGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#06B6D4;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <!-- DB cylinder -->
                    <ellipse cx="40" cy="22" rx="22" ry="8" fill="url(#dbGrad)" opacity="0.8"/>
                    <rect x="18" y="22" width="44" height="32" fill="url(#dbGrad)" opacity="0.9"/>
                    <ellipse cx="40" cy="54" rx="22" ry="8" fill="url(#dbGrad)"/>
                    <ellipse cx="40" cy="38" rx="22" ry="8" fill="url(#dbGrad)" opacity="0.5"/>
                    <ellipse cx="40" cy="22" rx="22" ry="8" fill="url(#dbGrad)" opacity="0.7"/>
                    <!-- Chat bubble -->
                    <rect x="72" y="12" rx="12" ry="12" width="52" height="36" fill="url(#chatGrad)" opacity="0.9"/>
                    <polygon points="78,48 86,48 72,60" fill="url(#chatGrad)" opacity="0.9"/>
                    <!-- Chat dots -->
                    <circle cx="88" cy="30" r="3" fill="white" opacity="0.9"/>
                    <circle cx="98" cy="30" r="3" fill="white" opacity="0.9"/>
                    <circle cx="108" cy="30" r="3" fill="white" opacity="0.9"/>
                    <!-- App name -->
                    <text x="132" y="38" font-family="'Inter', sans-serif" font-size="16" font-weight="700" fill="url(#dbGrad)">Data</text>
                    <text x="132" y="56" font-family="'Inter', sans-serif" font-size="16" font-weight="700" fill="url(#chatGrad)">ChatBot</text>
                </svg>
            </div>
            <p class="tagline">Talk to your PostgreSQL databases in plain English</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
