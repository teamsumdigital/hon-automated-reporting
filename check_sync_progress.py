#!/usr/bin/env python3
import requests
import time
from collections import Counter

def check_sync_progress():
    print('⏳ Waiting for sync to process more data...')
    time.sleep(10)
    print('🔍 Checking Meta Ad Level data again...')
    
    response = requests.get('http://localhost:8007/api/meta-ad-reports/ad-data', timeout=10)
    if response.status_code == 200:
        data = response.json()
        ads = data.get('ads', [])
        print(f'Total ads now: {len(ads)}')
        
        if len(ads) > 0:
            categories = Counter(ad['category'] for ad in ads)
            print(f'Categories found:')
            for category, count in categories.most_common():
                total_spend = sum(float(ad['amount_spent_usd']) for ad in ads if ad['category'] == category)
                print(f'  {category}: {count} ads, ${total_spend:.0f} spend')
            
            # Check for Standing Mat ads specifically
            standing_ads = [ad for ad in ads if ad['category'] == 'Standing Mats']
            print(f'\nStanding Mat ads found: {len(standing_ads)}')
            if standing_ads:
                standing_by_spend = sorted(standing_ads, key=lambda x: float(x['amount_spent_usd']), reverse=True)
                print('Top 5 Standing Mat ads by spend:')
                for i, ad in enumerate(standing_by_spend[:5]):
                    print(f'  {i+1}. ${float(ad["amount_spent_usd"]):.0f} - {ad["ad_name"][:60]}...')
            
            return True
        else:
            print('Still no data - sync may still be running')
            return False
    else:
        print(f'API error: {response.status_code}')
        return False

if __name__ == "__main__":
    check_sync_progress()