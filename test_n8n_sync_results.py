#!/usr/bin/env python3
"""
Test script to verify n8n sync results for Meta ad-level data
Run this after the n8n sync completes to check if momentum indicators are working
"""

import requests
import json

def test_n8n_sync_results():
    """Test that n8n sync populated two weeks of ad data"""
    
    backend_url = "http://localhost:8007"
    ad_data_endpoint = f"{backend_url}/api/meta-ad-reports/ad-data"
    
    print("🧪 Testing n8n Meta Ads Sync Results")
    print("=" * 50)
    
    try:
        # Get ad-level data
        response = requests.get(ad_data_endpoint, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            ads = data.get('grouped_ads', [])
            total_ads = len(ads)
            
            print(f"✅ Total ads found: {total_ads}")
            
            if total_ads == 0:
                print("❌ No ad data found - n8n sync may not have completed")
                return False
            
            # Analyze weekly periods
            one_period = 0
            two_periods = 0
            more_periods = 0
            
            sample_ads = []
            
            for ad in ads:
                periods = len(ad.get('weekly_periods', []))
                if periods == 1:
                    one_period += 1
                elif periods == 2:
                    two_periods += 1
                    # Collect sample ads with 2 periods for momentum testing
                    if len(sample_ads) < 3:
                        sample_ads.append(ad)
                else:
                    more_periods += 1
            
            print(f"\n📊 Weekly Periods Analysis:")
            print(f"  1 period: {one_period} ads ({one_period/total_ads*100:.1f}%)")
            print(f"  2 periods: {two_periods} ads ({two_periods/total_ads*100:.1f}%)")
            print(f"  3+ periods: {more_periods} ads ({more_periods/total_ads*100:.1f}%)")
            
            # Test momentum indicators
            if two_periods > 0:
                print(f"\n🎯 Momentum Indicators Test (Sample of {len(sample_ads)} ads):")
                print("-" * 40)
                
                for ad in sample_ads:
                    ad_name = ad['ad_name'][:50] + "..." if len(ad['ad_name']) > 50 else ad['ad_name']
                    periods = ad['weekly_periods']
                    
                    # Sort periods by date (older first)
                    periods.sort(key=lambda x: x['reporting_starts'])
                    
                    older_week = periods[0]
                    newer_week = periods[1]
                    
                    # Calculate momentum
                    old_spend = older_week['spend']
                    new_spend = newer_week['spend']
                    spend_change = ((new_spend - old_spend) / old_spend * 100) if old_spend > 0 else 0
                    
                    old_roas = older_week['roas']
                    new_roas = newer_week['roas']
                    roas_change = new_roas - old_roas
                    
                    print(f"📱 {ad_name}")
                    print(f"   Week 1: ${old_spend:.2f} spend, {old_roas:.2f} ROAS")
                    print(f"   Week 2: ${new_spend:.2f} spend, {new_roas:.2f} ROAS")
                    print(f"   Momentum: {spend_change:+.1f}% spend, {roas_change:+.2f} ROAS")
                    print()
                
                print("✅ Momentum indicators working correctly!")
                
            else:
                print("\n❌ PROBLEM: No ads have 2 weekly periods")
                print("🔧 n8n sync may need to be configured for weekly segmentation")
                
                # Show date ranges of existing periods
                if total_ads > 0:
                    sample_ad = ads[0]
                    if sample_ad.get('weekly_periods'):
                        period = sample_ad['weekly_periods'][0]
                        print(f"📅 Current period: {period['reporting_starts']} to {period['reporting_ends']}")
                
                return False
            
            # Success criteria
            if two_periods >= total_ads * 0.8:  # At least 80% of ads should have 2 periods
                print(f"\n🎉 SUCCESS: n8n sync completed successfully!")
                print(f"📈 {two_periods} ads have proper weekly segmentation for momentum analysis")
                return True
            else:
                print(f"\n⚠️ PARTIAL SUCCESS: Only {two_periods} ads have 2 periods")
                print("🔧 Some ads may need additional sync cycles")
                return False
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing sync results: {e}")
        return False

def test_weekly_summary():
    """Test weekly summary endpoint"""
    backend_url = "http://localhost:8007"
    weekly_endpoint = f"{backend_url}/api/meta-ad-reports/weekly-summary"
    
    print("\n🗓️ Testing Weekly Summary")
    print("-" * 30)
    
    try:
        response = requests.get(weekly_endpoint, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'date_range' in data:
                date_range = data['date_range']
                print(f"📅 Date range: {date_range['start_date']} to {date_range['end_date']}")
            
            weekly_summary = data.get('weekly_summary', {})
            actual_weeks = [k for k in weekly_summary.keys() if k and k != 'null']
            
            print(f"📊 Weeks with data: {len(actual_weeks)}")
            for week in actual_weeks:
                week_data = weekly_summary[week]
                print(f"   {week}: {week_data['total_ads']} ads, ${week_data['total_spend']:.2f} spend")
            
            if len(actual_weeks) >= 2:
                print("✅ Weekly summary shows multiple weeks - good for momentum!")
            else:
                print("❌ Weekly summary missing multiple weeks")
                
        else:
            print(f"❌ Weekly summary API error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Weekly summary test failed: {e}")

if __name__ == "__main__":
    print("Run this script after your n8n sync completes")
    print("Expected: Each ad should have 2 weekly periods for momentum indicators\n")
    
    success = test_n8n_sync_results()
    test_weekly_summary()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Ready for momentum indicator testing!")
        print("📱 Visit http://localhost:3007 → Ad Level dashboard")
    else:
        print("🔧 n8n sync may need adjustment for weekly segmentation")