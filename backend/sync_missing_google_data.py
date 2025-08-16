#!/usr/bin/env python3
"""
Sync missing Google Ads data - comprehensive backfill
Focus on missing months: Dec 2024, Jan-Jul 2025, and Aug 12-current
"""

import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables from parent directory
load_dotenv("../.env")

# Add the app directory to the path
sys.path.append('.')

print("🔄 Google Ads Missing Data Sync")
print("=" * 50)

try:
    from app.services.google_ads_service import GoogleAdsService
    
    # Initialize direct Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(url, key)
    
    # Initialize Google Ads service
    print("🚀 Initializing Google Ads service...")
    google_service = GoogleAdsService()
    
    # Test connection
    print("🔗 Testing Google Ads connection...")
    if not google_service.test_connection():
        print("❌ Connection failed")
        exit(1)
    print("✅ Connection successful")
    
    # Define missing periods to sync
    missing_periods = [
        # December 2024 (missing entirely)
        (date(2024, 12, 1), date(2024, 12, 31), "December 2024"),
        
        # All of 2025 except August 1-11
        (date(2025, 1, 1), date(2025, 1, 31), "January 2025"),
        (date(2025, 2, 1), date(2025, 2, 28), "February 2025"),
        (date(2025, 3, 1), date(2025, 3, 31), "March 2025"),
        (date(2025, 4, 1), date(2025, 4, 30), "April 2025"),
        (date(2025, 5, 1), date(2025, 5, 31), "May 2025"),
        (date(2025, 6, 1), date(2025, 6, 30), "June 2025"),
        (date(2025, 7, 1), date(2025, 7, 31), "July 2025"),
        
        # August 12 through current date
        (date(2025, 8, 12), date.today(), "August 2025 (continuation)"),
    ]
    
    total_stored = 0
    total_processed = 0
    
    for start_date, end_date, period_name in missing_periods:
        if start_date > date.today():
            continue
            
        # Adjust end_date if it's in the future
        end_date = min(end_date, date.today())
        
        print(f"\n📅 Syncing {period_name}: {start_date} to {end_date}")
        
        try:
            # Get insights for this period
            insights = google_service.get_campaign_insights(start_date, end_date)
            print(f"   📊 Retrieved {len(insights)} campaign insights")
            
            if insights:
                # Convert to campaign data
                campaign_data_list = google_service.convert_to_campaign_data(insights)
                print(f"   🔄 Converted {len(campaign_data_list)} campaigns")
                
                # Store directly in database with batch processing
                stored_count = 0
                duplicate_count = 0
                error_count = 0
                
                # Process in batches for better performance
                batch_size = 50
                for i in range(0, len(campaign_data_list), batch_size):
                    batch = campaign_data_list[i:i + batch_size]
                    
                    for campaign_data in batch:
                        try:
                            data = {
                                "campaign_id": campaign_data.campaign_id,
                                "campaign_name": campaign_data.campaign_name,
                                "category": campaign_data.category,
                                "reporting_starts": campaign_data.reporting_starts.isoformat(),
                                "reporting_ends": campaign_data.reporting_ends.isoformat(),
                                "amount_spent_usd": float(campaign_data.amount_spent_usd),
                                "website_purchases": campaign_data.website_purchases,
                                "purchases_conversion_value": float(campaign_data.purchases_conversion_value),
                                "impressions": campaign_data.impressions,
                                "link_clicks": campaign_data.link_clicks,
                                "cpa": float(campaign_data.cpa),
                                "roas": float(campaign_data.roas),
                                "cpc": float(campaign_data.cpc)
                            }
                            
                            # Try insert first
                            result = supabase.table("google_campaign_data").insert(data).execute()
                            stored_count += 1
                            
                        except Exception as e:
                            if "duplicate key value" in str(e):
                                duplicate_count += 1
                            else:
                                error_count += 1
                                if error_count <= 3:  # Show first 3 errors
                                    print(f"      ❌ Error: {str(e)[:100]}...")
                    
                    if (i + batch_size) % 100 == 0:
                        print(f"   📊 Processed {min(i + batch_size, len(campaign_data_list))}/{len(campaign_data_list)} campaigns...")
                
                print(f"   ✅ Stored: {stored_count}, Duplicates: {duplicate_count}, Errors: {error_count}")
                total_stored += stored_count
                total_processed += len(campaign_data_list)
                
            else:
                print("   ⚠️ No data found for this period")
                
        except Exception as period_error:
            print(f"   ❌ Period sync failed: {period_error}")
    
    print(f"\n" + "=" * 50)
    print(f"🏁 Missing data sync complete!")
    print(f"   📊 Total campaigns processed: {total_processed}")
    print(f"   💾 Total new records stored: {total_stored}")
    
    # Final comprehensive count
    final_result = supabase.table("google_campaign_data").select("*", count="exact").execute()
    print(f"   📈 Total Google Ads records: {final_result.count}")
    
    # Show updated date range and monthly distribution
    if final_result.data:
        dates_result = supabase.table("google_campaign_data").select("reporting_starts, reporting_ends").order("reporting_starts").execute()
        if dates_result.data:
            earliest = dates_result.data[0]["reporting_starts"]
            latest = dates_result.data[-1]["reporting_ends"]
            print(f"   📅 Complete data range: {earliest} to {latest}")
            
        # Show monthly breakdown
        from collections import Counter
        months = [record["reporting_starts"][:7] for record in dates_result.data]
        month_counts = Counter(months)
        
        print(f"\n📊 Monthly distribution:")
        for month in sorted(month_counts.keys()):
            print(f"   {month}: {month_counts[month]} records")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Visit http://localhost:3007/dashboard to see your complete Google Ads data!")