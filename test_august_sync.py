#!/usr/bin/env python3

import os
import sys
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from datetime import date, timedelta
from dotenv import load_dotenv
from app.services.google_ads_service import GoogleAdsService
from supabase import create_client

load_dotenv()

def test_august_sync():
    print('🔄 Testing Google Ads sync for August 2025...')

    service = GoogleAdsService()

    # Test sync for August 1-11, 2025 (limited data)
    start_date = date(2025, 8, 1)
    end_date = date(2025, 8, 11)

    print(f'Syncing {start_date} to {end_date}...')
    insights = service.get_campaign_insights(start_date, end_date)
    print(f'Retrieved {len(insights)} daily insights')

    # Convert and store
    campaign_data = service.convert_to_campaign_data(insights)
    print(f'Converted to {len(campaign_data)} campaign data records')

    stored_count = service.store_campaign_data(campaign_data)
    print(f'Stored {stored_count} records in database')

    # Check totals for this period
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')
    supabase = create_client(url, key)

    result = supabase.table('google_campaign_data').select('*').gte('reporting_starts', '2025-08-01').lte('reporting_starts', '2025-08-11').execute()

    total_spend = sum(float(r['amount_spent_usd'] or 0) for r in result.data)
    total_purchases = sum(int(r['website_purchases'] or 0) for r in result.data)
    total_revenue = sum(float(r['purchases_conversion_value'] or 0) for r in result.data)

    print(f'\nAugust 1-11 totals:')
    print(f'  Spend: ${total_spend:.2f}')
    print(f'  Purchases: {total_purchases}')
    print(f'  Revenue: ${total_revenue:.2f}')
    print(f'  Records: {len(result.data)}')
    
    # Check if daily records exist
    dates = set(r['reporting_starts'] for r in result.data)
    print(f'  Unique dates: {len(dates)}')
    print(f'  Date range: {min(dates)} to {max(dates)}')

if __name__ == "__main__":
    test_august_sync()