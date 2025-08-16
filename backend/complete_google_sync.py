#!/usr/bin/env python3
"""
Complete the Google Ads sync - final 2 missing months
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

print("🏁 Complete Google Ads Sync - Final 2 Months")
print("=" * 50)

try:
    from app.services.google_ads_service import GoogleAdsService
    
    # Initialize services
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(url, key)
    google_service = GoogleAdsService()
    
    # Final 2 missing periods
    final_periods = [
        (date(2025, 6, 1), date(2025, 6, 30), "June 2025"),
        (date(2025, 7, 1), date(2025, 7, 31), "July 2025"),
    ]
    
    total_added = 0
    
    for start_date, end_date, period_name in final_periods:
        print(f"\n📅 Syncing {period_name}: {start_date} to {end_date}")
        
        try:
            # Get insights
            insights = google_service.get_campaign_insights(start_date, end_date)
            print(f"   📊 Retrieved {len(insights)} insights")
            
            if insights:
                # Convert to campaign data
                campaign_data_list = google_service.convert_to_campaign_data(insights)
                print(f"   🔄 Converted {len(campaign_data_list)} campaigns")
                
                # Store in database
                stored_count = 0
                for campaign_data in campaign_data_list:
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
                        
                        result = supabase.table("google_campaign_data").insert(data).execute()
                        stored_count += 1
                        
                    except Exception as e:
                        if "duplicate key value" not in str(e):
                            print(f"      ❌ Error storing campaign: {e}")
                
                print(f"   ✅ Successfully stored {stored_count} campaigns")
                total_added += stored_count
                
            else:
                print("   ⚠️ No data found for this period")
                
        except Exception as e:
            print(f"   ❌ Failed to sync {period_name}: {e}")
    
    # Final verification
    print(f"\n" + "=" * 50)
    print(f"🎯 Final Google Ads Sync Results:")
    print(f"   📊 Added in this run: {total_added} campaigns")
    
    # Check final status
    final_result = supabase.table("google_campaign_data").select("reporting_starts", count="exact").execute()
    from collections import Counter
    months = [record["reporting_starts"][:7] for record in final_result.data]
    month_counts = Counter(months)
    
    print(f"   📈 Total campaigns: {final_result.count}")
    print(f"\n📅 Final monthly distribution:")
    for month in sorted(month_counts.keys()):
        print(f"   {month}: {month_counts[month]} campaigns")
    
    # Check if complete
    expected_months = []
    for year in [2024, 2025]:
        for month_num in range(1, 13 if year == 2024 else 9):
            expected_months.append(f"{year}-{month_num:02d}")
    
    existing_months = set(month_counts.keys())
    missing_months = [m for m in expected_months if m not in existing_months]
    
    if missing_months:
        print(f"\n⚠️ Still missing: {missing_months}")
        print("❌ SYNC INCOMPLETE")
    else:
        print(f"\n✅ ALL MONTHS PRESENT!")
        print("🎉 GOOGLE ADS SYNC COMPLETE!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Google Ads integration ready for dashboard!")