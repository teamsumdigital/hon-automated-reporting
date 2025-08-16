#!/usr/bin/env python3
"""Clear old TikTok data and resync with corrected service"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

# Add the backend path
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from app.services.tiktok_service import TikTokService

load_dotenv()

def clear_and_resync():
    """Clear old useless TikTok data and resync with corrected service"""
    
    print("🧹 Clearing old TikTok data and resyncing...")
    
    # Connect to database
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    # Check current data
    print("\n📊 Checking current TikTok data...")
    current_data = supabase.table("tiktok_campaign_data").select("*").execute()
    print(f"Found {len(current_data.data)} existing records")
    
    if current_data.data:
        # Show summary of current data
        total_spend = sum(c.get("amount_spent_usd", 0) for c in current_data.data)
        total_conversions = sum(c.get("website_purchases", 0) for c in current_data.data)
        print(f"Current total spend: ${total_spend}")
        print(f"Current total conversions: {total_conversions}")
        
        if total_spend == 0 and total_conversions == 0:
            print("⚠️ Confirmed: Current data is useless (all zeros)")
        
        # Clear the table
        print("\n🗑️ Clearing all existing TikTok data...")
        delete_result = supabase.table("tiktok_campaign_data").delete().neq("id", 0).execute()
        print(f"Deleted {len(delete_result.data)} records")
    
    # Initialize corrected service
    print("\n🔧 Initializing corrected TikTok service...")
    service = TikTokService()
    
    # Test connection
    connection_result = service.test_connection()
    if connection_result["status"] != "success":
        print(f"❌ Connection failed: {connection_result['message']}")
        return False
    
    print(f"✅ Connected: {connection_result['message']}")
    
    # Sync last 30 days of data
    print("\n📅 Syncing last 30 days of TikTok data...")
    end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"Date range: {start_date} to {end_date}")
    
    sync_count, sync_message = service.sync_campaign_data(start_date, end_date)
    print(f"Sync result: {sync_message}")
    
    if sync_count > 0:
        # Verify new data
        print("\n✅ Verifying new data...")
        new_data = supabase.table("tiktok_campaign_data").select("*").execute()
        print(f"New records: {len(new_data.data)}")
        
        # Show summary of new data
        total_spend = sum(c.get("amount_spent_usd", 0) for c in new_data.data)
        total_conversions = sum(c.get("website_purchases", 0) for c in new_data.data)
        total_revenue = sum(c.get("purchases_conversion_value", 0) for c in new_data.data)
        total_clicks = sum(c.get("link_clicks", 0) for c in new_data.data)
        
        print(f"\n📊 NEW DATA SUMMARY:")
        print(f"💰 Total spend: ${total_spend:,.2f}")
        print(f"🛒 Total conversions: {total_conversions}")
        print(f"💵 Total revenue: ${total_revenue:,.2f}")
        print(f"🖱️ Total clicks: {total_clicks:,}")
        
        # Show date range of new data
        dates = [c.get("reporting_starts") for c in new_data.data if c.get("reporting_starts")]
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            print(f"📅 Data covers: {min_date} to {max_date}")
        
        print("\n✅ SUCCESS! TikTok data has been cleared and resynced with real performance data")
        return True
    else:
        print("❌ Sync failed")
        return False

if __name__ == "__main__":
    print("🚀 TikTok Data Clear & Resync")
    print("=" * 50)
    
    success = clear_and_resync()
    
    if success:
        print("\n🎉 TikTok integration is now working with real data!")
        print("💡 You can now view accurate TikTok performance in the dashboard")
    else:
        print("\n❌ Something went wrong - check the error messages above")
    
    print("\n" + "=" * 50)