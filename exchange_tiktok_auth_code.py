#!/usr/bin/env python3
"""
Exchange TikTok authorization code for access token
Run this script to get your TikTok access token from the auth code
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def exchange_auth_code_for_token():
    """
    Exchange TikTok authorization code for access token
    """
    # Your TikTok credentials
    app_id = "7538619599563161616"
    app_secret = "51c35c7f4f089c33d793f709abc88bba293f6c83"
    auth_code = "4d8059943bd4210881936b3b32e455782fe5cb9a"
    
    print("🔐 Exchanging TikTok auth code for access token...")
    print(f"📱 App ID: {app_id}")
    print(f"🔑 Auth Code: {auth_code[:20]}...")
    
    # TikTok OAuth token endpoint
    token_url = "https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/"
    
    # Request payload
    payload = {
        "app_id": app_id,
        "secret": app_secret,
        "auth_code": auth_code,
        "grant_type": "authorization_code"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("📡 Making request to TikTok OAuth endpoint...")
        response = requests.post(token_url, json=payload, headers=headers)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Response Data: {json.dumps(data, indent=2)}")
            
            if data.get("code") == 0:  # TikTok success code
                token_data = data.get("data", {})
                access_token = token_data.get("access_token")
                refresh_token = token_data.get("refresh_token")
                expires_in = token_data.get("expires_in")
                advertiser_ids = token_data.get("advertiser_ids", [])
                
                print("\n🎉 SUCCESS! Access token obtained:")
                print(f"✅ Access Token: {access_token}")
                print(f"🔄 Refresh Token: {refresh_token}")
                print(f"⏰ Expires In: {expires_in} seconds")
                print(f"📢 Advertiser IDs: {advertiser_ids}")
                
                print("\n📝 Add these to your .env file:")
                print(f"TIKTOK_APP_ID={app_id}")
                print(f"TIKTOK_APP_SECRET={app_secret}")
                print(f"TIKTOK_ACCESS_TOKEN={access_token}")
                
                # Use the provided advertiser ID or first from response
                advertiser_id = "6961828676572839938"  # Your provided ID
                if advertiser_ids and advertiser_id not in [str(aid) for aid in advertiser_ids]:
                    print(f"⚠️  Warning: Provided advertiser ID {advertiser_id} not in authorized list: {advertiser_ids}")
                    if advertiser_ids:
                        advertiser_id = str(advertiser_ids[0])
                        print(f"🔄 Using first available advertiser ID: {advertiser_id}")
                
                print(f"TIKTOK_ADVERTISER_ID={advertiser_id}")
                print(f"TIKTOK_SANDBOX_MODE=false")
                
                if refresh_token:
                    print(f"TIKTOK_REFRESH_TOKEN={refresh_token}")
                
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": expires_in,
                    "advertiser_ids": advertiser_ids,
                    "advertiser_id": advertiser_id
                }
            else:
                error_msg = data.get("message", "Unknown error")
                print(f"❌ TikTok API Error: {error_msg}")
                print(f"📋 Full response: {json.dumps(data, indent=2)}")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📋 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return None

def test_access_token(access_token: str, advertiser_id: str):
    """
    Test the obtained access token by fetching advertiser info
    """
    print(f"\n🧪 Testing access token...")
    
    test_url = "https://business-api.tiktok.com/open_api/v1.3/advertiser/info/"
    
    headers = {
        "Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    params = {
        "advertiser_ids": [advertiser_id]
    }
    
    try:
        response = requests.get(test_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                advertiser_info = data.get("data", {}).get("list", [])
                if advertiser_info:
                    info = advertiser_info[0]
                    print(f"✅ Access token works!")
                    print(f"📢 Advertiser: {info.get('name', 'Unknown')}")
                    print(f"📊 Status: {info.get('status', 'Unknown')}")
                    print(f"💰 Currency: {info.get('currency', 'Unknown')}")
                    return True
                else:
                    print("❌ No advertiser info returned")
                    return False
            else:
                print(f"❌ TikTok API Error: {data.get('message', 'Unknown')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TikTok Marketing API - Auth Code Exchange")
    print("=" * 50)
    
    # Exchange auth code for access token
    token_info = exchange_auth_code_for_token()
    
    if token_info:
        # Test the access token
        test_result = test_access_token(
            token_info["access_token"], 
            token_info["advertiser_id"]
        )
        
        if test_result:
            print(f"\n🎯 TikTok API setup complete!")
            print(f"✅ Ready to sync TikTok campaign data")
        else:
            print(f"\n⚠️  Access token obtained but test failed")
            print(f"🔍 Check your advertiser ID and permissions")
    else:
        print(f"\n❌ Failed to obtain access token")
        print(f"🔍 Check your app credentials and auth code")
        
    print("\n" + "=" * 50)