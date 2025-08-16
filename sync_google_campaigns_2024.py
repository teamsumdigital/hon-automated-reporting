#!/usr/bin/env python3
"""
Sync Google Ads campaigns from January 2024 to August 12, 2024
Using Google Ads API with text-based categorization
"""

import os
import sys
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from datetime import date, datetime
from dotenv import load_dotenv
from app.services.google_ads_service import GoogleAdsService
from app.services.google_reporting import GoogleReportingService

load_dotenv()

def categorize_campaign(campaign_name):
    """
    Categorize campaign based on text matching
    """
    campaign_lower = campaign_name.lower()
    
    if 'standing' in campaign_lower:
        return 'Standing Mats'
    elif 'play' in campaign_lower and 'mat' in campaign_lower:
        return 'Play Mats'
    elif 'bath' in campaign_lower:
        return 'Bath Mats'
    elif 'tumbling' in campaign_lower:
        return 'Tumbling Mats'
    elif 'play' in campaign_lower and ('furniture' in campaign_lower or 'table' in campaign_lower):
        return 'Play Furniture'
    elif 'high chair' in campaign_lower:
        return 'High Chair Mats'
    else:
        return 'Multi Category'

def sync_google_campaigns():
    """Sync Google Ads campaigns for Jan 2024 - Aug 12, 2024"""
    print('🔄 Syncing Google Ads campaigns from January 2024 to August 12, 2024...')
    
    try:
        # Initialize services
        google_ads_service = GoogleAdsService()
        reporting_service = GoogleReportingService()
        
        # Test connection first
        print('🔍 Testing Google Ads API connection...')
        if not google_ads_service.test_connection():
            print('❌ Google Ads API connection failed')
            return
        
        print('✅ Google Ads API connection successful')
        
        # Define date range
        start_date = date(2024, 1, 1)
        end_date = date(2024, 8, 12)
        
        print(f'📊 Fetching campaign data from {start_date} to {end_date}...')
        
        # Get campaigns insights
        insights = google_ads_service.get_campaign_insights(start_date, end_date)
        
        if not insights:
            print('❌ No campaign insights returned from Google Ads API')
            return
        
        print(f'📈 Retrieved {len(insights)} campaign insights')
        
        # Convert insights to campaign data
        campaign_data_list = google_ads_service.convert_to_campaign_data(insights)
        
        # Apply text-based categorization
        for campaign_data in campaign_data_list:
            category = categorize_campaign(campaign_data.campaign_name)
            campaign_data.category = category
            
            print(f'✅ Processed: {campaign_data.campaign_name} -> {category} (${campaign_data.amount_spent_usd})')
        
        print(f'\n💾 Storing {len(campaign_data_list)} campaigns in database...')
        
        # Store in database
        success = reporting_service.store_campaign_data(campaign_data_list)
        
        if success:
            print('✅ Successfully stored all campaign data')
            
            # Show summary by category
            print('\n📊 Campaign summary by category:')
            category_summary = {}
            
            for campaign in campaign_data_list:
                category = campaign.category
                if category not in category_summary:
                    category_summary[category] = {
                        'count': 0,
                        'spend': 0,
                        'revenue': 0
                    }
                
                category_summary[category]['count'] += 1
                category_summary[category]['spend'] += float(campaign.amount_spent_usd)
                category_summary[category]['revenue'] += float(campaign.purchases_conversion_value)
            
            for category, data in sorted(category_summary.items()):
                print(f'  {category}: {data["count"]} campaigns, ${data["spend"]:,.2f} spend, ${data["revenue"]:,.2f} revenue')
            
            total_spend = sum(data['spend'] for data in category_summary.values())
            total_revenue = sum(data['revenue'] for data in category_summary.values())
            
            print(f'\n🎯 Total: ${total_spend:,.2f} spend, ${total_revenue:,.2f} revenue')
            
        else:
            print('❌ Failed to store campaign data')
            
    except Exception as e:
        print(f'❌ Error syncing Google Ads campaigns: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    sync_google_campaigns()