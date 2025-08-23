#!/usr/bin/env python3
"""
Debug Google Ads CPM calculation issue with Multi Category filter
"""

import requests

def debug_google_cpm():
    """Debug the Google Ads CPM calculation with filtering"""
    
    backend_url = "http://localhost:8007"
    
    print("🔍 Debugging Google Ads CPM with Multi Category Filter")
    print("=" * 60)
    
    try:
        # Test Google Ads data with Multi Category filter
        response = requests.get(f"{backend_url}/api/google-reports/campaigns?categories=Multi Category", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            return False
        
        data = response.json()
        campaigns = data.get('campaigns_data', [])[:5]  # First 5 campaigns
        
        if not campaigns:
            print("❌ No Multi Category campaigns found")
            return False
        
        print(f"📊 Found {len(campaigns)} Multi Category campaigns")
        print("\nCPM Analysis:")
        print("=" * 80)
        print(f"{'#':<2} {'Spend':<10} {'Impressions':<12} {'Reported CPM':<12} {'Calculated CPM':<15} {'Issue?'}")
        print("-" * 80)
        
        issues_found = 0
        
        for i, campaign in enumerate(campaigns, 1):
            spend = campaign.get('spend', 0)
            impressions = campaign.get('impressions', 0)
            reported_cpm = campaign.get('cpm', 0)
            
            # Calculate what CPM should be
            calculated_cpm = (spend / impressions) * 1000 if impressions > 0 else 0
            
            # Check if there's a significant discrepancy
            issue = ""
            if impressions == 0:
                issue = "No impressions"
            elif abs(reported_cpm - calculated_cpm) > 1:
                issue = "❌ Mismatch!"
                issues_found += 1
            else:
                issue = "✅ OK"
            
            print(f"{i:<2} ${spend:<9.0f} {impressions:<12,} ${reported_cpm:<11.2f} ${calculated_cpm:<14.2f} {issue}")
        
        print("-" * 80)
        
        if issues_found > 0:
            print(f"\n❌ Found {issues_found} CPM calculation issues!")
            print("\n🔍 Possible causes:")
            print("1. Impressions not being passed correctly to frontend")
            print("2. Backend CPM calculation using wrong impressions value")
            print("3. Frontend client-side filtering not recalculating CPM properly")
            
            # Let's check the raw API data without filtering
            print(f"\n🔍 Testing without category filter...")
            
            all_response = requests.get(f"{backend_url}/api/google-reports/campaigns", timeout=10)
            if all_response.status_code == 200:
                all_data = all_response.json()
                all_campaigns = [c for c in all_data.get('campaigns_data', []) if c.get('category') == 'Multi Category'][:3]
                
                print(f"\n📊 Same campaigns without filter (should be same data):")
                for i, campaign in enumerate(all_campaigns, 1):
                    spend = campaign.get('spend', 0)
                    impressions = campaign.get('impressions', 0)
                    cpm = campaign.get('cpm', 0)
                    print(f"  {i}. Spend: ${spend:.0f}, Impressions: {impressions:,}, CPM: ${cmp:.2f}")
            
            return False
        else:
            print(f"\n✅ All CPM calculations look correct!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    debug_google_cpm()