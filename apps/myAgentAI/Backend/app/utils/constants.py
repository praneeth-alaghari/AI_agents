"""
myAgentAI - Application Constants
====================================
Central place for all magic strings, enums, and configuration constants.
"""

# ── Supported API Key Services ───────────────────────────
SUPPORTED_SERVICES = ["openai", "gmail"]
USER_ONLY_SERVICES = ["gmail"]           # No system fallback allowed
SYSTEM_FALLBACK_SERVICES = ["openai"]    # Uses system key if user doesn't provide one

# ── Email Priority Labels ────────────────────────────────
PRIORITY_LABELS = {
    1: "Critical",
    2: "High",
    3: "Medium",
    4: "Low",
    5: "Spam",
}

# ── Sections Registry ────────────────────────────────────
# PhonePe-style sections — add new sections here as the app grows
SECTIONS = {
    "personal_management": {
        "name": "Personal Management",
        "description": "Tools for managing your personal digital life",
        "utilities": ["email_housekeeper"],
    },
    # Future sections:
    # "career": {
    #     "name": "Career Tools",
    #     "description": "AI-powered career assistance",
    #     "utilities": ["resume_master"],
    # },
    # "finance": {
    #     "name": "Finance & Insurance",
    #     "description": "Financial management utilities",
    #     "utilities": ["insurance_assistant", "utility_bill_analyzer"],
    # },
}
