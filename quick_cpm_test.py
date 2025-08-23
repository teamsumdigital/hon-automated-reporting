#!/usr/bin/env python3
import requests

def quick_cpm_test():
    backend_url = 'http://localhost:8007'
    response = requests.get(f'{backend_url}/api/google-reports/monthly?categories=Multi Category', timeout=10)

    if response.status_code == 200:
        data = response.json()[:3]  # First 3 months
        print('Multi Category Monthly CPM Analysis:')
        print('Month      | Spend    | Impressions | CPM    | Status')
        print('-' * 55)
        
        for month in data:
            spend = float(month['spend'])
            impressions = int(month['impressions'])
            cpm = float(month['cpm'])
            
            status = 'Good' if cpm < 50 else 'Too High!'
            print(f"{month['month']:<10} | ${spend:<8.0f} | {impressions:<11,} | ${cpm:<6.2f} | {status}")
            
        # Test if the fix worked
        high_cpms = [float(m['cpm']) for m in data if float(m['cpm']) > 50]
        if not high_cpms:
            print(f'\n✅ SUCCESS: All CPM values are reasonable!')
            print(f'🎉 Google Ads CPM fix appears to be working')
        else:
            print(f'\n❌ Still seeing high CPM values: {high_cpms}')
    else:
        print(f'Error: {response.status_code}')

if __name__ == "__main__":
    quick_cpm_test()