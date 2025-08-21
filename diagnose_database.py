#!/usr/bin/env python3
"""
Diagnose database connectivity issues for HON Automated Reporting
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

print("🔍 HON Database Diagnosis")
print("=" * 50)

try:
    from supabase import create_client
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    
    print(f"📋 Supabase URL: {url[:30] if url else 'None'}...")
    print(f"📋 Service Key: {key[:20] if key else 'None'}...")
    
    if not url or not key:
        print("❌ Missing Supabase credentials in .env file")
        print("\n🔧 Expected environment variables:")
        print("   SUPABASE_URL=your_supabase_project_url")
        print("   SUPABASE_SERVICE_KEY=your_service_key")
        sys.exit(1)
    
    print("🔗 Creating Supabase client...")
    supabase = create_client(url, key)
    print("✅ Supabase client created")
    
    # Test basic connection
    print("\n📊 Testing table access...")
    
    # Check if tables exist
    tables_to_check = ["campaign_data", "category_rules", "category_overrides"]
    
    for table in tables_to_check:
        try:
            result = supabase.table(table).select("count", count="exact").execute()
            count = result.count if hasattr(result, 'count') else 0
            print(f"   ✅ {table}: {count} records")
        except Exception as e:
            print(f"   ❌ {table}: Error - {e}")
    
    # Check campaign_data specifically
    print("\n📈 Checking campaign_data table...")
    try:
        result = supabase.table("campaign_data").select("*").limit(5).execute()
        if result.data:
            print(f"   📊 Sample data found: {len(result.data)} records")
            for record in result.data[:2]:
                print(f"      - {record.get('campaign_name', 'Unknown')}: ${record.get('amount_spent_usd', 0)}")
        else:
            print("   ⚠️  No campaign data found in database")
            print("   💡 This explains why the dashboard shows all zeros")
    except Exception as e:
        print(f"   ❌ Cannot access campaign_data: {e}")
    
    # Test insert capability
    print("\n🧪 Testing insert capability...")
    test_data = {
        "campaign_id": "test_diag_123",
        "campaign_name": "Database Test Campaign",
        "category": "Test",
        "reporting_starts": "2025-08-18",
        "reporting_ends": "2025-08-18",
        "amount_spent_usd": 1.00,
        "website_purchases": 1,
        "purchases_conversion_value": 2.50,
        "impressions": 100,
        "link_clicks": 5,
        "cpa": 1.00,
        "roas": 2.5,
        "cpc": 0.20,
        "cpm": 10.00
    }
    
    try:
        insert_result = supabase.table("campaign_data").insert(test_data).execute()
        print("   ✅ Test insert successful!")
        
        # Clean up test data
        delete_result = supabase.table("campaign_data").delete().eq("campaign_id", "test_diag_123").execute()
        print("   ✅ Test cleanup successful")
        
        print("\n✨ Database connectivity is working!")
        print("🔍 Issue: No actual campaign data in database")
        print("💡 Solution: Need to run data sync from Meta Ads API")
        
    except Exception as e:
        print(f"   ❌ Test insert failed: {e}")
        print("   🔍 This may indicate permission or schema issues")
    
except ImportError:
    print("❌ Missing supabase dependency")
    print("💡 Run: pip install supabase")
except Exception as e:
    print(f"❌ Database diagnosis failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🏁 Database diagnosis complete!")