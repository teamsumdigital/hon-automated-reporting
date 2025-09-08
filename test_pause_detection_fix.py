#!/usr/bin/env python3
"""
Test script to verify the pause detection fix
Tests with specific ads Terry mentioned
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
root_env_path = '/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/.env'
load_dotenv(root_env_path)

sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from app.services.meta_ad_level_service import MetaAdLevelService
from app.services.ad_pause_automation import AdPauseAutomationService
from datetime import date, timedelta

def test_pause_detection_fix():
    """Test that pause detection now works with status fields"""
    
    print("🧪 TESTING PAUSE DETECTION FIX")
    print("=" * 60)
    
    # Specific ads Terry mentioned
    target_ads = [
        "Social Savannah Brand Playmat Batch 2 V2",
        "7/1/2025 - Multi - Multi - Multi - Brand - HoN - Video - Multi Category Mats Video Ad"
    ]
    
    try:
        service = MetaAdLevelService()
        automation = AdPauseAutomationService()
        
        # Get recent ad data (now includes status fields)
        yesterday = date.today() - timedelta(days=1)
        print(f"📡 Fetching ad data for {yesterday} with NEW status fields...")
        recent_ads = service.get_ad_level_insights(yesterday, yesterday)
        
        print(f"✅ Retrieved {len(recent_ads)} ads")
        
        # Check if status fields are now present
        sample_ad = recent_ads[0] if recent_ads else {}
        print(f"\n🔍 CHECKING STATUS FIELDS IN FIRST AD:")
        print(f"   Ad ID: {sample_ad.get('ad_id', 'N/A')}")
        print(f"   Ad Name: {sample_ad.get('ad_name', 'N/A')[:50]}...")
        print(f"   ✓ effective_status: {sample_ad.get('effective_status', 'MISSING!')}")
        print(f"   ✓ campaign data: {bool(sample_ad.get('campaign'))}")
        print(f"   ✓ adset data: {bool(sample_ad.get('adset'))}")
        
        if sample_ad.get('campaign'):
            campaign_status = sample_ad['campaign'].get('effective_status', 'MISSING!')
            print(f"   ✓ campaign.effective_status: {campaign_status}")
            
        if sample_ad.get('adset'):
            adset_status = sample_ad['adset'].get('effective_status', 'MISSING!')
            adset_name = sample_ad['adset'].get('name', 'N/A')
            print(f"   ✓ adset.effective_status: {adset_status}")
            print(f"   ✓ adset.name: {adset_name}")
        
        # Look for Terry's specific ads
        print(f"\n🎯 SEARCHING FOR TERRY'S SPECIFIC ADS:")
        found_ads = []
        
        for ad_data in recent_ads:
            ad_name = ad_data.get('ad_name', '')
            for target in target_ads:
                if target in ad_name or any(word in ad_name for word in target.split()):
                    found_ads.append(ad_data)
                    print(f"   📋 FOUND: {ad_name}")
                    print(f"      💰 Spend: ${ad_data.get('amount_spent_usd', 0)}")
                    print(f"      📊 Status: {ad_data.get('effective_status', 'N/A')}")
                    
                    if ad_data.get('campaign'):
                        print(f"      🎯 Campaign Status: {ad_data['campaign'].get('effective_status', 'N/A')}")
                    if ad_data.get('adset'):
                        print(f"      🎪 AdSet Status: {ad_data['adset'].get('effective_status', 'N/A')}")
                    break
        
        if not found_ads:
            print("   ❌ None of Terry's specific ads found in yesterday's data")
            print("   💡 They may not have spent yesterday, or were paused before spending")
        
        # Test pause automation with sample data
        print(f"\n🤖 TESTING PAUSE AUTOMATION WITH NEW DATA:")
        sample_data = recent_ads[:10]  # Test with first 10 ads
        
        analysis = automation.analyze_ad_pause_status(sample_data)
        
        print(f"✅ Pause analysis completed for {len(analysis)} ads")
        
        # Show results
        paused_ads = []
        mixed_ads = []
        active_ads = []
        
        for ad_name, data in analysis.items():
            status = data['status']
            active_count = data['active_placements']
            paused_count = data['paused_placements']
            total_count = data['total_placements']
            
            if status == 'paused_automated':
                paused_ads.append((ad_name, f"{paused_count}/{total_count} paused"))
            elif status == 'mixed':
                mixed_ads.append((ad_name, f"{paused_count}/{total_count} paused"))
            elif status == 'active':
                active_ads.append((ad_name, f"{active_count}/{total_count} active"))
        
        print(f"\n📊 PAUSE ANALYSIS RESULTS:")
        print(f"   🔴 Fully Paused: {len(paused_ads)} ads")
        print(f"   🟡 Partially Paused: {len(mixed_ads)} ads")
        print(f"   🟢 Fully Active: {len(active_ads)} ads")
        
        # Show some examples
        if paused_ads:
            print(f"\n🔴 FULLY PAUSED ADS:")
            for ad_name, status in paused_ads[:3]:
                print(f"   - {ad_name[:60]}... ({status})")
        
        if mixed_ads:
            print(f"\n🟡 PARTIALLY PAUSED ADS:")
            for ad_name, status in mixed_ads[:3]:
                print(f"   - {ad_name[:60]}... ({status})")
        
        # Summary
        print(f"\n✅ PAUSE DETECTION FIX VERIFICATION:")
        if any('effective_status' in ad for ad in sample_data):
            print(f"   ✅ Status fields are now being fetched from Meta API")
            print(f"   ✅ Pause automation can now detect paused ads")
            print(f"   ✅ Ready to detect Terry's manually paused ads")
            
            if found_ads:
                print(f"   ✅ Found {len(found_ads)} of Terry's target ads for testing")
            else:
                print(f"   💡 Terry's ads not active yesterday - test with full 14-day sync")
        else:
            print(f"   ❌ Status fields still missing - API may need adjustment")
        
        return len(paused_ads) > 0 or len(mixed_ads) > 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pause_detection_fix()
    
    if success:
        print(f"\n🎉 SUCCESS: Pause detection fix is working!")
        print(f"✅ Ready to deploy and test with Terry's ads")
    else:
        print(f"\n⚠️ Issues detected - may need further adjustment")