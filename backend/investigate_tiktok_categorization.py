#!/usr/bin/env python3
"""
Investigate TikTok data categorization inconsistency between 2024 and 2025
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Database connection
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(supabase_url, supabase_key)

def investigate_categorization():
    print("INVESTIGATING TIKTOK CATEGORIZATION INCONSISTENCY")
    print("=" * 60)
    
    # Get July 2024 data
    print("\n1. JULY 2024 DATA ANALYSIS")
    print("-" * 40)
    
    july_2024_result = supabase.table("tiktok_ad_data")\
        .select("*")\
        .gte("reporting_starts", "2024-07-01")\
        .lte("reporting_ends", "2024-07-31")\
        .execute()
    
    print(f"Total July 2024 ads: {len(july_2024_result.data)}")
    
    # Analyze July 2024 by category
    july_2024_by_category = {}
    july_2024_total = 0
    
    for ad in july_2024_result.data:
        category = ad.get('category', 'Unknown')
        spend = ad.get('amount_spent_usd', 0)
        
        if category not in july_2024_by_category:
            july_2024_by_category[category] = 0
        july_2024_by_category[category] += spend
        july_2024_total += spend
    
    print(f"July 2024 total spend: ${july_2024_total:,.2f}")
    print("July 2024 by category:")
    for cat, spend in sorted(july_2024_by_category.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: ${spend:,.2f}")
    
    # Get July 2025 data
    print("\n2. JULY 2025 DATA ANALYSIS")
    print("-" * 40)
    
    july_2025_result = supabase.table("tiktok_ad_data")\
        .select("*")\
        .gte("reporting_starts", "2025-07-01")\
        .lte("reporting_ends", "2025-07-31")\
        .execute()
    
    print(f"Total July 2025 ads: {len(july_2025_result.data)}")
    
    # Analyze July 2025 by category
    july_2025_by_category = {}
    july_2025_total = 0
    
    for ad in july_2025_result.data:
        category = ad.get('category', 'Unknown')
        spend = ad.get('amount_spent_usd', 0)
        
        if category not in july_2025_by_category:
            july_2025_by_category[category] = 0
        july_2025_by_category[category] += spend
        july_2025_total += spend
    
    print(f"July 2025 total spend: ${july_2025_total:,.2f}")
    print("July 2025 by category:")
    for cat, spend in sorted(july_2025_by_category.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: ${spend:,.2f}")
    
    # Compare categories
    print("\n3. CATEGORY COMPARISON ANALYSIS")
    print("-" * 40)
    
    all_categories = set(july_2024_by_category.keys()) | set(july_2025_by_category.keys())
    
    print("Category comparison:")
    for category in sorted(all_categories):
        spend_2024 = july_2024_by_category.get(category, 0)
        spend_2025 = july_2025_by_category.get(category, 0)
        print(f"  {category}:")
        print(f"    2024: ${spend_2024:,.2f}")
        print(f"    2025: ${spend_2025:,.2f}")
    
    # Test filtering behavior
    print("\n4. FILTERING BEHAVIOR ANALYSIS")
    print("-" * 40)
    
    filter_categories = ['Play Mats', 'Standing Mats', 'Tumbling Mats', 'Play Furniture', 'Multi Category']
    
    # July 2024 filtered
    july_2024_filtered = supabase.table("tiktok_ad_data")\
        .select("*")\
        .gte("reporting_starts", "2024-07-01")\
        .lte("reporting_ends", "2024-07-31")\
        .in_("category", filter_categories)\
        .execute()
    
    july_2024_filtered_total = sum(ad.get('amount_spent_usd', 0) for ad in july_2024_filtered.data)
    
    # July 2025 filtered  
    july_2025_filtered = supabase.table("tiktok_ad_data")\
        .select("*")\
        .gte("reporting_starts", "2025-07-01")\
        .lte("reporting_ends", "2025-07-31")\
        .in_("category", filter_categories)\
        .execute()
    
    july_2025_filtered_total = sum(ad.get('amount_spent_usd', 0) for ad in july_2025_filtered.data)
    
    print("Filtering impact:")
    print(f"July 2024:")
    print(f"  No filter:   ${july_2024_total:,.2f}")
    print(f"  With filter: ${july_2024_filtered_total:,.2f}")
    print(f"  Difference:  ${july_2024_filtered_total - july_2024_total:,.2f}")
    
    print(f"July 2025:")
    print(f"  No filter:   ${july_2025_total:,.2f}")
    print(f"  With filter: ${july_2025_filtered_total:,.2f}")
    print(f"  Difference:  ${july_2025_filtered_total - july_2025_total:,.2f}")
    
    # Find the problem
    print("\n5. PROBLEM IDENTIFICATION")
    print("-" * 40)
    
    if july_2025_filtered_total > july_2025_total:
        print("🚨 FOUND THE BUG!")
        print(f"July 2025 filtered ({july_2025_filtered_total:,.2f}) > unfiltered ({july_2025_total:,.2f})")
        print("This is mathematically impossible - there's duplicate data or wrong categories!")
        
        # Check for ads that exist in filtered but not in unfiltered (should be impossible)
        unfiltered_ad_ids = set(ad['ad_id'] for ad in july_2025_result.data)
        filtered_ad_ids = set(ad['ad_id'] for ad in july_2025_filtered.data)
        
        extra_ads = filtered_ad_ids - unfiltered_ad_ids
        if extra_ads:
            print(f"Found {len(extra_ads)} ads that exist in filtered but not unfiltered!")
            print("This indicates a serious data integrity issue.")
        
        # Check for category issues
        print("\nChecking July 2025 categories:")
        july_2025_categories = set(ad.get('category') for ad in july_2025_result.data)
        print(f"All July 2025 categories: {sorted(july_2025_categories)}")
        
        missing_categories = set(filter_categories) - july_2025_categories
        if missing_categories:
            print(f"Filter categories missing from July 2025: {missing_categories}")
        
        uncategorized_count = len([ad for ad in july_2025_result.data if not ad.get('category') or ad.get('category') == 'Uncategorized'])
        print(f"Uncategorized July 2025 ads: {uncategorized_count}")
        
    else:
        print("July 2025 filtering looks normal")
        
    # Look at specific problematic ads
    print("\n6. SAMPLE PROBLEMATIC ADS")
    print("-" * 40)
    
    sample_2025_ads = july_2025_result.data[:5]
    for ad in sample_2025_ads:
        print(f"Ad ID: {ad.get('ad_id')}")
        print(f"  Name: {ad.get('ad_name', 'No name')}")
        print(f"  Category: {ad.get('category', 'No category')}")
        print(f"  Spend: ${ad.get('amount_spent_usd', 0):,.2f}")
        print()

if __name__ == "__main__":
    investigate_categorization()