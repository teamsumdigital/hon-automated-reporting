#!/usr/bin/env python3

"""
Check sync status and trigger a fresh 14-day sync if needed
"""

import os
from datetime import datetime, timedelta, date
from supabase import create_client
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
    print("🔍 Checking sync status for Meta ad level data")
    print("=" * 60)
    
    # Calculate expected date ranges
    today = date.today()
    end_date = today - timedelta(days=1)  # Yesterday
    start_date = end_date - timedelta(days=13)  # 14 days total
    
    print(f"📅 Today: {today}")
    print(f"📅 Expected start date: {start_date}")
    print(f"📅 Expected end date: {end_date}")
    print(f"📅 Total expected days: {(end_date - start_date).days + 1}")
    
    # Check what data we have
    result = supabase.table('meta_ad_data').select('reporting_starts, reporting_ends').gte('reporting_starts', start_date.isoformat()).execute()
    
    if not result.data:
        print("\n❌ No ad data found in expected range!")
        print("🚀 RECOMMENDATION: Trigger a fresh 14-day sync")
        return
    
    # Analyze date coverage
    date_ranges = set()
    for record in result.data:
        date_ranges.add((record['reporting_starts'], record['reporting_ends']))
    
    print(f"\n📊 Found {len(result.data)} total records")
    print(f"📅 Unique date ranges: {len(date_ranges)}")
    
    for start, end in sorted(date_ranges):
        count = sum(1 for r in result.data if r['reporting_starts'] == start and r['reporting_ends'] == end)
        print(f"   {start} to {end}: {count} records")
    
    # Check if we have both expected weeks
    expected_ranges = []
    
    # Week 1: start_date to start_date + 6 days
    week1_start = start_date
    week1_end = start_date + timedelta(days=6)
    expected_ranges.append((week1_start.isoformat(), week1_end.isoformat()))
    
    # Week 2: week1_end + 1 to end_date
    week2_start = week1_end + timedelta(days=1)
    week2_end = end_date
    expected_ranges.append((week2_start.isoformat(), week2_end.isoformat()))
    
    print(f"\n🎯 Expected date ranges:")
    for i, (start, end) in enumerate(expected_ranges, 1):
        print(f"   Week {i}: {start} to {end}")
        if (start, end) in date_ranges:
            print(f"     ✅ Found in database")
        else:
            print(f"     ❌ Missing from database")
    
    missing_weeks = 0
    for start, end in expected_ranges:
        if (start, end) not in date_ranges:
            missing_weeks += 1
    
    print(f"\n📈 Summary:")
    print(f"   Expected weeks: 2")
    print(f"   Found weeks: {len(date_ranges)}")
    print(f"   Missing weeks: {missing_weeks}")
    
    if missing_weeks > 0:
        print(f"\n🚨 ISSUE IDENTIFIED:")
        print(f"   We're missing {missing_weeks} weeks of data!")
        print(f"   This explains why some ads show only 1 week instead of 2.")
        print(f"\n🚀 RECOMMENDATION:")
        print(f"   Trigger a fresh 14-day sync to get missing data.")
        print(f"   Run: curl -X POST http://localhost:8007/api/meta-ad-reports/sync-14-days")
    else:
        print(f"\n✅ All expected weeks are present!")
        print(f"   Issue may be in the API response logic or frontend display.")

if __name__ == "__main__":
    main()