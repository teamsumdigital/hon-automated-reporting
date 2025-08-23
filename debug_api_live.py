#!/usr/bin/env python3
"""
Debug the live API to see what's actually happening
"""

import requests
import json

# API endpoints
BASE_URL = "http://localhost:8007/api/meta-ad-reports"

def debug_live_api():
    """Debug the live API responses"""
    
    print("🔍 Debugging Live API Responses\n")
    
    # Test 1: Get unfiltered data
    print("1️⃣ Testing unfiltered API call (All Categories)...")
    try:
        response = requests.get(f"{BASE_URL}/ad-data", timeout=30)
        response.raise_for_status()
        unfiltered_data = response.json()
        
        print(f"   Response status: {unfiltered_data.get('status', 'unknown')}")
        print(f"   Total ads returned: {unfiltered_data.get('count', 0)}")
        
        # Look for Standing Mat ads
        standing_mat_ads = []
        all_categories = {}
        
        for ad in unfiltered_data.get('grouped_ads', []):
            category = ad.get('category', 'Unknown')
            if category not in all_categories:
                all_categories[category] = 0
            all_categories[category] += 1
            
            if category == 'Standing Mats':
                standing_mat_ads.append({
                    'name': ad['ad_name'],
                    'spend': ad['total_spend']
                })
        
        print(f"\n   Categories found:")
        for cat, count in sorted(all_categories.items()):
            print(f"      {cat}: {count} ads")
        
        print(f"\n   Standing Mat ads found: {len(standing_mat_ads)}")
        
        # Check for specific high-spend ads
        high_spend_ads = [
            "Standing Mats Video Ad Don't Buy Iteration",
            "Standing Mat Launch Swatch Lifestyle Devon",
            "Standing Mat Launch Multiple Styles Video Ad V1"
        ]
        
        print("\n   Checking for high-spend Standing Mat ads in unfiltered view:")
        for ad_name in high_spend_ads:
            found = any(ad['name'] == ad_name for ad in standing_mat_ads)
            if found:
                spend = next(ad['spend'] for ad in standing_mat_ads if ad['name'] == ad_name)
                print(f"   ✅ Found: {ad_name} (${spend:,.2f})")
            else:
                print(f"   ❌ MISSING: {ad_name}")
        
        # Show top 5 Standing Mat ads that ARE in the unfiltered view
        if standing_mat_ads:
            print("\n   Top Standing Mat ads that ARE showing:")
            sorted_ads = sorted(standing_mat_ads, key=lambda x: x['spend'], reverse=True)[:5]
            for ad in sorted_ads:
                print(f"      ${ad['spend']:,.2f} - {ad['name']}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Get filtered data
    print("\n\n2️⃣ Testing filtered API call (Standing Mats only)...")
    try:
        response = requests.get(f"{BASE_URL}/ad-data", params={"categories": "Standing Mats"}, timeout=30)
        response.raise_for_status()
        filtered_data = response.json()
        
        print(f"   Total Standing Mat ads returned: {filtered_data.get('count', 0)}")
        
        # Get top 10 by spend
        filtered_ads = filtered_data.get('grouped_ads', [])
        sorted_filtered = sorted(filtered_ads, key=lambda x: x['total_spend'], reverse=True)[:10]
        
        print("\n   Top 10 Standing Mat ads when filtered:")
        for ad in sorted_filtered:
            print(f"      ${ad['total_spend']:,.2f} - {ad['ad_name']}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Check raw data count
    print("\n\n3️⃣ Checking if this is still a limit issue...")
    print("   If unfiltered returns exactly 100, 200, 500, or 1000 ads, we may have a limit issue")
    print(f"   Actual count: {unfiltered_data.get('count', 0)}")
    
    if unfiltered_data.get('count', 0) in [100, 200, 500, 1000]:
        print("   ⚠️  WARNING: Suspicious round number suggests a limit may still be in effect!")

if __name__ == "__main__":
    debug_live_api()