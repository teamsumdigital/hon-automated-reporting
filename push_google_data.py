#!/usr/bin/env python3
"""
Just push Google Ads data to Supabase - no slow categorization
"""

import os
import sys
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from datetime import date
from dotenv import load_dotenv
from app.services.google_ads_service import GoogleAdsService
from supabase import create_client
from decimal import Decimal

load_dotenv()

def simple_categorize(campaign_name):
    """Fast categorization"""
    name = campaign_name.lower()
    if 'standing' in name:
        return 'Standing Mats'
    elif 'playmat' in name:
        return 'Play Mats'
    elif 'bath' in name:
        return 'Bath Mats'
    elif 'tumbling' in name:
        return 'Tumbling Mats'
    elif 'furniture' in name:
        return 'Play Furniture'
    else:
        return 'Multi Category'

def main():
    print('📤 Pushing Google Ads data to Supabase...')
    
    # Connect to services
    google_ads = GoogleAdsService()
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
    
    # Get January 2024 data only (smaller dataset to start)
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    print(f'📊 Getting data for {start_date} to {end_date}...')
    insights = google_ads.get_campaign_insights(start_date, end_date)
    
    if not insights:
        print('❌ No data returned')
        return
    
    print(f'✅ Got {len(insights)} insights')
    
    # Process each insight directly
    records = []
    for insight in insights:
        # Convert micros to dollars
        spend_usd = float(insight.cost_micros) / 1_000_000 if insight.cost_micros else 0
        
        record = {
            'campaign_id': insight.campaign_id,
            'campaign_name': insight.campaign_name,
            'category': simple_categorize(insight.campaign_name),
            'reporting_starts': insight.date_start,
            'reporting_ends': insight.date_stop,
            'amount_spent_usd': spend_usd,
            'website_purchases': int(float(insight.conversions)) if insight.conversions else 0,
            'purchases_conversion_value': float(insight.conversions_value) if insight.conversions_value else 0,
            'impressions': int(insight.impressions) if insight.impressions else 0,
            'link_clicks': int(insight.clicks) if insight.clicks else 0,
            'cpa': spend_usd / float(insight.conversions) if insight.conversions and float(insight.conversions) > 0 else 0,
            'roas': float(insight.conversions_value) / spend_usd if insight.conversions_value and spend_usd > 0 else 0,
            'cpc': spend_usd / int(insight.clicks) if insight.clicks and int(insight.clicks) > 0 and spend_usd > 0 else 0
        }
        records.append(record)
    
    print(f'💾 Inserting {len(records)} records...')
    
    # Clear existing data first
    try:
        result = supabase.table('google_campaign_data').delete().neq('id', 0).execute()
        print(f'  Cleared existing data')
    except Exception as e:
        print(f'  Note: {e}')
    
    # Insert in batches using upsert
    batch_size = 50
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        result = supabase.table('google_campaign_data').upsert(batch).execute()
        print(f'  Upserted batch {i//batch_size + 1}/{(len(records)-1)//batch_size + 1}')
    
    print('✅ Data pushed to Supabase!')
    
    # Show summary
    result = supabase.table('google_campaign_data').select('category').execute()
    categories = {}
    for row in result.data:
        cat = row['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print('\n📊 Category summary:')
    for cat, count in sorted(categories.items()):
        print(f'  {cat}: {count} records')

if __name__ == "__main__":
    main()