#!/usr/bin/env python3
"""
Check if August 2025 data exists in the database
"""

import os
import sys
sys.path.append('./backend')

from dotenv import load_dotenv
load_dotenv()

from backend.app.services.tiktok_reporting import TikTokReportingService

def check_august_2025():
    print("🔍 CHECKING AUGUST 2025 DATA")
    print("=" * 50)
    
    try:
        service = TikTokReportingService()
        
        # Get all monthly aggregates
        monthly_data = service.get_monthly_aggregates()
        print("📅 ALL MONTHS IN DATABASE:")
        
        sorted_months = sorted(monthly_data.keys())
        for month in sorted_months:
            data = monthly_data[month]
            print(f"  {month}: ${data['spend']:,.2f} spend, {data['ads_count']} ads")
        
        # Check specifically for August 2025
        if '2025-08' in monthly_data:
            aug_data = monthly_data['2025-08']
            print(f"\n✅ AUGUST 2025 FOUND:")
            print(f"  Spend: ${aug_data['spend']:,.2f}")
            print(f"  Revenue: ${aug_data['revenue']:,.2f}")
            print(f"  Ads: {aug_data['ads_count']}")
        else:
            print(f"\n❌ AUGUST 2025 NOT FOUND in monthly aggregates")
            
        # Check raw database for August 2025
        print(f"\n🔍 CHECKING RAW DATABASE FOR AUGUST 2025:")
        from supabase import create_client
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
        
        result = supabase.table("tiktok_ad_data").select("*").gte("reporting_starts", "2025-08-01").lte("reporting_starts", "2025-08-31").execute()
        
        print(f"  Raw ads in August 2025: {len(result.data)}")
        if result.data:
            print("  Sample ads:")
            for ad in result.data[:3]:
                print(f"    {ad['ad_name']}: ${ad['amount_spent_usd']} - {ad['reporting_starts']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_august_2025()