#!/usr/bin/env python3
"""Pull all TikTok campaign data by month starting January 2024"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from calendar import monthrange

# Add the backend path
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from app.services.tiktok_service import TikTokService
from supabase import create_client

load_dotenv()

def get_month_ranges():
    """Generate month ranges from January 2024 to current"""
    
    ranges = []
    current_date = datetime.now()
    
    # Start from January 2024
    year = 2024
    month = 1
    
    while year < current_date.year or (year == current_date.year and month <= current_date.month):
        # Get first and last day of month
        first_day = datetime(year, month, 1)
        last_day_num = monthrange(year, month)[1]
        last_day = datetime(year, month, last_day_num)
        
        # Special case for current month (August 2025) - only go to 14th
        if year == 2025 and month == 8:
            last_day = datetime(year, month, 14)
        
        start_date = first_day.strftime("%Y-%m-%d")
        end_date = last_day.strftime("%Y-%m-%d")
        
        ranges.append({
            "start_date": start_date,
            "end_date": end_date,
            "month_name": first_day.strftime("%B %Y")
        })
        
        # Move to next month
        month += 1
        if month > 12:
            month = 1
            year += 1
    
    return ranges

def sync_month_data(service, start_date, end_date, month_name):
    """Sync data for a specific month"""
    
    print(f"\n📅 Processing {month_name} ({start_date} to {end_date})...")
    
    # Fetch campaigns and reports for this month
    campaigns = service.fetch_campaigns()
    reports = service.fetch_campaign_reports(start_date, end_date)
    
    if not reports:
        print(f"   ⚠️ No reports found for {month_name}")
        return 0, 0, 0, 0
    
    # Create lookup for reports by campaign_id
    reports_lookup = {report["dimensions"]["campaign_id"]: report for report in reports}
    
    # Prepare data for upsert
    upsert_data = []
    total_spend = 0
    total_conversions = 0
    total_clicks = 0
    total_impressions = 0
    
    for campaign in campaigns:
        campaign_id = campaign["campaign_id"]
        campaign_name = campaign["campaign_name"]
        
        # Get report data for this campaign
        report = reports_lookup.get(campaign_id, {})
        metrics = report.get("metrics", {})
        
        # Extract metrics
        spend = float(metrics.get("spend", 0))
        impressions = int(metrics.get("impressions", 0))
        clicks = int(metrics.get("clicks", 0))
        conversions = float(metrics.get("conversion", 0))
        cost_per_conversion = float(metrics.get("cost_per_conversion", 0))
        cpc = float(metrics.get("cpc", 0))
        
        # Add to totals
        total_spend += spend
        total_conversions += conversions
        total_clicks += clicks
        total_impressions += impressions
        
        # Prepare record for database
        campaign_record = {
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "category": None,  # Will be auto-categorized by trigger
            "campaign_type": service._classify_campaign_type(campaign_name),
            "reporting_starts": start_date,
            "reporting_ends": end_date,
            "amount_spent_usd": spend,
            "website_purchases": int(conversions),
            "purchases_conversion_value": 0.0,  # TikTok doesn't provide conversion value
            "impressions": impressions,
            "link_clicks": clicks,
            "cpa": cost_per_conversion,
            "roas": 0.0,  # Cannot calculate without conversion value
            "cpc": cpc
        }
        upsert_data.append(campaign_record)
    
    # Connect to database and upsert
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    # Delete existing records for this date range first
    delete_result = supabase.table("tiktok_campaign_data")\
        .delete()\
        .gte("reporting_starts", start_date)\
        .lte("reporting_ends", end_date)\
        .execute()
    
    # Upsert new data
    if upsert_data:
        result = supabase.table("tiktok_campaign_data").upsert(
            upsert_data,
            on_conflict="campaign_id,reporting_starts,reporting_ends"
        ).execute()
        
        records_synced = len(result.data)
    else:
        records_synced = 0
    
    print(f"   ✅ {month_name}: ${total_spend:,.0f} spend, {total_conversions:.0f} conversions, {records_synced} records")
    
    return total_spend, total_conversions, total_clicks, total_impressions

def main():
    """Main function to sync all historical TikTok data"""
    
    print("🚀 TikTok Historical Data Sync (January 2024 - Present)")
    print("=" * 70)
    
    # Initialize service
    service = TikTokService()
    
    # Test connection
    connection_result = service.test_connection()
    if connection_result["status"] != "success":
        print(f"❌ Connection failed: {connection_result['message']}")
        return False
    
    print(f"✅ Connected: {connection_result['message']}")
    
    # Get all month ranges
    month_ranges = get_month_ranges()
    print(f"\n📅 Will process {len(month_ranges)} months:")
    for range_info in month_ranges:
        print(f"   {range_info['month_name']} ({range_info['start_date']} to {range_info['end_date']})")
    
    # Auto-proceed as requested by user
    print(f"\n⚠️ This will replace ALL existing TikTok data in the database")
    print("✅ Auto-proceeding with historical sync as requested...")
    
    # Process each month
    print(f"\n🔄 Starting historical sync...")
    
    grand_total_spend = 0
    grand_total_conversions = 0
    grand_total_clicks = 0
    grand_total_impressions = 0
    months_processed = 0
    
    for range_info in month_ranges:
        try:
            spend, conversions, clicks, impressions = sync_month_data(
                service, 
                range_info['start_date'], 
                range_info['end_date'], 
                range_info['month_name']
            )
            
            grand_total_spend += spend
            grand_total_conversions += conversions
            grand_total_clicks += clicks
            grand_total_impressions += impressions
            months_processed += 1
            
        except Exception as e:
            print(f"   ❌ Error processing {range_info['month_name']}: {e}")
            continue
    
    # Final summary
    print(f"\n" + "=" * 70)
    print(f"🎉 HISTORICAL SYNC COMPLETE")
    print(f"=" * 70)
    print(f"📅 Months Processed: {months_processed}/{len(month_ranges)}")
    print(f"💰 Grand Total Spend: ${grand_total_spend:,.2f}")
    print(f"🛒 Grand Total Conversions: {grand_total_conversions:.0f}")
    print(f"🖱️ Grand Total Clicks: {grand_total_clicks:,}")
    print(f"👁️ Grand Total Impressions: {grand_total_impressions:,}")
    
    if grand_total_spend > 0:
        overall_cpa = grand_total_spend / grand_total_conversions if grand_total_conversions > 0 else 0
        overall_cpc = grand_total_spend / grand_total_clicks if grand_total_clicks > 0 else 0
        overall_ctr = (grand_total_clicks / grand_total_impressions * 100) if grand_total_impressions > 0 else 0
        
        print(f"📈 Overall CPA: ${overall_cpa:.2f}")
        print(f"📈 Overall CPC: ${overall_cpc:.2f}")
        print(f"📈 Overall CTR: {overall_ctr:.2f}%")
    
    print(f"\n💡 TikTok historical data is now available in the dashboard!")
    
    return True

if __name__ == "__main__":
    main()