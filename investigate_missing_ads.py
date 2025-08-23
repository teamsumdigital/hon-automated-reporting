#!/usr/bin/env python3
"""
Investigate why certain Standing Mat ads are missing in unfiltered view
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

def investigate_missing_ads():
    """Find why Standing Mat ads disappear"""
    
    print("🔍 Investigating Missing Standing Mat Ads\n")
    
    # Get last 14 days date range
    cutoff_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    
    # Get the top spending Standing Mat ads we know should exist
    known_missing_ads = [
        "Standing Mats Video Ad Don't Buy Iteration",
        "Standing Mat Launch Multiple Styles Video Ad V1", 
        "Standing Mat Launch Swatch Lifestyle Devon"
    ]
    
    print("1️⃣ Checking specific high-spend Standing Mat ads...")
    
    for ad_name in known_missing_ads:
        print(f"\n📊 Analyzing: {ad_name}")
        
        # Get all records for this ad
        ad_records = supabase.table('meta_ad_data')\
            .select('*')\
            .eq('ad_name', ad_name)\
            .gte('reporting_starts', cutoff_date)\
            .execute()
        
        if ad_records.data:
            total_spend = sum(r['amount_spent_usd'] for r in ad_records.data)
            print(f"   Total spend: ${total_spend:,.2f}")
            print(f"   Records found: {len(ad_records.data)}")
            
            # Check each record
            for record in ad_records.data:
                print(f"   - Period: {record['reporting_starts']} to {record['reporting_ends']}")
                print(f"     Category: '{record['category']}'")
                print(f"     Spend: ${record['amount_spent_usd']:,.2f}")
                
    # Now let's see what the API endpoint actually returns
    print("\n\n2️⃣ Simulating API endpoint behavior...")
    
    # Simulate unfiltered query
    print("\n🔹 Unfiltered query (All Categories):")
    unfiltered = supabase.table('meta_ad_data')\
        .select('*')\
        .gte('reporting_starts', cutoff_date)\
        .order('ad_name')\
        .order('reporting_starts')\
        .execute()
    
    # Count Standing Mat ads in unfiltered results
    standing_mat_ads = {}
    for ad in unfiltered.data:
        if ad['category'] == 'Standing Mats':
            ad_name = ad['ad_name']
            if ad_name not in standing_mat_ads:
                standing_mat_ads[ad_name] = 0
            standing_mat_ads[ad_name] += ad['amount_spent_usd']
    
    print(f"   Standing Mat ads found: {len(standing_mat_ads)}")
    
    # Check if our missing ads are in there
    for ad_name in known_missing_ads:
        if ad_name in standing_mat_ads:
            print(f"   ✅ Found: {ad_name} (${standing_mat_ads[ad_name]:,.2f})")
        else:
            print(f"   ❌ MISSING: {ad_name}")
    
    # Simulate filtered query
    print("\n🔹 Filtered query (Standing Mats only):")
    filtered = supabase.table('meta_ad_data')\
        .select('*')\
        .gte('reporting_starts', cutoff_date)\
        .in_('category', ['Standing Mats'])\
        .order('ad_name')\
        .order('reporting_starts')\
        .execute()
    
    filtered_standing_mat_ads = {}
    for ad in filtered.data:
        ad_name = ad['ad_name']
        if ad_name not in filtered_standing_mat_ads:
            filtered_standing_mat_ads[ad_name] = 0
        filtered_standing_mat_ads[ad_name] += ad['amount_spent_usd']
    
    print(f"   Standing Mat ads found: {len(filtered_standing_mat_ads)}")
    
    # Check if our missing ads are in filtered results
    for ad_name in known_missing_ads:
        if ad_name in filtered_standing_mat_ads:
            print(f"   ✅ Found: {ad_name} (${filtered_standing_mat_ads[ad_name]:,.2f})")
        else:
            print(f"   ❌ MISSING: {ad_name}")
    
    # Find the difference
    print("\n\n3️⃣ Analyzing the difference...")
    only_in_filtered = set(filtered_standing_mat_ads.keys()) - set(standing_mat_ads.keys())
    if only_in_filtered:
        print(f"❌ {len(only_in_filtered)} ads appear ONLY in filtered query!")
        print("   This suggests a problem with how the unfiltered query works")
        print("\n   First 5 ads that appear only when filtered:")
        for ad_name in list(only_in_filtered)[:5]:
            print(f"   - {ad_name} (${filtered_standing_mat_ads[ad_name]:,.2f})")

if __name__ == "__main__":
    investigate_missing_ads()