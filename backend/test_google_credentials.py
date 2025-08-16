#!/usr/bin/env python3
"""
Test Google Ads credentials loading and OAuth token generation
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

print("🔍 Testing Google Ads credentials loading...")
print("=" * 50)

# Check environment variables
developer_token = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET") 
refresh_token = os.getenv("GOOGLE_OAUTH_REFRESH_TOKEN")
customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

print(f"✅ Developer Token: {'✓' if developer_token else '✗'} ({developer_token[:20] if developer_token else 'Missing'}...)")
print(f"✅ Client ID: {'✓' if client_id else '✗'} ({client_id[:20] if client_id else 'Missing'}...)")
print(f"✅ Client Secret: {'✓' if client_secret else '✗'} ({client_secret[:10] if client_secret else 'Missing'}...)")
print(f"✅ Refresh Token: {'✓' if refresh_token else '✗'} ({refresh_token[:20] if refresh_token else 'Missing'}...)")
print(f"✅ Customer ID: {'✓' if customer_id else '✗'} ({customer_id if customer_id else 'Missing'})")

print("\n🔄 Testing OAuth token refresh...")

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    
    # Create credentials object
    credentials = Credentials(
        token=None,  # Access token will be refreshed
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",  # Required for token refresh
        client_id=client_id,
        client_secret=client_secret
    )
    
    print("🔧 Created OAuth credentials object")
    
    # Try to refresh the token
    print("🔄 Attempting to refresh access token...")
    credentials.refresh(Request())
    
    print("✅ Successfully refreshed access token!")
    print(f"   New access token (first 20 chars): {credentials.token[:20]}...")
    
except Exception as e:
    print(f"❌ OAuth token refresh failed: {e}")
    print()
    print("💡 Possible solutions:")
    print("   1. The refresh token may have expired (they expire after 6 months of no use)")
    print("   2. The OAuth client credentials may be incorrect")
    print("   3. The Google Ads account may need re-authentication")
    print()
    print("🔧 To get a new refresh token:")
    print("   1. Visit: https://developers.google.com/oauthplayground/")
    print("   2. Use your OAuth credentials")
    print("   3. Authorize Google Ads API scope: https://www.googleapis.com/auth/adwords")
    print("   4. Exchange for new refresh token")

print("\n" + "=" * 50)
print("🏁 Credential test complete!")