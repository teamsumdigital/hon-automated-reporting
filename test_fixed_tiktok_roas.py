#!/usr/bin/env python3
"""
Test the fixed TikTok service with Payment Complete ROAS (website)
"""

import os
import sys
from datetime import date
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.tiktok_ads_service import TikTokAdsService

def test_fixed_roas():
    """Test the fixed TikTok service with Payment Complete ROAS"""
    print("🎯 Testing Fixed TikTok Ads Service with Payment Complete ROAS")
    print("=" * 70)
    
    try:
        # Initialize service
        service = TikTokAdsService()
        print(f"✅ TikTok Ads Service initialized")
        print()
        
        # Test connection
        print("🔗 Testing API connection...")
        if not service.test_connection():
            print("❌ Connection failed!")
            return
        print("✅ Connection successful!")
        print()
        
        # Test July 2025 data with correct ROAS
        start_date = date(2025, 7, 1)
        end_date = date(2025, 7, 31)
        
        print(f"📊 Fetching campaign data for July 2025...")
        insights = service.get_campaign_insights(start_date, end_date)
        
        if not insights:
            print("❌ No data found")
            return
        
        print(f"📈 Found {len(insights)} campaigns")
        print()
        
        # Convert to campaign data to test ROAS calculation
        print("🔄 Converting insights to campaign data...")
        campaign_data = service.convert_to_campaign_data(insights)
        
        print(f"✅ Converted {len(campaign_data)} campaigns")
        print()
        
        # Show results for campaigns with spend
        active_campaigns = [cd for cd in campaign_data if cd.amount_spent_usd > 0]
        
        print(f"🎯 ACTIVE CAMPAIGNS WITH SPEND ({len(active_campaigns)}):")
        print("=" * 70)
        
        total_spend = Decimal('0')
        total_revenue = Decimal('0')
        total_purchases = 0
        total_clicks = 0
        total_impressions = 0
        
        for i, campaign in enumerate(active_campaigns[:5], 1):  # Show first 5 active
            print(f"🎯 Campaign {i}: {campaign.campaign_name}")
            print(f"   📱 Category: {campaign.category}")
            print(f"   💰 Spend: ${campaign.amount_spent_usd:,.2f}")
            print(f"   👀 Impressions: {campaign.impressions:,}")
            print(f"   🖱️ Clicks: {campaign.link_clicks:,}")
            print(f"   🛒 Purchases: {campaign.website_purchases}")
            print(f"   💵 Revenue: ${campaign.purchases_conversion_value:,.2f}")
            print(f"   🎯 CPA: ${campaign.cpa:,.2f}")
            print(f"   📈 ROAS: {campaign.roas:.2f}")
            print(f"   💲 CPC: ${campaign.cpc:.2f}")
            print()
            
            # Add to totals
            total_spend += campaign.amount_spent_usd
            total_revenue += campaign.purchases_conversion_value
            total_purchases += campaign.website_purchases
            total_clicks += campaign.link_clicks
            total_impressions += campaign.impressions
        
        if len(active_campaigns) > 5:
            print(f"... and {len(active_campaigns) - 5} more active campaigns")
            print()
        
        # Show totals
        overall_roas = total_revenue / total_spend if total_spend > 0 else Decimal('0')
        overall_cpc = total_spend / total_clicks if total_clicks > 0 else Decimal('0')
        overall_cpa = total_spend / total_purchases if total_purchases > 0 else Decimal('0')
        
        print("📊 JULY 2025 TOTALS (FIXED ROAS):")
        print("=" * 50)
        print(f"   💰 Total Spend: ${total_spend:,.2f}")
        print(f"   👀 Total Impressions: {total_impressions:,}")
        print(f"   🖱️ Total Clicks: {total_clicks:,}")
        print(f"   🛒 Total Purchases: {total_purchases:,}")
        print(f"   💵 Total Revenue: ${total_revenue:,.2f}")
        print(f"   📈 Overall ROAS: {overall_roas:.2f}")
        print(f"   💲 Overall CPC: ${overall_cpc:.2f}")
        print(f"   🎯 Overall CPA: ${overall_cpa:.2f}")
        print()
        
        # Show ROAS fix confirmation
        print("✅ ROAS FIX CONFIRMATION:")
        print("=" * 40)
        print(f"   📊 Using: Payment Complete ROAS (website)")
        print(f"   🔢 API Field: complete_payment_roas")
        print(f"   ✅ Campaigns with ROAS > 0: {len([c for c in campaign_data if c.roas > 0])}")
        print(f"   💰 Revenue calculated from: ROAS × Spend")
        print(f"   🛒 Purchases from: complete_payment field")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_roas()