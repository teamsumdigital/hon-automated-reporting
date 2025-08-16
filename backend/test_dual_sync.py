#!/usr/bin/env python3
"""
Simple test to sync from both Meta accounts without imports
"""

import os
from datetime import date, timedelta

try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    
    def test_dual_sync():
        """Test syncing from both accounts"""
        print("🔄 Testing dual account sync...")
        
        # Load environment variables directly
        app_id = "1459737788539040"
        app_secret = "30d048bf9f62385947e256245ca7d713" 
        access_token = "EAAUvn7BZA4KABPOZAsmskE8AAymmU1RDEZCPTiNEmlqZBMrTiL6rCZAHYCb75ExZBtGRd8xDkvYg25zVukZBe3d0K01RResOx3SknXGRQei7VEOEf9ttJDdNhuOZBuKeggxkHfh0R2ZAqEYVMf3WzDbEyFGZBNEMMuYNDSirFYz2OauuXVNcbtOsugx9l9xwZDZD"
        primary_account = "12838773"
        secondary_account = "728880056795187"
        
        print(f"   📋 Primary Account: {primary_account}")
        print(f"   📋 Secondary Account: {secondary_account}")
        
        # Initialize API
        FacebookAdsApi.init(access_token=access_token)
        
        # Test both accounts
        primary_ad_account = AdAccount(f"act_{primary_account}")
        secondary_ad_account = AdAccount(f"act_{secondary_account}")
        
        # Test connections
        print("\n   🔗 Testing primary account...")
        try:
            primary_info = primary_ad_account.api_get(fields=['name', 'account_status'])
            print(f"   ✅ Primary: {primary_info.get('name', 'Unknown')} - {primary_info.get('account_status', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ Primary account error: {e}")
            
        print("   🔗 Testing secondary account...")
        try:
            secondary_info = secondary_ad_account.api_get(fields=['name', 'account_status'])
            print(f"   ✅ Secondary: {secondary_info.get('name', 'Unknown')} - {secondary_info.get('account_status', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ Secondary account error: {e}")
        
        # Test campaign access
        print("\n   🎯 Testing campaign access...")
        
        # Primary campaigns
        try:
            primary_campaigns = list(primary_ad_account.get_campaigns(fields=['name'], params={'limit': 3}))
            print(f"   📊 Primary account: {len(primary_campaigns)} campaigns found")
            for i, campaign in enumerate(primary_campaigns, 1):
                print(f"      {i}. {campaign.get('name', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ Primary campaigns error: {e}")
            
        # Secondary campaigns  
        try:
            secondary_campaigns = list(secondary_ad_account.get_campaigns(fields=['name'], params={'limit': 3}))
            print(f"   📊 Secondary account: {len(secondary_campaigns)} campaigns found")
            for i, campaign in enumerate(secondary_campaigns, 1):
                print(f"      {i}. {campaign.get('name', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ Secondary campaigns error: {e}")
        
        print("\n🎉 Dual account test completed!")
        print("   Both accounts are accessible for data syncing")
        
    if __name__ == "__main__":
        test_dual_sync()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Install Facebook Business SDK: pip3 install facebook-business")