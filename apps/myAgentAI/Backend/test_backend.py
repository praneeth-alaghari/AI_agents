import requests
import json
import secrets

BASE_URL = "http://localhost:8000"

def test_backend():
    print("🚀 Starting Backend Health Check...")
    
    # 1. Health Check (if exists, or just root)
    try:
        resp = requests.get(f"{BASE_URL}/")
        print(f"✅ Root Endpoint: {resp.status_code}")
    except Exception as e:
        print(f"❌ Backend not reachable: {e}")
        return

    # 2. Register/Login User
    # Standard credentials matching frontend defaults/user expectations
    email = "user@example.com"
    password = "password"
    username = "user"
    
    print(f"\n🔐 Authenticating as {email}...")
    
    # Try Login first
    login_payload = {"email": email, "password": password}
    resp = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    
    token = None
    if resp.status_code == 200:
        print("✅ Login Successful")
        token = resp.json()["data"]["token"]["access_token"]
    else:
        print(f"⚠️ Login Failed ({resp.status_code}), trying Register...")
        # Try Register
        reg_payload = {"email": email, "password": password, "username": username}
        resp = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
        if resp.status_code in [200, 201]:
             print("✅ Registration Successful")
             token = resp.json()["data"]["token"]["access_token"]
        else:
             print(f"❌ Registration Failed: {resp.text}")
             return

    if not token:
        print("❌ Could not get Auth Token. Aborting.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 3. Run Email Housekeeper (Trigger Processing)
    print("\n🚀 Triggering Email Housekeeper Run...")
    try:
        run_payload = {"auto_mode": False, "max_emails": 5}
        resp = requests.post(f"{BASE_URL}/email/run", json=run_payload, headers=headers)
        if resp.status_code == 200:
             print("✅ POST /email/run: OK")
             print(f"   Processed: {resp.json()['data']['total_processed']}")
        else:
             print(f"❌ POST /email/run Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Error running housekeeper: {e}")

    # 4. Test Email Stats
    print("\n📊 Testing Email Stats Endpoint...")
    try:
        resp = requests.get(f"{BASE_URL}/email/stats", headers=headers)
        if resp.status_code == 200:
            print("✅ GET /email/stats: OK")
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"❌ GET /email/stats Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Error fetching stats: {e}")

    # 5. Test Email Review List
    print("\n📨 Testing Email Review List Endpoint...")
    try:
        resp = requests.get(f"{BASE_URL}/email/review", headers=headers)
        if resp.status_code == 200:
            print("✅ GET /email/review: OK")
            reviews = resp.json()['data']
            print(f"Found {len(reviews)} emails to review")
            
            if reviews:
                print("\n   --- Email Subjects ---")
                for email in reviews:
                    print(f"   • [{email['priority']}] {email['subject']} (Action: {email['suggested_action']})")
                print("   ----------------------")
            else:
                print("   (No low-confidence emails found to display subjects)")
                
        else:
            print(f"❌ GET /email/review Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Error fetching reviews: {e}")

if __name__ == "__main__":
    test_backend()
