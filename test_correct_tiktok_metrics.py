#!/usr/bin/env python3
"""Test TikTok API with correct metric field names"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def test_correct_metrics():
    """Test TikTok API with correct metric field names"""
    
    print("🔧 Testing TikTok API with corrected metrics...")
    
    # TikTok API credentials
    access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
    advertiser_id = os.getenv("TIKTOK_ADVERTISER_ID")
    
    headers = {
        "Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    reports_url = "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/"
    
    # Test with last 7 days and CORRECT metrics
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # CORRECTED metrics - using TikTok-specific field names
    correct_params = {
        "advertiser_id": advertiser_id,
        "report_type": "BASIC",
        "dimensions": json.dumps(["campaign_id"]),
        "metrics": json.dumps([
            "spend",           # Cost
            "impressions",     # Impressions  
            "clicks",          # Clicks
            "cpm",             # Cost per mille
            "cpc",             # Cost per click
            "ctr",             # Click-through rate
            "conversion",      # Conversions (singular, not plural)
            "cost_per_conversion",  # Cost per conversion
            "conversion_rate"       # Conversion rate
        ]),
        "data_level": "AUCTION_CAMPAIGN",
        "start_date": start_date,
        "end_date": end_date,
        "service_type": "AUCTION"
    }
    
    print(f"📅 Date range: {start_date} to {end_date}")
    print("📊 Testing with corrected metrics...")
    
    try:
        response = requests.get(reports_url, headers=headers, params=correct_params)
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Response code: {data.get('code')}")
            
            if data.get("code") == 0:
                reports = data.get("data", {}).get("list", [])
                print(f"✅ Success! Found {len(reports)} reports")
                
                if reports:
                    # Show first report structure
                    print("📊 First report structure:")
                    print(json.dumps(reports[0], indent=2))
                    
                    # Calculate totals
                    total_spend = sum(float(r.get("metrics", {}).get("spend", 0)) for r in reports)
                    total_impressions = sum(int(r.get("metrics", {}).get("impressions", 0)) for r in reports)
                    total_clicks = sum(int(r.get("metrics", {}).get("clicks", 0)) for r in reports)
                    total_conversions = sum(float(r.get("metrics", {}).get("conversion", 0)) for r in reports)
                    
                    print(f"\n📊 TOTALS (Last 7 days):")
                    print(f"💰 Spend: ${total_spend}")
                    print(f"👁️ Impressions: {total_impressions:,}")
                    print(f"🖱️ Clicks: {total_clicks}")
                    print(f"🛒 Conversions: {total_conversions}")
                    
                    return reports
                else:
                    print("⚠️ No reports found for date range")
            else:
                print(f"❌ API Error: {data.get('message')}")
                
                # Try with even more basic metrics
                print("\n🔧 Trying with minimal metrics...")
                basic_params = {
                    "advertiser_id": advertiser_id,
                    "report_type": "BASIC", 
                    "dimensions": json.dumps(["campaign_id"]),
                    "metrics": json.dumps(["spend", "impressions", "clicks"]),
                    "data_level": "AUCTION_CAMPAIGN",
                    "start_date": start_date,
                    "end_date": end_date,
                    "service_type": "AUCTION"
                }
                
                basic_response = requests.get(reports_url, headers=headers, params=basic_params)
                basic_data = basic_response.json()
                
                if basic_data.get("code") == 0:
                    basic_reports = basic_data.get("data", {}).get("list", [])
                    print(f"✅ Basic metrics work! Found {len(basic_reports)} reports")
                    
                    if basic_reports:
                        print("📊 Basic report structure:")
                        print(json.dumps(basic_reports[0], indent=2))
                        return basic_reports
                else:
                    print(f"❌ Even basic metrics failed: {basic_data.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 TikTok Corrected Metrics Test")
    print("=" * 50)
    
    reports = test_correct_metrics()
    
    if reports:
        print("\n✅ SUCCESS! Now we can update the TikTok service with correct metrics")
        print("📋 Available metrics in response:")
        if reports and "metrics" in reports[0]:
            metrics = reports[0]["metrics"]
            for key in metrics.keys():
                print(f"  - {key}: {metrics[key]}")
    else:
        print("\n❌ Still having issues - may need to check TikTok API documentation")
    
    print("\n" + "=" * 50)