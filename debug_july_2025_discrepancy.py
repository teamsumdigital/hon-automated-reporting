#!/usr/bin/env python3
"""
Debug the discrepancy between July 2025 TikTok data sources
"""

import os
import sys
from datetime import date

# Add the backend path to import services
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.tiktok_reporting import TikTokReportingService
from backend.app.models.tiktok_campaign_data import TikTokDashboardFilters

def debug_july_2025_data():
    """Debug July 2025 TikTok data discrepancy"""
    
    print("🔍 Debugging July 2025 TikTok Data Discrepancy")
    print("=" * 60)
    
    try:
        service = TikTokReportingService()
        
        # Test 1: Direct campaign data query (what I found earlier)
        print("📊 Test 1: Direct campaign data query")
        filters = TikTokDashboardFilters(
            start_date=date(2025, 7, 1),
            end_date=date(2025, 7, 31)
        )
        
        campaigns = service.get_campaign_data(filters)
        direct_spend = sum(float(campaign.amount_spent_usd) for campaign in campaigns)
        direct_revenue = sum(float(campaign.purchases_conversion_value) for campaign in campaigns)
        
        print(f"   Campaigns found: {len(campaigns)}")
        print(f"   Direct spend: ${direct_spend:,.2f}")
        print(f"   Direct revenue: ${direct_revenue:,.2f}")
        
        # Test 2: Pivot table data (what the dashboard uses)
        print("\n📊 Test 2: Pivot table data query")
        pivot_data = service.generate_pivot_table_data(filters)
        july_pivot = [month for month in pivot_data if month.month == '2025-07']
        
        if july_pivot:
            pivot_month = july_pivot[0]
            print(f"   Pivot spend: ${pivot_month.spend:,.2f}")
            print(f"   Pivot revenue: ${pivot_month.revenue:,.2f}")
            print(f"   Pivot purchases: {pivot_month.purchases:,}")
        else:
            print("   No July 2025 data in pivot results")
        
        # Test 3: Check what table the campaign data is coming from
        print("\n📊 Test 3: Database table inspection")
        
        # Direct database query to see what's in tiktok_campaign_data
        result = service.supabase.table("tiktok_campaign_data")\
            .select("*")\
            .gte("reporting_starts", "2025-07-01")\
            .lte("reporting_ends", "2025-07-31")\
            .execute()
        
        db_campaigns = result.data
        db_spend = sum(float(row['amount_spent_usd']) for row in db_campaigns)
        
        print(f"   Raw DB campaigns: {len(db_campaigns)}")
        print(f"   Raw DB spend: ${db_spend:,.2f}")
        
        # Test 4: Check for data table confusion
        print("\n📊 Test 4: Checking for data source confusion")
        
        # Check if there's data in the newer tiktok_ad_data table
        try:
            ad_result = service.supabase.table("tiktok_ad_data")\
                .select("*")\
                .gte("reporting_starts", "2025-07-01")\
                .lte("reporting_ends", "2025-07-31")\
                .execute()
            
            ad_data = ad_result.data
            ad_spend = sum(float(row['amount_spent_usd']) for row in ad_data)
            
            print(f"   tiktok_ad_data records: {len(ad_data)}")
            print(f"   tiktok_ad_data spend: ${ad_spend:,.2f}")
            
        except Exception as e:
            print(f"   tiktok_ad_data table error: {e}")
        
        # Test 5: Show sample records from both sources
        print("\n📊 Test 5: Sample data comparison")
        
        print("   Sample campaign data records:")
        for i, campaign in enumerate(campaigns[:3]):
            print(f"     {i+1}. {campaign.campaign_name[:50]}...")
            print(f"        Spend: ${campaign.amount_spent_usd}")
            print(f"        Date: {campaign.reporting_starts} to {campaign.reporting_ends}")
        
        # Test 6: Month-to-date summary (what KPI cards might use)
        print("\n📊 Test 6: Month-to-date summary")
        
        # Create filters for July 2025 specifically
        july_filters = TikTokDashboardFilters(
            start_date=date(2025, 7, 1),
            end_date=date(2025, 7, 31)
        )
        
        # Get summary for July (this is what the KPI cards would show)
        summary = service.get_month_to_date_summary(july_filters)
        
        print(f"   Summary spend: ${summary.get('total_spend', 0):,.2f}")
        print(f"   Summary revenue: ${summary.get('total_revenue', 0):,.2f}")
        print(f"   Summary campaigns: {summary.get('campaigns_count', 0)}")
        
        # Analysis
        print("\n📋 ANALYSIS:")
        print("=" * 40)
        
        if abs(direct_spend - db_spend) < 0.01:
            print("✅ Direct campaign query matches raw DB data")
        else:
            print(f"❌ Direct campaign query differs from raw DB: ${direct_spend - db_spend:+,.2f}")
        
        if july_pivot and abs(direct_spend - float(july_pivot[0].spend)) < 0.01:
            print("✅ Pivot data matches direct campaign data")
        else:
            if july_pivot:
                diff = direct_spend - float(july_pivot[0].spend)
                print(f"❌ Pivot data differs from direct: ${diff:+,.2f}")
            else:
                print("❌ No pivot data found for July 2025")
        
        summary_spend = summary.get('total_spend', 0)
        if abs(direct_spend - summary_spend) < 0.01:
            print("✅ Summary data matches direct campaign data")
        else:
            print(f"❌ Summary data differs from direct: ${direct_spend - summary_spend:+,.2f}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_july_2025_data()