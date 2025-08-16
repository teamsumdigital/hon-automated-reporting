#!/usr/bin/env python3
"""
Exchange authorization code for Google OAuth refresh token
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

# Authorization code from the URL
auth_code = "4/0AVMBsJgRNZiVYfDwMF9s3bMOEDRMQUnMzczyinPr-0Zqh_tCxxJmC3F9jenclj9I24OGZg"

print("🔄 Exchanging authorization code for refresh token...")
print("=" * 50)

try:
    # Exchange authorization code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": auth_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": "http://localhost",
        "grant_type": "authorization_code"
    }
    
    print("📡 Sending token exchange request...")
    response = requests.post(token_url, data=token_data)
    
    if response.status_code == 200:
        tokens = response.json()
        refresh_token = tokens.get("refresh_token")
        access_token = tokens.get("access_token")
        expires_in = tokens.get("expires_in", 3600)
        
        print("✅ Successfully obtained tokens!")
        print(f"\n🔑 NEW REFRESH TOKEN:")
        print(refresh_token)
        print(f"\n💡 Access Token (expires in {expires_in} seconds):")
        print(access_token[:50] + "...")
        
        print(f"\n📝 UPDATE YOUR .env FILE WITH:")
        print("=" * 40)
        print(f"GOOGLE_OAUTH_REFRESH_TOKEN={refresh_token}")
        print("=" * 40)
        
        # Test the refresh token
        print(f"\n🧪 Testing refresh token...")
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        
        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Try to refresh to get a new access token
        credentials.refresh(Request())
        print("✅ Refresh token is working perfectly!")
        print(f"   New access token: {credentials.token[:30]}...")
        
    else:
        print(f"❌ Token exchange failed: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🏁 Token exchange complete!")