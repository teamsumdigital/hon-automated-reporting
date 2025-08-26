#!/usr/bin/env python3
"""
Test API directly to check July 2025 values
"""

import requests

def test_api_directly():
    print("TESTING TIKTOK API DIRECTLY")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8007/api/tiktok-reports/dashboard")
        response.raise_for_status()
        data = response.json()
        
        # Find July months
        july_months = [p for p in data.get('pivot_data', []) if p.get('month', '').endswith('-07')]
        
        print("July months found:")
        total_july = 0
        for july in july_months:
            month = july.get('month')
            spend = july.get('spend', 0)
            print(f"  {month}: ${spend:,.2f}")
            total_july += spend
            
        print(f"\nTotal July (all years): ${total_july:,.2f}")
        
        # Test with filters
        print("\n" + "="*30)
        print("TESTING WITH FILTERS")
        print("="*30)
        
        response_filtered = requests.get("http://localhost:8007/api/tiktok-reports/dashboard", params={
            "categories": "Play Mats,Standing Mats,Tumbling Mats,Play Furniture,Multi Category"
        })
        response_filtered.raise_for_status()
        data_filtered = response_filtered.json()
        
        july_months_filtered = [p for p in data_filtered.get('pivot_data', []) if p.get('month', '').endswith('-07')]
        
        print("July months found (filtered):")
        total_july_filtered = 0
        for july in july_months_filtered:
            month = july.get('month')
            spend = july.get('spend', 0)
            print(f"  {month}: ${spend:,.2f}")
            total_july_filtered += spend
            
        print(f"\nTotal July filtered (all years): ${total_july_filtered:,.2f}")
        
        print("\n" + "="*30)
        print("COMPARISON")
        print("="*30)
        print(f"No filters:   ${total_july:,.2f}")
        print(f"With filters: ${total_july_filtered:,.2f}")
        print(f"Difference:   ${total_july_filtered - total_july:,.2f}")
        
        if total_july_filtered > total_july:
            print("🚨 BUG STILL EXISTS IN API!")
        else:
            print("✅ API is working correctly now")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_directly()