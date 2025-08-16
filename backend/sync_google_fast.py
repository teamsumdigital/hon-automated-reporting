#!/usr/bin/env python3
"""
Fast Google Ads sync - remaining missing periods without categorization delay
"""

import os
import sys
from datetime import date
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables from parent directory
load_dotenv("../.env")

# Add the app directory to the path
sys.path.append('.')

print("⚡ Fast Google Ads Sync - Remaining Data")
print("=" * 50)

try:
    from app.services.google_ads_service import GoogleAdsService
    
    # Initialize direct Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(url, key)
    
    # Initialize Google Ads service
    google_service = GoogleAdsService()
    
    # Check what we have currently
    current_result = supabase.table("google_campaign_data").select("reporting_starts").execute()
    existing_months = set([record["reporting_starts"][:7] for record in current_result.data])
    print(f"Current months in database: {sorted(existing_months)}")
    
    # Define remaining periods to sync (skip what we already have)
    remaining_periods = []
    
    # Missing 2025 months
    for month in [5, 6, 7]:
        month_key = f"2025-{month:02d}"
        if month_key not in existing_months:
            if month == 2:
                end_day = 28
            elif month in [4, 6, 9, 11]:
                end_day = 30
            else:
                end_day = 31
            remaining_periods.append((
                date(2025, month, 1), 
                date(2025, month, end_day), 
                f"{month_key}"
            ))
    
    # August 12-current
    aug_current = f"2025-08"
    if aug_current in existing_months:
        remaining_periods.append((
            date(2025, 8, 12), 
            date.today(), 
            "August 2025 continuation"
        ))
    
    print(f"Periods to sync: {len(remaining_periods)}")
    
    total_stored = 0
    
    for start_date, end_date, period_name in remaining_periods:
        if start_date > date.today():
            continue
            
        end_date = min(end_date, date.today())
        print(f"\n📅 {period_name}: {start_date} to {end_date}")
        
        try:
            # Get insights
            insights = google_service.get_campaign_insights(start_date, end_date)
            print(f"   📊 {len(insights)} insights")
            
            if insights:
                # Convert (this is the slow part, but necessary)
                campaign_data_list = google_service.convert_to_campaign_data(insights)
                print(f"   🔄 {len(campaign_data_list)} campaigns converted")
                
                # Bulk store with minimal error handling for speed
                batch_data = []
                for campaign_data in campaign_data_list:
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
                    batch_data.append(data)
                
                # Bulk insert
                try:
                    result = supabase.table("google_campaign_data").insert(batch_data).execute()
                    stored_count = len(result.data) if result.data else 0
                    print(f"   ✅ Stored {stored_count} campaigns")
                    total_stored += stored_count
                except Exception as bulk_error:
                    # Fallback to individual inserts if bulk fails
                    stored_count = 0
                    for data in batch_data:
                        try:
                            supabase.table("google_campaign_data").insert(data).execute()
                            stored_count += 1
                        except:
                            pass  # Skip duplicates/errors for speed
                    print(f"   ✅ Stored {stored_count} campaigns (individual)")
                    total_stored += stored_count
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    # Final summary
    final_result = supabase.table("google_campaign_data").select("*", count="exact").execute()
    print(f"\n🏁 Fast sync complete!")
    print(f"   📊 Added: {total_stored} campaigns")
    print(f"   📈 Total: {final_result.count} campaigns")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🎯 Google Ads data sync continuing in background...")