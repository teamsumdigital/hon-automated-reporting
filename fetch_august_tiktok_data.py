#!/usr/bin/env python3
"""Fetch accurate TikTok data for August 1-14, 2025 and present for review"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the backend path
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from app.services.tiktok_service import TikTokService

load_dotenv()

def fetch_august_data():
    """Fetch TikTok data for August 1-14, 2025 and present for review"""
    
    print("📊 Fetching TikTok data for August 1-14, 2025...")
    
    # Date range: August 1-14, 2025
    start_date = "2025-08-01"
    end_date = "2025-08-14"
    
    print(f"📅 Date range: {start_date} to {end_date}")
    
    # Initialize service
    service = TikTokService()
    
    # Test connection
    connection_result = service.test_connection()
    if connection_result["status"] != "success":
        print(f"❌ Connection failed: {connection_result['message']}")
        return None
    
    print(f"✅ Connected: {connection_result['message']}")
    
    # Fetch campaigns and reports
    print("\n📋 Fetching campaigns...")
    campaigns = service.fetch_campaigns()
    print(f"Found {len(campaigns)} campaigns")
    
    print("\n📊 Fetching campaign reports...")
    reports = service.fetch_campaign_reports(start_date, end_date)
    print(f"Found {len(reports)} reports")
    
    if not reports:
        print("⚠️ No reports found for this date range")
        return None
    
    # Create lookup for reports by campaign_id
    reports_lookup = {report["dimensions"]["campaign_id"]: report for report in reports}
    
    # Combine campaign info with performance data
    campaign_data = []
    
    for campaign in campaigns:
        campaign_id = campaign["campaign_id"]
        campaign_name = campaign["campaign_name"]
        
        # Get report data for this campaign
        report = reports_lookup.get(campaign_id, {})
        metrics = report.get("metrics", {})
        
        # Extract metrics with proper field names
        spend = float(metrics.get("spend", 0))
        impressions = int(metrics.get("impressions", 0))
        clicks = int(metrics.get("clicks", 0))
        conversions = float(metrics.get("conversion", 0))
        cpm = float(metrics.get("cpm", 0))
        cpc = float(metrics.get("cpc", 0))
        ctr = float(metrics.get("ctr", 0))
        cost_per_conversion = float(metrics.get("cost_per_conversion", 0))
        
        campaign_data.append({
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "spend": spend,
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "cpm": cpm,
            "cpc": cpc,
            "ctr": ctr,
            "cost_per_conversion": cost_per_conversion,
            "campaign_type": service._classify_campaign_type(campaign_name)
        })
    
    # Sort by spend descending
    campaign_data.sort(key=lambda x: x["spend"], reverse=True)
    
    # Present data in table format
    print(f"\n📊 TIKTOK CAMPAIGN DATA - AUGUST 1-14, 2025")
    print("=" * 120)
    
    # Print header
    print(f"{'Campaign Name':<35} {'Spend':<12} {'Impressions':<12} {'Clicks':<8} {'Conv':<6} {'CPM':<8} {'CPC':<8} {'CTR':<8} {'CPA':<8} {'Type':<12}")
    print("-" * 120)
    
    # Print campaign data
    for campaign in campaign_data:
        name = campaign["campaign_name"][:33] + ".." if len(campaign["campaign_name"]) > 35 else campaign["campaign_name"]
        spend = f"${campaign['spend']:,.0f}"
        impressions = f"{campaign['impressions']:,}"
        clicks = f"{campaign['clicks']:,}"
        conversions = f"{campaign['conversions']:.0f}"
        cpm = f"${campaign['cpm']:.2f}"
        cpc = f"${campaign['cpc']:.2f}"
        ctr = f"{campaign['ctr']:.1f}%"
        cpa = f"${campaign['cost_per_conversion']:.0f}" if campaign['cost_per_conversion'] > 0 else "N/A"
        campaign_type = campaign["campaign_type"]
        
        print(f"{name:<35} {spend:<12} {impressions:<12} {clicks:<8} {conversions:<6} {cpm:<8} {cpc:<8} {ctr:<8} {cpa:<8} {campaign_type:<12}")
    
    # Calculate and show totals
    total_spend = sum(c["spend"] for c in campaign_data)
    total_impressions = sum(c["impressions"] for c in campaign_data)
    total_clicks = sum(c["clicks"] for c in campaign_data)
    total_conversions = sum(c["conversions"] for c in campaign_data)
    
    print(f"\n📊 TOTALS:")
    print(f"💰 Total Spend: ${total_spend:,.2f}")
    print(f"👁️ Total Impressions: {total_impressions:,}")
    print(f"🖱️ Total Clicks: {total_clicks:,}")
    print(f"🛒 Total Conversions: {total_conversions:.0f}")
    
    if total_spend > 0:
        avg_cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
        avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
        
        print(f"📈 Overall CPM: ${avg_cpm:.2f}")
        print(f"📈 Overall CPC: ${avg_cpc:.2f}")
        print(f"📈 Overall CTR: {avg_ctr:.2f}%")
        print(f"📈 Overall CPA: ${avg_cpa:.2f}")
    
    print(f"\n⚠️ Campaigns with 0 purchases: {sum(1 for c in campaign_data if c['conversions'] == 0)}")
    print(f"⚠️ Campaigns with 0 clicks: {sum(1 for c in campaign_data if c['clicks'] == 0)}")
    print(f"⚠️ Campaigns with 0 impressions: {sum(1 for c in campaign_data if c['impressions'] == 0)}")
    
    return campaign_data, start_date, end_date

def upsert_to_database(campaign_data, start_date, end_date):
    """Upsert the approved data to Supabase"""
    
    print("\n🔄 Upserting approved data to Supabase...")
    
    # Initialize service for database operations
    service = TikTokService()
    
    # Clear existing data for this date range first
    from supabase import create_client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    # Delete existing records for this date range
    delete_result = supabase.table("tiktok_campaign_data")\
        .delete()\
        .gte("reporting_starts", start_date)\
        .lte("reporting_ends", end_date)\
        .execute()
    
    print(f"🗑️ Cleared {len(delete_result.data)} existing records for date range")
    
    # Prepare data for upsert
    upsert_data = []
    for campaign in campaign_data:
        campaign_record = {
            "campaign_id": campaign["campaign_id"],
            "campaign_name": campaign["campaign_name"],
            "category": None,  # Will be auto-categorized by trigger
            "campaign_type": campaign["campaign_type"],
            "reporting_starts": start_date,
            "reporting_ends": end_date,
            "amount_spent_usd": campaign["spend"],
            "website_purchases": int(campaign["conversions"]),
            "purchases_conversion_value": 0.0,  # TikTok doesn't provide conversion value
            "impressions": campaign["impressions"],
            "link_clicks": campaign["clicks"],
            "cpa": campaign["cost_per_conversion"],
            "roas": 0.0,  # Cannot calculate without conversion value
            "cpc": campaign["cpc"]
        }
        upsert_data.append(campaign_record)
    
    # Upsert to database
    result = supabase.table("tiktok_campaign_data").upsert(
        upsert_data,
        on_conflict="campaign_id,reporting_starts,reporting_ends"
    ).execute()
    
    print(f"✅ Successfully upserted {len(result.data)} records")
    
    # Verify the data
    verify_result = supabase.table("tiktok_campaign_data")\
        .select("*")\
        .gte("reporting_starts", start_date)\
        .lte("reporting_ends", end_date)\
        .execute()
    
    verified_spend = sum(c.get("amount_spent_usd", 0) for c in verify_result.data)
    verified_conversions = sum(c.get("website_purchases", 0) for c in verify_result.data)
    
    print(f"✅ Verified in database:")
    print(f"   Records: {len(verify_result.data)}")
    print(f"   Total spend: ${verified_spend:,.2f}")
    print(f"   Total conversions: {verified_conversions}")
    
    return True

if __name__ == "__main__":
    print("🚀 TikTok August Data Fetch & Review")
    print("=" * 60)
    
    # Fetch the data
    result = fetch_august_data()
    
    if result:
        campaign_data, start_date, end_date = result
        
        print("\n" + "=" * 60)
        print("🔍 PLEASE REVIEW THE DATA ABOVE")
        print("=" * 60)
        
        # Auto-approve as requested by user
        approval = 'yes'
        print("\n✅ Data auto-approved as requested!")
        
        if approval in ['yes', 'y']:
            print("\n✅ Data approved! Proceeding with upsert...")
            success = upsert_to_database(campaign_data, start_date, end_date)
            
            if success:
                print("\n🎉 SUCCESS! TikTok data for August 1-14 has been updated in the database")
            else:
                print("\n❌ Upsert failed")
        else:
            print("\n❌ Data not approved. No changes made to database.")
    else:
        print("\n❌ Failed to fetch data")
    
    print("\n" + "=" * 60)