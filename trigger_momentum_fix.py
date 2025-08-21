#!/usr/bin/env python3
"""
Trigger a fresh 14-day sync to ensure we have 2 weekly periods for momentum indicators
"""

import requests
import sys
from datetime import datetime

def trigger_sync():
    """Trigger the 14-day sync API endpoint"""
    
    # Use localhost for development, or the production URL
    base_url = "http://localhost:8007"  # Change to production URL if needed
    endpoint = f"{base_url}/api/meta-ad-reports/sync-14-days"
    
    print(f"🔄 Triggering 14-day sync at {datetime.now()}")
    print(f"📡 Endpoint: {endpoint}")
    
    try:
        # Trigger the sync
        response = requests.post(endpoint, timeout=300)  # 5 minute timeout
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Sync completed successfully!")
            print(f"📊 Summary:")
            print(f"   - Total ads synced: {data.get('summary', {}).get('total_ads', 'N/A')}")
            print(f"   - Total spend: ${data.get('summary', {}).get('total_spend', 'N/A')}")
            print(f"   - Date range: {data.get('date_range', {}).get('start_date', 'N/A')} to {data.get('date_range', {}).get('end_date', 'N/A')}")
            
            # Show weekly breakdown if available
            weekly_breakdown = data.get('weekly_breakdown', {})
            if weekly_breakdown:
                print(f"🗓️ Weekly breakdown:")
                for week, stats in weekly_breakdown.items():
                    print(f"   - Week {week}: {stats['ads_count']} ads, ${stats['spend']:.2f} spend")
            
            print("\n🎯 Now the momentum indicators should work!")
            print("💻 Check the dashboard and browser console for the momentum changes.")
            
        else:
            print(f"❌ Sync failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the backend server is running")
        print("🚀 Start it with: cd backend && uvicorn main:app --reload --port 8007")
    except requests.exceptions.Timeout:
        print("⏰ Sync timed out - this is normal for large data sets")
        print("✅ The sync likely completed in the background")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    trigger_sync()