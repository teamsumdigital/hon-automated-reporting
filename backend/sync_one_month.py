#!/usr/bin/env python3
"""
Sync Google Ads data for one month (August 2025) to verify system
"""

import os
import sys
from datetime import date
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv("../.env")

# Add the app directory to the path
sys.path.append('.')

print("🔄 Syncing Google Ads Data for August 2025 (1-11)")
print("=" * 50)

try:
    from app.services.google_ads_service import GoogleAdsService
    from app.services.google_reporting import GoogleReportingService
    
    # Date range: August 1-11, 2025
    start_date = date(2025, 8, 1)
    end_date = date(2025, 8, 11)
    
    print(f"📅 Date range: {start_date} to {end_date}")
    
    # Initialize services
    print("🚀 Initializing services...")
    google_service = GoogleAdsService()
    reporting_service = GoogleReportingService()
    
    # Test connection
    print("🔗 Testing Google Ads connection...")
    if not google_service.test_connection():
        print("❌ Connection failed")
        exit(1)
    
    print("✅ Connection successful")
    
    # Get insights
    print(f"📊 Fetching campaign insights...")
    insights = google_service.get_campaign_insights(start_date, end_date)
    print(f"✅ Retrieved {len(insights)} campaign insights")
    
    if insights:
        # Convert to campaign data
        print(f"🔄 Converting to campaign data...")
        campaign_data_list = google_service.convert_to_campaign_data(insights)
        print(f"✅ Converted {len(campaign_data_list)} campaigns")
        
        # Store in database
        print(f"💾 Storing in database...")
        try:
            success = reporting_service.store_campaign_data(campaign_data_list)
            
            if success:
                print(f"✅ Successfully stored {len(campaign_data_list)} campaigns!")
                
                # Show sample data
                if campaign_data_list:
                    sample = campaign_data_list[0]
                    print(f"\n📊 Sample stored campaign:")
                    print(f"   Name: {sample.campaign_name}")
                    print(f"   Category: {sample.category}")
                    print(f"   Spend: ${sample.amount_spent_usd}")
                    print(f"   ROAS: {sample.roas}")
                    print(f"   Purchases: {sample.website_purchases}")
                    
            else:
                print("❌ Failed to store data in database")
        except Exception as db_error:
            print(f"❌ Database error: {db_error}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️ No campaign data found for this period")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🏁 One month sync complete!")
print("🎯 Visit http://localhost:3007/dashboard to see your data")