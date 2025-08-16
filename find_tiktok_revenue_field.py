#!/usr/bin/env python3
"""
Find the correct TikTok revenue field that matches platform data
"""

import os
import sys
from datetime import date
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.tiktok_ads_service import TikTokAdsService

def find_revenue_field():
    """Find the correct revenue field TikTok uses"""
    print("🔍 Finding TikTok Revenue Field")
    print("=" * 40)
    
    try:
        service = TikTokAdsService()
        
        # Test July 2025 data
        start_date = date(2025, 7, 1)
        end_date = date(2025, 7, 31)
        
        print(f"📅 Testing July 2025...")
        
        # Test minimal metrics first
        endpoint = f"{service.base_url}/report/integrated/get/"
        
        request_data = {
            "advertiser_id": service.advertiser_id,
            "report_type": "BASIC",
            "data_level": "AUCTION_CAMPAIGN",
            "dimensions": ["campaign_id"],
            "metrics": [
                "spend",
                "complete_payment_roas",
                "complete_payment"
            ],
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "page": 1,
            "page_size": 1000
        }
        
        # Convert to query parameters
        params = {}
        for key, value in request_data.items():
            if isinstance(value, list):
                params[key] = json.dumps(value)
            else:
                params[key] = value
        
        response = service.session.get(endpoint, params=params)
        data = response.json()
        
        if data.get("code") == 0 and "data" in data:
            campaigns = data["data"]["list"]
            
            print(f"✅ Retrieved {len(campaigns)} campaigns")
            
            # Calculate totals to match your platform data
            total_spend = 0
            total_complete_payment = 0
            total_calculated_revenue = 0
            
            for campaign in campaigns:
                metrics = campaign.get("metrics", {})
                
                spend = float(metrics.get("spend", 0))
                complete_payment = int(float(metrics.get("complete_payment", 0)))
                complete_payment_roas = float(metrics.get("complete_payment_roas", 0))
                
                # This is what I'm currently calculating
                calculated_revenue = complete_payment_roas * spend
                
                total_spend += spend
                total_complete_payment += complete_payment
                total_calculated_revenue += calculated_revenue
            
            print(f"\n📊 JULY 2025 TOTALS:")
            print(f"   💰 Spend: ${total_spend:,.2f}")
            print(f"   🛒 Complete Payments: {total_complete_payment}")
            print(f"   📈 Calculated Revenue (ROAS×Spend): ${total_calculated_revenue:,.2f}")
            
            if total_spend > 0:
                calculated_roas = total_calculated_revenue / total_spend
                calculated_cpa = total_spend / total_complete_payment if total_complete_payment > 0 else 0
                
                print(f"   📈 Calculated ROAS: {calculated_roas:.2f}")
                print(f"   🎯 Calculated CPA: ${calculated_cpa:.2f}")
            
            print(f"\n🎯 YOUR PLATFORM SHOWS:")
            print(f"   💰 Spend: $30,452 (matches: {abs(total_spend - 30452) < 100})")
            print(f"   🛒 Conversions: 900 (my calc: {total_complete_payment})")
            print(f"   📈 ROAS: 7.8 (my calc: {calculated_roas:.1f})")
            print(f"   🎯 CPA: $33.84 (my calc: ${calculated_cpa:.2f})")
            
            print(f"\n🔍 ANALYSIS:")
            print(f"   Spend matches: ✅")
            print(f"   Purchases close: {'✅' if abs(total_complete_payment - 900) < 100 else '❌'}")
            print(f"   ROAS close: {'✅' if abs(calculated_roas - 7.8) < 0.5 else '❌'}")
            
            # The issue might be that we need to check if there are other conversion events
            # or if complete_payment_roas includes something different
            
            # Let me also check what the weighted average ROAS is
            weighted_roas_sum = 0
            total_spend_for_roas = 0
            
            for campaign in campaigns:
                metrics = campaign.get("metrics", {})
                spend = float(metrics.get("spend", 0))
                roas = float(metrics.get("complete_payment_roas", 0))
                
                if spend > 0:
                    weighted_roas_sum += roas * spend
                    total_spend_for_roas += spend
            
            if total_spend_for_roas > 0:
                weighted_avg_roas = weighted_roas_sum / total_spend_for_roas
                print(f"\n🧮 WEIGHTED AVERAGE ROAS: {weighted_avg_roas:.2f}")
                print(f"   vs Platform ROAS: 7.8")
                print(f"   Difference: {abs(weighted_avg_roas - 7.8):.1f}")
            
            print(f"\n💡 CONCLUSION:")
            if abs(calculated_roas - 7.8) < 0.3:
                print(f"   ✅ My calculation is close - might be rounding differences")
                print(f"   📊 Use complete_payment_roas directly from TikTok")
                print(f"   💵 Calculate revenue as: ROAS × Spend")
            else:
                print(f"   ⚠️ Significant difference - need to investigate conversion events")
                print(f"   🔍 TikTok might be using different conversion events for ROAS")
        
        else:
            print(f"❌ API Error: {data}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    find_revenue_field()