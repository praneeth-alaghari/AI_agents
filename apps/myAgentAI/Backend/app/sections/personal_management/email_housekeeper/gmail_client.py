from typing import Any, Dict, Optional
import google_auth_oauthlib.flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import json
import logging

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class GmailClient:
    """
    Wrapper for Gmail API with automatic token refreshing.
    Requires user's stored API key to be a valid JSON credentials string or Refresh Token.
    """

    def __init__(self, token_data: str):
        self.creds = None
        self.token_data = token_data
        self._load_credentials()

    def _load_credentials(self):
        """
        Load credentials from the stored token string.
        Logic:
        1. Try parsing as full JSON (access_token, refresh_token, etc.)
        2. If just a string, assume it's a raw access token (legacy/manual mode).
        """
        try:
            data = json.loads(self.token_data)
            
            # Inject Client Config if missing (Critical for Refresh)
            if 'client_id' not in data:
                data['client_id'] = settings.GOOGLE_CLIENT_ID
            if 'client_secret' not in data:
                data['client_secret'] = settings.GOOGLE_CLIENT_SECRET
            if 'token_uri' not in data:
                data['token_uri'] = "https://oauth2.googleapis.com/token"
            
            # If scopes are missing, add default
            if 'scopes' not in data:
                 data['scopes'] = ["https://www.googleapis.com/auth/gmail.modify"]

            self.creds = Credentials.from_authorized_user_info(data)
            
        except json.JSONDecodeError:
             # Fallback: Assume it's just a raw access token string
            logger.warning("Using raw access token. Refresh will not work.")
            self.creds = Credentials(token=self.token_data)

    def get_service(self):
        """Get the Gmail service resource, refreshing token if expired."""
        if not self.creds:
            raise ValueError("No credentials loaded")

        # Force refresh if expired or no valid token but we have refresh token
        if not self.creds.valid:
            if self.creds.refresh_token:
                try:
                    logger.info("Access token expired. Refreshing...")
                    self.creds.refresh(Request())
                    logger.info("Token refreshed successfully.")
                    # meaningful TODO: Update DB with new token if refresh happened
                except Exception as e:
                    logger.error(f"Failed to refresh token: {e}")
                    raise ValueError(f"Token refresh failed: {e}")
            else:
                 logger.warning("Token expired and no refresh token available.")

        return build('gmail', 'v1', credentials=self.creds)

    def fetch_emails(self, max_results: int = 50) -> list[Dict[str, Any]]:
        """Fetch emails from Inbox received in the last 24 hours."""
        try:
            service = self.get_service()
            
            # Calculate timestamp for 24 hours ago
            import time
            one_day_ago = int(time.time()) - (24 * 60 * 60)
            query = f"after:{one_day_ago} category:primary"
            # Added category:primary to avoid fetching 100s of promotions/social updates which clogs the demo
            
            logger.info(f"Fetching emails with query: {query}")
            
            results = service.users().messages().list(
                userId='me', 
                q=query,
                labelIds=['INBOX'], 
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} messages.")
            
            emails = []
            for msg in messages:
                try:
                    txt = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                    payload = txt.get('payload', {})
                    headers = payload.get('headers', [])
                    
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown)')
                    snippet = txt.get('snippet', '')
                    
                    emails.append({
                        "email_id": msg['id'],
                        "subject": subject,
                        "sender": sender,
                        "snippet": snippet
                    })
                except Exception as e:
                    logger.warning(f"Failed to fetch email details for {msg['id']}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Gmail API Error: {e}")
            raise

    def trash_email(self, email_id: str) -> bool:
        """Move an email to Trash."""
        try:
            service = self.get_service()
            service.users().messages().trash(userId='me', id=email_id).execute()
            logger.info(f"Email moved to trash: {email_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to trash email {email_id}: {e}")
            return False
