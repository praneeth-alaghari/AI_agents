import json
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from app.core.config import get_settings

# Suppress oauthlib logs
logging.getLogger('google_auth_oauthlib').setLevel(logging.ERROR)

def generate_token():
    settings = get_settings()
    
    print("🚀 Starting Google OAuth Token Generator...")
    print(f"   Client ID: {settings.GOOGLE_CLIENT_ID[:15]}...")
    
    # Scopes needed for the app
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    
    # Create OAuth Flow
    try:
        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {  # treating as installed app for local flow
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"]
                }
            },
            scopes=SCOPES
        )
        
        print("\n🌐 Opening browser for authentication...")
        print("⚠️ IMPORTANT: Ensure 'http://localhost:8080/' is added to 'Authorized redirect URIs' in Google Cloud Console.")
        
        # Run local server on port 8080 to match a fixed redirect URI
        creds = flow.run_local_server(port=8080)
        
        # Build the JSON string for config
        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "scopes": SCOPES
        }
        
        json_output = json.dumps(token_data).replace('"', '\\"') # Escape quotes for Python string
        
        print("\n✅ Authentication Successful!")
        print("-" * 80)
        print("👇 COPY THIS COMPLETE STRING (including single quotes) into `config.py`:")
        print("-" * 80)
        print(f"'{json.dumps(token_data)}'")
        print("-" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during OAuth flow: {e}")
        print("Tip: If using 'Web Application' credentials, allow 'http://localhost' authorized entry.")

if __name__ == "__main__":
    generate_token()
