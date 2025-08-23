#!/usr/bin/env python3
"""
Debug category filtering discrepancy in Google Ads backend
"""

import requests
import json
from collections import Counter

def debug_category_filtering():
    backend_url = "http://localhost:8007"
    
    print("🔍 Debugging Category Filtering Logic")
    print("=" * 50)
    
    try:
        # Step 1: Get ALL campaigns without filters
        print("📊 STEP 1: All Google Ads Campaigns")
        all_response = requests.get(f"{backend_url}/api/google-reports/campaigns", timeout=10)
        all_campaigns = all_response.json()
        
        print(f"Total campaigns in database: {len(all_campaigns)}")
        
        # Count categories
        all_categories = Counter(c['category'] for c in all_campaigns)
        print("\nAll Campaign Categories:")
        for category, count in all_categories.most_common():
            print(f"  {category}: {count} campaigns")
        
        # Step 2: Get Multi Category campaigns specifically
        print(f"\n📊 STEP 2: Multi Category Filter Applied")
        multi_response = requests.get(f"{backend_url}/api/google-reports/campaigns?category=Multi Category", timeout=10)
        multi_campaigns = multi_response.json()
        
        print(f"Multi Category campaigns returned: {len(multi_campaigns)}")
        
        if len(multi_campaigns) != all_categories.get("Multi Category", 0):
            print(f"❌ DISCREPANCY: Expected {all_categories.get('Multi Category', 0)} but got {len(multi_campaigns)}")
        
        # Step 3: Check what the monthly API uses for filtering
        print(f"\n📊 STEP 3: Monthly API Backend Logic")
        print("Testing what gets passed to generate_pivot_table_data...")
        
        # Let's see what categories exactly match "Multi Category"
        multi_variations = [c['category'] for c in all_campaigns if 'multi' in c['category'].lower()]
        unique_multi = set(multi_variations)
        print(f"\nCategory variations containing 'multi': {unique_multi}")
        
        # Check exact matches
        exact_matches = [c for c in all_campaigns if c['category'] == 'Multi Category']
        print(f"Exact 'Multi Category' matches: {len(exact_matches)}")
        
        # Step 4: Test monthly endpoint with debug info
        print(f"\n📊 STEP 4: Monthly Endpoint Analysis")
        monthly_response = requests.get(f"{backend_url}/api/google-reports/monthly?categories=Multi Category", timeout=10)
        monthly_data = monthly_response.json()
        
        print(f"Monthly data points returned: {len(monthly_data)}")
        
        # Calculate what should be the totals
        total_spend_individual = sum(float(c['amount_spent_usd']) for c in multi_campaigns)
        total_impressions_individual = sum(int(c['impressions']) for c in multi_campaigns)
        
        total_spend_monthly = sum(float(m['spend']) for m in monthly_data)
        total_impressions_monthly = sum(int(m['impressions']) for m in monthly_data)
        
        print(f"\nComparison:")
        print(f"Individual campaigns total: ${total_spend_individual:.0f} spend, {total_impressions_individual:,} impressions")
        print(f"Monthly aggregation total:  ${total_spend_monthly:.0f} spend, {total_impressions_monthly:,} impressions")
        
        if abs(total_spend_individual - total_spend_monthly) > 100:
            print("❌ MAJOR DISCREPANCY: Monthly API is losing data during aggregation!")
            
            # Let's check if there are date filtering issues
            print(f"\nInvestigating potential causes...")
            
            # Check date ranges
            dates_individual = [c['reporting_starts'] for c in multi_campaigns]
            date_range_individual = f"{min(dates_individual)} to {max(dates_individual)}"
            
            dates_monthly = [m['month'] + '-01' for m in monthly_data]  # Convert YYYY-MM to date
            date_range_monthly = f"{min(dates_monthly)} to {max(dates_monthly)}"
            
            print(f"Date range - Individual: {date_range_individual}")
            print(f"Date range - Monthly: {date_range_monthly}")
        else:
            print("✅ Totals match - aggregation is working correctly")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_category_filtering()