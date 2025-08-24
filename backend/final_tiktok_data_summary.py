#!/usr/bin/env python3
"""
Final TikTok data summary
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from collections import defaultdict

# Load environment variables
load_dotenv()

# Database connection
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Get all data with pagination
all_data = []
limit = 1000
offset = 0

while True:
    result = supabase.table("tiktok_ad_data")\
        .select("*")\
        .range(offset, offset + limit - 1)\
        .execute()
    
    if not result.data:
        break
        
    all_data.extend(result.data)
    offset += limit
    
    if len(result.data) < limit:
        break

result.data = all_data

if result.data:
    print("TIKTOK AD DATA FINAL SUMMARY")
    print("="*60)
    
    # Total records
    print(f"Total ad records: {len(result.data):,}")
    
    # Date range
    dates = [(r['reporting_starts'], r['reporting_ends']) for r in result.data]
    unique_dates = sorted(list(set(dates)))
    print(f"Date coverage: {unique_dates[0][0]} to {unique_dates[-1][1]}")
    print(f"Total unique date periods: {len(unique_dates)}")
    
    # Category breakdown
    categories = defaultdict(int)
    for r in result.data:
        categories[r['category']] += 1
    
    print("\nCategory breakdown:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count:,} ads")
    
    # Monthly summary
    monthly_data = defaultdict(lambda: {'count': 0, 'spend': 0, 'revenue': 0, 'purchases': 0})
    
    for r in result.data:
        month = r['reporting_starts'][:7]
        monthly_data[month]['count'] += 1
        monthly_data[month]['spend'] += r['amount_spent_usd']
        monthly_data[month]['revenue'] += r['purchases_conversion_value']
        monthly_data[month]['purchases'] += r['website_purchases']
    
    print("\nMonthly performance summary:")
    print(f"{'Month':<10} {'Records':<10} {'Spend':<15} {'Revenue':<15} {'ROAS':<8} {'Purchases':<10}")
    print("-"*75)
    
    total_spend = 0
    total_revenue = 0
    total_purchases = 0
    
    for month in sorted(monthly_data.keys()):
        data = monthly_data[month]
        roas = data['revenue'] / data['spend'] if data['spend'] > 0 else 0
        total_spend += data['spend']
        total_revenue += data['revenue']
        total_purchases += data['purchases']
        
        print(f"{month:<10} {data['count']:<10,} ${data['spend']:<14,.2f} ${data['revenue']:<14,.2f} {roas:<8.2f} {data['purchases']:<10,}")
    
    print("-"*75)
    overall_roas = total_revenue / total_spend if total_spend > 0 else 0
    print(f"{'TOTAL':<10} {len(result.data):<10,} ${total_spend:<14,.2f} ${total_revenue:<14,.2f} {overall_roas:<8.2f} {total_purchases:<10,}")
    
    # Top spending ads with names
    print("\nTop 10 spending ads:")
    top_ads = sorted(result.data, key=lambda x: x['amount_spent_usd'], reverse=True)[:10]
    
    for i, ad in enumerate(top_ads, 1):
        print(f"\n{i}. Ad ID: {ad['ad_id']}")
        print(f"   Name: {ad['ad_name'][:80]}...")
        print(f"   Campaign: {ad['campaign_name']}")
        print(f"   Category: {ad['category']}")
        print(f"   Period: {ad['reporting_starts']} to {ad['reporting_ends']}")
        print(f"   Spend: ${ad['amount_spent_usd']:,.2f} | Revenue: ${ad['purchases_conversion_value']:,.2f} | ROAS: {ad['roas']:.2f}")
    
    # Check for any remaining "Ad %" names
    unnamed_count = sum(1 for r in result.data if r['ad_name'].startswith('Ad '))
    if unnamed_count > 0:
        print(f"\nNote: {unnamed_count} ads still have generic names (starting with 'Ad ')")
    else:
        print("\n✅ All ads have proper names!")
    
    print("\n" + "="*60)
    print("DATA QUALITY CHECK COMPLETE")
    print("="*60)
else:
    print("No data found in tiktok_ad_data table")