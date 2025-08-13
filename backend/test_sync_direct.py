#!/usr/bin/env python3
"""
Test the sync functionality directly
"""

import os
from dotenv import load_dotenv
from app.services.meta_api import MetaAdsService
from datetime import date

def test_sync():
    """Test the sync functionality"""
    load_dotenv()
    
    print("🔄 Testing data sync functionality...")
    
    try:
        # Initialize service
        meta_service = MetaAdsService()
        
        # Test connection first
        print("   🔗 Testing connection...")
        if not meta_service.test_connection():
            print("   ❌ Connection test failed")
            return False
        
        print("   ✅ Connection successful")
        
        # Get month-to-date data (last few days to avoid too much data)
        print("   📊 Getting recent campaign data...")
        start_date = date(2025, 8, 10)  # Just a few days of data
        end_date = date(2025, 8, 11)
        
        insights = meta_service.get_campaign_insights(start_date, end_date)
        print(f"   ✅ Retrieved {len(insights)} insights")
        
        if insights:
            print("   📋 Sample insights:")
            for i, insight in enumerate(insights[:3], 1):
                print(f"      {i}. {insight.campaign_name}: ${insight.spend}")
        
        # Convert to campaign data
        campaign_data = meta_service.convert_to_campaign_data(insights)
        print(f"   ✅ Converted to {len(campaign_data)} campaign records")
        
        if campaign_data:
            print("   📋 Sample campaign data:")
            for i, data in enumerate(campaign_data[:3], 1):
                print(f"      {i}. {data.campaign_name}: ${data.amount_spent_usd} - {data.category}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Sync test failed: {e}")
        return False

if __name__ == "__main__":
    test_sync()