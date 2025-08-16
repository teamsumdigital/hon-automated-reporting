#!/usr/bin/env python3
"""
Insert all Google Ads campaign data (Jan 2024 - Aug 12, 2024)
"""

import os
import sys
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from datetime import date
from dotenv import load_dotenv
from app.services.google_ads_service import GoogleAdsService
from supabase import create_client

load_dotenv()

def simple_categorize(campaign_name):
    """Fast text-based categorization"""
    name = campaign_name.lower()
    if 'standing' in name:
        return 'Standing Mats'
    elif 'playmat' in name or 'play mat' in name:
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
    print('🚀 Inserting ALL Google Ads campaign data...')
    
    # Connect to services
    google_ads = GoogleAdsService()
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
    
    # Clear existing data first
    print('🧹 Clearing existing data...')
    supabase.table('google_campaign_data').delete().gte('id', 0).execute()
    
    # Get all data: January 2024 - August 12, 2024
    start_date = date(2024, 1, 1)
    end_date = date(2024, 8, 12)
    
    print(f'📊 Getting ALL Google Ads data from {start_date} to {end_date}...')
    insights = google_ads.get_campaign_insights(start_date, end_date)
    
    if not insights:
        print('❌ No data returned')
        return
    
    print(f'✅ Retrieved {len(insights)} campaign insights')
    
    # Process insights into records
    records = []
    campaign_names = set()
    
    for insight in insights:
        # Track unique campaign names
        campaign_names.add(insight.campaign_name)
        
        # Convert cost from micros to dollars
        spend_usd = float(insight.cost_micros) / 1_000_000 if insight.cost_micros else 0
        conversions = float(insight.conversions) if insight.conversions else 0
        conversions_value = float(insight.conversions_value) if insight.conversions_value else 0
        clicks = int(insight.clicks) if insight.clicks else 0
        
        # Calculate metrics safely
        cpa = spend_usd / conversions if conversions > 0 else 0
        roas = conversions_value / spend_usd if spend_usd > 0 else 0
        cpc = spend_usd / clicks if clicks > 0 else 0
        
        record = {
            'campaign_id': insight.campaign_id,
            'campaign_name': insight.campaign_name,
            'category': simple_categorize(insight.campaign_name),
            'reporting_starts': insight.date_start,
            'reporting_ends': insight.date_stop,
            'amount_spent_usd': spend_usd,
            'website_purchases': int(conversions),
            'purchases_conversion_value': conversions_value,
            'impressions': int(insight.impressions) if insight.impressions else 0,
            'link_clicks': clicks,
            'cpa': cpa,
            'roas': roas,
            'cpc': cpc
        }
        records.append(record)
    
    print(f'📈 Processed {len(records)} records from {len(campaign_names)} unique campaigns')
    print(f'   Campaign examples: {list(campaign_names)[:5]}')
    
    # Insert in batches
    print(f'💾 Inserting {len(records)} records in batches...')
    batch_size = 100
    success_count = 0
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        try:
            result = supabase.table('google_campaign_data').insert(batch).execute()
            success_count += len(batch)
            print(f'  ✅ Batch {i//batch_size + 1}/{(len(records)-1)//batch_size + 1}: {len(batch)} records')
        except Exception as e:
            print(f'  ❌ Batch {i//batch_size + 1} failed: {e}')
            # Try individual inserts for this batch
            for record in batch:
                try:
                    supabase.table('google_campaign_data').insert(record).execute()
                    success_count += 1
                except Exception as e2:
                    print(f'    Failed individual record: {record["campaign_name"]} - {e2}')
    
    print(f'✅ Successfully inserted {success_count}/{len(records)} records!')
    
    # Show final summary
    result = supabase.table('google_campaign_data').select('*').execute()
    print(f'\n📊 Final database summary: {len(result.data)} total records')
    
    # Category breakdown
    categories = {}
    total_spend = 0
    for row in result.data:
        cat = row['category']
        categories[cat] = categories.get(cat, 0) + 1
        total_spend += row['amount_spent_usd']
    
    print(f'\nCategory distribution:')
    for cat, count in sorted(categories.items()):
        print(f'  {cat}: {count} records')
    
    print(f'\nTotal spend: ${total_spend:,.2f}')
    
    # Test API
    print(f'\n🔍 Testing API response...')
    import requests
    try:
        response = requests.get('http://localhost:8007/api/google-reports/dashboard')
        if response.status_code == 200:
            data = response.json()
            print(f'✅ API working: {data["summary"]["campaigns_count"]} campaigns, ${data["summary"]["total_spend"]:,.2f} spend')
            print(f'   Available categories: {data["categories"]}')
        else:
            print(f'❌ API error: {response.status_code}')
    except Exception as e:
        print(f'❌ API test failed: {e}')

if __name__ == "__main__":
    main()