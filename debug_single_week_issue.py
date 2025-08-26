#!/usr/bin/env python3

"""
Debug script to investigate single week issue in Meta ad level dashboard
"""

import os
from datetime import datetime, timedelta, date
from supabase import create_client
from collections import defaultdict
import sys

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Initialize Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

if not supabase_url or not supabase_key:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    sys.exit(1)

supabase = create_client(supabase_url, supabase_key)

def main():
    print("🔍 Investigating single week issue in Meta ad level dashboard")
    print("=" * 80)
    
    # Get data from the last 14 days
    cutoff_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    print(f"📅 Cutoff date (14 days ago): {cutoff_date}")
    
    # Fetch all ad data
    print("\n📊 Fetching ad data from database...")
    result = supabase.table('meta_ad_data').select('*').gte('reporting_starts', cutoff_date).order('ad_name').order('reporting_starts').execute()
    
    if not result.data:
        print("❌ No data found!")
        return
    
    print(f"✅ Found {len(result.data)} total records")
    
    # Group by ad name
    grouped_ads = defaultdict(list)
    for record in result.data:
        grouped_ads[record['ad_name']].append(record)
    
    print(f"📈 Unique ads: {len(grouped_ads)}")
    
    # Focus on the specific ads from the screenshot
    problem_ads = [
        "New Ula Back in Stock",
        "New Bath Mats Collection V3", 
        "Standing Mats Video Ad Don't Buy Iteration",
        "Sale Ad Refresh Static Bath Mats"
    ]
    
    print("\n🎯 Analyzing problem ads from screenshot:")
    print("-" * 50)
    
    for ad_name in problem_ads:
        if ad_name in grouped_ads:
            records = grouped_ads[ad_name]
            print(f"\n🔸 {ad_name}")
            print(f"   Total records: {len(records)}")
            
            # Group by date range 
            date_ranges = defaultdict(list)
            for record in records:
                date_key = f"{record['reporting_starts']} to {record['reporting_ends']}"
                date_ranges[date_key].append(record)
            
            print(f"   Unique date ranges: {len(date_ranges)}")
            
            for date_range, date_records in date_ranges.items():
                total_spend = sum(r['amount_spent_usd'] for r in date_records)
                print(f"     📅 {date_range}: {len(date_records)} records, ${total_spend:.2f} total spend")
                
                # Show individual records for debugging
                for i, record in enumerate(date_records):
                    print(f"        Record {i+1}: Campaign: {record['campaign_name']}, Spend: ${record['amount_spent_usd']:.2f}")
        else:
            print(f"\n❌ {ad_name} - NOT FOUND in database!")
    
    # Check if we're missing a week
    print("\n📊 Analyzing date range coverage:")
    print("-" * 50)
    
    # Expected date ranges for last 14 days
    today = date.today()
    end_date = today - timedelta(days=1)  # Yesterday
    start_date = end_date - timedelta(days=13)  # 14 days total
    
    # Calculate expected weekly periods
    week1_start = start_date
    week1_end = start_date + timedelta(days=6)
    week2_start = week1_end + timedelta(days=1)
    week2_end = end_date
    
    expected_week1 = f"{week1_start} to {week1_end}"
    expected_week2 = f"{week2_start} to {week2_end}"
    
    print(f"📅 Expected week 1: {expected_week1}")
    print(f"📅 Expected week 2: {expected_week2}")
    
    # Check actual date ranges in data
    actual_date_ranges = set()
    for record in result.data:
        date_range = f"{record['reporting_starts']} to {record['reporting_ends']}"
        actual_date_ranges.add(date_range)
    
    print(f"\n🎯 Actual date ranges in database:")
    for date_range in sorted(actual_date_ranges):
        count = sum(1 for r in result.data if f"{r['reporting_starts']} to {r['reporting_ends']}" == date_range)
        print(f"   📅 {date_range}: {count} records")
    
    # Check for missing periods
    print(f"\n❓ Missing periods analysis:")
    if expected_week1 not in actual_date_ranges:
        print(f"   ❌ Missing expected week 1: {expected_week1}")
    else:
        print(f"   ✅ Found expected week 1: {expected_week1}")
        
    if expected_week2 not in actual_date_ranges:
        print(f"   ❌ Missing expected week 2: {expected_week2}")
    else:
        print(f"   ✅ Found expected week 2: {expected_week2}")
    
    # Check API response logic
    print(f"\n🔧 Checking API endpoint logic:")
    print("-" * 50)
    
    # Simulate the API logic on our problem ad
    if "New Ula Back in Stock" in grouped_ads:
        print("🎯 Analyzing 'New Ula Back in Stock' using API logic:")
        
        records = grouped_ads["New Ula Back in Stock"]
        
        # Simulate the deduplication logic from the API
        weekly_periods = {}
        for record in records:
            date_key = f"{record['reporting_starts']}_{record['reporting_ends']}"
            
            if date_key not in weekly_periods:
                weekly_periods[date_key] = {
                    'reporting_starts': record['reporting_starts'],
                    'reporting_ends': record['reporting_ends'],
                    'spend': record['amount_spent_usd'],
                    'revenue': record['purchases_conversion_value'],
                    'purchases': record['purchases'],
                    'clicks': record['link_clicks'],
                    'impressions': record['impressions']
                }
                print(f"   ✅ Added period: {record['reporting_starts']} to {record['reporting_ends']} (${record['amount_spent_usd']:.2f})")
            else:
                print(f"   🔄 Aggregating duplicate period: {record['reporting_starts']} to {record['reporting_ends']} (${record['amount_spent_usd']:.2f})")
                existing = weekly_periods[date_key]
                existing['spend'] += record['amount_spent_usd']
                existing['revenue'] += record['purchases_conversion_value']
                existing['purchases'] += record['purchases']
                existing['clicks'] += record['link_clicks']
                existing['impressions'] += record['impressions']
        
        # Convert to list and sort (API logic)
        periods_list = list(weekly_periods.values())
        periods_list.sort(key=lambda x: x['reporting_starts'])
        final_periods = periods_list[-2:]  # Keep only last 2 periods
        
        print(f"   📊 Final periods after API processing: {len(final_periods)}")
        for i, period in enumerate(final_periods):
            print(f"      Period {i+1}: {period['reporting_starts']} to {period['reporting_ends']} (${period['spend']:.2f})")

if __name__ == "__main__":
    main()