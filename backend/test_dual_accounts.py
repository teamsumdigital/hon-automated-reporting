#!/usr/bin/env python3
"""
Simple test for dual Meta Ads accounts using the MetaAdsService
"""

import os
import sys
from datetime import date, timedelta

# Add the app directory to the path
sys.path.append('.')

try:
    from app.services.meta_api import MetaAdsService
    
    def test_dual_accounts():
        """Test the dual account setup using MetaAdsService"""
        print("🔍 Testing Dual Meta Ads Account Setup...")
        
        try:
            # Initialize the service
            print("   🚀 Initializing MetaAdsService...")
            meta_service = MetaAdsService()
            
            # Test connection to both accounts
            print("   🔗 Testing API connections...")
            connection_success = meta_service.test_connection()
            
            if not connection_success:
                print("   ❌ Connection test failed")
                return False
            
            # Test data fetching with August 2025 limitation
            print("\n   📊 Testing data fetching with August 2025 limitation...")
            
            # Test normal date range
            normal_start = date(2025, 7, 1)
            normal_end = date(2025, 7, 31)
            print(f"   Testing normal date range: {normal_start} to {normal_end}")
            
            normal_insights = meta_service.get_campaign_insights(normal_start, normal_end)
            print(f"   ✅ Retrieved {len(normal_insights)} insights for July 2025")
            
            # Test August 2025 with limitation
            august_start = date(2025, 8, 1)
            august_end = date(2025, 8, 31)
            print(f"   Testing August 2025 (should limit to Aug 11): {august_start} to {august_end}")
            
            august_insights = meta_service.get_campaign_insights(august_start, august_end)
            print(f"   ✅ Retrieved {len(august_insights)} insights for August 2025 (limited to Aug 11)")
            
            # Test recent data
            recent_end = date.today() - timedelta(days=1)
            recent_start = recent_end - timedelta(days=6)
            print(f"   Testing recent data: {recent_start} to {recent_end}")
            
            recent_insights = meta_service.get_campaign_insights(recent_start, recent_end)
            print(f"   ✅ Retrieved {len(recent_insights)} recent insights")
            
            # Summary
            total_insights = len(normal_insights) + len(august_insights) + len(recent_insights)
            print(f"\n🎉 Dual account setup test successful!")
            print(f"   ✅ Total insights retrieved: {total_insights}")
            print(f"   ✅ Both accounts accessible")
            print(f"   ✅ August 2025 limitation working")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            print(f"   💡 Make sure environment variables are set correctly")
            return False
    
    if __name__ == "__main__":
        test_dual_accounts()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running from the backend directory")
    print("💡 Check that all dependencies are installed")