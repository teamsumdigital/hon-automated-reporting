#!/usr/bin/env python3

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(url, key)

print('📊 Checking current Google Ads data...')

# Check total records
result = supabase.table('google_campaign_data').select('*', count='exact').execute()
print('Total records:', result.count)

# Check aggregated totals
result = supabase.table('google_campaign_data').select('amount_spent_usd,website_purchases,purchases_conversion_value').execute()

total_spend = sum(float(r['amount_spent_usd'] or 0) for r in result.data)
total_purchases = sum(int(r['website_purchases'] or 0) for r in result.data)
total_revenue = sum(float(r['purchases_conversion_value'] or 0) for r in result.data)

print('\nCurrent totals:')
print(f'  Spend: ${total_spend:.2f}')
print(f'  Purchases: {total_purchases:,}')
print(f'  Revenue: ${total_revenue:.2f}')

print('\nExpected totals from Excel:')
print('  Spend: $1,248,778.00')
print('  Purchases: 44,575')
print('  Revenue: $12,509,783.00')

print('\nData completeness:')
print(f'  Spend: {total_spend / 1248778 * 100 if total_spend > 0 else 0:.1f}%')
print(f'  Purchases: {total_purchases / 44575 * 100 if total_purchases > 0 else 0:.1f}%')
print(f'  Revenue: {total_revenue / 12509783 * 100 if total_revenue > 0 else 0:.1f}%')

print('\n📅 Checking date range coverage...')
result = supabase.table('google_campaign_data').select('reporting_starts').execute()

if result.data:
    dates = [r['reporting_starts'] for r in result.data]
    unique_dates = set(dates)
    print(f'  Unique dates: {len(unique_dates)}')
    print(f'  Date range: {min(unique_dates)} to {max(unique_dates)}')
    print(f'  Records per date: {len(dates) / len(unique_dates):.1f} avg')
else:
    print('  No data found')