#!/usr/bin/env python3
"""
Test pivot table aggregation for July 2025
"""

import os
import sys
from datetime import date

# Add the backend path to import services
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.tiktok_reporting import TikTokReportingService
from backend.app.models.tiktok_campaign_data import TikTokDashboardFilters

def test_pivot_aggregation():
    """Test pivot table generation for July 2025"""
    
    service = TikTokReportingService()

    print('🔍 Testing Pivot Table Generation for July 2025')
    print('=' * 60)

    # Test with no filters (should include all data)
    print('📊 Test 1: No filters (all data)')
    all_pivot = service.generate_pivot_table_data(None)
    july_all = [month for month in all_pivot if month.month == '2025-07']

    if july_all:
        july_data = july_all[0]
        print(f'   July 2025 spend: ${july_data.spend:,.2f}')
        print(f'   July 2025 revenue: ${july_data.revenue:,.2f}')
    else:
        print('   No July 2025 data found')

    # Test with July-specific filters
    print('\n📊 Test 2: July 2025 specific filters')
    july_filters = TikTokDashboardFilters(
        start_date=date(2025, 7, 1),
        end_date=date(2025, 7, 31)
    )
    july_pivot = service.generate_pivot_table_data(july_filters)

    print(f'   Filtered pivot results: {len(july_pivot)} months')
    for month in july_pivot:
        print(f'     {month.month}: ${month.spend:,.2f}')

    # Test individual campaign data for July
    print('\n📊 Test 3: Individual campaigns for July 2025')
    campaigns = service.get_campaign_data(july_filters)
    total_spend = sum(float(c.amount_spent_usd) for c in campaigns)
    print(f'   Individual campaigns: {len(campaigns)}')
    print(f'   Individual total spend: ${total_spend:,.2f}')

    # Check for campaign deduplication issues
    print('\n📊 Test 4: Campaign deduplication check')
    campaign_ids = [c.campaign_id for c in campaigns]
    unique_ids = set(campaign_ids)
    print(f'   Total campaign records: {len(campaign_ids)}')
    print(f'   Unique campaign IDs: {len(unique_ids)}')

    if len(campaign_ids) != len(unique_ids):
        print('   ⚠️  DUPLICATE CAMPAIGNS DETECTED!')
        from collections import Counter
        duplicates = Counter(campaign_ids)
        for campaign_id, count in duplicates.items():
            if count > 1:
                print(f'     Campaign {campaign_id}: {count} records')
    else:
        print('   ✅ No duplicate campaign IDs found')

    print('\n📋 PIVOT AGGREGATION ANALYSIS:')
    if july_all and abs(float(july_all[0].spend) - total_spend) < 0.01:
        print('✅ Pivot aggregation matches individual campaign sum')
    else:
        if july_all:
            diff = float(july_all[0].spend) - total_spend
            print(f'❌ Pivot aggregation differs by ${diff:+,.2f}')
            print(f'   Expected: ${total_spend:,.2f}')
            print(f'   Pivot shows: ${july_all[0].spend:,.2f}')
        else:
            print('❌ No July data in pivot table')

    # Test the actual dashboard API call to see what it returns
    print('\n📊 Test 5: Direct API call simulation')
    try:
        import requests
        api_response = requests.get('http://localhost:8007/api/tiktok-reports/dashboard')
        if api_response.status_code == 200:
            data = api_response.json()
            pivot_data = data.get('pivot_data', [])
            api_july = [month for month in pivot_data if month['month'] == '2025-07']
            
            if api_july:
                api_july_data = api_july[0]
                print(f'   API July 2025 spend: ${api_july_data["spend"]:,.2f}')
                print(f'   API July 2025 revenue: ${api_july_data["revenue"]:,.2f}')
                
                if abs(api_july_data["spend"] - 10385) < 1:
                    print('   🚨 CONFIRMED: API is returning the wrong $10,385 value!')
                elif abs(api_july_data["spend"] - total_spend) < 0.01:
                    print('   ✅ API is returning the correct value')
                else:
                    print(f'   ⚠️  API is returning unexpected value: ${api_july_data["spend"]:,.2f}')
            else:
                print('   ❌ API response contains no July 2025 data')
        else:
            print(f'   ❌ API call failed: {api_response.status_code}')
    except Exception as e:
        print(f'   ❌ API call error: {e}')

if __name__ == "__main__":
    test_pivot_aggregation()