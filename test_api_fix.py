#!/usr/bin/env python3
"""
Test the API fix to ensure Standing Mat ads appear consistently
"""

import requests
import json
from collections import defaultdict

# API endpoints
BASE_URL = "http://localhost:8007/api/meta-ad-reports"

def test_api_fix():
    """Test that the API fix resolves the Standing Mat issue"""
    
    print("🧪 Testing API Fix for Standing Mat Issue\n")
    
    # Test 1: Get unfiltered data (All Categories)
    print("1️⃣ Testing unfiltered API call (All Categories)...")
    try:
        response = requests.get(f"{BASE_URL}/ad-data")
        response.raise_for_status()
        unfiltered_data = response.json()
        
        print(f"   Status: {unfiltered_data.get('status', 'unknown')}")
        print(f"   Total ads returned: {unfiltered_data.get('count', 0)}")
        
        # Count Standing Mat ads
        standing_mat_ads = {}
        for ad in unfiltered_data.get('grouped_ads', []):
            if ad['category'] == 'Standing Mats':
                standing_mat_ads[ad['ad_name']] = ad['total_spend']
        
        print(f"   Standing Mat ads found: {len(standing_mat_ads)}")
        
        # Check for specific high-spend ads
        target_ads = [
            "Standing Mats Video Ad Don't Buy Iteration",
            "Standing Mat Launch Multiple Styles Video Ad V1",
            "Standing Mat Launch Swatch Lifestyle Devon"
        ]
        
        print("\n   Checking for high-spend Standing Mat ads:")
        for ad_name in target_ads:
            if ad_name in standing_mat_ads:
                print(f"   ✅ Found: {ad_name} (${standing_mat_ads[ad_name]:,.2f})")
            else:
                print(f"   ❌ MISSING: {ad_name}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Get filtered data (Standing Mats only)
    print("\n\n2️⃣ Testing filtered API call (Standing Mats only)...")
    try:
        response = requests.get(f"{BASE_URL}/ad-data", params={"categories": "Standing Mats"})
        response.raise_for_status()
        filtered_data = response.json()
        
        print(f"   Status: {filtered_data.get('status', 'unknown')}")
        print(f"   Total ads returned: {filtered_data.get('count', 0)}")
        
        filtered_standing_mat_ads = {}
        for ad in filtered_data.get('grouped_ads', []):
            filtered_standing_mat_ads[ad['ad_name']] = ad['total_spend']
        
        print(f"   Standing Mat ads found: {len(filtered_standing_mat_ads)}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: Compare results
    print("\n\n3️⃣ Comparing results...")
    
    # Both should have the same Standing Mat ads
    if len(standing_mat_ads) == len(filtered_standing_mat_ads):
        print(f"   ✅ SUCCESS: Both queries return {len(standing_mat_ads)} Standing Mat ads!")
        
        # Verify the high-spend ads are in both
        all_found = True
        for ad_name in target_ads:
            if ad_name not in standing_mat_ads or ad_name not in filtered_standing_mat_ads:
                all_found = False
                break
        
        if all_found:
            print("   ✅ All high-spend Standing Mat ads are present in both views!")
            return True
        else:
            print("   ❌ Some high-spend ads are still missing")
            return False
    else:
        print(f"   ❌ MISMATCH: Unfiltered has {len(standing_mat_ads)} ads, filtered has {len(filtered_standing_mat_ads)}")
        
        # Find the difference
        missing_in_unfiltered = set(filtered_standing_mat_ads.keys()) - set(standing_mat_ads.keys())
        if missing_in_unfiltered:
            print(f"\n   Missing in unfiltered view: {len(missing_in_unfiltered)} ads")
            print("   Top 5 by spend:")
            sorted_missing = sorted(
                [(ad, filtered_standing_mat_ads[ad]) for ad in missing_in_unfiltered],
                key=lambda x: x[1],
                reverse=True
            )[:5]
            for ad_name, spend in sorted_missing:
                print(f"      ${spend:,.2f} - {ad_name}")
        
        return False
    
    # Test 4: Check summary endpoint
    print("\n\n4️⃣ Testing summary endpoint...")
    try:
        # Unfiltered summary
        response = requests.get(f"{BASE_URL}/summary")
        response.raise_for_status()
        unfiltered_summary = response.json()
        
        # Standing Mats only summary
        response = requests.get(f"{BASE_URL}/summary", params={"categories": "Standing Mats"})
        response.raise_for_status()
        standing_mats_summary = response.json()
        
        print(f"   Unfiltered total spend: ${unfiltered_summary.get('total_spend', 0):,.2f}")
        print(f"   Standing Mats spend: ${standing_mats_summary.get('total_spend', 0):,.2f}")
        print(f"   Standing Mats % of total: {(standing_mats_summary.get('total_spend', 0) / unfiltered_summary.get('total_spend', 1) * 100):.1f}%")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("⚠️  Make sure the backend server is running on port 8007")
    print("   Run: cd backend && uvicorn main:app --reload --port 8007\n")
    
    success = test_api_fix()
    
    if success:
        print("\n\n✅ API FIX VERIFIED: Standing Mat ads now appear consistently!")
    else:
        print("\n\n❌ API FIX INCOMPLETE: Issues still remain")