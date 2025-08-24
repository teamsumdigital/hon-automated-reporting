#!/usr/bin/env python3
"""
Check TikTok ad data in the database
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

def check_tiktok_data():
    # Get total count
    count_result = supabase.table("tiktok_ad_data").select("*", count="exact").execute()
    total_count = count_result.count
    print(f"Total TikTok ad records: {total_count}")
    
    # Get date range
    date_result = supabase.table("tiktok_ad_data").select("reporting_starts, reporting_ends").execute()
    if date_result.data:
        dates = [(d['reporting_starts'], d['reporting_ends']) for d in date_result.data]
        unique_dates = list(set(dates))
        unique_dates.sort()
        
        print(f"\nDate ranges in database:")
        print(f"Earliest: {unique_dates[0][0]} to {unique_dates[0][1]}")
        print(f"Latest: {unique_dates[-1][0]} to {unique_dates[-1][1]}")
        print(f"Total unique date ranges: {len(unique_dates)}")
    
    # Get category breakdown
    category_result = supabase.table("tiktok_ad_data").select("category").execute()
    if category_result.data:
        categories = [d['category'] for d in category_result.data]
        category_counts = {}
        for cat in categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        print(f"\nCategory breakdown:")
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count} ads")
    
    # Get spend summary
    spend_result = supabase.table("tiktok_ad_data").select("amount_spent_usd").execute()
    if spend_result.data:
        total_spend = sum(d['amount_spent_usd'] for d in spend_result.data)
        print(f"\nTotal spend across all ads: ${total_spend:,.2f}")
    
    # Get sample of recent ads
    sample_result = supabase.table("tiktok_ad_data")\
        .select("ad_id, ad_name, category, amount_spent_usd, website_purchases, roas")\
        .order("reporting_starts", desc=True)\
        .limit(5)\
        .execute()
    
    if sample_result.data:
        print(f"\nSample of recent ads:")
        for ad in sample_result.data:
            print(f"  {ad['ad_id']}: {ad['ad_name'][:50]}...")
            print(f"    Category: {ad['category']}, Spend: ${ad['amount_spent_usd']}, Purchases: {ad['website_purchases']}, ROAS: {ad['roas']}")

if __name__ == "__main__":
    check_tiktok_data()