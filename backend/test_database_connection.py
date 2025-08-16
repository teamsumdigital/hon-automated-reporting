#!/usr/bin/env python3
"""
Test database connection and table access for Google Ads
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

print("🔍 Testing Database Connection for Google Ads")
print("=" * 50)

try:
    from supabase import create_client
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    
    print(f"📋 Supabase URL: {url[:30]}...")
    print(f"📋 Service Key: {key[:20] if key else 'None'}...")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        exit(1)
    
    print("🔗 Creating Supabase client...")
    supabase = create_client(url, key)
    print("✅ Supabase client created")
    
    # Test table access
    print("📊 Testing google_campaign_data table access...")
    result = supabase.table("google_campaign_data").select("count").execute()
    print("✅ Table access successful")
    print(f"   Current records: {result}")
    
    # Test simple insert
    print("🧪 Testing simple data insertion...")
    test_data = {
        "campaign_id": "test_123",
        "campaign_name": "Test Campaign",
        "category": "Test",
        "reporting_starts": "2025-08-13",
        "reporting_ends": "2025-08-13",
        "amount_spent_usd": 10.50,
        "website_purchases": 1,
        "purchases_conversion_value": 25.00,
        "impressions": 100,
        "link_clicks": 10,
        "cpa": 10.50,
        "roas": 2.3810,
        "cpc": 1.05
    }
    
    insert_result = supabase.table("google_campaign_data").insert(test_data).execute()
    print("✅ Test insertion successful!")
    print(f"   Inserted ID: {insert_result.data[0]['id'] if insert_result.data else 'Unknown'}")
    
    # Clean up test data
    print("🧹 Cleaning up test data...")
    delete_result = supabase.table("google_campaign_data").delete().eq("campaign_id", "test_123").execute()
    print("✅ Test cleanup successful")
    
except Exception as e:
    print(f"❌ Database test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🏁 Database test complete!")