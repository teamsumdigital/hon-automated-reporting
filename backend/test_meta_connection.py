#!/usr/bin/env python3
"""
Test Meta Ads API connection and pull sample data
"""

import os
from dotenv import load_dotenv
from datetime import date, timedelta

def test_meta_connection():
    """Test Meta Ads API connection and data retrieval"""
    load_dotenv()
    
    print("🔍 Testing Meta Ads API connection...")
    
    try:
        from facebook_business.api import FacebookAdsApi
        from facebook_business.adobjects.adaccount import AdAccount
        
        app_id = os.getenv("META_APP_ID")
        app_secret = os.getenv("META_APP_SECRET")
        access_token = os.getenv("META_ACCESS_TOKEN")
        account_id = os.getenv("META_ACCOUNT_ID")
        
        print(f"   📋 Account ID: {account_id}")
        
        # Initialize API
        FacebookAdsApi.init(access_token=access_token)
        ad_account = AdAccount(f"act_{account_id}")
        
        # Test basic account access
        print("   🔗 Testing account access...")
        account_info = ad_account.api_get(fields=['name', 'account_status', 'currency'])
        print(f"   ✅ Account: {account_info.get('name', 'Unknown')}")
        print(f"   ✅ Status: {account_info.get('account_status', 'Unknown')}")
        print(f"   ✅ Currency: {account_info.get('currency', 'Unknown')}")
        
        # Test campaign access
        print("   🎯 Testing campaign access...")
        campaigns = ad_account.get_campaigns(fields=['name', 'status'], params={'limit': 5})
        campaign_list = list(campaigns)
        print(f"   ✅ Found {len(campaign_list)} campaigns (showing first 5)")
        
        for i, campaign in enumerate(campaign_list[:3], 1):
            print(f"      {i}. {campaign.get('name', 'Unknown')} - {campaign.get('status', 'Unknown')}")
        
        # Test insights access (last 7 days)
        print("   📊 Testing insights access...")
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=6)
        
        insights = ad_account.get_insights(
            fields=['campaign_name', 'spend', 'impressions', 'clicks'],
            params={
                'time_range': {
                    'since': start_date.strftime('%Y-%m-%d'),
                    'until': end_date.strftime('%Y-%m-%d')
                },
                'level': 'campaign',
                'limit': 3
            }
        )
        
        insights_list = list(insights)
        print(f"   ✅ Retrieved {len(insights_list)} campaign insights (last 7 days)")
        
        total_spend = sum(float(insight.get('spend', 0)) for insight in insights_list)
        total_impressions = sum(int(insight.get('impressions', 0)) for insight in insights_list)
        total_clicks = sum(int(insight.get('clicks', 0)) for insight in insights_list)
        
        print(f"   📈 Total Spend: ${total_spend:.2f}")
        print(f"   👁️  Total Impressions: {total_impressions:,}")
        print(f"   👆 Total Clicks: {total_clicks:,}")
        
        if insights_list:
            print("   📋 Sample campaigns:")
            for insight in insights_list[:3]:
                name = insight.get('campaign_name', 'Unknown')
                spend = float(insight.get('spend', 0))
                print(f"      • {name}: ${spend:.2f}")
        
        print("\n🎉 Meta Ads API connection successful!")
        print("   ✅ Ready for automated reporting")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Meta Ads API test failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   • Check that access token has 'ads_read' permission")
        print("   • Verify account ID is correct")
        print("   • Ensure token hasn't expired")
        return False

if __name__ == "__main__":
    test_meta_connection()