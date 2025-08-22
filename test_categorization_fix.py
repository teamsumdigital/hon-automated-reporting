#!/usr/bin/env python3
"""
Test script to verify the categorization fix is working
Checks if Playmat and Play Mat categories have been consolidated
"""

import requests
import time

def test_categorization_fix():
    """Test that categorization fix consolidated Playmat -> Play Mat"""
    
    backend_url = "http://localhost:8007"
    ad_data_endpoint = f"{backend_url}/api/meta-ad-reports/ad-data"
    
    print("🔧 Testing Categorization Fix")
    print("=" * 40)
    
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get(ad_data_endpoint, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                ads = data.get('grouped_ads', [])
                
                # Check category distribution
                category_totals = {}
                for ad in ads:
                    cat = ad.get('category', 'None')
                    if cat not in category_totals:
                        category_totals[cat] = {'count': 0, 'spend': 0}
                    category_totals[cat]['count'] += 1
                    category_totals[cat]['spend'] += ad['total_spend']
                
                print(f"\nAttempt {attempt + 1}/{max_attempts} - Category distribution:")
                for cat, info in sorted(category_totals.items(), key=lambda x: x[1]['spend'], reverse=True):
                    print(f"  {cat:15s}: {info['count']:3d} ads, ${info['spend']:7.0f} spend")
                
                # Check if fix worked
                has_playmat = 'Playmat' in category_totals
                has_play_mat = 'Play Mat' in category_totals
                
                if has_playmat:
                    print(f"\n⏳ Sync still in progress... Playmat category still exists")
                    if attempt < max_attempts - 1:
                        print("   Waiting 15 seconds for sync to complete...")
                        time.sleep(15)
                        continue
                    else:
                        print(f"\n❌ TIMEOUT: Sync did not complete after {max_attempts * 15} seconds")
                        return False
                else:
                    print(f"\n✅ SUCCESS: Playmat category has been consolidated!")
                    
                    if has_play_mat:
                        play_mat_info = category_totals['Play Mat']
                        print(f"📊 Play Mat category: {play_mat_info['count']} ads, ${play_mat_info['spend']:,.0f} spend")
                        
                        if play_mat_info['spend'] > 20000:  # Should have the high-spending ads now
                            print("🎯 High-spending play mat ads now properly categorized!")
                        else:
                            print("⚠️ Play Mat spend seems low - some ads may still be miscategorized")
                    
                    return True
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    return False

def test_dashboard_consistency():
    """Test that ads appear consistently in filtered and unfiltered views"""
    print(f"\n🔍 Testing Dashboard Consistency")
    print("-" * 30)
    
    backend_url = "http://localhost:8007"
    
    try:
        # Get all ads (unfiltered)
        all_ads_response = requests.get(f"{backend_url}/api/meta-ad-reports/ad-data", timeout=10)
        all_ads_data = all_ads_response.json()
        all_ads = all_ads_data.get('grouped_ads', [])
        
        # Get only Play Mat ads (filtered)
        play_mat_response = requests.get(f"{backend_url}/api/meta-ad-reports/ad-data?categories=Play Mat", timeout=10)
        play_mat_data = play_mat_response.json()  
        play_mat_ads = play_mat_data.get('grouped_ads', [])
        
        # Find Play Mat ads in the all ads list
        all_play_mats = [ad for ad in all_ads if ad.get('category') == 'Play Mat']
        
        print(f"📊 All ads count: {len(all_ads)}")
        print(f"📊 Play Mat ads (filtered): {len(play_mat_ads)}")
        print(f"📊 Play Mat ads (in all view): {len(all_play_mats)}")
        
        if len(play_mat_ads) == len(all_play_mats):
            print("✅ Consistency check PASSED: Same ads appear in both views")
            
            # Check if high spenders are present
            top_spender = max(all_play_mats, key=lambda x: x['total_spend']) if all_play_mats else None
            if top_spender and top_spender['total_spend'] > 3000:
                print(f"🎯 Top Play Mat spender: {top_spender['ad_name'][:50]}... (${top_spender['total_spend']:,.0f})")
                print("✅ High-spending ads now visible in All Categories view!")
            else:
                print("⚠️ Top spender seems low - may need additional investigation")
                
            return True
        else:
            print("❌ Consistency check FAILED: Different ads in filtered vs unfiltered views")
            return False
            
    except Exception as e:
        print(f"❌ Consistency test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing categorization fix for missing Standing Mat ads...")
    print("This script will wait for the n8n sync to complete and verify the fix.\n")
    
    # Test the categorization fix
    fix_success = test_categorization_fix()
    
    if fix_success:
        # Test dashboard consistency
        consistency_success = test_dashboard_consistency()
        
        if consistency_success:
            print("\n" + "=" * 50)
            print("🎉 ALL TESTS PASSED!")
            print("🔧 Categorization fix successfully applied")
            print("📱 Visit http://localhost:3007 → Ad Level dashboard")
            print("✅ High-spending play mat ads should now appear in All Categories view")
        else:
            print("\n" + "=" * 50)
            print("⚠️ Categorization fixed but consistency issues remain")
    else:
        print("\n" + "=" * 50)
        print("❌ Categorization fix did not complete successfully")
        print("🔧 May need to manually re-run the sync or check logs")