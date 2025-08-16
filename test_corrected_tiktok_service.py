#!/usr/bin/env python3
"""Test the corrected TikTok service with real API data"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the backend path
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from app.services.tiktok_service import TikTokService

load_dotenv()

def test_corrected_service():
    """Test the corrected TikTok service"""
    
    print("🔧 Testing corrected TikTok service...")
    
    # Initialize service
    service = TikTokService()
    
    # Test connection first
    print("\n🔗 Testing connection...")
    connection_result = service.test_connection()
    print(f"Connection: {connection_result}")
    
    if connection_result["status"] != "success":
        print("❌ Connection failed, cannot proceed")
        return False
    
    # Test fetching campaigns
    print("\n📋 Fetching campaigns...")
    campaigns = service.fetch_campaigns()
    print(f"Found {len(campaigns)} campaigns")
    
    if campaigns:
        print("First campaign:", campaigns[0]["campaign_name"])
    
    # Test fetching reports for last 7 days
    print("\n📊 Fetching reports for last 7 days...")
    end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    print(f"Date range: {start_date} to {end_date}")
    
    reports = service.fetch_campaign_reports(start_date, end_date)
    print(f"Found {len(reports)} reports")
    
    if reports:
        # Show first report structure
        print("\n📊 First report:")
        first_report = reports[0]
        print(f"Campaign ID: {first_report.get('dimensions', {}).get('campaign_id')}")
        print(f"Metrics: {first_report.get('metrics', {})}")
        
        # Calculate totals
        total_spend = sum(float(r.get("metrics", {}).get("spend", 0)) for r in reports)
        total_impressions = sum(int(r.get("metrics", {}).get("impressions", 0)) for r in reports)
        total_clicks = sum(int(r.get("metrics", {}).get("clicks", 0)) for r in reports)
        total_conversions = sum(float(r.get("metrics", {}).get("conversion", 0)) for r in reports)
        
        print(f"\n📊 TOTALS (Last 7 days):")
        print(f"💰 Spend: ${total_spend:,.2f}")
        print(f"👁️ Impressions: {total_impressions:,}")
        print(f"🖱️ Clicks: {total_clicks}")
        print(f"🛒 Conversions: {total_conversions}")
    
    # Test sync functionality
    print(f"\n🔄 Testing sync for date range {start_date} to {end_date}...")
    sync_count, sync_message = service.sync_campaign_data(start_date, end_date)
    print(f"Sync result: {sync_message}")
    
    if sync_count > 0:
        print("✅ SUCCESS! TikTok data sync is now working correctly")
        
        # Test dashboard data
        print("\n📊 Testing dashboard data...")
        dashboard_data = service.get_dashboard_data()
        summary = dashboard_data["summary"]
        
        print(f"Dashboard summary:")
        print(f"  Total spend: ${summary['total_spend']:,.2f}")
        print(f"  Total clicks: {summary['total_clicks']:,}")
        print(f"  Total purchases: {summary['total_purchases']}")
        print(f"  Campaigns: {summary['campaigns_count']}")
        
        return True
    else:
        print("❌ Sync failed")
        return False

if __name__ == "__main__":
    print("🚀 TikTok Corrected Service Test")
    print("=" * 50)
    
    success = test_corrected_service()
    
    if success:
        print("\n✅ SUCCESS! TikTok service is now working with real data")
        print("💡 The TikTok integration is ready for use")
    else:
        print("\n❌ Still having issues - check the error messages above")
    
    print("\n" + "=" * 50)