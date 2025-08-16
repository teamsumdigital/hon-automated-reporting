#!/usr/bin/env python3
"""
Fast Google Ads sync - bypassing categorization service
"""

import os
import sys
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from datetime import date
from dotenv import load_dotenv
from app.services.google_ads_service import GoogleAdsService
from supabase import create_client

load_dotenv()

def categorize_campaign_simple(campaign_name):
    """Simple, fast categorization without service dependency"""
    name_lower = campaign_name.lower()
    
    if 'standing' in name_lower:
        return 'Standing Mats'
    elif 'playmat' in name_lower or 'play mat' in name_lower:
        return 'Play Mats'
    elif 'bath' in name_lower:
        return 'Bath Mats'
    elif 'tumbling' in name_lower:
        return 'Tumbling Mats'
    elif 'play' in name_lower and ('furniture' in name_lower or 'table' in name_lower):
        return 'Play Furniture'
    else:
        return 'Multi Category'

def main():
    """Fast sync of Google Ads data"""
    print('🚀 Fast Google Ads sync...')
    
    # Initialize services
    google_ads_service = GoogleAdsService()
    
    # Initialize Supabase directly
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')
    supabase = create_client(url, key)
    
    # Clear existing data
    print('🧹 Clearing existing data...')
    supabase.table('google_campaign_data').delete().neq('id', 0).execute()
    
    # Test connection
    if not google_ads_service.test_connection():
        print('❌ Google Ads API connection failed')
        return
    
    print('✅ Connected to Google Ads API')
    
    # Get data for Jan 2024 - Aug 12, 2024
    start_date = date(2024, 1, 1)
    end_date = date(2024, 8, 12)
    
    print(f'📊 Fetching data from {start_date} to {end_date}...')
    insights = google_ads_service.get_campaign_insights(start_date, end_date)
    
    if not insights:
        print('❌ No insights returned')
        return
    
    print(f'📈 Retrieved {len(insights)} insights')
    
    # Convert to campaign data
    campaign_data_list = google_ads_service.convert_to_campaign_data(insights)
    
    print(f'💾 Processing {len(campaign_data_list)} campaign records...')
    
    # Store each record directly with simple categorization
    stored_count = 0
    for campaign_data in campaign_data_list:
        # Apply simple categorization
        category = categorize_campaign_simple(campaign_data.campaign_name)
        
        # Create record
        record = {
            "campaign_id": campaign_data.campaign_id,
            "campaign_name": campaign_data.campaign_name,
            "category": category,
            "reporting_starts": campaign_data.reporting_starts.isoformat(),
            "reporting_ends": campaign_data.reporting_ends.isoformat(),
            "amount_spent_usd": float(campaign_data.amount_spent_usd),
            "website_purchases": campaign_data.website_purchases,
            "purchases_conversion_value": float(campaign_data.purchases_conversion_value),
            "impressions": campaign_data.impressions,
            "link_clicks": campaign_data.link_clicks,
            "cpa": float(campaign_data.cpa),
            "roas": float(campaign_data.roas),
            "cpc": float(campaign_data.cpc)
        }
        
        # Insert directly
        result = supabase.table('google_campaign_data').insert(record).execute()
        
        if result.data:
            stored_count += 1
            if stored_count % 100 == 0:
                print(f'  Stored {stored_count} records...')
    
    print(f'✅ Successfully stored {stored_count} Google Ads records')
    
    # Show summary
    result = supabase.table('google_campaign_data').select('category').execute()
    categories = {}
    for row in result.data:
        cat = row['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f'\n📊 Category distribution:')
    for cat, count in sorted(categories.items()):
        print(f'  {cat}: {count} records')

if __name__ == "__main__":
    main()