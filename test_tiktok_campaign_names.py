#!/usr/bin/env python3

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_tiktok_campaign_names():
    """Test TikTok API to get campaign names"""
    
    # TikTok API credentials
    access_token = os.getenv('TIKTOK_ACCESS_TOKEN')
    advertiser_id = os.getenv('TIKTOK_ADVERTISER_ID')
    
    print(f"Testing TikTok API with advertiser_id: {advertiser_id}")
    
    # Test campaign IDs from your data
    test_campaign_ids = [
        "1835848882707505",
        "1804414323981361", 
        "1804312808724513",
        "1804311710999553",
        "1804231373274161"
    ]
    
    # Test 1: Try campaign/get endpoint
    print("\n=== Testing /campaign/get/ endpoint ===")
    
    campaign_url = "https://business-api.tiktok.com/open_api/v1.3/campaign/get/"
    
    params = {
        'advertiser_id': advertiser_id,
        'campaign_ids': json.dumps(test_campaign_ids)
    }
    
    headers = {
        'Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(campaign_url, params=params, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Parsed response: {json.dumps(data, indent=2)}")
            
            if data.get('code') == 0 and data.get('data', {}).get('list'):
                print("\n=== Campaign Names Found ===")
                for campaign in data['data']['list']:
                    print(f"ID: {campaign.get('campaign_id')} -> Name: {campaign.get('campaign_name')}")
                return data['data']['list']
            else:
                print(f"API Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"Exception: {e}")
        
    # Test 2: Try different endpoint format
    print("\n=== Testing alternative endpoint format ===")
    
    # Try single campaign at a time
    for campaign_id in test_campaign_ids[:2]:  # Test first 2
        try:
            single_params = {
                'advertiser_id': advertiser_id,
                'campaign_ids': f'["{campaign_id}"]'
            }
            
            response = requests.get(campaign_url, params=single_params, headers=headers)
            print(f"\nCampaign {campaign_id}:")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0 and data.get('data', {}).get('list'):
                    campaign_info = data['data']['list'][0]
                    print(f"Name: {campaign_info.get('campaign_name')}")
                else:
                    print(f"Error: {data.get('message')}")
            else:
                print(f"HTTP Error: {response.text}")
                
        except Exception as e:
            print(f"Exception for {campaign_id}: {e}")
    
    return None

if __name__ == "__main__":
    test_tiktok_campaign_names()