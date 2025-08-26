#!/usr/bin/env python3
"""
Test TikTok dashboard data calculation to find the filtering bug
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_dashboard_filtering():
    print("TESTING TIKTOK DASHBOARD API FILTERING")
    print("=" * 60)
    
    API_BASE_URL = "http://localhost:8007"
    
    # Test 1: No filters (should show ALL categories)
    print("\n1. TESTING NO FILTERS (ALL CATEGORIES)")
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
            print(f"July 2024 spend (no filters): ${july_2024_no_filter['spend']:,.2f}")
        else:
            print("No July 2024 data found in pivot_data")
            
        print(f"Available categories: {data_no_filter.get('categories', [])}")
        
    except Exception as e:
        print(f"Error fetching no-filter data: {e}")
        return
    
    # Test 2: With multiple category filters
    print("\n\n2. TESTING WITH CATEGORY FILTERS")
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
        
        # Find July 2024 in pivot data
        july_2024_filtered = None
        for pivot in data_filtered.get('pivot_data', []):
            if pivot.get('month') == '2024-07':
                july_2024_filtered = pivot
                break
        
        if july_2024_filtered:
            print(f"July 2024 spend (with filters): ${july_2024_filtered['spend']:,.2f}")
        else:
            print("No July 2024 data found in filtered pivot_data")
            
        print(f"Filtered categories: Play Mats,Standing Mats,Tumbling Mats,Play Furniture,Multi Category")
        
    except Exception as e:
        print(f"Error fetching filtered data: {e}")
        return
    
    # Compare results
    print("\n\n3. COMPARISON")
    print("-" * 40)
    
    if july_2024_no_filter and july_2024_filtered:
        no_filter_spend = july_2024_no_filter['spend']
        filtered_spend = july_2024_filtered['spend']
        
        print(f"No filters:    ${no_filter_spend:,.2f}")
        print(f"With filters:  ${filtered_spend:,.2f}")
        print(f"Difference:    ${filtered_spend - no_filter_spend:,.2f}")
        
        if filtered_spend > no_filter_spend:
            print("\n🚨 CRITICAL BUG CONFIRMED!")
            print("   Filtered total is HIGHER than unfiltered total.")
            print("   This is the bug the user reported.")
            
            # Show the exact numbers the user reported
            print(f"\n   User reported:")
            print(f"   - No filters: ~$53,290")
            print(f"   - With filters: ~$64,071") 
            print(f"   - Difference: ~$10,781")
            print(f"\n   We found:")
            print(f"   - No filters: ${no_filter_spend:,.2f}")
            print(f"   - With filters: ${filtered_spend:,.2f}")
            print(f"   - Difference: ${filtered_spend - no_filter_spend:,.2f}")
            
        else:
            print("\n✅ Dashboard filtering appears correct.")
            print("   The issue may be elsewhere or resolved.")
    
    else:
        print("\nCould not compare - missing July 2024 data in one or both responses")

if __name__ == "__main__":
    test_dashboard_filtering()