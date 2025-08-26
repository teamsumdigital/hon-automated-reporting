#!/usr/bin/env python3
"""
Debug the actual TikTok API response to see what's causing the filtering bug
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_api_responses():
    print("DEBUGGING TIKTOK API RESPONSES")
    print("=" * 60)
    
    API_BASE_URL = "http://localhost:8007"
    
    print("\n1. TESTING API RESPONSE - NO FILTERS")
    print("-" * 40)
    
    try:
        response_no_filter = requests.get(
            f"{API_BASE_URL}/api/tiktok-reports/dashboard",
            params={"_t": "123456"}
        )
        response_no_filter.raise_for_status()
        data_no_filter = response_no_filter.json()
        
        # Find July 2024 in pivot data
        july_2024_no_filter = None
        for pivot in data_no_filter.get('pivot_data', []):
            if pivot.get('month') == '2024-07':
                july_2024_no_filter = pivot
                break
        
        if july_2024_no_filter:
            print(f"July 2024 spend (API - no filters): ${july_2024_no_filter['spend']:,.2f}")
            print(f"July 2024 data: {july_2024_no_filter}")
        else:
            print("No July 2024 data found in no-filter response")
            print("Available months:", [p.get('month') for p in data_no_filter.get('pivot_data', [])])
            
        # Check for ALL July months (2024, 2025, etc.)
        july_months_no_filter = [p for p in data_no_filter.get('pivot_data', []) if p.get('month', '').endswith('-07')]
        print(f"\nALL July months (no filters):")
        for july in july_months_no_filter:
            print(f"  {july.get('month')}: ${july.get('spend', 0):,.2f}")
        
        total_july_no_filter = sum(july.get('spend', 0) for july in july_months_no_filter)
        print(f"TOTAL July spend (all years): ${total_july_no_filter:,.2f}")
            
    except Exception as e:
        print(f"Error with no-filter request: {e}")
        return
    
    print("\n2. TESTING API RESPONSE - WITH FILTERS")
    print("-" * 40)
    
    try:
        response_filtered = requests.get(
            f"{API_BASE_URL}/api/tiktok-reports/dashboard",
            params={
                "categories": "Play Mats,Standing Mats,Tumbling Mats,Play Furniture,Multi Category",
                "_t": "123456"
            }
        )
        response_filtered.raise_for_status()
        data_filtered = response_filtered.json()
        
        # Find July 2024 in filtered pivot data
        july_2024_filtered = None
        for pivot in data_filtered.get('pivot_data', []):
            if pivot.get('month') == '2024-07':
                july_2024_filtered = pivot
                break
        
        if july_2024_filtered:
            print(f"July 2024 spend (API - with filters): ${july_2024_filtered['spend']:,.2f}")
            print(f"July 2024 data: {july_2024_filtered}")
        else:
            print("No July 2024 data found in filtered response")
            print("Available months:", [p.get('month') for p in data_filtered.get('pivot_data', [])])
            
        # Check for ALL July months (2024, 2025, etc.)
        july_months_filtered = [p for p in data_filtered.get('pivot_data', []) if p.get('month', '').endswith('-07')]
        print(f"\nALL July months (with filters):")
        for july in july_months_filtered:
            print(f"  {july.get('month')}: ${july.get('spend', 0):,.2f}")
        
        total_july_filtered = sum(july.get('spend', 0) for july in july_months_filtered)
        print(f"TOTAL July spend (all years): ${total_july_filtered:,.2f}")
            
    except Exception as e:
        print(f"Error with filtered request: {e}")
        return
    
    print("\n3. COMPARISON AND ROOT CAUSE ANALYSIS")
    print("-" * 40)
    
    if july_2024_no_filter and july_2024_filtered:
        no_filter_spend = july_2024_no_filter['spend']
        filtered_spend = july_2024_filtered['spend']
        
        print(f"Backend API says:")
        print(f"  No filters:   ${no_filter_spend:,.2f}")
        print(f"  With filters: ${filtered_spend:,.2f}")
        print(f"  Difference:   ${filtered_spend - no_filter_spend:,.2f}")
        
        if filtered_spend > no_filter_spend:
            print(f"\n🚨 CONFIRMED: Backend API is returning WRONG data!")
            print(f"   The TikTok service backend logic has a bug")
            print(f"   Filtered ({filtered_spend:,.2f}) > Unfiltered ({no_filter_spend:,.2f})")
            
            print(f"\n   But our database query showed:")
            print(f"   - Raw DB no filters:   $42,904.99")
            print(f"   - Raw DB with filters: $42,166.23")
            print(f"   ")
            print(f"   This means the TikTok SERVICE pivot calculation is wrong!")
            
        else:
            print(f"\n✅ Backend API is returning correct data")
            print(f"   The issue must be in frontend calculation")
    else:
        print("Cannot compare - missing data in one or both responses")

if __name__ == "__main__":
    debug_api_responses()