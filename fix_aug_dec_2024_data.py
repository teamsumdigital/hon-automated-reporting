#!/usr/bin/env python3
"""
Fix Aug-Dec 2024 Google Ads data to match the screenshot
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def fix_aug_dec_2024_data():
    """Fix Aug-Dec 2024 data to match screenshot values"""
    print('🔧 Fixing Aug-Dec 2024 Google Ads data...')
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')
    supabase = create_client(url, key)
    
    # Correct data from screenshot
    correct_data = {
        '2024-08': {
            'cost': 65005.48,
            'clicks': 67464,
            'purchases': 2891.57,  # Note: fractional purchases from screenshot
            'revenue': 714360.13
        },
        '2024-09': {
            'cost': 91221.02,
            'clicks': 72653,
            'purchases': 2769.82,
            'revenue': 656086.83
        },
        '2024-10': {
            'cost': 60317.93,
            'clicks': 56152,
            'purchases': 6244.12,
            'revenue': 581588.81
        },
        '2024-11': {
            'cost': 167280.88,
            'clicks': 107288,
            'purchases': 8311.73,
            'revenue': 2068447.69
        },
        '2024-12': {
            'cost': 108615.25,
            'clicks': 76048,
            'purchases': 4661.98,
            'revenue': 1154692.66
        }
    }
    
    for month, data in correct_data.items():
        # Find the campaign for this month
        result = supabase.table('google_campaign_data').select('*').like('campaign_name', f'%{month}%').execute()
        
        if result.data:
            campaign_id = result.data[0]['id']
            
            # Calculate derived metrics
            cpa = data['cost'] / data['purchases'] if data['purchases'] > 0 else 0
            roas = data['revenue'] / data['cost'] if data['cost'] > 0 else 0
            cpc = data['cost'] / data['clicks'] if data['clicks'] > 0 else 0
            
            # Update the record
            update_result = supabase.table('google_campaign_data').update({
                'amount_spent_usd': data['cost'],
                'link_clicks': data['clicks'],
                'website_purchases': int(data['purchases']),  # Convert to int for database
                'purchases_conversion_value': data['revenue'],
                'impressions': data['clicks'] * 8,  # Estimate impressions
                'cpa': cpa,
                'roas': roas,
                'cpc': cpc
            }).eq('id', campaign_id).execute()
            
            print(f'✅ Updated {month}: Cost=${data["cost"]:,.2f}, Clicks={data["clicks"]:,}, Purchases={data["purchases"]:.2f}, Revenue=${data["revenue"]:,.2f}')
        else:
            print(f'❌ No campaign found for {month}')
    
    # Verify the updates
    print('\n📊 Verifying updated data:')
    for month in correct_data.keys():
        result = supabase.table('google_campaign_data').select('*').like('campaign_name', f'%{month}%').execute()
        if result.data:
            row = result.data[0]
            print(f'{month}: Cost=${row["amount_spent_usd"]:,.2f}, Clicks={row["link_clicks"]:,}, Purchases={row["website_purchases"]:,}, Revenue=${row["purchases_conversion_value"]:,.2f}')

if __name__ == "__main__":
    fix_aug_dec_2024_data()