#!/usr/bin/env python3
"""
Sync Meta Ads data from both accounts directly
"""

import os
import sys
from datetime import date, timedelta

# Add the app directory to the path
sys.path.append('.')

try:
    from app.services.meta_api import MetaAdsService
    from app.services.reporting import ReportingService
    
    def sync_dual_accounts():
        """Sync data from both Meta Ads accounts"""
        print("🔄 Starting dual Meta Ads account sync...")
        
        try:
            # Initialize services
            print("   🚀 Initializing services...")
            meta_service = MetaAdsService()
            reporting_service = ReportingService()
            
            # Test connection to both accounts
            print("   🔗 Testing connections...")
            connection_success = meta_service.test_connection()
            
            if not connection_success:
                print("   ❌ Connection test failed")
                return False
            
            # Sync recent data (last 30 days)
            end_date = date.today() - timedelta(days=1)  # Yesterday
            start_date = end_date - timedelta(days=29)   # Last 30 days
            
            print(f"   📅 Syncing data from {start_date} to {end_date}")
            
            # Get insights from both accounts
            insights = meta_service.get_campaign_insights(start_date, end_date)
            print(f"   📊 Retrieved {len(insights)} total campaign insights")
            
            if not insights:
                print("   ⚠️  No data found for the specified date range")
                return True
            
            # Convert to campaign data
            campaign_data_list = meta_service.convert_to_campaign_data(insights)
            print(f"   🔄 Converted {len(campaign_data_list)} campaigns")
            
            # Store in database
            success = reporting_service.store_campaign_data(campaign_data_list)
            
            if success:
                print(f"   ✅ Successfully synced {len(campaign_data_list)} campaigns")
                print("   📊 Data from both accounts now available in dashboard")
                return True
            else:
                print("   ❌ Failed to store campaign data in database")
                return False
                
        except Exception as e:
            print(f"   ❌ Sync failed: {e}")
            return False
    
    if __name__ == "__main__":
        success = sync_dual_accounts()
        if success:
            print("\n🎉 Dual account sync completed successfully!")
        else:
            print("\n💥 Sync failed - check logs for details")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running from the backend directory")