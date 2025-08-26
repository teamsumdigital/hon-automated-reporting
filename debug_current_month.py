#!/usr/bin/env python3
"""
Debug current month filtering for KPI summary
"""

import os
import sys
sys.path.append('./backend')

from dotenv import load_dotenv
load_dotenv()

from datetime import date
from backend.app.services.tiktok_reporting import TikTokReportingService
from backend.app.models.tiktok_campaign_data import TikTokDashboardFilters

def debug_current_month():
    print("🔍 DEBUGGING CURRENT MONTH KPI FILTERING")
    print("=" * 50)
    
    try:
        service = TikTokReportingService()
        
        current_date = date.today()
        print(f"📅 Current date: {current_date}")
        current_month_start = current_date.replace(day=1)
        print(f"📅 Current month start: {current_month_start}")
        
        # Test summary with current month filter
        summary_filters = TikTokDashboardFilters()
        summary_filters.start_date = current_month_start
        
        print(f"\n📊 TESTING SUMMARY WITH FILTER {current_month_start}:")
        summary = service.get_month_to_date_summary(summary_filters)
        print(f"  Spend: ${summary.get('total_spend', 0):,.2f}")
        print(f"  Revenue: ${summary.get('total_revenue', 0):,.2f}")
        print(f"  Campaigns: {summary.get('campaigns_count', 0)}")
        
        # Test with August 2025 specifically
        august_filters = TikTokDashboardFilters()
        august_filters.start_date = date(2025, 8, 1)
        
        print(f"\n📊 TESTING SUMMARY WITH AUGUST 2025 FILTER:")
        august_summary = service.get_month_to_date_summary(august_filters)
        print(f"  Spend: ${august_summary.get('total_spend', 0):,.2f}")
        print(f"  Revenue: ${august_summary.get('total_revenue', 0):,.2f}")
        print(f"  Campaigns: {august_summary.get('campaigns_count', 0)}")
        
        # Test without any filter
        print(f"\n📊 TESTING SUMMARY WITHOUT FILTER:")
        no_filter_summary = service.get_month_to_date_summary(None)
        print(f"  Spend: ${no_filter_summary.get('total_spend', 0):,.2f}")
        print(f"  Revenue: ${no_filter_summary.get('total_revenue', 0):,.2f}")
        print(f"  Campaigns: {no_filter_summary.get('campaigns_count', 0)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_current_month()