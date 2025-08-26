#!/usr/bin/env python3
"""
Check total number of ads in tiktok_ad_data table
"""

import os
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

def check_total_ads():
    print("🔍 CHECKING TOTAL ADS IN DATABASE")
    print("=" * 50)
    
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
        
        # Get total count
        result = supabase.table("tiktok_ad_data").select("id", count="exact").execute()
        total_count = result.count
        
        print(f"📊 TOTAL ADS IN DATABASE: {total_count}")
        
        # Check date range
        earliest = supabase.table("tiktok_ad_data").select("reporting_starts").order("reporting_starts", desc=False).limit(1).execute()
        latest = supabase.table("tiktok_ad_data").select("reporting_starts").order("reporting_starts", desc=True).limit(1).execute()
        
        if earliest.data and latest.data:
            print(f"📅 DATE RANGE: {earliest.data[0]['reporting_starts']} to {latest.data[0]['reporting_starts']}")
        
        # Get monthly counts
        print(f"\n📊 CHECKING IF WE CAN GET ALL DATA WITH HIGHER LIMIT:")
        all_data = supabase.table("tiktok_ad_data").select("reporting_starts").limit(10000).execute()
        print(f"  Retrieved {len(all_data.data)} ads with limit 10000")
        
        if len(all_data.data) >= total_count:
            print(f"  ✅ Successfully got all data")
        else:
            print(f"  ❌ Still missing {total_count - len(all_data.data)} ads")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_total_ads()