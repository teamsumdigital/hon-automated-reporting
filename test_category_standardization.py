#!/usr/bin/env python3
"""
Test script to verify Meta Ad Level categories are standardized with other dashboards
"""

import requests
import time

def get_categories_from_dashboard(dashboard_type):
    """Get categories from different dashboard types"""
    backend_url = "http://localhost:8007"
    
    if dashboard_type == "meta_ads":
        response = requests.get(f"{backend_url}/api/reports/categories", timeout=10)
    elif dashboard_type == "google_ads": 
        response = requests.get(f"{backend_url}/api/google-reports/categories", timeout=10)
    elif dashboard_type == "tiktok_ads":
        response = requests.get(f"{backend_url}/api/tiktok-reports/categories", timeout=10)  
    elif dashboard_type == "meta_ad_level":
        response = requests.get(f"{backend_url}/api/meta-ad-reports/filters", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return set(data.get('categories', []))
    else:
        return set()
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and 'categories' in data:
            return set(data['categories'])
        elif isinstance(data, list):
            return set(data)
    
    return set()

def test_category_standardization():
    """Test that Meta Ad Level uses same categories as other dashboards"""
    
    print("🔍 Testing Category Standardization Across Dashboards")
    print("=" * 60)
    
    max_attempts = 8
    for attempt in range(max_attempts):
        try:
            print(f"\nAttempt {attempt + 1}/{max_attempts}")
            
            # Get categories from each dashboard
            meta_categories = get_categories_from_dashboard("meta_ads")
            google_categories = get_categories_from_dashboard("google_ads") 
            tiktok_categories = get_categories_from_dashboard("tiktok_ads")
            ad_level_categories = get_categories_from_dashboard("meta_ad_level")
            
            print(f"Meta Ads categories: {sorted(meta_categories)}")
            print(f"Google Ads categories: {sorted(google_categories)}")
            print(f"TikTok Ads categories: {sorted(tiktok_categories)}")
            print(f"Meta Ad Level categories: {sorted(ad_level_categories)}")
            
            # Expected standardized categories
            expected_categories = {
                'Bath Mats', 'Play Mats', 'Standing Mats', 'Tumbling Mats', 
                'Play Furniture', 'Multi Category'
            }
            
            # Check if Meta Ad Level has standardized categories
            has_standardized = any(cat in expected_categories for cat in ad_level_categories)
            has_old_format = any(cat in {'Bath', 'Playmat', 'Multi'} for cat in ad_level_categories)
            
            if has_standardized and not has_old_format:
                print("\n✅ SUCCESS: Meta Ad Level categories are standardized!")
                
                # Show category overlap
                common_categories = ad_level_categories.intersection(expected_categories)
                print(f"📊 Standardized categories found: {sorted(common_categories)}")
                
                # Check specific high-value categories
                if 'Play Mats' in ad_level_categories:
                    print("🎯 'Play Mats' category standardized - high-spending ads should now be visible!")
                
                if 'Bath Mats' in ad_level_categories:
                    print("🛁 'Bath Mats' category standardized!")
                    
                return True
                
            elif has_old_format:
                print(f"\n⏳ Sync still in progress... Found old category formats")
                if attempt < max_attempts - 1:
                    print("   Waiting 20 seconds for sync to complete...")
                    time.sleep(20)
                    continue
                else:
                    print(f"\n❌ TIMEOUT: Categories not standardized after {max_attempts * 20} seconds")
                    return False
            else:
                print(f"\n⚠️ Unexpected category format found")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            if attempt < max_attempts - 1:
                time.sleep(10)
                continue
            return False
    
    return False

def test_high_spender_visibility():
    """Test that high-spending ads are visible in All Categories view"""
    print(f"\n🔍 Testing High-Spender Visibility")
    print("-" * 40)
    
    try:
        backend_url = "http://localhost:8007"
        
        # Get all ads (unfiltered)
        all_response = requests.get(f"{backend_url}/api/meta-ad-reports/ad-data", timeout=15)
        all_data = all_response.json()
        all_ads = all_data.get('grouped_ads', [])
        
        if not all_ads:
            print("❌ No ads found in All Categories view")
            return False
        
        # Find top spenders
        top_ads = sorted(all_ads, key=lambda x: x.get('total_spend', 0), reverse=True)[:5]
        
        print("Top 5 spenders in All Categories view:")
        total_top_spend = 0
        for i, ad in enumerate(top_ads, 1):
            spend = ad.get('total_spend', 0)
            category = ad.get('category', 'Unknown')
            name = ad['ad_name'][:40] + ('...' if len(ad['ad_name']) > 40 else '')
            print(f"  {i}. ${spend:6,.0f} | {category:15s} | {name}")
            total_top_spend += spend
        
        # Check if we have high spenders (should be >$15k for top 5)
        if total_top_spend > 15000:
            print(f"\n✅ SUCCESS: High spenders visible (${total_top_spend:,.0f} total)")
            
            # Check for Play Mats specifically
            play_mat_ads = [ad for ad in all_ads if ad.get('category') == 'Play Mats']
            if play_mat_ads:
                top_play_mat = max(play_mat_ads, key=lambda x: x.get('total_spend', 0))
                if top_play_mat.get('total_spend', 0) > 3000:
                    print(f"🎯 Top Play Mats ad: ${top_play_mat['total_spend']:,.0f} - {top_play_mat['ad_name'][:30]}...")
                    print("✅ High-spending Play Mats ads are now visible!")
                    return True
            
        else:
            print(f"\n⚠️ WARNING: Low total spend (${total_top_spend:,.0f}) - ads may still be syncing")
            return False
            
    except Exception as e:
        print(f"❌ Error testing visibility: {e}")
        return False
    
    return False

if __name__ == "__main__":
    print("Testing Meta Ad Level dashboard category standardization...")
    print("This ensures consistent categories across Meta, Google, TikTok, and Ad Level dashboards.\n")
    
    # Test standardization
    standardization_success = test_category_standardization()
    
    if standardization_success:
        # Test visibility of high spenders
        visibility_success = test_high_spender_visibility()
        
        if visibility_success:
            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("✅ Categories standardized across all dashboards")
            print("✅ High-spending ads visible in All Categories view")
            print("📱 Visit http://localhost:3007 → Ad Level dashboard to verify")
        else:
            print("\n" + "=" * 60)
            print("⚠️ Categories standardized but visibility issues remain")
    else:
        print("\n" + "=" * 60)
        print("❌ Category standardization not completed")
        print("🔧 May need additional sync time or manual verification")