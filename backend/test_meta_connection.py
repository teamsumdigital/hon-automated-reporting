#!/usr/bin/env python3
"""
Test Meta Ads API connection and pull sample data
"""

import os
from dotenv import load_dotenv
from datetime import date, timedelta

def test_meta_connection():
    """Test Meta Ads API connection and data retrieval for dual accounts"""
    load_dotenv()
    
    print("🔍 Testing Meta Ads API connection...")
    
    try:
        from facebook_business.api import FacebookAdsApi
        from facebook_business.adobjects.adaccount import AdAccount
        
        app_id = os.getenv("META_APP_ID")
        app_secret = os.getenv("META_APP_SECRET")
        access_token = os.getenv("META_ACCESS_TOKEN")
        account_id = os.getenv("META_ACCOUNT_ID")
        secondary_account_id = os.getenv("META_ACCOUNT_ID_SECONDARY")
        
        print(f"   📋 Primary Account ID: {account_id}")
        if secondary_account_id:
            print(f"   📋 Secondary Account ID: {secondary_account_id}")
        
        # Initialize API
        FacebookAdsApi.init(access_token=access_token)
        ad_account = AdAccount(f"act_{account_id}")
        
        # Initialize secondary account if configured
        secondary_ad_account = None
        if secondary_account_id:
            secondary_ad_account = AdAccount(f"act_{secondary_account_id}")
        
        # Test basic account access for both accounts
        def test_account(account, account_name, account_id):
            print(f"   🔗 Testing {account_name} account access...")
            account_info = account.api_get(fields=['name', 'account_status', 'currency'])
            print(f"   ✅ {account_name} Account: {account_info.get('name', 'Unknown')} (ID: {account_id})")
            print(f"   ✅ Status: {account_info.get('account_status', 'Unknown')}")
            print(f"   ✅ Currency: {account_info.get('currency', 'Unknown')}")
            
            # Test campaign access
            print(f"   🎯 Testing {account_name} campaign access...")
            campaigns = account.get_campaigns(fields=['name', 'status'], params={'limit': 5})
            campaign_list = list(campaigns)
            print(f"   ✅ Found {len(campaign_list)} campaigns in {account_name} account")
            
            for i, campaign in enumerate(campaign_list[:3], 1):
                print(f"      {i}. {campaign.get('name', 'Unknown')} - {campaign.get('status', 'Unknown')}")
            
            return len(campaign_list)
        
        # Test primary account
        primary_campaigns = test_account(ad_account, "Primary", account_id)
        
        # Test secondary account if configured
        secondary_campaigns = 0
        if secondary_ad_account:
            print()  # Add spacing
            secondary_campaigns = test_account(secondary_ad_account, "Secondary", secondary_account_id)
        
        total_campaigns = primary_campaigns + secondary_campaigns
        print(f"\n   📊 Total campaigns across all accounts: {total_campaigns}")
        
        # Test insights access (last 7 days) for both accounts
        def test_insights(account, account_name):
            print(f"   📊 Testing {account_name} insights access...")
            end_date = date.today() - timedelta(days=1)
            start_date = end_date - timedelta(days=6)
            
            insights = account.get_insights(
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
            print(f"   ✅ Retrieved {len(insights_list)} {account_name} campaign insights (last 7 days)")
            
            account_spend = sum(float(insight.get('spend', 0)) for insight in insights_list)
            account_impressions = sum(int(insight.get('impressions', 0)) for insight in insights_list)
            account_clicks = sum(int(insight.get('clicks', 0)) for insight in insights_list)
            
            print(f"   📈 {account_name} Spend: ${account_spend:.2f}")
            print(f"   👁️  {account_name} Impressions: {account_impressions:,}")
            print(f"   👆 {account_name} Clicks: {account_clicks:,}")
            
            if insights_list:
                print(f"   📋 Sample {account_name} campaigns:")
                for insight in insights_list[:2]:
                    name = insight.get('campaign_name', 'Unknown')
                    spend = float(insight.get('spend', 0))
                    print(f"      • {name}: ${spend:.2f}")
            
            return account_spend, account_impressions, account_clicks
        
        # Test insights for primary account
        primary_spend, primary_impressions, primary_clicks = test_insights(ad_account, "Primary")
        
        # Test insights for secondary account if configured
        secondary_spend, secondary_impressions, secondary_clicks = 0, 0, 0
        if secondary_ad_account:
            print()  # Add spacing
            secondary_spend, secondary_impressions, secondary_clicks = test_insights(secondary_ad_account, "Secondary")
        
        # Show combined totals
        total_spend = primary_spend + secondary_spend
        total_impressions = primary_impressions + secondary_impressions
        total_clicks = primary_clicks + secondary_clicks
        
        print(f"\n   🎯 COMBINED TOTALS (Last 7 Days):")
        print(f"   📈 Total Spend: ${total_spend:.2f}")
        print(f"   👁️  Total Impressions: {total_impressions:,}")
        print(f"   👆 Total Clicks: {total_clicks:,}")
        
        if secondary_ad_account:
            print(f"   📊 Dual account setup successfully tested!")
        
        print("\n🎉 Meta Ads API connection successful!")
        if secondary_ad_account:
            print("   ✅ Dual account setup ready for automated reporting")
        else:
            print("   ✅ Single account ready for automated reporting")
        print("   🚨 August 2025 data will be limited to August 11 for testing")
        
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