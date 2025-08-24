#!/usr/bin/env python3
"""
Verify TikTok data date coverage
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

# Load environment variables
load_dotenv()

# Database connection
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Get all unique date ranges
result = supabase.table("tiktok_ad_data")\
    .select("reporting_starts, reporting_ends")\
    .execute()

if result.data:
    # Get unique date ranges
    date_ranges = set()
    for record in result.data:
        date_ranges.add((record['reporting_starts'], record['reporting_ends']))
    
    # Sort by start date
    sorted_ranges = sorted(list(date_ranges))
    
    print(f"Total unique date ranges: {len(sorted_ranges)}")
    print("\nDate coverage:")
    
    # Group by month for easier viewing
    current_month = None
    for start, end in sorted_ranges:
        month = start[:7]  # YYYY-MM
        if month != current_month:
            print(f"\n{month}:")
            current_month = month
        print(f"  {start} to {end}")
    
    # Check for gaps
    print("\nChecking for gaps in coverage...")
    gaps = []
    for i in range(len(sorted_ranges) - 1):
        current_end = datetime.strptime(sorted_ranges[i][1], '%Y-%m-%d')
        next_start = datetime.strptime(sorted_ranges[i+1][0], '%Y-%m-%d')
        
        expected_next = current_end.replace(day=current_end.day + 1)
        if next_start != expected_next:
            gaps.append((sorted_ranges[i][1], sorted_ranges[i+1][0]))
    
    if gaps:
        print(f"Found {len(gaps)} gaps:")
        for end, start in gaps:
            print(f"  Gap between {end} and {start}")
    else:
        print("No gaps found - continuous coverage!")
    
    # Summary statistics
    print(f"\nCoverage summary:")
    print(f"Earliest date: {sorted_ranges[0][0]}")
    print(f"Latest date: {sorted_ranges[-1][1]}")
    
    # Count records per month
    print("\nRecords per month:")
    month_counts = {}
    for record in result.data:
        month = record['reporting_starts'][:7]
        month_counts[month] = month_counts.get(month, 0) + 1
    
    for month in sorted(month_counts.keys()):
        print(f"  {month}: {month_counts[month]:,} records")
    
    # Total spend by month
    spend_result = supabase.table("tiktok_ad_data")\
        .select("reporting_starts, amount_spent_usd")\
        .execute()
    
    if spend_result.data:
        month_spend = {}
        for record in spend_result.data:
            month = record['reporting_starts'][:7]
            month_spend[month] = month_spend.get(month, 0) + record['amount_spent_usd']
        
        print("\nTotal spend by month:")
        total_spend = 0
        for month in sorted(month_spend.keys()):
            spend = month_spend[month]
            total_spend += spend
            print(f"  {month}: ${spend:,.2f}")
        print(f"  TOTAL: ${total_spend:,.2f}")
else:
    print("No data found in tiktok_ad_data table")