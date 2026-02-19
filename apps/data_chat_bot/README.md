# 🗃️💬 Data Chat Bot

A web application that lets you **talk to your PostgreSQL databases** using natural language. Built with Streamlit, deployable to Streamlit Cloud Community.

## Features

- 📊 **Database Explorer** – Browse databases, tables, and paginated data
- 💬 **Natural Language Chat** – Ask questions in plain English, get SQL + results
- 🔄 **Dynamic Pagination** – Configure rows-per-page, navigate with Next/Previous
- 📱 **Responsive UI** – Works on desktop and mobile
- ☁️ **Cloud Ready** – Deploy to Streamlit Cloud in minutes

## Project Structure

```
data_chat_bot/
├── app.py                    # Main Streamlit entry point
├── requirements.txt          # All dependencies
├── .streamlit/
│   ├── config.toml           # Theme & server config
│   ├── secrets.toml          # Local secrets (gitignored)
│   └── secrets.toml.example  # Template for secrets
├── core/                     # Business logic
│   ├── config.py             # Settings (st.secrets + env fallback)
│   ├── database.py           # PostgreSQL operations
│   └── text_to_sql.py        # NL → SQL → Summary pipeline
├── components/               # Streamlit UI components
│   ├── header.py             # Logo & branding
│   ├── db_explorer.py        # Database/table dropdowns
│   ├── data_viewer.py        # Paginated table viewer
│   └── chat_interface.py     # WhatsApp-style chat
├── assets/
│   └── styles.css            # Custom CSS
├── backend/                  # (Optional) Standalone FastAPI backend
└── frontend/                 # (Optional) Original frontend w/ API client
```

## Local Development

```bash
cd apps/data_chat_bot

# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your secrets to .streamlit/secrets.toml (copy from .example)

# 3. Run
streamlit run app.py
```

## Streamlit Cloud Deployment

See the deployment steps in the README or follow the guide provided.
