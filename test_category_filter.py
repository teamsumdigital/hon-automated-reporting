#!/usr/bin/env python3
"""
Test Google Ads category filtering directly
"""

import os
import sys
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from dotenv import load_dotenv
from app.services.google_reporting import GoogleReportingService
from app.models.google_campaign_data import GoogleDashboardFilters

load_dotenv()

def test_category_filtering():
    print('🔍 Testing Google Ads category filtering...')
    
    service = GoogleReportingService()
    
    # Test without filters
    print('\n1. Testing without filters:')
    campaigns = service.get_campaign_data()
    print(f'   Total campaigns: {len(campaigns)}')
    if campaigns:
        total_spend = sum(float(c.amount_spent_usd) for c in campaigns)
        print(f'   Total spend: ${total_spend:,.2f}')
        categories = set(c.category for c in campaigns)
        print(f'   Categories: {sorted(categories)}')
    
    # Test with Bath Mats filter
    print('\n2. Testing with Bath Mats filter:')
    filters = GoogleDashboardFilters()
    filters.categories = ['Bath Mats']
    
    campaigns = service.get_campaign_data(filters)
    print(f'   Bath Mats campaigns: {len(campaigns)}')
    if campaigns:
        total_spend = sum(float(c.amount_spent_usd) for c in campaigns)
        print(f'   Bath Mats spend: ${total_spend:,.2f}')
        for campaign in campaigns[:3]:
            print(f'     {campaign.campaign_name}: ${campaign.amount_spent_usd}')
    
    # Test pivot data generation
    print('\n3. Testing pivot data generation with Bath Mats filter:')
    pivot_data = service.generate_pivot_table_data(filters)
    print(f'   Pivot data entries: {len(pivot_data)}')
    if pivot_data:
        total_spend = sum(float(p.spend) for p in pivot_data)
        print(f'   Pivot total spend: ${total_spend:,.2f}')
        for p in pivot_data[:3]:
            print(f'     {p.month}: ${p.spend}')

if __name__ == "__main__":
    test_category_filtering()