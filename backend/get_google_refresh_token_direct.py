#!/usr/bin/env python3
"""
Generate Google Ads OAuth refresh token using direct OAuth flow
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

print("🔑 Google Ads OAuth Token Generator")
print("=" * 50)

print("\n📋 Step 1: Visit this URL in your browser:")
print("=" * 50)

oauth_url = f"""https://accounts.google.com/o/oauth2/auth?client_id={client_id}&redirect_uri=http://localhost&scope=https://www.googleapis.com/auth/adwords&response_type=code&access_type=offline&prompt=consent"""

print(oauth_url)

print("\n📋 Step 2: Authorization Steps:")
print("1. Click the URL above")
print("2. Sign in with your Google Ads account")
print("3. Grant permissions to the app")
print("4. You'll be redirected to a localhost URL that won't load")
print("5. Copy the 'code' parameter from the URL")
print("   Example: http://localhost/?code=4/XXXXXXX&scope=...")
print("   Copy everything after 'code=' and before '&'")

print("\n📋 Step 3: Paste the authorization code here:")
auth_code = input("Authorization code: ").strip()

if not auth_code:
    print("❌ No authorization code provided. Exiting.")
    exit(1)

print(f"\n🔄 Exchanging authorization code for tokens...")

try:
    import requests
    
    # Exchange authorization code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": auth_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": "http://localhost",
        "grant_type": "authorization_code"
    }
    
    response = requests.post(token_url, data=token_data)
    
    if response.status_code == 200:
        tokens = response.json()
        refresh_token = tokens.get("refresh_token")
        access_token = tokens.get("access_token")
        
        print("✅ Successfully obtained tokens!")
        print(f"\n🔑 Refresh Token:")
        print(refresh_token)
        print(f"\n💡 Access Token (expires in 1 hour):")
        print(access_token[:50] + "...")
        
        print(f"\n📝 Update your .env file:")
        print(f"GOOGLE_OAUTH_REFRESH_TOKEN={refresh_token}")
        
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
        
        # Refresh to get a new access token
        credentials.refresh(Request())
        print("✅ Refresh token is working!")
        
    else:
        print(f"❌ Token exchange failed: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("🏁 Token generation complete!")