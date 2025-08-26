#!/usr/bin/env python3
"""
Debug TikTok category filtering discrepancy
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

def debug_july_filtering():
    print("TIKTOK JULY FILTERING DEBUG")
    print("=" * 60)
    
    # Get July 2024 data with NO filters (should be ALL categories)
    print("\n1. JULY 2024 - NO FILTERS (ALL CATEGORIES)")
    print("-" * 40)
    
    no_filter_result = supabase.table("tiktok_ad_data")\
        .select("*")\
        .gte("reporting_starts", "2024-07-01")\
        .lte("reporting_ends", "2024-07-31")\
        .execute()
    
    print(f"Total ads found: {len(no_filter_result.data)}")
    
    # Aggregate by category
    category_totals = {}
    total_spend_no_filter = 0
    
    for ad in no_filter_result.data:
        category = ad.get('category', 'Unknown')
        spend = ad.get('amount_spent_usd', 0)
        
        if category not in category_totals:
            category_totals[category] = 0
        category_totals[category] += spend
        total_spend_no_filter += spend
    
    print(f"Total spend (no filters): ${total_spend_no_filter:,.2f}")
    print("\nBreakdown by category:")
    for cat, spend in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: ${spend:,.2f}")
    
    # Now test with MULTIPLE categories selected
    print("\n\n2. JULY 2024 - WITH CATEGORY FILTERS")
    print("-" * 40)
    
    # Get the categories that should be included
    categories_to_test = ['Play Mats', 'Standing Mats', 'Tumbling Mats', 'Play Furniture', 'Multi Category']
    
    filter_result = supabase.table("tiktok_ad_data")\
        .select("*")\
        .gte("reporting_starts", "2024-07-01")\
        .lte("reporting_ends", "2024-07-31")\
        .in_("category", categories_to_test)\
        .execute()
    
    print(f"Total ads found with filters: {len(filter_result.data)}")
    
    # Aggregate filtered data
    filtered_category_totals = {}
    total_spend_filtered = 0
    
    for ad in filter_result.data:
        category = ad.get('category', 'Unknown')
        spend = ad.get('amount_spent_usd', 0)
        
        if category not in filtered_category_totals:
            filtered_category_totals[category] = 0
        filtered_category_totals[category] += spend
        total_spend_filtered += spend
    
    print(f"Total spend (with filters): ${total_spend_filtered:,.2f}")
    print(f"Categories included: {categories_to_test}")
    print("\nBreakdown by category:")
    for cat, spend in sorted(filtered_category_totals.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: ${spend:,.2f}")
    
    # Compare the results
    print("\n\n3. COMPARISON & ANALYSIS")
    print("-" * 40)
    print(f"No filters total:   ${total_spend_no_filter:,.2f}")
    print(f"With filters total: ${total_spend_filtered:,.2f}")
    print(f"Difference:         ${total_spend_filtered - total_spend_no_filter:,.2f}")
    
    if total_spend_filtered > total_spend_no_filter:
        print("🚨 CRITICAL BUG: Filtered total is HIGHER than unfiltered total!")
        print("   This is mathematically impossible.")
        
        # Find missing categories in no-filter result
        all_categories_no_filter = set(category_totals.keys())
        all_categories_filtered = set(filtered_category_totals.keys())
        
        print(f"\nCategories in no-filter: {sorted(all_categories_no_filter)}")
        print(f"Categories in filtered:  {sorted(all_categories_filtered)}")
        
        # Check for duplicate ad IDs
        print("\n4. CHECKING FOR DUPLICATE ADS")
        print("-" * 30)
        
        no_filter_ad_ids = [ad['ad_id'] for ad in no_filter_result.data]
        filtered_ad_ids = [ad['ad_id'] for ad in filter_result.data]
        
        print(f"Unique ads (no filter): {len(set(no_filter_ad_ids))}")
        print(f"Unique ads (filtered):  {len(set(filtered_ad_ids))}")
        
        # Check for ads that appear in filtered but not in no-filter
        filtered_set = set(filtered_ad_ids)
        no_filter_set = set(no_filter_ad_ids)
        
        missing_in_no_filter = filtered_set - no_filter_set
        if missing_in_no_filter:
            print(f"Ads in filtered but NOT in no-filter: {len(missing_in_no_filter)}")
            print("First few examples:")
            for ad_id in list(missing_in_no_filter)[:5]:
                # Get details of this ad
                ad_detail = supabase.table("tiktok_ad_data")\
                    .select("ad_id, ad_name, category, reporting_starts, reporting_ends, amount_spent_usd")\
                    .eq("ad_id", ad_id)\
                    .gte("reporting_starts", "2024-07-01")\
                    .lte("reporting_ends", "2024-07-31")\
                    .execute()
                
                if ad_detail.data:
                    ad = ad_detail.data[0]
                    print(f"  Ad {ad_id}: {ad['category']}, ${ad['amount_spent_usd']}, {ad['reporting_starts']}-{ad['reporting_ends']}")
    else:
        print("✅ Filtering logic is working correctly.")
    
    # NEW: Test the TikTok Service pivot calculation (dashboard aggregation)
    print("\n\n4. DASHBOARD PIVOT DATA TEST")
    print("-" * 40)
    
    # Import TikTokService to test the same logic used by the dashboard
    import sys
    sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend/app/services')
    from tiktok_service import TikTokService
    
    tiktok_service = TikTokService()
    
    # Test dashboard data without filters
    dashboard_data_no_filter = tiktok_service.get_dashboard_data()
    july_2024_no_filter = None
    for pivot in dashboard_data_no_filter.get('pivot_data', []):
        if pivot['month'] == '2024-07':
            july_2024_no_filter = pivot
            break
    
    # Test dashboard data with filters
    dashboard_data_filtered = tiktok_service.get_dashboard_data(categories="Play Mats,Standing Mats,Tumbling Mats,Play Furniture,Multi Category")
    july_2024_filtered = None
    for pivot in dashboard_data_filtered.get('pivot_data', []):
        if pivot['month'] == '2024-07':
            july_2024_filtered = pivot
            break
    
    print("\nDashboard Pivot Data July 2024:")
    if july_2024_no_filter:
        print(f"  No filters: ${july_2024_no_filter['spend']:,.2f}")
    else:
        print("  No filters: No July 2024 data found")
        
    if july_2024_filtered:
        print(f"  With filters: ${july_2024_filtered['spend']:,.2f}")
    else:
        print("  With filters: No July 2024 data found")
        
    if july_2024_no_filter and july_2024_filtered:
        if july_2024_filtered['spend'] > july_2024_no_filter['spend']:
            print("🚨 DASHBOARD BUG: Filtered pivot total is HIGHER than unfiltered!")
            print("   The issue is in the TikTok Service pivot data calculation.")
        else:
            print("✅ Dashboard pivot data calculation is correct.")

if __name__ == "__main__":
    debug_july_filtering()