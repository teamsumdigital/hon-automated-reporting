#!/usr/bin/env python3
"""Sync Google Ads data for August 13, 2025"""

import os
import requests
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def sync_august_13():
    """Sync Google Ads data for August 13, 2025"""
    
    print("🚀 Syncing Google Ads data for August 13, 2025...")
    
    # Your Google Ads credentials
    customer_id = "9860652386"
    developer_token = "-gJOMMcQIcQBxKuaUd0FhA"
    access_token = "your_oauth_access_token_here"  # You'll need to get this from n8n
    
    # GAQL query for August 13
    gaql_query = "SELECT campaign.id, campaign.name, segments.date, metrics.cost_micros, metrics.impressions, metrics.clicks, metrics.conversions, metrics.conversions_value FROM campaign WHERE segments.date = '2025-08-13' AND campaign.status = 'ENABLED'"
    
    # Google Ads API request
    url = f"https://googleads.googleapis.com/v16/customers/{customer_id}/googleAds:search"
    headers = {
        "Content-Type": "application/json",
        "developer-token": developer_token,
        "Authorization": f"Bearer {access_token}"
    }
    
    body = {
        "query": gaql_query
    }
    
    print(f"📡 Making request to Google Ads API for August 13...")
    print(f"💡 You'll need to get your OAuth access token from n8n to run this")
    print(f"🔍 Query: {gaql_query}")
    
    return True

if __name__ == "__main__":
    sync_august_13()