#!/usr/bin/env python3
"""
Debug the TikTokReportingService to see why August 2025 is missing
"""

import os
import sys
sys.path.append('./backend')

from dotenv import load_dotenv
load_dotenv()

from backend.app.services.tiktok_reporting import TikTokReportingService

def debug_service_filters():
    print("🔍 DEBUGGING TIKTOK REPORTING SERVICE FILTERS")
    print("=" * 50)
    
    try:
        service = TikTokReportingService()
        
        print("📊 TESTING get_monthly_aggregates() WITH NO FILTERS:")
        monthly_data = service.get_monthly_aggregates(filters=None)
        
        print(f"  Total months: {len(monthly_data)}")
        print(f"  Months: {sorted(monthly_data.keys())}")
        
        if '2025-08' in monthly_data:
            aug_data = monthly_data['2025-08']
            print(f"  ✅ August 2025: ${aug_data['spend']:,.2f}, {aug_data['ads_count']} ads")
        else:
            print(f"  ❌ August 2025 NOT FOUND")
        
        print(f"\n🔍 RAW QUERY DEBUG:")
        # Let's manually check the query
        query = service.supabase.table("tiktok_ad_data").select("*")
        result = query.execute()
        
        print(f"  Total raw ads in database: {len(result.data)}")
        
        # Check for August 2025 manually
        august_ads = [ad for ad in result.data if ad['reporting_starts'].startswith('2025-08')]
        print(f"  August 2025 ads found: {len(august_ads)}")
        
        if august_ads:
            total_august_spend = sum(float(ad['amount_spent_usd']) for ad in august_ads)
            print(f"  August 2025 total spend: ${total_august_spend:,.2f}")
            print(f"  Sample August ad: {august_ads[0]['ad_name'][:50]}")
        
        # Now let's trace through the get_monthly_aggregates logic step by step
        print(f"\n🔍 TRACING MONTHLY AGGREGATES LOGIC:")
        monthly_totals = {}
        processed_ads = set()
        
        august_processed = 0
        for row in result.data:
            if row['reporting_starts'].startswith('2025-08'):
                # Check deduplication
                ad_period_key = f"{row['ad_id']}_{row['reporting_starts']}_{row['reporting_ends']}"
                if ad_period_key not in processed_ads:
                    processed_ads.add(ad_period_key)
                    august_processed += 1
        
        print(f"  August 2025 ads after deduplication: {august_processed}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_service_filters()