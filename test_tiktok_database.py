#!/usr/bin/env python3
"""Test TikTok database tables and structure"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def test_tiktok_database():
    """Test TikTok database tables were created successfully"""
    
    print("🔍 Testing TikTok Database Structure...")
    
    # Connect to Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: TikTok campaign data table exists
    print("\n📊 Test 1: TikTok campaign data table...")
    try:
        result = supabase.table("tiktok_campaign_data").select("id").limit(1).execute()
        print("✅ tiktok_campaign_data table exists")
        tests_passed += 1
    except Exception as e:
        print(f"❌ tiktok_campaign_data table missing: {e}")
    
    # Test 2: TikTok monthly reports table exists
    print("\n📈 Test 2: TikTok monthly reports table...")
    try:
        result = supabase.table("tiktok_monthly_reports").select("id").limit(1).execute()
        print("✅ tiktok_monthly_reports table exists")
        tests_passed += 1
    except Exception as e:
        print(f"❌ tiktok_monthly_reports table missing: {e}")
    
    # Test 3: Unified campaign data view
    print("\n🔗 Test 3: Unified campaign data view...")
    try:
        result = supabase.table("unified_campaign_data").select("platform").limit(1).execute()
        print("✅ unified_campaign_data view exists")
        
        # Check platforms available
        platform_result = supabase.rpc("execute_sql", {
            "query": "SELECT DISTINCT platform FROM unified_campaign_data ORDER BY platform"
        }).execute()
        
        if platform_result.data:
            platforms = [row['platform'] for row in platform_result.data]
            print(f"📋 Available platforms: {', '.join(platforms)}")
        
        tests_passed += 1
    except Exception as e:
        print(f"❌ unified_campaign_data view missing: {e}")
    
    # Test 4: Check table structure
    print("\n🏗️  Test 4: TikTok table structure...")
    try:
        # Try inserting a test record (will be rolled back)
        test_data = {
            "campaign_id": "test_tiktok_campaign_123",
            "campaign_name": "Test TikTok Campaign",
            "category": "Test Category",
            "campaign_type": "Test Type",
            "reporting_starts": "2025-01-01",
            "reporting_ends": "2025-01-31",
            "amount_spent_usd": 100.00,
            "website_purchases": 5,
            "purchases_conversion_value": 500.00,
            "impressions": 10000,
            "link_clicks": 100,
            "cpa": 20.00,
            "roas": 5.00,
            "cpc": 1.00
        }
        
        # Insert test data
        insert_result = supabase.table("tiktok_campaign_data").insert(test_data).execute()
        
        if insert_result.data:
            print("✅ Table structure accepts all required fields")
            
            # Clean up test data
            supabase.table("tiktok_campaign_data").delete().eq("campaign_id", "test_tiktok_campaign_123").execute()
            print("✅ Test data cleaned up")
            tests_passed += 1
        else:
            print("❌ Failed to insert test data")
            
    except Exception as e:
        print(f"❌ Table structure issue: {e}")
    
    # Test 5: Auto-categorization function
    print("\n🏷️  Test 5: Auto-categorization function...")
    try:
        # Test the auto-categorization function
        result = supabase.rpc("auto_categorize_tiktok_campaign", {
            "campaign_name_input": "Test Standing Mats Campaign"
        }).execute()
        
        if result.data:
            category = result.data
            print(f"✅ Auto-categorization works: 'Test Standing Mats Campaign' → '{category}'")
            tests_passed += 1
        else:
            print("❌ Auto-categorization function not working")
            
    except Exception as e:
        print(f"❌ Auto-categorization function missing: {e}")
    
    # Summary
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 TikTok database setup complete!")
        print("✅ Ready for TikTok campaign data integration")
        return True
    else:
        print("⚠️  Some issues found - check migration")
        return False

if __name__ == "__main__":
    print("🚀 TikTok Database Structure Test")
    print("=" * 50)
    
    success = test_tiktok_database()
    
    if success:
        print(f"\n🎯 Next steps:")
        print(f"  1. Get proper TikTok API access token with scopes 1,2,15")
        print(f"  2. Test TikTok API connection")
        print(f"  3. Sync TikTok campaign data")
    else:
        print(f"\n🔧 Fix database issues first:")
        print(f"  1. Run the fixed migration: add_tiktok_campaign_data_fixed.sql")
        print(f"  2. Verify all tables were created")
        
    print("\n" + "=" * 50)