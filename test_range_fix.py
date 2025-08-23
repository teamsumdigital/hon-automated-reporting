#!/usr/bin/env python3
"""
Test if range() method works better than limit()
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

if not supabase_url or not supabase_key:
    print("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    sys.exit(1)

supabase = create_client(supabase_url, supabase_key)

def test_range_fix():
    """Test if range() bypasses the limit"""
    
    print("🔍 Testing range() method fix\n")
    
    # Get last 14 days date range
    cutoff_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    
    # Test with range
    print("Testing with .range(0, 9999):")
    result = supabase.table('meta_ad_data')\
        .select('*')\
        .gte('reporting_starts', cutoff_date)\
        .order('ad_name')\
        .order('reporting_starts')\
        .range(0, 9999)\
        .execute()
    
    print(f"Records returned: {len(result.data)}")
    
    # Count Standing Mats
    standing_mats = [r for r in result.data if r['category'] == 'Standing Mats']
    unique_standing_mats = set(r['ad_name'] for r in standing_mats)
    print(f"Standing Mat records: {len(standing_mats)}")
    print(f"Unique Standing Mat ads: {len(unique_standing_mats)}")
    
    # Check for high-spend ads
    target_ads = [
        "Standing Mats Video Ad Don't Buy Iteration",
        "Standing Mat Launch Swatch Lifestyle Devon",
        "Standing Mat Launch Multiple Styles Video Ad V1"
    ]
    
    print("\nChecking for high-spend Standing Mat ads:")
    for ad_name in target_ads:
        if ad_name in unique_standing_mats:
            records = [r for r in standing_mats if r['ad_name'] == ad_name]
            total_spend = sum(r['amount_spent_usd'] for r in records)
            print(f"✅ Found: {ad_name} (${total_spend:,.2f})")
        else:
            print(f"❌ Missing: {ad_name}")

if __name__ == "__main__":
    test_range_fix()