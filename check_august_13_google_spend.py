#!/usr/bin/env python3
"""Check Google Ads spend for August 13, 2025"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def check_august_13_spend():
    """Check Google Ads spend for August 13, 2025"""
    
    print("🔍 Checking Google Ads spend for August 13, 2025...")
    
    # Connect to Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        # Query Google campaign data for August 13, 2025
        result = supabase.table("google_campaign_data")\
            .select("campaign_id, campaign_name, campaign_type, amount_spent_usd, website_purchases, purchases_conversion_value, category")\
            .eq("reporting_starts", "2025-08-13")\
            .order("amount_spent_usd", desc=True)\
            .execute()
        
        campaigns = result.data
        
        if not campaigns:
            print("❌ No Google Ads data found for August 13, 2025")
            print("💡 Data might not be synced yet or no campaigns ran that day")
            return False
        
        print(f"✅ Found {len(campaigns)} Google Ads campaigns for August 13, 2025\n")
        
        # Calculate totals
        total_spend = sum(c.get("amount_spent_usd", 0) for c in campaigns)
        total_conversions = sum(c.get("website_purchases", 0) for c in campaigns)
        total_revenue = sum(c.get("purchases_conversion_value", 0) for c in campaigns)
        
        print("📊 AUGUST 13, 2025 - GOOGLE ADS SUMMARY")
        print("=" * 50)
        print(f"💰 Total Spend: ${total_spend:,.2f}")
        print(f"🛒 Total Conversions: {total_conversions}")
        print(f"💵 Total Revenue: ${total_revenue:,.2f}")
        print(f"📈 ROAS: {total_revenue/total_spend:.2f}" if total_spend > 0 else "📈 ROAS: 0.00")
        print()
        
        # Campaign breakdown
        print("📋 CAMPAIGN BREAKDOWN:")
        print("-" * 80)
        print(f"{'Campaign Name':<40} {'Type':<10} {'Spend':<12} {'Conv':<6} {'Revenue':<12}")
        print("-" * 80)
        
        for campaign in campaigns:
            name = campaign.get("campaign_name", "Unknown")[:38]
            camp_type = campaign.get("campaign_type", "N/A")[:8]
            spend = campaign.get("amount_spent_usd", 0)
            conversions = campaign.get("website_purchases", 0)
            revenue = campaign.get("purchases_conversion_value", 0)
            
            print(f"{name:<40} {camp_type:<10} ${spend:<11.2f} {conversions:<6} ${revenue:<11.2f}")
        
        # Category breakdown
        category_totals = {}
        for campaign in campaigns:
            category = campaign.get("category", "Uncategorized")
            spend = campaign.get("amount_spent_usd", 0)
            conversions = campaign.get("website_purchases", 0)
            revenue = campaign.get("purchases_conversion_value", 0)
            
            if category not in category_totals:
                category_totals[category] = {"spend": 0, "conversions": 0, "revenue": 0}
            
            category_totals[category]["spend"] += spend
            category_totals[category]["conversions"] += conversions
            category_totals[category]["revenue"] += revenue
        
        print("\n🏷️ CATEGORY BREAKDOWN:")
        print("-" * 50)
        print(f"{'Category':<20} {'Spend':<12} {'Conv':<6} {'Revenue':<12}")
        print("-" * 50)
        
        for category, totals in sorted(category_totals.items(), key=lambda x: x[1]["spend"], reverse=True):
            spend = totals["spend"]
            conversions = totals["conversions"]
            revenue = totals["revenue"]
            print(f"{category:<20} ${spend:<11.2f} {conversions:<6} ${revenue:<11.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error querying database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Google Ads Spend Check - August 13, 2025")
    print("=" * 50)
    
    success = check_august_13_spend()
    
    if not success:
        print("\n💡 To get August 13 data:")
        print("1. Run your n8n workflow manually for August 13")
        print("2. Or modify the GAQL query to pull historical data")
        print("3. Check if campaigns were active on August 13")
    
    print("\n" + "=" * 50)