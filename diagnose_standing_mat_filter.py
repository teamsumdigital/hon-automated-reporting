#!/usr/bin/env python3
"""
Diagnose the Standing Mat filtering issue in Meta Ad Level API
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
from collections import defaultdict

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

if not supabase_url or not supabase_key:
    print("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    sys.exit(1)

supabase = create_client(supabase_url, supabase_key)

def analyze_standing_mat_data():
    """Analyze Standing Mat data to identify filtering issues"""
    
    print("🔍 Analyzing Standing Mat Filtering Issue\n")
    
    # Get last 14 days date range
    cutoff_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    
    # 1. Get ALL data from last 14 days
    print("1️⃣ Fetching ALL data from last 14 days...")
    all_data = supabase.table('meta_ad_data').select('*').gte('reporting_starts', cutoff_date).execute()
    
    if not all_data.data:
        print("❌ No data found in meta_ad_data table")
        return
    
    print(f"   Total records: {len(all_data.data)}")
    
    # 2. Count unique ads by category
    ads_by_category = defaultdict(set)
    standing_mat_ads = {}
    
    for ad in all_data.data:
        ad_name = ad['ad_name']
        category = ad['category']
        ads_by_category[category].add(ad_name)
        
        if category == 'Standing Mats':
            if ad_name not in standing_mat_ads:
                standing_mat_ads[ad_name] = {
                    'total_spend': 0,
                    'records': []
                }
            standing_mat_ads[ad_name]['total_spend'] += ad['amount_spent_usd']
            standing_mat_ads[ad_name]['records'].append(ad)
    
    print(f"\n2️⃣ Category breakdown:")
    for category, ads in sorted(ads_by_category.items()):
        print(f"   {category}: {len(ads)} unique ads")
    
    # 3. Find top Standing Mat ads by spend
    print(f"\n3️⃣ Top 10 Standing Mat ads by total spend:")
    top_standing_mats = sorted(standing_mat_ads.items(), key=lambda x: x[1]['total_spend'], reverse=True)[:10]
    
    for ad_name, data in top_standing_mats:
        print(f"   ${data['total_spend']:,.2f} - {ad_name}")
    
    # 4. Test filtered query (Standing Mats only)
    print(f"\n4️⃣ Testing filtered query (Standing Mats only)...")
    filtered_query = supabase.table('meta_ad_data')\
        .select('*')\
        .gte('reporting_starts', cutoff_date)\
        .in_('category', ['Standing Mats'])\
        .execute()
    
    filtered_standing_mat_ads = set()
    for ad in filtered_query.data:
        filtered_standing_mat_ads.add(ad['ad_name'])
    
    print(f"   Filtered query returned: {len(filtered_standing_mat_ads)} unique Standing Mat ads")
    
    # 5. Test unfiltered query (mimicking "All Categories")
    print(f"\n5️⃣ Testing unfiltered query (All Categories)...")
    unfiltered_query = supabase.table('meta_ad_data')\
        .select('*')\
        .gte('reporting_starts', cutoff_date)\
        .execute()
    
    unfiltered_standing_mat_ads = set()
    for ad in unfiltered_query.data:
        if ad['category'] == 'Standing Mats':
            unfiltered_standing_mat_ads.add(ad['ad_name'])
    
    print(f"   Unfiltered query found: {len(unfiltered_standing_mat_ads)} unique Standing Mat ads")
    
    # 6. Find missing ads
    missing_ads = filtered_standing_mat_ads - unfiltered_standing_mat_ads
    if missing_ads:
        print(f"\n❌ PROBLEM FOUND: {len(missing_ads)} Standing Mat ads missing in unfiltered view!")
        print("   Missing ads:")
        for ad_name in list(missing_ads)[:5]:  # Show first 5
            if ad_name in standing_mat_ads:
                print(f"      ${standing_mat_ads[ad_name]['total_spend']:,.2f} - {ad_name}")
    else:
        print(f"\n✅ No discrepancy found between filtered and unfiltered queries")
    
    # 7. Check for data issues
    print(f"\n6️⃣ Checking for potential data issues...")
    
    # Check for duplicate records
    ad_period_counts = defaultdict(int)
    for ad in all_data.data:
        key = f"{ad['ad_name']}|{ad['reporting_starts']}|{ad['reporting_ends']}"
        ad_period_counts[key] += 1
    
    duplicates = [(k, v) for k, v in ad_period_counts.items() if v > 1]
    if duplicates:
        print(f"   ⚠️  Found {len(duplicates)} duplicate ad/period combinations")
        for dup, count in duplicates[:5]:
            ad_name = dup.split('|')[0]
            print(f"      {count} copies of: {ad_name}")
    
    # Check for null/empty categories
    null_categories = [ad for ad in all_data.data if not ad.get('category')]
    if null_categories:
        print(f"   ⚠️  Found {len(null_categories)} ads with null/empty category")
    
    # Check category variations
    category_variations = set()
    for ad in all_data.data:
        if ad.get('category') and 'standing mat' in ad['category'].lower():
            category_variations.add(ad['category'])
    
    if len(category_variations) > 1:
        print(f"   ⚠️  Found multiple Standing Mat category variations:")
        for cat in category_variations:
            count = len([ad for ad in all_data.data if ad.get('category') == cat])
            print(f"      '{cat}': {count} records")

if __name__ == "__main__":
    analyze_standing_mat_data()