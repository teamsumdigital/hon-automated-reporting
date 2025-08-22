#!/usr/bin/env python3
"""Test momentum calculation with real data"""

import requests
import json
from datetime import datetime

try:
    response = requests.get('http://localhost:8007/api/meta-ad-reports/ad-data')
    if response.status_code == 200:
        data = response.json()
        print(f'✅ Found {data.get("count", 0)} total ads')
        
        momentum_visible_count = 0
        total_ads_with_periods = 0
        
        for i, ad in enumerate(data.get('grouped_ads', [])[:5]):
            print(f'\n📊 Ad {i+1}: {ad.get("ad_name", "unknown")}')
            periods = ad.get('weekly_periods', [])
            print(f'🗓️ Weekly periods: {len(periods)}')
            
            if len(periods) >= 2:
                total_ads_with_periods += 1
                # Sort periods by date
                sorted_periods = sorted(periods, key=lambda x: x['reporting_starts'])
                older = sorted_periods[0]
                newer = sorted_periods[1]
                
                print(f'   Week 1: {older["reporting_starts"]} - Spend: ${older["spend"]:.2f}, ROAS: {older["roas"]}')
                print(f'   Week 2: {newer["reporting_starts"]} - Spend: ${newer["spend"]:.2f}, ROAS: {newer["roas"]}')
                
                # Calculate momentum
                spend_change = ((newer['spend'] - older['spend']) / older['spend']) * 100 if older['spend'] > 0 else None
                roas_change = ((newer['roas'] - older['roas']) / older['roas']) * 100 if older['roas'] > 0 else None
                
                momentum_visible = False
                
                if spend_change is not None and abs(spend_change) >= 1:
                    print(f'   📈 Spend momentum: {spend_change:+.1f}% (VISIBLE)')
                    momentum_visible = True
                else:
                    print(f'   📊 Spend momentum: {spend_change:+.1f}% (hidden - too small)' if spend_change else '   📊 Spend momentum: N/A')
                
                if roas_change is not None and abs(roas_change) >= 1:
                    print(f'   📈 ROAS momentum: {roas_change:+.1f}% (VISIBLE)')
                    momentum_visible = True
                else:
                    print(f'   📊 ROAS momentum: {roas_change:+.1f}% (hidden - too small)' if roas_change else '   📊 ROAS momentum: N/A')
                
                if momentum_visible:
                    momentum_visible_count += 1
            else:
                print(f'   ❌ Only {len(periods)} periods - need 2 for momentum')
        
        print(f'\n🎯 Summary:')
        print(f'   - Ads with 2+ periods: {total_ads_with_periods}')
        print(f'   - Ads with visible momentum: {momentum_visible_count}')
        print(f'   - Momentum should be working for {momentum_visible_count} ads!')
        
        if momentum_visible_count > 0:
            print(f'\n✅ MOMENTUM IS WORKING! Check the Ad Level Dashboard')
            print(f'🌐 Frontend: http://localhost:3007')
            print(f'📊 Click on "Ad Level" tab to see momentum indicators')
        else:
            print(f'\n⚠️ No visible momentum - all changes are < 1%')
    else:
        print(f'❌ API error: {response.status_code}')
except Exception as e:
    print(f'❌ Error: {e}')