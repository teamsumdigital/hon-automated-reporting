#!/usr/bin/env python3
"""
Test Google Ads sync with a very small date range
"""

import os
from datetime import date, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

print("🔍 Testing Google Ads Sync - Small Date Range")
print("=" * 50)

try:
    import sys
    sys.path.append('.')
    
    from app.services.google_ads_service import GoogleAdsService
    
    # Test with yesterday only
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    print(f"📅 Testing date: {yesterday}")
    
    service = GoogleAdsService()
    print("✅ Google Ads service initialized")
    
    # Test insights for yesterday
    print(f"\n🔍 Getting campaign insights for {yesterday}...")
    insights = service.get_campaign_insights(yesterday, yesterday)
    
    print(f"✅ Query successful! Retrieved {len(insights)} insights")
    
    if insights:
        print(f"\n📊 Campaign insights found:")
        for i, insight in enumerate(insights[:3]):  # Show first 3
            print(f"   {i+1}. {insight.campaign_name} (ID: {insight.campaign_id})")
            cost_dollars = float(insight.cost_micros) / 1_000_000
            print(f"      Cost: ${cost_dollars:.2f}")
            print(f"      Clicks: {insight.clicks}")
            print(f"      Conversions: {insight.conversions}")
            
        # Test conversion to campaign data
        print(f"\n🔄 Converting to campaign data format...")
        campaign_data_list = service.convert_to_campaign_data(insights)
        print(f"✅ Converted {len(campaign_data_list)} campaigns")
        
        if campaign_data_list:
            print(f"\n📊 Sample campaign data:")
            data = campaign_data_list[0]
            print(f"   Campaign: {data.campaign_name}")
            print(f"   Amount Spent: ${data.amount_spent_usd}")
            print(f"   ROAS: {data.roas}")
            print(f"   CPC: ${data.cpc}")
            print(f"   Category: {data.category}")
            
    else:
        print("⚠️ No campaign data found for yesterday")
        print("   This might be normal if there was no activity yesterday")
        
        # Try last 7 days
        week_ago = today - timedelta(days=7)
        print(f"\n🔍 Trying last 7 days ({week_ago} to {today})...")
        insights = service.get_campaign_insights(week_ago, today)
        print(f"✅ 7-day query: Retrieved {len(insights)} insights")
        
        if insights:
            print(f"📊 Found campaign activity in the last 7 days!")
            insight = insights[0]
            print(f"   Sample: {insight.campaign_name}")
            cost_dollars = float(insight.cost_micros) / 1_000_000
            print(f"   Cost: ${cost_dollars:.2f}")
            print(f"   Period: {insight.date_start} to {insight.date_stop}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🏁 Small sync test complete!")