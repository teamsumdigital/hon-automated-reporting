#!/usr/bin/env python3
"""
Test script to check current TikTok Ads metrics and fix ROAS to use Payment Complete ROAS (website)
"""

import os
import sys
import json
import requests
from datetime import date, datetime
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.tiktok_ads_service import TikTokAdsService

def test_current_metrics():
    """Test current TikTok metrics for July 2025"""
    print("🧪 Testing TikTok Ads API - Current Metrics")
    print("=" * 60)
    
    try:
        # Initialize service
        service = TikTokAdsService()
        print(f"✅ TikTok Ads Service initialized")
        print(f"📍 Advertiser ID: {service.advertiser_id}")
        print(f"🔧 Mode: {'Sandbox' if service.sandbox_mode else 'Production'}")
        print()
        
        # Test connection
        print("🔗 Testing API connection...")
        if not service.test_connection():
            print("❌ Connection failed!")
            return
        print("✅ Connection successful!")
        print()
        
        # Test July 2025 data
        start_date = date(2025, 7, 1)
        end_date = date(2025, 7, 31)
        
        print(f"📊 Fetching campaign data for July 2025 ({start_date} to {end_date})")
        insights = service.get_campaign_insights(start_date, end_date)
        
        if not insights:
            print("❌ No data found for July 2025")
            return
        
        print(f"📈 Found {len(insights)} campaigns")
        print()
        
        # Show current metrics for each campaign
        for i, insight in enumerate(insights[:3], 1):  # Show first 3 campaigns
            print(f"🎯 Campaign {i}: {insight.campaign_name}")
            print(f"   ID: {insight.campaign_id}")
            print(f"   💰 Spend: ${insight.spend}")
            print(f"   👀 Impressions: {insight.impressions}")
            print(f"   🖱️ Clicks: {insight.clicks}")
            print(f"   🛒 Conversions: {insight.conversions}")
            print(f"   💵 Conversion Value: ${insight.conversion_value}")
            print(f"   📊 CTR: {insight.ctr}%")
            print(f"   💲 CPC: ${insight.cpc}")
            print(f"   📈 CPM: ${insight.cpm}")
            print(f"   🎯 Cost per Conversion: ${insight.cost_per_conversion}")
            print(f"   📈 Conversion Rate: {insight.conversion_rate}%")
            
            # Calculate current ROAS
            try:
                spend = Decimal(insight.spend)
                conv_value = Decimal(insight.conversion_value)
                current_roas = conv_value / spend if spend > 0 else Decimal('0')
                print(f"   🔢 Current ROAS: {current_roas:.2f}")
            except:
                print(f"   🔢 Current ROAS: Error calculating")
            
            print()
        
        if len(insights) > 3:
            print(f"... and {len(insights) - 3} more campaigns")
            print()
        
        # Show totals
        total_spend = sum(Decimal(insight.spend) for insight in insights)
        total_conversions = sum(int(insight.conversions) for insight in insights)
        total_value = sum(Decimal(insight.conversion_value) for insight in insights)
        total_impressions = sum(int(insight.impressions) for insight in insights)
        total_clicks = sum(int(insight.clicks) for insight in insights)
        
        overall_roas = total_value / total_spend if total_spend > 0 else Decimal('0')
        overall_cpc = total_spend / total_clicks if total_clicks > 0 else Decimal('0')
        
        print("📊 JULY 2025 TOTALS:")
        print(f"   💰 Total Spend: ${total_spend:,.2f}")
        print(f"   👀 Total Impressions: {total_impressions:,}")
        print(f"   🖱️ Total Clicks: {total_clicks:,}")
        print(f"   🛒 Total Conversions: {total_conversions:,}")
        print(f"   💵 Total Conversion Value: ${total_value:,.2f}")
        print(f"   🔢 Overall ROAS: {overall_roas:.2f}")
        print(f"   💲 Overall CPC: ${overall_cpc:.2f}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_available_metrics():
    """Test what metrics are available from TikTok API"""
    print("🔍 Testing Available TikTok Metrics")
    print("=" * 60)
    
    try:
        service = TikTokAdsService()
        
        # Try to get available metrics through API documentation or test call
        endpoint = f"{service.base_url}/report/integrated/get/"
        
        # Test request with extended metrics including website ROAS
        request_data = {
            "advertiser_id": service.advertiser_id,
            "report_type": "BASIC",
            "data_level": "AUCTION_CAMPAIGN",
            "dimensions": ["campaign_id"],
            "metrics": [
                "spend",
                "impressions", 
                "clicks",
                "conversions",
                "conversion_value",
                "ctr",
                "cpc",
                "cpm",
                "cost_per_conversion",
                "conversion_rate",
                # Try website-specific metrics
                "website_conversions",
                "website_conversion_value", 
                "website_roas",
                "complete_payment",
                "complete_payment_roas",
                "complete_payment_value",
                "website_complete_payment",
                "website_complete_payment_roas",
                "website_complete_payment_value",
                # Other potential ROAS metrics
                "purchase_roas",
                "purchase_value_roas",
                "conversion_value_roas"
            ],
            "start_date": "2025-07-01",
            "end_date": "2025-07-31",
            "page": 1,
            "page_size": 1
        }
        
        print("🔍 Testing extended metrics request...")
        print(f"📊 Metrics requested: {len(request_data['metrics'])}")
        
        response = service.session.post(endpoint, json=request_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print("✅ Extended metrics request successful!")
                
                if "data" in data and "list" in data["data"] and data["data"]["list"]:
                    metrics = data["data"]["list"][0].get("metrics", {})
                    print(f"📈 Available metrics in response:")
                    
                    for metric, value in metrics.items():
                        print(f"   • {metric}: {value}")
                else:
                    print("📊 No data returned, but request format accepted")
            else:
                print(f"❌ API Error: {data.get('message', 'Unknown error')}")
                print(f"📝 Error details: {data}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing metrics: {e}")

if __name__ == "__main__":
    print("🚀 TikTok Ads ROAS Metrics Test")
    print("=" * 60)
    print()
    
    # Test current metrics
    test_current_metrics()
    print()
    
    # Test available metrics
    test_available_metrics()
    
    print("✅ Test complete!")