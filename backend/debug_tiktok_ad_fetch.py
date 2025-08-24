#!/usr/bin/env python3
"""
Debug TikTok ad fetching
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
advertiser_id = os.getenv("TIKTOK_ADVERTISER_ID")
base_url = "https://business-api.tiktok.com/open_api/v1.3"
headers = {
    "Access-Token": access_token,
    "Content-Type": "application/json"
}

# Get a few ad IDs from the database
from supabase import create_client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Get some ad IDs
result = supabase.table("tiktok_ad_data")\
    .select("ad_id")\
    .like("ad_name", "Ad %")\
    .limit(5)\
    .execute()

ad_ids = [record['ad_id'] for record in result.data]
print(f"Testing with ad IDs: {ad_ids}")

# Try fetching these ads
endpoint = f"{base_url}/ad/get/"
params = {
    "advertiser_id": advertiser_id,
    "ad_ids": json.dumps(ad_ids),
    "fields": json.dumps([
        "ad_id", "ad_name", "campaign_id", "campaign_name"
    ])
}

print(f"\nRequest params: {json.dumps(params, indent=2)}")

response = requests.get(endpoint, headers=headers, params=params)
print(f"\nResponse status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")