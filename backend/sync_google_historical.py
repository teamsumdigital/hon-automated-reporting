#!/usr/bin/env python3
"""
Sync Google Ads historical data from January 2024 through August 11, 2025
"""

import os
import sys
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# Load environment variables
from dotenv import load_dotenv
load_dotenv("../.env")  # Load from parent directory

# Add the app directory to the path
sys.path.append('.')

try:
    from app.services.google_ads_service import GoogleAdsService
    from app.services.google_reporting import GoogleReportingService
    
    def sync_google_historical_data():
        """Sync Google Ads data month by month from Jan 2024 to Aug 11, 2025"""
        print("🔄 Starting Google Ads historical data sync...")
        print("📅 Date range: January 2024 → August 11, 2025")
        print("="*60)
        
        try:
            # Initialize services
            print("   🚀 Initializing Google Ads services...")
            google_service = GoogleAdsService()
            reporting_service = GoogleReportingService()
            
            # Test connection
            print("   🔗 Testing Google Ads API connection...")
            connection_success = google_service.test_connection()
            
            if not connection_success:
                print("   ❌ Google Ads API connection failed")
                return False
            
            # Define date range
            start_date = date(2024, 1, 1)  # January 1, 2024
            end_date = date(2025, 8, 11)   # August 11, 2025 (for testing)
            
            print(f"   📊 Syncing from {start_date} to {end_date}")
            
            # Track totals
            total_campaigns = 0
            months_processed = 0
            
            # Process month by month
            current_date = start_date
            
            while current_date <= end_date:
                # Calculate month end (or final end date)
                if current_date.year == 2025 and current_date.month == 8:
                    # August 2025 - limit to August 11
                    month_end = min(
                        date(2025, 8, 11),
                        current_date + relativedelta(months=1) - timedelta(days=1)
                    )
                else:
                    # Regular month end
                    month_end = current_date + relativedelta(months=1) - timedelta(days=1)
                
                # Ensure we don't go past our end date
                if month_end > end_date:
                    month_end = end_date
                
                month_name = current_date.strftime("%B %Y")
                print(f"\n   📅 Processing {month_name} ({current_date} to {month_end})")
                
                try:
                    # Get insights for this month
                    insights = google_service.get_campaign_insights(current_date, month_end)
                    print(f"      📊 Retrieved {len(insights)} campaign insights")
                    
                    if insights:
                        # Convert to campaign data
                        campaign_data_list = google_service.convert_to_campaign_data(insights)
                        print(f"      🔄 Converted {len(campaign_data_list)} campaigns")
                        
                        # Store in database
                        success = reporting_service.store_campaign_data(campaign_data_list)
                        
                        if success:
                            total_campaigns += len(campaign_data_list)
                            print(f"      ✅ Stored {len(campaign_data_list)} campaigns for {month_name}")
                        else:
                            print(f"      ❌ Failed to store campaigns for {month_name}")
                    else:
                        print(f"      ⚠️  No data found for {month_name}")
                        
                    months_processed += 1
                    
                except Exception as e:
                    print(f"      ❌ Error processing {month_name}: {e}")
                
                # Move to next month
                current_date = current_date + relativedelta(months=1)
                
                # Break if we've reached our end date
                if current_date > end_date:
                    break
            
            print(f"\n🎉 Google Ads historical sync completed!")
            print(f"   📊 Months processed: {months_processed}")
            print(f"   📈 Total campaigns synced: {total_campaigns}")
            print(f"   🎯 Data available in dashboard from Jan 2024 to Aug 11, 2025")
            
            return True
                
        except Exception as e:
            print(f"   ❌ Historical sync failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    if __name__ == "__main__":
        print("📦 Installing required packages...")
        os.system("pip3 install python-dateutil")
        print()
        
        success = sync_google_historical_data()
        
        if success:
            print("\n✅ Historical sync completed successfully!")
            print("   Visit http://localhost:3007/dashboard to see your Google Ads data")
        else:
            print("\n❌ Historical sync failed - check logs for details")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running from the backend directory")
    print("💡 Install dependencies: pip3 install google-ads python-dateutil")