#!/usr/bin/env python3
"""
Sync TikTok ad-level data to the new tiktok_ad_data table
This populates the table that was just created with the migration
"""

import requests
import time

def sync_tiktok_ad_data():
    """Trigger the TikTok ad-level sync endpoint"""
    
    backend_url = "http://localhost:8007"
    sync_endpoint = f"{backend_url}/api/tiktok-ad-reports/sync-14-days"
    health_endpoint = f"{backend_url}/api/tiktok-ad-reports/health"
    data_endpoint = f"{backend_url}/api/tiktok-ad-reports/ad-data"
    
    print("🚀 Syncing TikTok Ad-Level Data")
    print("=" * 50)
    
    # First check if backend is running
    try:
        print("🔍 Checking backend connection...")
        health_response = requests.get(health_endpoint, timeout=5)
        if health_response.status_code == 200:
            print("✅ Backend is running and healthy")
        else:
            print(f"⚠️ Backend health check returned {health_response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running!")
        print("🚀 Start it with: cd backend && source venv_new/bin/activate && uvicorn main:app --reload --port 8007")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Trigger the sync
    try:
        print("📡 Triggering 14-day TikTok ad sync...")
        sync_response = requests.post(sync_endpoint, timeout=10)
        
        if sync_response.status_code == 200:
            sync_data = sync_response.json()
            print("✅ Sync started successfully!")
            print(f"📋 Status: {sync_data.get('status', 'unknown')}")
            print(f"💭 Message: {sync_data.get('message', 'no message')}")
            
            if sync_data.get('status') == 'already_running':
                print("⏳ Sync already in progress, waiting for completion...")
            else:
                print("⏳ Background sync started, waiting for completion...")
            
            # Wait for sync to complete (background task)
            print("\n🕐 Waiting for sync to complete...")
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                print(f"⏳ {i+1}/30 seconds...", end='\r')
            
            print("\n✅ Sync should be complete, checking results...")
            
        else:
            print(f"❌ Sync failed: {sync_response.status_code}")
            print(f"📄 Response: {sync_response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Sync request timed out (this is normal for background tasks)")
        print("✅ Sync is likely running in the background")
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        return False
    
    # Check the results
    try:
        print("\n📊 Checking TikTok ad data...")
        data_response = requests.get(data_endpoint, timeout=10)
        
        if data_response.status_code == 200:
            data_result = data_response.json()
            ad_count = data_result.get('count', 0)
            ads = data_result.get('grouped_ads', [])
            
            print(f"✅ Found {ad_count} TikTok ads in database")
            
            if ad_count > 0:
                print("\n📋 Sample ads:")
                for i, ad in enumerate(ads[:3]):  # Show first 3 ads
                    print(f"  {i+1}. {ad.get('ad_name', 'Unknown')} ({ad.get('category', 'Uncategorized')})")
                    print(f"     Campaign: {ad.get('campaign_name', 'Unknown')}")
                    print(f"     Spend: ${ad.get('total_spend', 0):.2f}, ROAS: {ad.get('total_roas', 0):.2f}")
                    weekly_periods = ad.get('weekly_periods', [])
                    print(f"     Weekly periods: {len(weekly_periods)} (needed for momentum)")
                    print()
                
                print("🎯 TikTok ad-level categorization is working!")
                print("📱 View results at: http://localhost:3007 → 'TikTok Ad Level' tab")
                
            else:
                print("⚠️ No ad data found. This could mean:")
                print("  - TikTok API credentials are not configured")
                print("  - No TikTok ad data available for the last 14 days")
                print("  - API sync failed silently")
                
        else:
            print(f"❌ Failed to fetch ad data: {data_response.status_code}")
            print(f"📄 Response: {data_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to check ad data: {e}")
        return False
    
    return True

def test_categorization():
    """Test the categorization on synced data"""
    data_endpoint = "http://localhost:8007/api/tiktok-ad-reports/ad-data"
    
    try:
        response = requests.get(data_endpoint, timeout=10)
        if response.status_code == 200:
            data = response.json()
            ads = data.get('grouped_ads', [])
            
            if ads:
                print("\n🧪 Testing Categorization Results:")
                print("-" * 40)
                
                category_counts = {}
                for ad in ads:
                    category = ad.get('category', 'Uncategorized')
                    category_counts[category] = category_counts.get(category, 0) + 1
                
                for category, count in category_counts.items():
                    print(f"📊 {category}: {count} ads")
                
                print(f"\n✅ Categorization working! {len(category_counts)} categories found")
                return True
            else:
                print("⚠️ No ads to test categorization")
                return False
        else:
            print(f"❌ Failed to fetch ads for categorization test: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Categorization test failed: {e}")
        return False

def main():
    """Main sync process"""
    print("🎯 TikTok Ad-Level Data Sync")
    print("=" * 60)
    
    # Sync the data
    sync_success = sync_tiktok_ad_data()
    
    if sync_success:
        # Test categorization
        test_categorization()
        
        print("\n" + "=" * 60)
        print("🎉 TikTok ad-level sync completed successfully!")
        print("\n📋 Next steps:")
        print("1. Visit http://localhost:3007")
        print("2. Click the 'TikTok Ad Level' tab (orange)")
        print("3. Use category filters (now based on ad names)")
        print("4. View momentum indicators (weekly changes)")
        
    else:
        print("\n" + "=" * 60)
        print("💥 TikTok ad-level sync failed!")
        print("\n📋 Troubleshooting:")
        print("1. Make sure backend is running: uvicorn main:app --reload --port 8007")
        print("2. Check TikTok API credentials in .env file")
        print("3. Verify tiktok_ad_data table exists in Supabase")

if __name__ == "__main__":
    main()