#!/usr/bin/env python3

import os
import sys
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from datetime import date
from dotenv import load_dotenv
from app.services.google_ads_service import GoogleAdsService
from app.services.google_reporting import GoogleReportingService
from supabase import create_client

load_dotenv()

def sync_july_2025():
    print('🔄 Syncing Google Ads data for July 2025...')

    # Initialize services
    ads_service = GoogleAdsService()
    reporting_service = GoogleReportingService()
    
    # Sync July 2025 (complete month)
    start_date = date(2025, 7, 1)
    end_date = date(2025, 7, 31)

    print(f'Fetching data for {start_date} to {end_date}...')
    
    try:
        # Use the reporting service sync method
        result = reporting_service.sync_google_ads_data(start_date, end_date)
        print(f'✅ Sync completed: {result}')
        
        # Check what was stored
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY')
        supabase = create_client(url, key)

        result = supabase.table('google_campaign_data').select('*').gte('reporting_starts', '2025-07-01').lte('reporting_starts', '2025-07-31').execute()

        if result.data:
            total_spend = sum(float(r['amount_spent_usd'] or 0) for r in result.data)
            total_purchases = sum(int(r['website_purchases'] or 0) for r in result.data)
            total_revenue = sum(float(r['purchases_conversion_value'] or 0) for r in result.data)
            
            print(f'\n📊 July 2025 totals:')
            print(f'  Records: {len(result.data)}')
            print(f'  Spend: ${total_spend:.2f}')
            print(f'  Purchases: {total_purchases}')
            print(f'  Revenue: ${total_revenue:.2f}')
            
            # Verify we have daily data (should be ~31 days × campaigns)
            unique_dates = set(r['reporting_starts'] for r in result.data)
            print(f'  Unique dates: {len(unique_dates)}')
            print(f'  Avg records per date: {len(result.data) / len(unique_dates):.1f}')
            
            # Expected from Excel: July 2025 = $102,248 spend, 4,628 purchases, $1,435,304 revenue
            print(f'\n💡 Expected (from Excel): $102,248 spend, 4,628 purchases, $1,435,304 revenue')
            
        else:
            print('❌ No data was stored!')
            
    except Exception as e:
        print(f'❌ Sync failed: {e}')

if __name__ == "__main__":
    sync_july_2025()