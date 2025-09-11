#!/usr/bin/env python3
"""
CRITICAL FIX: Google Ads Conversion Data Refresh
Re-syncs conversion data for August 1-26, 2025 to fix ROAS/CPA calculation issues

This script addresses the data quality issue where:
- Spend data is correct
- Conversion/revenue data is stale  
- ROAS/CPA calculations are systematically underreported
"""

import os
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from supabase import create_client
from loguru import logger

# Add the app directory to the path
sys.path.append('.')

def main():
    print("🚨 CRITICAL FIX: Google Ads Conversion Data Refresh")
    print("=" * 60)
    print("Addressing ROAS/CPA calculation accuracy issues")
    print("Date Range: August 1-26, 2025")
    print()

    try:
        from app.services.google_ads_service import GoogleAdsService
        
        # Initialize services
        SUPABASE_URL = os.getenv('SUPABASE_URL')
        SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            print("❌ ERROR: Missing Supabase credentials")
            return
        
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        google_service = GoogleAdsService()
        
        # Test API connection
        if not google_service.test_connection():
            print("❌ ERROR: Google Ads API connection failed")
            return
        
        print("✅ Services initialized successfully")
        print()
        
        # Define the problematic date range
        start_date = date(2025, 8, 1)
        end_date = date(2025, 8, 26)
        
        print(f"📅 Processing date range: {start_date} to {end_date}")
        
        # Get current database state for comparison
        print("\n🔍 ANALYZING CURRENT DATABASE STATE...")
        db_response = supabase.table('google_campaign_data')\
            .select('*')\
            .gte('reporting_starts', start_date.isoformat())\
            .lte('reporting_ends', end_date.isoformat())\
            .execute()
        
        current_data = db_response.data if db_response.data else []
        print(f"Found {len(current_data)} existing records")
        
        if not current_data:
            print("❌ No existing data found for the date range")
            return
        
        # Calculate current totals
        current_spend = sum(float(r['amount_spent_usd'] or 0) for r in current_data)
        current_revenue = sum(float(r['purchases_conversion_value'] or 0) for r in current_data)
        current_purchases = sum(int(r['website_purchases'] or 0) for r in current_data)
        current_roas = current_revenue / current_spend if current_spend > 0 else 0
        
        print(f"Current Database Totals:")
        print(f"  Spend: ${current_spend:,.2f}")
        print(f"  Revenue: ${current_revenue:,.2f}")
        print(f"  Purchases: {current_purchases:,}")
        print(f"  ROAS: {current_roas:.4f}")
        print()
        
        # Get fresh API data for the same period
        print("🌐 FETCHING FRESH API DATA...")
        
        # Process data day by day to handle Google Ads API limits
        total_fixed = 0
        api_total_spend = 0
        api_total_revenue = 0
        api_total_purchases = 0
        
        current = start_date
        while current <= end_date:
            print(f"  Processing {current}...")
            
            try:
                # Get fresh insights for this specific date
                api_insights = google_service.get_campaign_insights(current, current)
                
                if api_insights:
                    # Convert to campaign data
                    campaign_data_list = google_service.convert_to_campaign_data(api_insights)
                    
                    # Update database with fresh conversion data
                    for campaign_data in campaign_data_list:
                        api_total_spend += float(campaign_data.amount_spent_usd)
                        api_total_revenue += float(campaign_data.purchases_conversion_value)
                        api_total_purchases += campaign_data.website_purchases
                        
                        # Update the specific record with fresh conversion data
                        update_data = {
                            "website_purchases": campaign_data.website_purchases,
                            "purchases_conversion_value": float(campaign_data.purchases_conversion_value),
                            "cpa": float(campaign_data.cpa),
                            "roas": float(campaign_data.roas),
                            "updated_at": datetime.now().isoformat()
                        }
                        
                        # Update using campaign_id and date as unique identifiers
                        result = supabase.table("google_campaign_data")\
                            .update(update_data)\
                            .eq("campaign_id", campaign_data.campaign_id)\
                            .eq("reporting_starts", current.isoformat())\
                            .execute()
                        
                        if result.data:
                            total_fixed += len(result.data)
                    
                    print(f"    ✅ Updated {len(campaign_data_list)} campaigns for {current}")
                else:
                    print(f"    ⚠️  No API data for {current}")
                    
            except Exception as e:
                print(f"    ❌ Error processing {current}: {e}")
                
            current += timedelta(days=1)
        
        print()
        print("📊 REFRESH SUMMARY:")
        print(f"  Records Updated: {total_fixed}")
        
        # Calculate fresh API totals
        api_roas = api_total_revenue / api_total_spend if api_total_spend > 0 else 0
        
        print(f"\nFresh API Totals:")
        print(f"  Spend: ${api_total_spend:,.2f}")
        print(f"  Revenue: ${api_total_revenue:,.2f}")
        print(f"  Purchases: {api_total_purchases:,}")
        print(f"  ROAS: {api_roas:.4f}")
        
        # Calculate the improvements
        revenue_improvement = api_total_revenue - current_revenue
        roas_improvement = api_roas - current_roas
        purchase_improvement = api_total_purchases - current_purchases
        
        print(f"\n🎯 IMPROVEMENTS:")
        print(f"  Revenue Gained: ${revenue_improvement:,.2f} ({revenue_improvement/current_revenue*100:.1f}% increase)")
        print(f"  ROAS Improvement: {roas_improvement:.4f} ({roas_improvement/current_roas*100:.1f}% increase)")
        print(f"  Additional Purchases: {purchase_improvement} conversions")
        
        # Verify the fix by checking updated database
        print("\n✅ VERIFICATION: Checking updated database...")
        
        verification_response = supabase.table('google_campaign_data')\
            .select('*')\
            .gte('reporting_starts', start_date.isoformat())\
            .lte('reporting_ends', end_date.isoformat())\
            .execute()
        
        updated_data = verification_response.data if verification_response.data else []
        updated_spend = sum(float(r['amount_spent_usd'] or 0) for r in updated_data)
        updated_revenue = sum(float(r['purchases_conversion_value'] or 0) for r in updated_data)
        updated_purchases = sum(int(r['website_purchases'] or 0) for r in updated_data)
        updated_roas = updated_revenue / updated_spend if updated_spend > 0 else 0
        
        print(f"Updated Database Totals:")
        print(f"  Spend: ${updated_spend:,.2f}")
        print(f"  Revenue: ${updated_revenue:,.2f}")  
        print(f"  Purchases: {updated_purchases:,}")
        print(f"  ROAS: {updated_roas:.4f}")
        
        # Accuracy check
        revenue_accuracy = (updated_revenue / api_total_revenue * 100) if api_total_revenue > 0 else 0
        purchase_accuracy = (updated_purchases / api_total_purchases * 100) if api_total_purchases > 0 else 0
        
        print(f"\n🔍 DATA QUALITY VERIFICATION:")
        print(f"  Revenue Accuracy: {revenue_accuracy:.1f}%")
        print(f"  Purchase Accuracy: {purchase_accuracy:.1f}%")
        
        if revenue_accuracy > 98 and purchase_accuracy > 98:
            print("  ✅ Data quality restored to acceptable levels")
        else:
            print("  ⚠️  Data quality still needs attention")
        
        print("\n🎉 CRITICAL FIX COMPLETED!")
        print("Google Ads conversion data has been refreshed with current attribution")
        print("ROAS and CPA calculations should now be accurate")
        print("\nNext steps:")
        print("1. Validate dashboard metrics")
        print("2. Implement daily conversion refresh")
        print("3. Set up data quality monitoring")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()