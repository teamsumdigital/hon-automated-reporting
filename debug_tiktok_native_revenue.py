#!/usr/bin/env python3
"""
Debug TikTok native revenue fields to get the exact revenue TikTok uses for ROAS calculation
"""

import os
import sys
from datetime import date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.tiktok_ads_service import TikTokAdsService

def debug_tiktok_revenue_fields():
    """Debug TikTok revenue fields to match platform exactly"""
    print("🔍 Debugging TikTok Revenue Fields")
    print("=" * 50)
    
    try:
        service = TikTokAdsService()
        
        # Test July 2025 to match your screenshot
        start_date = date(2025, 7, 1)
        end_date = date(2025, 7, 31)
        
        print(f"📅 Testing July 2025 data...")
        
        # Try different revenue metrics
        endpoint = f"{service.base_url}/report/integrated/get/"
        
        # Extended metrics including all possible revenue fields
        test_metrics = [
            "spend",
            "impressions", 
            "clicks",
            "ctr",
            "cpc",
            "cpm",
            "cost_per_conversion",
            "conversion_rate",
            
            # Payment Complete metrics
            "complete_payment_roas",
            "complete_payment",
            "complete_payment_value",  # This might be the native revenue!
            
            # Other potential revenue fields
            "purchase_roas",
            "purchase_value",
            "total_purchase_value",
            "conversion_value",
            "total_conversion_value",
            "revenue",
            "total_revenue"
        ]
        
        request_data = {
            "advertiser_id": service.advertiser_id,
            "report_type": "BASIC",
            "data_level": "AUCTION_CAMPAIGN",
            "dimensions": ["campaign_id"],
            "metrics": test_metrics,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "page": 1,
            "page_size": 1000
        }
        
        # Convert to query parameters for GET request
        params = {}
        for key, value in request_data.items():
            if isinstance(value, list):
                params[key] = __import__('json').dumps(value)
            else:
                params[key] = value
        
        print(f"📊 Testing {len(test_metrics)} metrics...")
        
        response = service.session.get(endpoint, params=params)
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        data = response.json()
        
        if data.get("code") != 0:
            print(f"❌ TikTok API Error: {data.get('message')}")
            
            # Check which metrics failed
            if "invalid metric fields" in data.get('message', '').lower():
                print("📋 Invalid metrics detected. Let's test core metrics only...")
                
                # Test with core metrics only
                core_metrics = [
                    "spend", "impressions", "clicks", "complete_payment_roas", 
                    "complete_payment", "complete_payment_value"
                ]
                
                request_data["metrics"] = core_metrics
                params["metrics"] = __import__('json').dumps(core_metrics)
                
                response = service.session.get(endpoint, params=params)
                data = response.json()
        
        if data.get("code") == 0 and "data" in data and "list" in data["data"]:
            campaigns = data["data"]["list"]
            
            print(f"✅ Retrieved {len(campaigns)} campaigns")
            
            # Show metrics for campaigns with spend
            active_campaigns = [c for c in campaigns if float(c.get("metrics", {}).get("spend", 0)) > 0]
            
            print(f"📊 Active campaigns with spend: {len(active_campaigns)}")
            print()
            
            total_spend = 0
            total_complete_payment = 0
            total_complete_payment_value = 0
            calculated_total_revenue = 0
            
            for campaign in active_campaigns[:3]:  # Show first 3
                metrics = campaign.get("metrics", {})
                campaign_id = campaign.get("dimensions", {}).get("campaign_id")
                
                spend = float(metrics.get("spend", 0))
                complete_payment = int(float(metrics.get("complete_payment", 0)))
                complete_payment_roas = float(metrics.get("complete_payment_roas", 0))
                complete_payment_value = float(metrics.get("complete_payment_value", 0))
                
                # Calculate what revenue would be with our method
                calculated_revenue = complete_payment_roas * spend
                
                print(f"🎯 Campaign {campaign_id}:")
                print(f"   💰 Spend: ${spend:,.2f}")
                print(f"   🛒 Complete Payments: {complete_payment}")
                print(f"   📈 Complete Payment ROAS: {complete_payment_roas:.2f}")
                print(f"   💵 Complete Payment Value (TikTok): ${complete_payment_value:,.2f}")
                print(f"   🔢 Calculated Revenue (ROAS×Spend): ${calculated_revenue:,.2f}")
                print(f"   ⚠️ Difference: ${abs(complete_payment_value - calculated_revenue):,.2f}")
                print()
                
                total_spend += spend
                total_complete_payment += complete_payment
                total_complete_payment_value += complete_payment_value
                calculated_total_revenue += calculated_revenue
            
            print("📊 JULY 2025 TOTALS:")
            print(f"   💰 Total Spend: ${total_spend:,.2f}")
            print(f"   🛒 Total Complete Payments: {total_complete_payment}")
            print(f"   💵 TikTok Native Revenue: ${total_complete_payment_value:,.2f}")
            print(f"   🔢 My Calculated Revenue: ${calculated_total_revenue:,.2f}")
            
            # Calculate what ROAS should be with TikTok's native revenue
            if total_spend > 0:
                native_roas = total_complete_payment_value / total_spend
                calculated_roas = calculated_total_revenue / total_spend
                
                print(f"   📈 ROAS with TikTok Revenue: {native_roas:.2f}")
                print(f"   📈 ROAS with Calculated Revenue: {calculated_roas:.2f}")
                print()
                
                print("🎯 SOLUTION:")
                if abs(native_roas - 7.8) < 0.1:  # Close to your platform ROAS of 7.8
                    print("   ✅ Use complete_payment_value instead of calculating revenue!")
                    print("   ✅ Use complete_payment_roas directly from TikTok")
                else:
                    print("   ⚠️ Need to investigate further...")
            
            # Show all available metrics for reference
            if campaigns:
                print("\n📋 All available metrics in response:")
                sample_metrics = campaigns[0].get("metrics", {})
                for metric, value in sample_metrics.items():
                    print(f"   • {metric}: {value}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_tiktok_revenue_fields()