#!/usr/bin/env python3
"""
Quick check to get real Meta ad IDs for verification
No heavy processing - just connection test and raw ad IDs
"""

import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv
from loguru import logger
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

# Load environment variables
load_dotenv()

def quick_real_ad_ids_check():
    """
    Quick check to get some real ad IDs without heavy processing
    """
    try:
        # Initialize Meta Ads API
        app_id = os.getenv("META_APP_ID")
        app_secret = os.getenv("META_APP_SECRET")
        access_token = os.getenv("META_ACCESS_TOKEN")
        account_id = os.getenv("META_ACCOUNT_ID")
        
        if not all([app_id, app_secret, access_token, account_id]):
            raise ValueError("Missing Meta Ads API credentials")
        
        FacebookAdsApi.init(access_token=access_token)
        ad_account = AdAccount(f"act_{account_id}")
        
        logger.info(f"🔌 Testing connection to Meta Ads account: {account_id}")
        
        # Test connection
        account_info = ad_account.api_get(fields=['name', 'account_status'])
        logger.info(f"✅ Connected to: {account_info.get('name', 'Unknown')} (Status: {account_info.get('account_status', 'Unknown')})")
        
        # Get yesterday's date for recent ads
        yesterday = date.today() - timedelta(days=1)
        
        # Get a small sample of ads with minimal fields
        logger.info(f"📋 Fetching sample ads from {yesterday} (limited to 10 ads)...")
        
        params = {
            'time_range': {
                'since': yesterday.strftime('%Y-%m-%d'),
                'until': yesterday.strftime('%Y-%m-%d')
            },
            'fields': [
                'ad_id',
                'ad_name'
            ],
            'level': 'ad',
            'limit': 10  # Just get 10 ads for verification
        }
        
        insights = ad_account.get_insights(params=params)
        
        print("\n" + "=" * 80)
        print("🎯 REAL META ADS ID VERIFICATION")
        print("=" * 80)
        print(f"📅 Sample from: {yesterday}")
        print(f"🏢 Account: {account_info.get('name', 'Unknown')} (ID: {account_id})")
        print("\n🔍 REAL AD IDs FOR VERIFICATION:")
        
        real_ads_found = []
        for i, insight in enumerate(insights, 1):
            ad_id = insight.get('ad_id', 'Unknown')
            ad_name = insight.get('ad_name', 'Unknown')
            
            real_ads_found.append({
                'ad_id': ad_id,
                'ad_name': ad_name
            })
            
            print(f"   {i}. Ad ID: {ad_id}")
            print(f"      Name: {ad_name[:70]}...")
            print("")
        
        if real_ads_found:
            print(f"✅ Found {len(real_ads_found)} real ads from yesterday")
            print("🔍 You can search for these ad IDs in Meta Ads Manager to verify they exist")
        else:
            print("⚠️  No ads found for yesterday - try a different date range")
        
        print("=" * 80)
        
        return real_ads_found
        
    except Exception as e:
        logger.error(f"❌ Error getting real ad IDs: {e}")
        print(f"\n❌ Failed to get real ad IDs: {e}")
        return []

if __name__ == "__main__":
    quick_real_ad_ids_check()