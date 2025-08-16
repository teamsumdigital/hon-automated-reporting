#!/usr/bin/env python3
"""
Test Google Ads API query with a small date range
"""

import os
from datetime import date, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

print("🔍 Testing Google Ads API Query")
print("=" * 40)

try:
    from app.services.google_ads_service import GoogleAdsService
    
    # Test with just today's date
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    print(f"📅 Testing date range: {yesterday} to {today}")
    
    service = GoogleAdsService()
    print("✅ Google Ads service initialized")
    
    # Test connection first
    connection_test = service.test_connection()
    if not connection_test:
        print("❌ Connection test failed")
        exit(1)
    
    print("✅ Connection test passed")
    
    # Test query with small date range
    print(f"\n🔍 Testing campaign insights query...")
    insights = service.get_campaign_insights(yesterday, today)
    
    print(f"✅ Query successful! Retrieved {len(insights)} insights")
    
    if insights:
        print(f"\n📊 Sample insight:")
        insight = insights[0]
        print(f"   Campaign ID: {insight.campaign_id}")
        print(f"   Campaign Name: {insight.campaign_name}")
        print(f"   Cost: ${insight.cost}")
        print(f"   Clicks: {insight.clicks}")
        print(f"   Conversions: {insight.conversions}")
    else:
        print("⚠️ No insights found for this date range")
        print("   This might be normal if there's no recent campaign activity")
        
        # Try with a longer date range
        print(f"\n🔍 Trying longer date range (last 7 days)...")
        week_ago = today - timedelta(days=7)
        insights = service.get_campaign_insights(week_ago, today)
        
        print(f"✅ 7-day query successful! Retrieved {len(insights)} insights")
        
        if insights:
            print(f"\n📊 Sample insight from 7-day range:")
            insight = insights[0]
            print(f"   Campaign ID: {insight.campaign_id}")
            print(f"   Campaign Name: {insight.campaign_name}")
            print(f"   Cost: ${insight.cost}")
            print(f"   Clicks: {insight.clicks}")
            print(f"   Conversions: {insight.conversions}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 40)
print("🏁 Query test complete!")