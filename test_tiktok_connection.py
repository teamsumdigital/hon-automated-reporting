#!/usr/bin/env python3
"""Test TikTok Marketing API connection with obtained credentials"""

import os
import requests
import json

def test_tiktok_connection():
    """Test TikTok Marketing API connection"""
    
    # Your TikTok credentials
    app_id = "7538619599563161616"
    app_secret = "51c35c7f4f089c33d793f709abc88bba293f6c83"
    access_token = "a3d1496268b35f9ad9a6f0d9d4492ab35d4c0bea"
    advertiser_id = "6961828676572839938"
    
    print("🔍 Testing TikTok Marketing API Connection...")
    print(f"📱 App ID: {app_id}")
    print(f"🎯 Advertiser ID: {advertiser_id}")
    print(f"🔑 Access Token: {access_token[:20]}...")
    
    # Test 1: Get advertiser info
    print("\n🏢 Test 1: Getting advertiser info...")
    
    advertiser_url = "https://business-api.tiktok.com/open_api/v1.3/advertiser/info/"
    headers = {
        "Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    try:
        # Fix the params format - TikTok expects JSON string
        params = {
            "advertiser_ids": json.dumps([advertiser_id])
        }
        
        response = requests.get(advertiser_url, headers=headers, params=params)
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Response: {json.dumps(data, indent=2)}")
            
            if data.get("code") == 0:
                advertiser_list = data.get("data", {}).get("list", [])
                if advertiser_list:
                    info = advertiser_list[0]
                    print(f"✅ Advertiser: {info.get('name', 'Unknown')}")
                    print(f"📊 Status: {info.get('status', 'Unknown')}")
                    print(f"💰 Currency: {info.get('currency', 'Unknown')}")
                    print(f"🌍 Timezone: {info.get('timezone', 'Unknown')}")
                else:
                    print("❌ No advertiser data returned")
                    return False
            else:
                print(f"❌ TikTok API Error: {data.get('message', 'Unknown')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    # Test 2: Get campaigns list
    print("\n🎯 Test 2: Getting campaigns list...")
    
    campaigns_url = "https://business-api.tiktok.com/open_api/v1.3/campaign/get/"
    
    try:
        params = {
            "advertiser_id": advertiser_id,
            "filtering": json.dumps({
                "campaign_statuses": ["ENABLE", "DISABLE", "PAUSED"]
            }),
            "fields": json.dumps([
                "campaign_id", "campaign_name", "operation_status", 
                "objective_type", "budget", "create_time"
            ])
        }
        
        response = requests.get(campaigns_url, headers=headers, params=params)
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("code") == 0:
                campaigns = data.get("data", {}).get("list", [])
                print(f"✅ Found {len(campaigns)} campaigns")
                
                # Show first 3 campaigns
                for i, campaign in enumerate(campaigns[:3], 1):
                    print(f"  {i}. {campaign.get('campaign_name', 'Unknown')} - {campaign.get('operation_status', 'Unknown')}")
                
                if len(campaigns) > 3:
                    print(f"  ... and {len(campaigns) - 3} more campaigns")
                    
                return True
            else:
                print(f"❌ TikTok API Error: {data.get('message', 'Unknown')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TikTok Marketing API Connection Test")
    print("=" * 50)
    
    success = test_tiktok_connection()
    
    if success:
        print(f"\n🎉 TikTok API connection successful!")
        print(f"✅ Ready to integrate TikTok Ads data")
        print(f"\n📝 Next steps:")
        print(f"  1. Create TikTok campaign data table in database")
        print(f"  2. Sync historical TikTok campaign data")
        print(f"  3. Build TikTok dashboard component")
    else:
        print(f"\n❌ TikTok API connection failed")
        print(f"🔍 Check credentials and permissions")
        
    print("\n" + "=" * 50)