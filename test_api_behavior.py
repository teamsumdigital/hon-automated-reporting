#!/usr/bin/env python3
"""
Test the exact API behavior to find the root cause
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

def test_api_queries():
    """Test different query patterns to find the issue"""
    
    print("🔍 Testing API Query Patterns\n")
    
    # Get last 14 days date range
    cutoff_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    
    # Test 1: Basic unfiltered query
    print("1️⃣ Basic unfiltered query (just date filter):")
    q1 = supabase.table('meta_ad_data').select('*').gte('reporting_starts', cutoff_date).execute()
    print(f"   Total records: {len(q1.data)}")
    standing_mats_1 = [r for r in q1.data if r['category'] == 'Standing Mats']
    print(f"   Standing Mats records: {len(standing_mats_1)}")
    unique_ads_1 = set(r['ad_name'] for r in standing_mats_1)
    print(f"   Unique Standing Mat ads: {len(unique_ads_1)}")
    
    # Test 2: With ordering (like the API does)
    print("\n2️⃣ With ordering (ad_name, reporting_starts):")
    q2 = supabase.table('meta_ad_data')\
        .select('*')\
        .gte('reporting_starts', cutoff_date)\
        .order('ad_name')\
        .order('reporting_starts')\
        .execute()
    print(f"   Total records: {len(q2.data)}")
    standing_mats_2 = [r for r in q2.data if r['category'] == 'Standing Mats']
    print(f"   Standing Mats records: {len(standing_mats_2)}")
    unique_ads_2 = set(r['ad_name'] for r in standing_mats_2)
    print(f"   Unique Standing Mat ads: {len(unique_ads_2)}")
    
    # Test 3: Check if there's a limit being applied
    print("\n3️⃣ Checking for implicit limits...")
    if len(q1.data) == 1000 or len(q2.data) == 1000:
        print("   ⚠️  WARNING: Query returns exactly 1000 records - possible default limit!")
        
        # Count how many categories are in the first 1000 records
        category_counts = {}
        for r in q2.data:
            cat = r['category']
            if cat not in category_counts:
                category_counts[cat] = 0
            category_counts[cat] += 1
        
        print("\n   Category distribution in returned records:")
        for cat, count in sorted(category_counts.items()):
            print(f"      {cat}: {count} records")
    
    # Test 4: Filtered query for comparison
    print("\n4️⃣ Filtered query (Standing Mats only):")
    q4 = supabase.table('meta_ad_data')\
        .select('*')\
        .gte('reporting_starts', cutoff_date)\
        .in_('category', ['Standing Mats'])\
        .order('ad_name')\
        .order('reporting_starts')\
        .execute()
    print(f"   Total records: {len(q4.data)}")
    unique_ads_4 = set(r['ad_name'] for r in q4.data)
    print(f"   Unique Standing Mat ads: {len(unique_ads_4)}")
    
    # Find missing ads
    missing_ads = unique_ads_4 - unique_ads_2
    if missing_ads:
        print(f"\n❌ FOUND THE ISSUE: {len(missing_ads)} Standing Mat ads missing in unfiltered query!")
        
        # Check if these are high-spend ads
        ad_spends = {}
        for r in q4.data:
            if r['ad_name'] in missing_ads:
                if r['ad_name'] not in ad_spends:
                    ad_spends[r['ad_name']] = 0
                ad_spends[r['ad_name']] += r['amount_spent_usd']
        
        print("\n   Top 5 missing ads by spend:")
        sorted_missing = sorted(ad_spends.items(), key=lambda x: x[1], reverse=True)[:5]
        for ad_name, spend in sorted_missing:
            print(f"      ${spend:,.2f} - {ad_name}")
    
    # Test 5: Try to get ALL records without limit
    print("\n5️⃣ Testing query without limit (using count):")
    count_result = supabase.table('meta_ad_data')\
        .select('*', count='exact')\
        .gte('reporting_starts', cutoff_date)\
        .execute()
    
    print(f"   Actual total records in date range: {count_result.count}")
    print(f"   Records returned by default: {len(q1.data)}")
    
    if count_result.count > len(q1.data):
        print(f"\n   ⚠️  CONFIRMED: Default query limit of {len(q1.data)} is truncating results!")
        print(f"   Missing {count_result.count - len(q1.data)} records")

if __name__ == "__main__":
    test_api_queries()