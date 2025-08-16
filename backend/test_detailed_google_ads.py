#!/usr/bin/env python3
"""
Test Google Ads API connection with detailed error reporting
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

print("🔍 Detailed Google Ads API Connection Test")
print("=" * 50)

try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    
    # Get credentials
    developer_token = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_OAUTH_REFRESH_TOKEN")
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    login_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
    
    print(f"📋 Configuration:")
    print(f"   Developer Token: {developer_token[:20]}...")
    print(f"   Customer ID: {customer_id}")
    print(f"   Login Customer ID: {login_customer_id}")
    print(f"   Client ID: {client_id[:20]}...")
    
    # Create client configuration
    client_config = {
        "developer_token": developer_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "login_customer_id": login_customer_id,
        "use_proto_plus": True
    }
    
    print(f"\n🔧 Creating Google Ads client...")
    client = GoogleAdsClient.load_from_dict(client_config)
    print("✅ Client created successfully")
    
    print(f"\n🔗 Testing connection to customer {customer_id}...")
    ga_service = client.get_service("GoogleAdsService")
    
    # Try a simple query to test connection
    query = f"""
        SELECT customer.id, customer.descriptive_name
        FROM customer
        WHERE customer.id = {customer_id}
        LIMIT 1
    """
    
    response = ga_service.search(customer_id=customer_id, query=query)
    
    # Try to get results
    for row in response:
        account_name = row.customer.descriptive_name or "Unknown"
        print(f"✅ Connected to Google Ads account: {account_name} (ID: {customer_id})")
        print(f"\n🎉 Google Ads API connection is working!")
        break
    else:
        print(f"⚠️ No results found for customer ID: {customer_id}")
        
except GoogleAdsException as ex:
    print(f"❌ Google Ads API error:")
    print(f"   Request ID: {ex.request_id}")
    print(f"   Error: {ex}")
    
    for error in ex.failure.errors:
        print(f"   - Error Code: {error.error_code}")
        print(f"   - Message: {error.message}")
        
        # Check specific error types
        if hasattr(error.error_code, 'authorization_error'):
            if error.error_code.authorization_error.name == 'MISSING_TOS':
                print(f"\n💡 Solution: Sign Terms of Service")
                print(f"   1. Visit: https://ads.google.com/aw/apicenter")
                print(f"   2. Sign in with the Google account that has the developer token")
                print(f"   3. Accept the Google Ads API Terms of Service")
                print(f"   4. Wait 5-10 minutes for changes to take effect")
                
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🏁 Connection test complete!")