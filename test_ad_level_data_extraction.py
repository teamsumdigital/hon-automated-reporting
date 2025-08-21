#!/usr/bin/env python3
"""
Test script for Meta Ads ad-level data extraction with weekly segmentation
"""

import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv

# Add the backend app to Python path
sys.path.append('./backend')

from backend.app.services.meta_ad_level_service import MetaAdLevelService

# Load environment variables
load_dotenv('./backend/.env')

def test_connection():
    """Test Meta Ads API connection for ad-level data"""
    print("🧪 Testing Meta Ads API connection for ad-level data...")
    
    try:
        service = MetaAdLevelService()
        if service.test_connection():
            print("✅ Connection successful!")
            return True
        else:
            print("❌ Connection failed!")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_14_day_extraction():
    """Test extracting last 14 days of ad-level data with weekly segments"""
    print("\n📊 Testing 14-day ad-level data extraction with weekly segments...")
    
    try:
        service = MetaAdLevelService()
        
        # Calculate date range
        today = date.today()
        end_date = today - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=13)  # 14 days before yesterday
        
        print(f"📅 Date range: {start_date} to {end_date}")
        
        # Fetch ad-level data
        ad_data = service.get_last_14_days_ad_data()
        
        if not ad_data:
            print("⚠️  No ad data found for the last 14 days")
            return False
        
        print(f"📈 Retrieved {len(ad_data)} ad records")
        
        # Analyze the data
        weeks = set()
        categories = set()
        total_spend = 0
        total_purchases = 0
        total_revenue = 0
        
        for ad in ad_data[:5]:  # Show first 5 ads as examples
            weeks.add(ad['week_number'])
            categories.add(ad['category'])
            total_spend += ad['amount_spent_usd']
            total_purchases += ad['purchases']
            total_revenue += ad['purchases_conversion_value']
            
            print(f"\n📱 Ad Example:")
            print(f"   Ad ID: {ad['ad_id']}")
            print(f"   Ad Name: {ad['ad_name'][:50]}...")
            print(f"   Campaign: {ad['campaign_name'][:50]}...")
            print(f"   Week: {ad['week_number']}")
            print(f"   Category: {ad['category']}")
            print(f"   Product: {ad['product']}")
            print(f"   Color: {ad['color']}")
            print(f"   Content Type: {ad['content_type']}")
            print(f"   Spend: ${ad['amount_spent_usd']:.2f}")
            print(f"   Purchases: {ad['purchases']}")
            print(f"   Revenue: ${ad['purchases_conversion_value']:.2f}")
            print(f"   Impressions: {ad['impressions']:,}")
            print(f"   Link Clicks: {ad['link_clicks']}")
            print(f"   Launch Date: {ad['launch_date']}")
            print(f"   Days Live: {ad['days_live']}")
        
        print(f"\n📊 Summary for first 5 ads:")
        print(f"   Unique Weeks: {sorted(list(weeks))}")
        print(f"   Categories Found: {sorted(list(categories))}")
        print(f"   Total Spend: ${total_spend:.2f}")
        print(f"   Total Purchases: {total_purchases}")
        print(f"   Total Revenue: ${total_revenue:.2f}")
        print(f"   ROAS: {total_revenue/total_spend:.2f}x" if total_spend > 0 else "   ROAS: N/A")
        
        # Group by week for weekly breakdown
        weekly_breakdown = {}
        for ad in ad_data:
            week = ad['week_number']
            if week not in weekly_breakdown:
                weekly_breakdown[week] = {
                    'ads_count': 0,
                    'spend': 0,
                    'purchases': 0,
                    'revenue': 0
                }
            weekly_breakdown[week]['ads_count'] += 1
            weekly_breakdown[week]['spend'] += ad['amount_spent_usd']
            weekly_breakdown[week]['purchases'] += ad['purchases']
            weekly_breakdown[week]['revenue'] += ad['purchases_conversion_value']
        
        print(f"\n📅 Weekly Breakdown (All {len(ad_data)} ads):")
        for week, data in weekly_breakdown.items():
            roas = data['revenue'] / data['spend'] if data['spend'] > 0 else 0
            print(f"   {week}:")
            print(f"      Ads: {data['ads_count']}")
            print(f"      Spend: ${data['spend']:.2f}")
            print(f"      Purchases: {data['purchases']}")
            print(f"      Revenue: ${data['revenue']:.2f}")
            print(f"      ROAS: {roas:.2f}x")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during 14-day extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_categorization():
    """Test campaign categorization logic"""
    print("\n🏷️  Testing campaign categorization...")
    
    service = MetaAdLevelService()
    
    test_campaigns = [
        "House of Noa | Play Mat Collection | Video",
        "HON Standing Desk Mat Campaign",
        "Bath Mat Summer Sale",
        "Tumbling Mat for Kids",
        "Play Furniture Collection",
        "Multi Category Bundle",
        "Random Campaign Name"
    ]
    
    for campaign in test_campaigns:
        category = service.categorize_campaign(campaign)
        print(f"   '{campaign}' → {category}")

def test_product_extraction():
    """Test product info extraction from ad names"""
    print("\n🎯 Testing product information extraction...")
    
    service = MetaAdLevelService()
    
    test_ad_names = [
        "Play Mat - Black - Video Creative",
        "Standing Mat Blue Square Image",
        "Bath Mat Grey Vertical Story",
        "Tumbling Mat Pink Horizontal Video",
        "Unknown Product Test Ad"
    ]
    
    for ad_name in test_ad_names:
        product_info = service.extract_product_info(ad_name)
        print(f"   '{ad_name}':")
        print(f"      Product: {product_info['product']}")
        print(f"      Color: {product_info['color']}")
        print(f"      Content Type: {product_info['content_type']}")
        print(f"      Format: {product_info['format']}")

def main():
    """Run all tests"""
    print("🚀 Meta Ads Ad-Level Data Extraction Test")
    print("=" * 60)
    
    # Test 1: Connection
    if not test_connection():
        print("\n❌ Connection test failed. Please check your Meta Ads API credentials.")
        return
    
    # Test 2: Categorization
    test_categorization()
    
    # Test 3: Product extraction
    test_product_extraction()
    
    # Test 4: 14-day data extraction
    if test_14_day_extraction():
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Next steps:")
        print("1. Run the database migration: python run_meta_ad_data_migration.py")
        print("2. Test the API endpoint: POST /api/meta-ad-reports/sync-14-days")
        print("3. View the weekly summary: GET /api/meta-ad-reports/weekly-summary")
    else:
        print("\n❌ 14-day extraction test failed.")

if __name__ == "__main__":
    main()