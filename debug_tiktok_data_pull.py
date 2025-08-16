#!/usr/bin/env python3
"""Debug and fix TikTok data pull to get real performance metrics"""

import os
import json
import requests
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()

def debug_tiktok_api():
    """Debug TikTok API to understand data structure and fix metrics pull"""
    
    print("🔍 Debugging TikTok Marketing API data structure...")
    
    # TikTok API credentials
    app_id = os.getenv("TIKTOK_APP_ID")
    app_secret = os.getenv("TIKTOK_APP_SECRET")
    access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
    advertiser_id = os.getenv("TIKTOK_ADVERTISER_ID")
    
    if not all([app_id, app_secret, access_token, advertiser_id]):
        print("❌ Missing TikTok credentials")
        return False
    
    print(f"📱 App ID: {app_id}")
    print(f"🎯 Advertiser ID: {advertiser_id}")
    print(f"🔑 Access Token: {access_token[:20]}...")
    
    headers = {
        "Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    # Test 1: Get campaigns (basic info)
    print("\n🎯 Test 1: Getting campaigns...")
    campaigns_url = "https://business-api.tiktok.com/open_api/v1.3/campaign/get/"
    
    campaign_params = {
        "advertiser_id": advertiser_id,
        "filtering": json.dumps({
            "campaign_statuses": ["ENABLE", "DISABLE", "PAUSED"]
        }),
        "fields": json.dumps([
            "campaign_id", "campaign_name", "operation_status", 
            "objective_type", "budget", "create_time", "modify_time"
        ])
    }
    
    try:
        response = requests.get(campaigns_url, headers=headers, params=campaign_params)
        print(f"📊 Campaigns Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                campaigns = data.get("data", {}).get("list", [])
                print(f"✅ Found {len(campaigns)} campaigns")
                
                # Show first campaign structure
                if campaigns:
                    print("📋 First campaign structure:")
                    print(json.dumps(campaigns[0], indent=2))
            else:
                print(f"❌ API Error: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    # Test 2: Get campaign reports (performance metrics)
    print("\n📊 Test 2: Getting campaign reports...")
    reports_url = "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/"
    
    # Test with yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"📅 Testing date: {yesterday}")
    
    report_params = {
        "advertiser_id": advertiser_id,
        "report_type": "BASIC",
        "dimensions": json.dumps(["campaign_id"]),
        "metrics": json.dumps([
            "spend", "impressions", "clicks", "conversions", "conversion_value",
            "cpm", "cpc", "ctr", "conversion_rate"
        ]),
        "data_level": "AUCTION_CAMPAIGN",
        "start_date": yesterday,
        "end_date": yesterday,
        "service_type": "AUCTION"
    }
    
    try:
        response = requests.get(reports_url, headers=headers, params=report_params)
        print(f"📊 Reports Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Full response structure:")
            print(json.dumps(data, indent=2))
            
            if data.get("code") == 0:
                reports = data.get("data", {}).get("list", [])
                print(f"✅ Found {len(reports)} campaign reports")
                
                # Show report structure
                if reports:
                    print("📊 First report structure:")
                    print(json.dumps(reports[0], indent=2))
                else:
                    print("⚠️ No reports found - campaigns might not have data for yesterday")
            else:
                print(f"❌ Reports API Error: {data.get('message')}")
        else:
            print(f"❌ Reports HTTP Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Reports Exception: {e}")
    
    # Test 3: Try different date range (last 7 days)
    print("\n📊 Test 3: Trying last 7 days...")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    report_params_week = {
        "advertiser_id": advertiser_id,
        "report_type": "BASIC",
        "dimensions": json.dumps(["campaign_id"]),
        "metrics": json.dumps([
            "spend", "impressions", "clicks", "conversions", "conversion_value"
        ]),
        "data_level": "AUCTION_CAMPAIGN",
        "start_date": start_date,
        "end_date": end_date,
        "service_type": "AUCTION"
    }
    
    try:
        response = requests.get(reports_url, headers=headers, params=report_params_week)
        print(f"📊 Week Reports Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                reports = data.get("data", {}).get("list", [])
                print(f"✅ Found {len(reports)} reports for last 7 days")
                
                if reports:
                    # Calculate totals
                    total_spend = sum(float(r.get("metrics", {}).get("spend", 0)) for r in reports)
                    total_impressions = sum(int(r.get("metrics", {}).get("impressions", 0)) for r in reports)
                    total_clicks = sum(int(r.get("metrics", {}).get("clicks", 0)) for r in reports)
                    total_conversions = sum(float(r.get("metrics", {}).get("conversions", 0)) for r in reports)
                    
                    print(f"💰 Total spend (7 days): ${total_spend}")
                    print(f"👁️ Total impressions: {total_impressions:,}")
                    print(f"🖱️ Total clicks: {total_clicks}")
                    print(f"🛒 Total conversions: {total_conversions}")
                    
                    # Show top spending campaign
                    top_campaign = max(reports, key=lambda x: float(x.get("metrics", {}).get("spend", 0)))
                    print(f"\n🏆 Top spending campaign:")
                    print(json.dumps(top_campaign, indent=2))
            else:
                print(f"❌ Week Reports Error: {data.get('message')}")
        else:
            print(f"❌ Week Reports HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Week Reports Exception: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 TikTok API Debug Session")
    print("=" * 60)
    
    debug_tiktok_api()
    
    print("\n" + "=" * 60)
    print("💡 Next steps:")
    print("1. Review the API response structure above")
    print("2. Update TikTok service to use correct field names")
    print("3. Ensure date ranges have actual campaign activity")
    print("4. Re-sync with corrected service")