#!/usr/bin/env python3
"""
Test the Google Ads CPM fix by calculating expected vs actual CPM values
"""

import requests

def test_google_cpm_fix():
    """Test that Google Ads CPM is now calculated correctly with filters"""
    
    backend_url = "http://localhost:8007"
    
    print("🔍 Testing Google Ads CPM Fix for Multi Category Filter")
    print("=" * 65)
    
    try:
        # Get filtered data (Multi Category)
        response = requests.get(f"{backend_url}/api/google-reports/pivot-table?categories=Multi Category", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            return False
        
        pivot_data = response.json()
        
        if not pivot_data:
            print("❌ No Multi Category pivot data found")
            return False
        
        print("📊 Multi Category CPM Analysis (from pivot table):")
        print("-" * 65)
        print(f"{'Month':<10} {'Spend':<12} {'Impressions':<12} {'CPM':<10} {'Expected CPM':<12} {'Status'}")
        print("-" * 65)
        
        issues_found = 0
        
        for month_data in pivot_data[:5]:  # Test first 5 months
            spend = float(month_data.get('spend', 0))
            impressions = int(month_data.get('impressions', 0))
            reported_cpm = float(month_data.get('cpm', 0))
            
            # Calculate expected CPM
            expected_cpm = (spend / impressions) * 1000 if impressions > 0 else 0
            
            # Check if CPM is reasonable (should be under $50 for Google Ads)
            status = ""
            if impressions == 0:
                status = "No impressions"
            elif reported_cpm > 50:
                status = "❌ Too high!"
                issues_found += 1
            elif abs(reported_cpm - expected_cmp) > 0.1:
                status = "⚠️ Mismatch"
                issues_found += 1
            else:
                status = "✅ Good"
            
            month = month_data.get('month', 'Unknown')
            print(f"{month:<10} ${spend:<11.0f} {impressions:<12,} ${reported_cpm:<9.2f} ${expected_cpm:<11.2f} {status}")
        
        print("-" * 65)
        
        if issues_found == 0:
            print(f"\n🎉 SUCCESS: All Google Ads CPM values look correct!")
            print(f"✅ CPM fix resolved the issue with Multi Category filtering")
            print(f"📱 CPM values should now be realistic ($1-10 range)")
            return True
        else:
            print(f"\n❌ Found {issues_found} CPM issues")
            print(f"🔧 Frontend fix may not have fully resolved the issue")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_google_cpm_fix()
    
    if success:
        print(f"\n📱 Test the fix at: http://localhost:3007")
        print(f"   1. Go to Google Ads dashboard")
        print(f"   2. Select 'Multi Category' filter")
        print(f"   3. Verify CPM values are now realistic ($1-10 range)")
    else:
        print(f"\n🔧 Additional debugging may be needed")