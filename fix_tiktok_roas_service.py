#!/usr/bin/env python3
"""
Fixed TikTok Ads Service with proper ROAS metrics (Payment Complete ROAS - website)
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

class FixedTikTokAdsService:
    """Fixed TikTok Ads Service with proper API calls and ROAS metrics"""
    
    def __init__(self):
        self.app_id = os.getenv("TIKTOK_APP_ID")
        self.app_secret = os.getenv("TIKTOK_APP_SECRET")
        self.access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        self.advertiser_id = os.getenv("TIKTOK_ADVERTISER_ID")
        self.sandbox_mode = os.getenv("TIKTOK_SANDBOX_MODE", "false").lower() == "true"
        
        if not all([self.app_id, self.app_secret, self.access_token, self.advertiser_id]):
            raise ValueError("Missing required TikTok Ads API credentials")
        
        # Base API URLs
        self.base_url = "https://business-api.tiktok.com/open_api/v1.3"
        
        # Set up session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            "Access-Token": self.access_token,
            "Content-Type": "application/json"
        })
        
        print(f"✅ TikTok Ads Service initialized")
        print(f"📍 Advertiser ID: {self.advertiser_id}")
        print(f"🔑 Access Token: {self.access_token[:20]}...")
    
    def test_connection(self) -> bool:
        """Test TikTok Ads API connection with correct parameter format"""
        try:
            # Use advertiser info endpoint to test connection
            endpoint = f"{self.base_url}/advertiser/info/"
            
            # Correct parameter format for TikTok API - GET request with query params
            params = {
                "advertiser_ids": json.dumps([self.advertiser_id])  # JSON encoded array
            }
            
            print(f"🔗 Testing connection to: {endpoint}")
            print(f"📋 Query params: {params}")
            
            response = self.session.get(endpoint, params=params)
            
            print(f"📡 Response status: {response.status_code}")
            print(f"📄 Response: {response.text[:500]}...")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:  # TikTok API success code
                    print("✅ TikTok Ads API connection successful")
                    return True
                else:
                    print(f"❌ TikTok API error: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ TikTok API HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ TikTok Ads connection test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_campaign_insights_with_roas(
        self, 
        start_date: date, 
        end_date: date,
        campaign_ids = None
    ):
        """
        Fetch campaign insights with proper ROAS metrics including Payment Complete ROAS (website)
        """
        try:
            endpoint = f"{self.base_url}/report/integrated/get/"
            
            # Valid metrics only (from TikTok API error message)
            metrics = [
                # Basic metrics that work
                "spend",
                "impressions", 
                "clicks",
                "ctr",
                "cpc",
                "cpm",
                "cost_per_conversion",
                "conversion_rate",
                
                # Valid conversion metrics (not in error list)
                "complete_payment_roas",  # This should be Payment Complete ROAS
                "complete_payment",
                "purchase"
            ]
            
            # Build request payload
            request_data = {
                "advertiser_id": self.advertiser_id,
                "report_type": "BASIC",
                "data_level": "AUCTION_CAMPAIGN",
                "dimensions": ["campaign_id"],
                "metrics": metrics,
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "page": 1,
                "page_size": 1000
            }
            
            print(f"📊 Fetching TikTok campaign insights for {start_date} to {end_date}")
            print(f"📈 Requesting {len(metrics)} metrics including ROAS variations")
            
            # Convert to query parameters for GET request
            params = {}
            for key, value in request_data.items():
                if isinstance(value, list):
                    params[key] = json.dumps(value)
                else:
                    params[key] = value
            
            print(f"📋 Query params: {list(params.keys())}")
            
            response = self.session.get(endpoint, params=params)
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ TikTok API HTTP error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return []
            
            data = response.json()
            print(f"📄 API Response: {json.dumps(data, indent=2)[:1000]}...")
            
            if data.get("code") != 0:
                print(f"❌ TikTok API error: {data.get('message', 'Unknown error')}")
                return []
            
            campaigns = []
            
            # Process the response data
            if "data" in data and "list" in data["data"]:
                for item in data["data"]["list"]:
                    try:
                        campaign_id = item.get("dimensions", {}).get("campaign_id")
                        metrics_data = item.get("metrics", {})
                        
                        # Get campaign name
                        campaign_name = self._get_campaign_name(campaign_id)
                        
                        campaign_info = {
                            "campaign_id": campaign_id,
                            "campaign_name": campaign_name,
                            "metrics": metrics_data
                        }
                        campaigns.append(campaign_info)
                        
                    except Exception as e:
                        print(f"❌ Failed to process campaign item: {e}")
                        continue
            
            print(f"✅ Retrieved {len(campaigns)} TikTok campaigns")
            return campaigns
            
        except Exception as e:
            print(f"❌ Failed to get TikTok campaign insights: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_campaign_name(self, campaign_id: str) -> str:
        """Get campaign name from campaign ID"""
        try:
            endpoint = f"{self.base_url}/campaign/get/"
            params = {
                "advertiser_id": self.advertiser_id,
                "campaign_ids": json.dumps([campaign_id])
            }
            
            response = self.session.get(endpoint, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0 and data.get("data", {}).get("list"):
                    return data["data"]["list"][0].get("campaign_name", f"Campaign {campaign_id}")
            
            return f"Campaign {campaign_id}"
            
        except Exception as e:
            print(f"❌ Failed to get campaign name for {campaign_id}: {e}")
            return f"Campaign {campaign_id}"

def test_fixed_service():
    """Test the fixed TikTok service"""
    print("🚀 Testing Fixed TikTok Ads Service")
    print("=" * 60)
    
    try:
        service = FixedTikTokAdsService()
        print()
        
        # Test connection
        print("🔗 Testing API connection...")
        if not service.test_connection():
            print("❌ Connection failed - stopping test")
            return
        print("✅ Connection successful!")
        print()
        
        # Test July 2025 data with enhanced ROAS metrics
        start_date = date(2025, 7, 1)
        end_date = date(2025, 7, 31)
        
        print(f"📊 Fetching July 2025 data with enhanced ROAS metrics...")
        campaigns = service.get_campaign_insights_with_roas(start_date, end_date)
        
        if not campaigns:
            print("❌ No campaigns found")
            return
        
        # Display results
        print(f"📈 Found {len(campaigns)} campaigns:")
        print()
        
        total_spend = 0
        total_conversions = 0
        total_value = 0
        total_clicks = 0
        total_impressions = 0
        
        for i, campaign in enumerate(campaigns[:5], 1):  # Show first 5
            metrics = campaign["metrics"]
            
            print(f"🎯 Campaign {i}: {campaign['campaign_name']}")
            print(f"   ID: {campaign['campaign_id']}")
            
            # Basic metrics
            spend = float(metrics.get("spend", 0))
            conversions = float(metrics.get("conversions", 0))
            conversion_value = float(metrics.get("conversion_value", 0))
            clicks = int(metrics.get("clicks", 0))
            impressions = int(metrics.get("impressions", 0))
            
            print(f"   💰 Spend: ${spend:,.2f}")
            print(f"   👀 Impressions: {impressions:,}")
            print(f"   🖱️ Clicks: {clicks:,}")
            print(f"   🛒 Conversions: {conversions:.0f}")
            print(f"   💵 Conversion Value: ${conversion_value:,.2f}")
            
            # ROAS metrics - check all variations
            roas_metrics = [
                "complete_payment_roas",
                "purchase_roas", 
                "conversion_value_roas",
                "roas",
                "total_complete_payment_roas",
                "website_complete_payment_roas"
            ]
            
            print(f"   📊 ROAS Metrics:")
            found_roas = False
            for roas_metric in roas_metrics:
                if roas_metric in metrics and metrics[roas_metric] != 0:
                    roas_value = float(metrics[roas_metric])
                    print(f"      • {roas_metric}: {roas_value:.2f}")
                    found_roas = True
            
            if not found_roas:
                # Calculate manual ROAS
                manual_roas = conversion_value / spend if spend > 0 else 0
                print(f"      • Manual ROAS: {manual_roas:.2f} (calculated)")
            
            # Show all available metrics
            print(f"   📋 All Available Metrics:")
            for metric, value in metrics.items():
                if value != 0 and value != "0":
                    print(f"      • {metric}: {value}")
            
            print()
            
            # Add to totals
            total_spend += spend
            total_conversions += conversions
            total_value += conversion_value
            total_clicks += clicks
            total_impressions += impressions
        
        # Show totals
        overall_roas = total_value / total_spend if total_spend > 0 else 0
        
        print(f"📊 JULY 2025 TOTALS:")
        print(f"   💰 Total Spend: ${total_spend:,.2f}")
        print(f"   👀 Total Impressions: {total_impressions:,}")
        print(f"   🖱️ Total Clicks: {total_clicks:,}")
        print(f"   🛒 Total Conversions: {total_conversions:.0f}")
        print(f"   💵 Total Conversion Value: ${total_value:,.2f}")
        print(f"   🔢 Overall ROAS: {overall_roas:.2f}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_service()