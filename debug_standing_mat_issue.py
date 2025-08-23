#!/usr/bin/env python3
"""
Debug Standing Mat categorization issue in Meta Ad Level dashboard
"""

import requests
import json
from collections import Counter

def debug_standing_mat_issue():
    backend_url = "http://localhost:8007"
    
    print("🔍 Meta Ad Level Standing Mat Categorization Debug")
    print("=" * 60)
    
    try:
        # Step 1: Get all Meta Ad Level data
        print("📊 STEP 1: All Meta Ad Level Data")
        all_response = requests.get(f"{backend_url}/api/meta-ad-reports/ad-data", timeout=15)
        
        if all_response.status_code != 200:
            print(f"❌ API Error: {all_response.status_code}")
            return
            
        all_data = all_response.json()
        all_ads = all_data.get('grouped_ads', [])
        
        print(f"Total ads in Meta Ad Level: {len(all_ads)}")
        
        # Count categories
        all_categories = Counter(ad['category'] for ad in all_ads)
        print("\nAll Meta Ad Level Categories:")
        for category, count in all_categories.most_common():
            total_spend = sum(float(ad['total_spend']) for ad in all_ads if ad['category'] == category)
            print(f"  {category}: {count} ads, ${total_spend:,.0f} spend")
        
        # Step 2: Get Standing Mat filtered data
        print(f"\n📊 STEP 2: Standing Mat Filtered Data")
        standing_response = requests.get(f"{backend_url}/api/meta-ad-reports/ad-data?categories=Standing Mats", timeout=15)
        
        if standing_response.status_code == 200:
            standing_data = standing_response.json()
            standing_ads = standing_data.get('grouped_ads', [])
            
            print(f"Standing Mat filtered ads: {len(standing_ads)}")
            
            # Show top spenders when filtered
            standing_by_spend = sorted(standing_ads, key=lambda x: float(x['total_spend']), reverse=True)
            
            print("\nTop 10 Standing Mat ads (when filtered):")
            print(f"{'Ad Name':<50} {'Spend':<8} {'Category':<15}")
            print("-" * 85)
            
            top_standing_ads = []
            for i, ad in enumerate(standing_by_spend[:10]):
                spend = float(ad['total_spend'])
                ad_name = ad['ad_name'][:47] + "..." if len(ad['ad_name']) > 50 else ad['ad_name']
                category = ad['category']
                
                print(f"{ad_name:<50} ${spend:<7.0f} {category:<15}")
                top_standing_ads.append(ad)
        
        # Step 3: Check if these same ads appear in "All Categories"
        print(f"\n📊 STEP 3: Cross-Reference with All Categories")
        
        if 'top_standing_ads' in locals():
            print("Checking if top Standing Mat ads appear in 'All Categories' view...")
            
            found_count = 0
            missing_count = 0
            
            for top_ad in top_standing_ads:
                top_ad_name = top_ad['ad_name']
                
                # Look for this ad in all_ads
                found_ad = next((ad for ad in all_ads if ad['ad_name'] == top_ad_name), None)
                
                if found_ad:
                    found_count += 1
                    if found_ad['category'] != 'Standing Mats':
                        print(f"  ❌ Ad {top_ad_name[:30]}...: Category changed from 'Standing Mats' to '{found_ad['category']}'")
                else:
                    missing_count += 1
                    print(f"  ❌ Ad {top_ad_name[:30]}...: MISSING from All Categories view!")
            
            print(f"\nSummary:")
            print(f"  Found in All Categories: {found_count}/10")
            print(f"  Missing from All Categories: {missing_count}/10")
            
            if missing_count > 0:
                print(f"  🚨 ISSUE CONFIRMED: {missing_count} top Standing Mat ads are missing!")
        
        # Step 4: Check for category inconsistencies in ad name parsing
        print(f"\n📊 STEP 4: Category Analysis")
        
        # Look for ads that contain "standing" in the name but aren't categorized as Standing Mats
        standing_name_ads = [ad for ad in all_ads if 'standing' in ad['ad_name'].lower()]
        
        standing_name_categories = Counter(ad['category'] for ad in standing_name_ads)
        print(f"\nAds with 'standing' in name by category:")
        for category, count in standing_name_categories.most_common():
            print(f"  {category}: {count} ads")
        
        # Look for potential mis-categorizations
        non_standing_mat_but_has_standing = [
            ad for ad in standing_name_ads 
            if ad['category'] != 'Standing Mats'
        ]
        
        if non_standing_mat_but_has_standing:
            print(f"\n🔍 Potential mis-categorized Standing Mat ads:")
            for ad in non_standing_mat_but_has_standing[:5]:  # Show first 5
                print(f"  Ad: {ad['ad_name'][:60]}...")
                print(f"  Category: {ad['category']} (should be Standing Mats?)")
                print(f"  Spend: ${float(ad['total_spend']):.0f}")
                print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_standing_mat_issue()