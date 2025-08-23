#!/usr/bin/env python3
"""
Clean up old category names using the backend API
"""

import requests
import json

def cleanup_via_api():
    """Use the backend API to clean up old categories"""
    
    backend_url = "http://localhost:8007"
    
    print("🧹 Cleaning up old category names via API")
    print("=" * 50)
    
    # Category mapping from old -> new
    category_mapping = {
        'Bath': 'Bath Mats',
        'Multi': 'Multi Category', 
        'Playmat': 'Play Mats',
        'Standing Mat': 'Standing Mats',
        'Tumbling Mat': 'Tumbling Mats'
    }
    
    try:
        # Get current filter options to see all categories
        filters_response = requests.get(f"{backend_url}/api/meta-ad-reports/filters", timeout=10)
        
        if filters_response.status_code != 200:
            print(f"❌ Failed to get filter options: {filters_response.status_code}")
            return False
        
        filters_data = filters_response.json()
        current_categories = filters_data.get('categories', [])
        
        print("📊 Current categories in database:")
        for cat in sorted(current_categories):
            marker = "🔄" if cat in category_mapping else "✅" if cat in category_mapping.values() else "➡️"
            print(f"  {marker} {cat}")
        
        # Check which old categories exist
        old_categories_present = [cat for cat in current_categories if cat in category_mapping]
        
        if not old_categories_present:
            print(f"\n✅ No old categories found - cleanup not needed!")
            return True
        
        print(f"\n🔄 Need to clean up: {old_categories_present}")
        
        # Unfortunately, we need direct database access to update categories
        # The API doesn't have an endpoint for batch category updates
        print(f"\n⚠️ Direct database update required for category cleanup")
        print(f"📝 SQL commands needed:")
        
        for old_cat in old_categories_present:
            new_cat = category_mapping[old_cat]
            print(f"   UPDATE meta_ad_data SET category = '{new_cat}' WHERE category = '{old_cat}';")
        
        return False
        
    except Exception as e:
        print(f"❌ Error during API cleanup: {e}")
        return False

def trigger_fresh_sync():
    """Trigger a fresh sync to recategorize all data"""
    
    backend_url = "http://localhost:8007"
    
    print(f"\n🔄 Triggering fresh sync to recategorize data...")
    
    try:
        sync_response = requests.post(f"{backend_url}/api/meta-ad-reports/sync-14-days", timeout=10)
        
        if sync_response.status_code == 200:
            result = sync_response.json()
            print(f"✅ Sync triggered: {result.get('message', 'Success')}")
            print(f"⏱️ This will take 5-10 minutes to complete")
            print(f"📊 All ads will be recategorized with standardized names")
            return True
        else:
            print(f"❌ Failed to trigger sync: {sync_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error triggering sync: {e}")
        return False

if __name__ == "__main__":
    print("Category Cleanup via Backend API")
    print("This will attempt to clean up duplicate categories\n")
    
    # Try API cleanup first
    api_success = cleanup_via_api()
    
    if not api_success:
        # If API cleanup can't do it, trigger a fresh sync
        # The sync will use the new categorization logic
        sync_success = trigger_fresh_sync()
        
        if sync_success:
            print(f"\n" + "=" * 50)
            print("🔄 FRESH SYNC STARTED!")
            print("⏱️ Wait 5-10 minutes for sync to complete")
            print("🧹 All data will be recategorized with new standardized names")
            print("📱 After sync: Visit http://localhost:3007 → Meta Ad Level dashboard")
            print("✅ Filter dropdown should show only standardized categories")
        else:
            print(f"\n" + "=" * 50)
            print("❌ Could not trigger automatic cleanup")
            print("🔧 Manual database intervention required")
    else:
        print(f"\n" + "=" * 50)
        print("🎉 Categories are already clean!")