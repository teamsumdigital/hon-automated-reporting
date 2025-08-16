#!/usr/bin/env python3
"""
Test inserting a single Google Ads record
"""

import os
import sys
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from datetime import date
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def main():
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
    
    # Check current data
    result = supabase.table('google_campaign_data').select('*').execute()
    print(f'Current records: {len(result.data)}')
    
    # Insert a simple test record
    test_record = {
        'campaign_id': 'test_123',
        'campaign_name': 'Test Campaign - Playmats',
        'category': 'Play Mats',
        'reporting_starts': '2024-01-01',
        'reporting_ends': '2024-01-01',
        'amount_spent_usd': 100.50,
        'website_purchases': 5,
        'purchases_conversion_value': 250.75,
        'impressions': 1000,
        'link_clicks': 50,
        'cpa': 20.10,
        'roas': 2.49,
        'cpc': 2.01
    }
    
    try:
        result = supabase.table('google_campaign_data').insert(test_record).execute()
        print('✅ Test record inserted successfully!')
        print(f'Inserted: {result.data[0]["campaign_name"]}')
        
        # Check total records now
        result = supabase.table('google_campaign_data').select('*').execute()
        print(f'Total records now: {len(result.data)}')
        
        # Test the API
        print('\\nTesting API...')
        import requests
        response = requests.get('http://localhost:8007/api/google-reports/dashboard')
        if response.status_code == 200:
            data = response.json()
            print(f'API response: {data["summary"]["campaigns_count"]} campaigns, ${data["summary"]["total_spend"]:.2f} spend')
        else:
            print(f'API error: {response.status_code}')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    main()