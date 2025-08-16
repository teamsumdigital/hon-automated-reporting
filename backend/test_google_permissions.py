#!/usr/bin/env python3
"""
Test different levels of Google Ads API permissions
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

print("🔍 Testing Google Ads API Permission Levels")
print("=" * 50)

try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    
    # Initialize client
    developer_token = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_OAUTH_REFRESH_TOKEN")
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    login_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
    
    client_config = {
        "developer_token": developer_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "login_customer_id": login_customer_id,
        "use_proto_plus": True
    }
    
    client = GoogleAdsClient.load_from_dict(client_config)
    ga_service = client.get_service("GoogleAdsService")
    
    print("✅ Client initialized successfully")
    
    # Test 1: Basic customer access (this should work)
    print(f"\n🧪 Test 1: Basic customer information")
    try:
        query = f"SELECT customer.id, customer.descriptive_name FROM customer WHERE customer.id = {customer_id}"
        response = ga_service.search(customer_id=customer_id, query=query)
        for row in response:
            print(f"✅ Customer access works: {row.customer.descriptive_name}")
    except Exception as e:
        print(f"❌ Customer access failed: {e}")
    
    # Test 2: Campaign list access (basic campaign info)
    print(f"\n🧪 Test 2: Campaign list (basic info)")
    try:
        query = f"SELECT campaign.id, campaign.name, campaign.status FROM campaign"
        response = ga_service.search(customer_id=customer_id, query=query)
        campaigns = list(response)
        print(f"✅ Campaign list access works: Found {len(campaigns)} campaigns")
        if campaigns:
            print(f"   Sample: {campaigns[0].campaign.name} (ID: {campaigns[0].campaign.id})")
    except Exception as e:
        print(f"❌ Campaign list failed: {e}")
    
    # Test 3: Campaign metrics access (this is what's failing)
    print(f"\n🧪 Test 3: Campaign metrics (performance data)")
    try:
        query = f"""
            SELECT campaign.id, campaign.name, metrics.cost_micros, metrics.clicks
            FROM campaign
            WHERE segments.date = '2025-08-12'
            LIMIT 1
        """
        response = ga_service.search(customer_id=customer_id, query=query)
        metrics = list(response)
        print(f"✅ Campaign metrics access works: Found {len(metrics)} results")
    except GoogleAdsException as ex:
        print(f"❌ Campaign metrics failed:")
        for error in ex.failure.errors:
            print(f"   - {error.error_code}: {error.message}")
            if hasattr(error.error_code, 'authorization_error'):
                if error.error_code.authorization_error.name == 'MISSING_TOS':
                    print(f"   🔧 Solution: This requires 'Standard Access' in Google Ads API")
                    print(f"      Visit: https://ads.google.com/aw/apicenter")
                    print(f"      Apply for 'Standard Access' if only 'Basic Access' is approved")
    
    # Test 4: Try simpler metrics
    print(f"\n🧪 Test 4: Basic campaign info with date segmentation")
    try:
        query = f"""
            SELECT campaign.id, campaign.name, segments.date
            FROM campaign
            WHERE segments.date = '2025-08-12'
            LIMIT 1
        """
        response = ga_service.search(customer_id=customer_id, query=query)
        results = list(response)
        print(f"✅ Date segmentation works: Found {len(results)} results")
    except Exception as e:
        print(f"❌ Date segmentation failed: {e}")
        
except Exception as e:
    print(f"❌ Initialization error: {e}")

print("\n" + "=" * 50)
print("💡 SUMMARY:")
print("If Test 1 passes but Test 3 fails with MISSING_TOS:")
print("• You have 'Basic Access' but need 'Standard Access'")
print("• Visit https://ads.google.com/aw/apicenter")
print("• Apply for 'Standard Access' to read performance metrics")
print("• This is a common requirement for production apps")
print("🏁 Permission test complete!")