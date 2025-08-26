#!/usr/bin/env python3
"""
Debug why August 2025 data isn't showing up in monthly aggregates
"""

import os
import sys
sys.path.append('./backend')

from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
from supabase import create_client

def debug_august_aggregation():
    print("🔍 DEBUGGING AUGUST 2025 AGGREGATION")
    print("=" * 50)
    
    try:
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
        
        # Get August 2025 raw data
        result = supabase.table("tiktok_ad_data").select("*").gte("reporting_starts", "2025-08-01").lte("reporting_starts", "2025-08-31").execute()
        
        print(f"📊 RAW AUGUST 2025 DATA: {len(result.data)} ads")
        
        # Simulate the monthly aggregation logic
        monthly_totals = {}
        processed_ads = set()
        
        total_spend = 0
        for row in result.data[:5]:  # Check first 5 ads
            print(f"\n🔍 Processing ad: {row['ad_name'][:50]}...")
            print(f"  reporting_starts: {row['reporting_starts']} (type: {type(row['reporting_starts'])})")
            print(f"  reporting_ends: {row['reporting_ends']}")
            print(f"  amount_spent_usd: ${row['amount_spent_usd']}")
            
            # Extract month key (same logic as TikTokReportingService)
            ad_period_key = f"{row['ad_id']}_{row['reporting_starts']}_{row['reporting_ends']}"
            
            if ad_period_key in processed_ads:
                print(f"  ⚠️  DUPLICATE - skipping")
                continue
            processed_ads.add(ad_period_key)
            
            # Get month key
            try:
                month_key = datetime.fromisoformat(row["reporting_starts"]).strftime("%Y-%m")
                print(f"  ✅ Month key: {month_key}")
                
                # Initialize month if needed
                if month_key not in monthly_totals:
                    monthly_totals[month_key] = {
                        'spend': 0.0,
                        'revenue': 0.0,
                        'purchases': 0,
                        'clicks': 0,
                        'impressions': 0,
                        'ads_count': 0
                    }
                
                # Add to monthly totals
                monthly_totals[month_key]['spend'] += float(row["amount_spent_usd"])
                monthly_totals[month_key]['revenue'] += float(row["purchases_conversion_value"])
                monthly_totals[month_key]['purchases'] += row["website_purchases"]
                monthly_totals[month_key]['clicks'] += row["link_clicks"]
                monthly_totals[month_key]['impressions'] += row["impressions"]
                monthly_totals[month_key]['ads_count'] += 1
                
                total_spend += float(row["amount_spent_usd"])
                print(f"  ✅ Added to {month_key}: ${row['amount_spent_usd']}")
                
            except Exception as e:
                print(f"  ❌ Error processing date: {e}")
        
        print(f"\n📊 AGGREGATION RESULTS:")
        for month_key, totals in monthly_totals.items():
            print(f"  {month_key}: ${totals['spend']:,.2f} spend, {totals['ads_count']} ads")
        
        print(f"\n💰 TOTAL SPEND FROM SAMPLE: ${total_spend:,.2f}")
        
        # Check if there are date format issues
        print(f"\n🔍 CHECKING ALL AUGUST 2025 DATES:")
        unique_dates = set()
        for row in result.data:
            unique_dates.add(row['reporting_starts'])
        
        print(f"  Unique reporting_starts dates: {sorted(unique_dates)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_august_aggregation()