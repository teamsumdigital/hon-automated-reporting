#!/usr/bin/env python3
"""
Test TikTok API to understand available fields for ads and campaigns
"""

import os
import json
import requests
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

class TikTokAPITester:
    def __init__(self):
        self.access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        self.advertiser_id = os.getenv("TIKTOK_ADVERTISER_ID")
        self.base_url = "https://business-api.tiktok.com/open_api/v1.3"
        self.headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
    
    def test_ad_fields(self):
        """Test fetching a single ad with all available fields"""
        print("\n=== Testing Ad Fields ===")
        
        # First get some ad IDs from report
        endpoint = f"{self.base_url}/report/integrated/get/"
        params = {
            "advertiser_id": self.advertiser_id,
            "report_type": "BASIC",
            "data_level": "AUCTION_AD",
            "dimensions": json.dumps(["ad_id"]),
            "metrics": json.dumps(["spend"]),
            "start_date": "2024-07-01",
            "end_date": "2024-07-07",
            "page": 1,
            "page_size": 5
        }
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        if response.status_code != 200:
            print(f"Error getting ad report: {response.status_code}")
            return
        
        data = response.json()
        if data.get("code") != 0:
            print(f"API Error: {data.get('message')}")
            return
        
        ads = data.get("data", {}).get("list", [])
        if not ads:
            print("No ads found in report")
            return
        
        # Get first ad ID
        ad_id = ads[0]["dimensions"]["ad_id"]
        print(f"Testing with ad ID: {ad_id}")
        
        # Now test fetching this ad with different field combinations
        field_sets = [
            # Basic fields
            ["ad_id", "ad_name", "campaign_id", "campaign_name"],
            # Extended fields
            ["ad_id", "ad_name", "campaign_id", "adgroup_id", "adgroup_name", "primary_status", "secondary_status"],
            # All possible fields (will test what's available)
            ["ad_id", "ad_name", "campaign_id", "campaign_name", "adgroup_id", "adgroup_name", 
             "primary_status", "secondary_status", "operation_status", "is_aco", "create_time", 
             "modify_time", "ad_texts", "ad_format", "ad_text", "app_name", "call_to_action_id",
             "creative_authorized", "display_name", "image_ids", "landing_page_url", "page_id",
             "playable_url", "profile_image", "video_id"]
        ]
        
        for i, fields in enumerate(field_sets, 1):
            print(f"\n--- Test {i}: Fields: {fields[:3]}... ({len(fields)} total) ---")
            
            endpoint = f"{self.base_url}/ad/get/"
            params = {
                "advertiser_id": self.advertiser_id,
                "ad_ids": json.dumps([str(ad_id)]),
                "fields": json.dumps(fields)
            }
            
            try:
                response = requests.get(endpoint, headers=self.headers, params=params)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Response code: {data.get('code')}")
                    print(f"Message: {data.get('message', 'Success')}")
                    
                    if data.get("code") == 0 and data.get("data", {}).get("list"):
                        ad_data = data["data"]["list"][0]
                        print("Available fields in response:")
                        for field, value in ad_data.items():
                            print(f"  {field}: {value}")
                    else:
                        print(f"Error details: {json.dumps(data, indent=2)}")
                else:
                    print(f"HTTP Error: {response.text[:200]}")
                    
            except Exception as e:
                print(f"Exception: {e}")
    
    def test_campaign_fields(self):
        """Test fetching campaign details"""
        print("\n\n=== Testing Campaign Fields ===")
        
        # Get a campaign ID from the ad data
        endpoint = f"{self.base_url}/campaign/get/"
        params = {
            "advertiser_id": self.advertiser_id,
            "page": 1,
            "page_size": 1
        }
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        if response.status_code != 200:
            print(f"Error getting campaigns: {response.status_code}")
            return
        
        data = response.json()
        if data.get("code") != 0 or not data.get("data", {}).get("list"):
            print(f"No campaigns found: {data.get('message')}")
            return
        
        campaign = data["data"]["list"][0]
        print(f"Campaign fields available:")
        for field, value in campaign.items():
            print(f"  {field}: {value}")
    
    def test_ad_group_fields(self):
        """Test if we can get ad group information"""
        print("\n\n=== Testing Ad Group Fields ===")
        
        endpoint = f"{self.base_url}/adgroup/get/"
        params = {
            "advertiser_id": self.advertiser_id,
            "page": 1,
            "page_size": 1
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0 and data.get("data", {}).get("list"):
                    adgroup = data["data"]["list"][0]
                    print(f"Ad Group fields available:")
                    for field, value in adgroup.items():
                        print(f"  {field}: {value}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    tester = TikTokAPITester()
    tester.test_ad_fields()
    tester.test_campaign_fields()
    tester.test_ad_group_fields()