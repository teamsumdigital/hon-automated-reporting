#!/usr/bin/env python3
"""
Test if Supabase limit is actually working
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

def test_limit_behavior():
    """Test different limit configurations"""
    
    print("🔍 Testing Supabase Limit Behavior\n")
    
    # Get last 14 days date range
    cutoff_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    
    # Test 1: No limit, no ordering
    print("1️⃣ Test without limit or ordering:")
    result1 = supabase.table('meta_ad_data').select('*').gte('reporting_starts', cutoff_date).execute()
    print(f"   Records returned: {len(result1.data)}")
    standing_mats_1 = [r for r in result1.data if r['category'] == 'Standing Mats']
    print(f"   Standing Mat records: {len(standing_mats_1)}")
    
    # Test 2: With ordering but no explicit limit
    print("\n2️⃣ Test with ordering but no explicit limit:")
    result2 = supabase.table('meta_ad_data')\
        .select('*')\
        .gte('reporting_starts', cutoff_date)\
        .order('ad_name')\
        .order('reporting_starts')\
        .execute()
    print(f"   Records returned: {len(result2.data)}")
    standing_mats_2 = [r for r in result2.data if r['category'] == 'Standing Mats']
    print(f"   Standing Mat records: {len(standing_mats_2)}")
    
    # Test 3: With ordering and explicit limit
    print("\n3️⃣ Test with ordering AND explicit limit(10000):")
    result3 = supabase.table('meta_ad_data')\
        .select('*')\
        .gte('reporting_starts', cutoff_date)\
        .order('ad_name')\
        .order('reporting_starts')\
        .limit(10000)\
        .execute()
    print(f"   Records returned: {len(result3.data)}")
    standing_mats_3 = [r for r in result3.data if r['category'] == 'Standing Mats']
    print(f"   Standing Mat records: {len(standing_mats_3)}")
    
    # Test 4: Try with range instead of limit
    print("\n4️⃣ Test using range() instead of limit():")
    try:
        result4 = supabase.table('meta_ad_data')\
            .select('*')\
            .gte('reporting_starts', cutoff_date)\
            .order('ad_name')\
            .order('reporting_starts')\
            .range(0, 9999)\
            .execute()
        print(f"   Records returned: {len(result4.data)}")
        standing_mats_4 = [r for r in result4.data if r['category'] == 'Standing Mats']
        print(f"   Standing Mat records: {len(standing_mats_4)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check for the missing high-spend ads
    print("\n5️⃣ Checking for specific ads in each test:")
    target_ad = "Standing Mats Video Ad Don't Buy Iteration"
    
    print(f"\n   Looking for: {target_ad}")
    print(f"   Test 1 (no limit/order): {'✅ Found' if any(r['ad_name'] == target_ad for r in result1.data) else '❌ Missing'}")
    print(f"   Test 2 (order, no limit): {'✅ Found' if any(r['ad_name'] == target_ad for r in result2.data) else '❌ Missing'}")
    print(f"   Test 3 (order + limit): {'✅ Found' if any(r['ad_name'] == target_ad for r in result3.data) else '❌ Missing'}")
    
    # Check what position this ad would be in when ordered
    if result3.data:
        ad_names_ordered = sorted(set(r['ad_name'] for r in result3.data))
        if target_ad in ad_names_ordered:
            position = ad_names_ordered.index(target_ad) + 1
            print(f"   Position of '{target_ad}' when ordered: {position} out of {len(ad_names_ordered)}")

if __name__ == "__main__":
    test_limit_behavior()