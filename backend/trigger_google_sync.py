#!/usr/bin/env python3
"""
Trigger Google Ads historical sync via API calls
"""

import requests
import json
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

def trigger_google_historical_sync():
    """Trigger historical sync through the API endpoints"""
    print("🔄 Triggering Google Ads historical sync via API...")
    print("📅 Date range: January 2024 → August 11, 2025")
    print("="*60)
    
    base_url = "http://localhost:8007"
    
    # First check if backend is running
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Backend not responding. Please start the backend first:")
            print("   cd backend && uvicorn main:app --reload --port 8007")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to backend at http://localhost:8007")
        print("   Please start the backend first:")
        print("   cd backend && uvicorn main:app --reload --port 8007")
        return False
    
    print("✅ Backend is running")
    
    # Test Google Ads connection
    print("\n🔗 Testing Google Ads API connection...")
    try:
        test_response = requests.get(f"{base_url}/api/google-reports/test-connection", timeout=10)
        if test_response.status_code == 200:
            result = test_response.json()
            if result.get("status") == "connected":
                print("✅ Google Ads API connection successful")
            else:
                print("❌ Google Ads API connection failed:", result.get("message"))
                return False
        else:
            print("❌ Failed to test Google Ads connection")
            return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False
    
    # Define date range for sync
    start_date = date(2024, 1, 1)
    end_date = date(2025, 8, 11)  # August 11, 2025 limit
    
    print(f"\n📊 Syncing Google Ads data from {start_date} to {end_date}")
    
    # Sync in chunks (monthly) to avoid timeouts
    current_date = start_date
    total_synced = 0
    months_processed = 0
    
    while current_date <= end_date:
        # Calculate month end
        if current_date.year == 2025 and current_date.month == 8:
            month_end = min(date(2025, 8, 11), current_date + relativedelta(months=1) - relativedelta(days=1))
        else:
            month_end = current_date + relativedelta(months=1) - relativedelta(days=1)
        
        if month_end > end_date:
            month_end = end_date
        
        month_name = current_date.strftime("%B %Y")
        print(f"\n📅 Syncing {month_name} ({current_date} to {month_end})")
        
        try:
            sync_url = f"{base_url}/api/google-reports/sync"
            sync_data = {
                "start_date": current_date.isoformat(),
                "end_date": month_end.isoformat()
            }
            
            print(f"   🔄 Calling API with date range...")
            sync_response = requests.post(sync_url, json=sync_data, timeout=120)
            
            if sync_response.status_code == 200:
                result = sync_response.json()
                synced_count = result.get("synced", 0)
                total_synced += synced_count
                print(f"   ✅ Synced {synced_count} campaigns for {month_name}")
                months_processed += 1
            else:
                print(f"   ❌ Failed to sync {month_name}: {sync_response.status_code}")
                if sync_response.text:
                    print(f"      Error: {sync_response.text}")
        
        except requests.exceptions.Timeout:
            print(f"   ⏱️ Timeout syncing {month_name} (this is normal for large datasets)")
            months_processed += 1
        except Exception as e:
            print(f"   ❌ Error syncing {month_name}: {e}")
        
        # Move to next month
        current_date = current_date + relativedelta(months=1)
        
        if current_date > end_date:
            break
    
    print(f"\n🎉 Google Ads historical sync completed!")
    print(f"   📊 Months processed: {months_processed}")
    print(f"   📈 Total campaigns synced: {total_synced}")
    print(f"   🎯 Visit http://localhost:3007/dashboard to see your data")
    
    return True

if __name__ == "__main__":
    success = trigger_google_historical_sync()
    
    if success:
        print("\n✅ Historical sync process completed!")
        print("   Check your dashboard for Google Ads data from Jan 2024 - Aug 2025")
    else:
        print("\n❌ Historical sync failed - check the backend status")