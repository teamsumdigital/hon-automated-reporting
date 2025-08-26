#!/usr/bin/env python3
"""
Test TikTok Reporting Service directly to see if it has data
"""

import os
import sys
sys.path.append('./backend')

from dotenv import load_dotenv
load_dotenv()

from backend.app.services.tiktok_reporting import TikTokReportingService

def test_direct_service():
    print("🔍 TESTING TIKTOK REPORTING SERVICE DIRECTLY")
    print("=" * 50)
    
    try:
        service = TikTokReportingService()
        
        # Get monthly aggregates (raw method)
        print("📊 GETTING MONTHLY AGGREGATES:")
        monthly_data = service.get_monthly_aggregates()
        print(f"  Monthly data keys: {list(monthly_data.keys())}")
        
        for month, data in monthly_data.items():
            print(f"  {month}: ${data['spend']:,.2f} spend, {data['ads_count']} ads")
        
        # Get summary
        print("\n📋 GETTING SUMMARY:")
        summary = service.get_month_to_date_summary()
        print(f"  Total spend: ${summary.get('total_spend', 0):,.2f}")
        print(f"  Total ads: {summary.get('total_ads', 0)}")
        
        # Get pivot data
        print("\n📅 GETTING PIVOT DATA:")
        pivot_data = service.generate_pivot_table_data()
        print(f"  Pivot data count: {len(pivot_data)}")
        
        for pivot in pivot_data[:5]:  # First 5
            print(f"  {pivot.month}: ${float(pivot.spend):,.2f}")
        
        # Test with current month filter
        print("\n🗓️  TESTING WITH AUGUST 2025 FILTER:")
        from datetime import date
        from backend.app.models.tiktok_campaign_data import TikTokDashboardFilters
        
        filters = TikTokDashboardFilters()
        filters.start_date = date(2025, 8, 1)
        
        filtered_summary = service.get_month_to_date_summary(filters)
        print(f"  Filtered spend: ${filtered_summary.get('total_spend', 0):,.2f}")
        
        filtered_pivot = service.generate_pivot_table_data(filters)
        print(f"  Filtered pivot count: {len(filtered_pivot)}")
        
        for pivot in filtered_pivot:
            print(f"  {pivot.month}: ${float(pivot.spend):,.2f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_service()