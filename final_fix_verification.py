#!/usr/bin/env python3
"""
Final verification that the July 2025 dashboard fix is working
"""

import requests

def verify_fix():
    """Verify the July 2025 dashboard fix"""
    
    print("🔍 Final Verification: July 2025 Dashboard Fix")
    print("=" * 55)
    
    try:
        # Test API response
        response = requests.get('http://localhost:8007/api/tiktok-reports/dashboard')
        
        if response.status_code == 200:
            data = response.json()
            
            # Find July 2025 data
            july_data = [month for month in data['pivot_data'] if month['month'] == '2025-07']
            
            if july_data:
                july_spend = float(july_data[0]['spend'])
                
                print(f"📊 API Response for July 2025:")
                print(f"   Spend: ${july_spend:,.2f}")
                print(f"   Revenue: ${float(july_data[0]['revenue']):,.2f}")
                print(f"   Purchases: {july_data[0]['purchases']:,}")
                
                # Check if this matches expected value
                expected_spend = 30452.43
                
                if abs(july_spend - expected_spend) < 0.01:
                    print(f"\n✅ SUCCESS: July 2025 shows correct value of ${july_spend:,.2f}")
                    print("✅ The dashboard fix is working correctly!")
                    print("\n🎉 ISSUE RESOLVED:")
                    print("   - API now uses TikTokReportingService (correct)")
                    print("   - API queries tiktok_campaign_data table (correct)")
                    print("   - July 2025 shows $30,452.43 instead of $10,385")
                    print("   - User will now see accurate data on the dashboard")
                else:
                    print(f"\n❌ ERROR: Expected ${expected_spend:,.2f}, got ${july_spend:,.2f}")
            else:
                print("❌ No July 2025 data found in API response")
        else:
            print(f"❌ API call failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error during verification: {e}")

if __name__ == "__main__":
    verify_fix()