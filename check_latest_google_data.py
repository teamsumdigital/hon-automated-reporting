#!/usr/bin/env python3
"""Check the latest Google Ads data available"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def check_latest_google_data():
    """Check what's the latest date we have Google Ads data for"""
    
    print("🔍 Checking latest Google Ads data...")
    
    # Connect to Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        # Get latest date
        result = supabase.table("google_campaign_data")\
            .select("reporting_starts")\
            .order("reporting_starts", desc=True)\
            .limit(1)\
            .execute()
        
        if not result.data:
            print("❌ No Google Ads data found in database")
            return False
        
        latest_date = result.data[0]["reporting_starts"]
        print(f"📅 Latest Google Ads data: {latest_date}")
        
        # Get count of campaigns for latest date
        count_result = supabase.table("google_campaign_data")\
            .select("*", count="exact")\
            .eq("reporting_starts", latest_date)\
            .execute()
        
        campaign_count = count_result.count
        print(f"📊 Campaigns on {latest_date}: {campaign_count}")
        
        # Get spend total for latest date
        spend_result = supabase.table("google_campaign_data")\
            .select("amount_spent_usd, website_purchases, purchases_conversion_value")\
            .eq("reporting_starts", latest_date)\
            .execute()
        
        campaigns = spend_result.data
        total_spend = sum(c.get("amount_spent_usd", 0) for c in campaigns)
        total_conversions = sum(c.get("website_purchases", 0) for c in campaigns)
        total_revenue = sum(c.get("purchases_conversion_value", 0) for c in campaigns)
        
        print(f"💰 Total spend on {latest_date}: ${total_spend:,.2f}")
        print(f"🛒 Total conversions: {total_conversions}")
        print(f"💵 Total revenue: ${total_revenue:,.2f}")
        
        # Get all available dates
        dates_result = supabase.table("google_campaign_data")\
            .select("reporting_starts")\
            .execute()
        
        unique_dates = sorted(list(set([row["reporting_starts"] for row in dates_result.data])), reverse=True)
        
        print(f"\n📋 All available dates ({len(unique_dates)} total):")
        for date in unique_dates[:10]:  # Show last 10 dates
            date_count = sum(1 for row in dates_result.data if row["reporting_starts"] == date)
            print(f"  {date}: {date_count} campaigns")
        
        if len(unique_dates) > 10:
            print(f"  ... and {len(unique_dates) - 10} more dates")
        
        return True
        
    except Exception as e:
        print(f"❌ Error querying database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Google Ads Data Check")
    print("=" * 40)
    
    check_latest_google_data()
    
    print("\n" + "=" * 40)