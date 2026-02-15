import json
from app.core.config import get_settings

def check_token():
    settings = get_settings()
    token_str = settings.DEFAULT_GMAIL_TOKEN
    
    if not token_str:
        print("❌ No Default Token found in settings.")
        return

    try:
        data = json.loads(token_str)
        scopes = data.get('scopes', [])
        
        print("\n🔍 Token Analysis:")
        print(f"   Client ID: {data.get('client_id', 'Unknown')[:10]}...")
        print(f"   Scopes Found: {scopes}")
        
        required_scope = "https://www.googleapis.com/auth/gmail.modify"
        
        if required_scope in scopes:
            print("\n✅ Token has WRITE access (gmail.modify). Deletion SHOULD work.")
        else:
            print("\n❌ Token is READ-ONLY or missing 'gmail.modify' scope.")
            print("   Deletion will FAIL with 403 Forbidden.")
            print("   👉 Please run `python generate_token.py` and replace the token in `app/core/config.py`.")
            
    except json.JSONDecodeError:
        print("⚠️ Token is not valid JSON. Cannot verify scopes.")

if __name__ == "__main__":
    check_token()
