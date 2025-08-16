#!/usr/bin/env python3
"""
Simple Google Ads sync - one month at a time
"""

import os
import sys
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from datetime import date
from dotenv import load_dotenv
from app.services.google_ads_service import GoogleAdsService
from app.services.google_reporting import GoogleReportingService

load_dotenv()

def categorize_campaign(campaign_name):
    """Simple text-based categorization"""
    campaign_lower = campaign_name.lower()
    
    if 'standing' in campaign_lower:
        return 'Standing Mats'
    elif 'playmat' in campaign_lower or 'play mat' in campaign_lower:
        return 'Play Mats'
    elif 'bath' in campaign_lower:
        return 'Bath Mats'
    elif 'tumbling' in campaign_lower:
        return 'Tumbling Mats'
    elif 'play' in campaign_lower and ('furniture' in campaign_lower or 'table' in campaign_lower):
        return 'Play Furniture'
    else:
        return 'Multi Category'

def sync_one_month(year, month):
    """Sync one month of data"""
    print(f'📊 Syncing {year}-{month:02d}...')
    
    try:
        google_ads_service = GoogleAdsService()
        reporting_service = GoogleReportingService()
        
        # Define date range for the month
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        
        # Get insights for this month
        insights = google_ads_service.get_campaign_insights(start_date, end_date)
        
        if not insights:
            print(f'  No data for {year}-{month:02d}')
            return
        
        print(f'  Retrieved {len(insights)} insights')
        
        # Convert and categorize
        campaign_data_list = google_ads_service.convert_to_campaign_data(insights)
        
        for campaign_data in campaign_data_list:
            campaign_data.category = categorize_campaign(campaign_data.campaign_name)
        
        # Store in database
        success = reporting_service.store_campaign_data(campaign_data_list)
        
        if success:
            spend_total = sum(float(c.amount_spent_usd) for c in campaign_data_list)
            print(f'  ✅ Stored {len(campaign_data_list)} records, ${spend_total:,.2f} total spend')
        else:
            print(f'  ❌ Failed to store data')
            
    except Exception as e:
        print(f'  ❌ Error: {e}')

def main():
    """Sync Jan 2024 through Aug 2024"""
    print('🔄 Syncing Google Ads data by month...')
    
    # Test connection first
    google_ads_service = GoogleAdsService()
    if not google_ads_service.test_connection():
        print('❌ Google Ads API connection failed')
        return
    
    print('✅ Connected to Google Ads API')
    
    # Sync each month
    months = [
        (2024, 1), (2024, 2), (2024, 3), (2024, 4),
        (2024, 5), (2024, 6), (2024, 7), (2024, 8)
    ]
    
    for year, month in months:
        sync_one_month(year, month)
    
    print('\n🎯 Sync complete!')

if __name__ == "__main__":
    main()