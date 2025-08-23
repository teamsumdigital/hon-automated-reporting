#!/usr/bin/env python3
"""
Test a pagination approach to get all records
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

def test_pagination():
    """Test fetching data in pages"""
    
    print("🔍 Testing Pagination Approach\n")
    
    # Get last 14 days date range
    cutoff_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    
    # First, get total count
    count_result = supabase.table('meta_ad_data')\
        .select('*', count='exact')\
        .gte('reporting_starts', cutoff_date)\
        .execute()
    
    total_records = count_result.count
    print(f"Total records in date range: {total_records}")
    
    # Approach 1: Try fetching without ordering first
    print("\n1️⃣ Fetching WITHOUT ordering:")
    result_no_order = supabase.table('meta_ad_data')\
        .select('*')\
        .gte('reporting_starts', cutoff_date)\
        .execute()
    
    print(f"   Records returned: {len(result_no_order.data)}")
    
    # Count Standing Mats
    standing_mats_no_order = [r for r in result_no_order.data if r['category'] == 'Standing Mats']
    unique_no_order = set(r['ad_name'] for r in standing_mats_no_order)
    print(f"   Unique Standing Mat ads: {len(unique_no_order)}")
    
    # Check for target ads
    target_ad = "Standing Mats Video Ad Don't Buy Iteration"
    found_no_order = target_ad in unique_no_order
    print(f"   Target ad found: {'✅ Yes' if found_no_order else '❌ No'}")
    
    # Approach 2: Paginate through results
    print("\n2️⃣ Testing pagination (multiple requests):")
    all_records = []
    page_size = 500
    
    for offset in range(0, min(total_records, 2000), page_size):
        page_result = supabase.table('meta_ad_data')\
            .select('*')\
            .gte('reporting_starts', cutoff_date)\
            .order('ad_name')\
            .order('reporting_starts')\
            .range(offset, offset + page_size - 1)\
            .execute()
        
        all_records.extend(page_result.data)
        print(f"   Page {offset//page_size + 1}: Got {len(page_result.data)} records (total so far: {len(all_records)})")
        
        if len(page_result.data) < page_size:
            break
    
    # Analyze paginated results
    standing_mats_paginated = [r for r in all_records if r['category'] == 'Standing Mats']
    unique_paginated = set(r['ad_name'] for r in standing_mats_paginated)
    print(f"\n   Total records fetched: {len(all_records)}")
    print(f"   Unique Standing Mat ads: {len(unique_paginated)}")
    
    # Check for target ads
    target_ads = [
        "Standing Mats Video Ad Don't Buy Iteration",
        "Standing Mat Launch Swatch Lifestyle Devon",
        "Standing Mat Launch Multiple Styles Video Ad V1"
    ]
    
    print("\n   Checking for high-spend ads in paginated results:")
    for ad_name in target_ads:
        if ad_name in unique_paginated:
            records = [r for r in standing_mats_paginated if r['ad_name'] == ad_name]
            total_spend = sum(r['amount_spent_usd'] for r in records)
            print(f"   ✅ Found: {ad_name} (${total_spend:,.2f})")
        else:
            print(f"   ❌ Missing: {ad_name}")

if __name__ == "__main__":
    test_pagination()