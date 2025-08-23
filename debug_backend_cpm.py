#!/usr/bin/env python3
"""
Debug backend CPM calculation for Multi Category
"""

import requests
import json

def debug_backend_cpm():
    backend_url = "http://localhost:8007"
    
    print("🔍 Debugging Backend CPM Calculation for Multi Category")
    print("=" * 60)
    
    try:
        # Get raw campaign data for Multi Category
        response = requests.get(f"{backend_url}/api/google-reports/campaigns?categories=Multi Category", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            return
            
        campaigns = response.json()[:10]  # First 10 campaigns
        
        print("Raw Multi Category Campaigns (Individual Records):")
        print("-" * 70)
        print(f"{'Campaign ID':<15} {'Date':<12} {'Spend':<8} {'Impressions':<12} {'Expected CPM':<12}")
        print("-" * 70)
        
        # Group by month to understand aggregation
        monthly_groups = {}
        
        for campaign in campaigns:
            spend = float(campaign['amount_spent_usd'])
            impressions = int(campaign['impressions'])
            expected_cpm = (spend / impressions) * 1000 if impressions > 0 else 0
            date = campaign['reporting_starts']
            month = date[:7]  # YYYY-MM
            
            print(f"{campaign['campaign_id']:<15} {date:<12} ${spend:<7.0f} {impressions:<12,} ${expected_cpm:<11.2f}")
            
            # Group for monthly analysis
            if month not in monthly_groups:
                monthly_groups[month] = {'spend': 0, 'impressions': 0, 'campaigns': []}
            monthly_groups[month]['spend'] += spend
            monthly_groups[month]['impressions'] += impressions
            monthly_groups[month]['campaigns'].append(campaign['campaign_id'])
        
        print("\nMonthly Aggregation Analysis:")
        print("-" * 60)
        print(f"{'Month':<10} {'Total Spend':<12} {'Total Impressions':<16} {'Calculated CPM':<15}")
        print("-" * 60)
        
        for month, data in sorted(monthly_groups.items())[:5]:
            total_spend = data['spend']
            total_impressions = data['impressions']
            calculated_cpm = (total_spend / total_impressions) * 1000 if total_impressions > 0 else 0
            
            print(f"{month:<10} ${total_spend:<11.0f} {total_impressions:<16,} ${calculated_cpm:<14.2f}")
        
        # Compare with monthly API endpoint
        print(f"\n🔄 Comparing with /monthly API endpoint...")
        monthly_response = requests.get(f"{backend_url}/api/google-reports/monthly?categories=Multi Category", timeout=10)
        
        if monthly_response.status_code == 200:
            monthly_data = monthly_response.json()[:3]
            print(f"\nMonthly API Results:")
            print("-" * 50)
            print(f"{'Month':<10} {'API CPM':<10} {'Should Be':<12}")
            print("-" * 50)
            
            for month_data in monthly_data:
                api_cpm = float(month_data['cpm'])
                month = month_data['month']
                
                # Find corresponding manual calculation
                manual_cpm = 0
                if month in monthly_groups:
                    manual_cpm = (monthly_groups[month]['spend'] / monthly_groups[month]['impressions']) * 1000
                
                status = "✅ Match" if abs(api_cpm - manual_cpm) < 1 else "❌ Mismatch"
                print(f"{month:<10} ${api_cpm:<9.2f} ${manual_cpm:<11.2f} {status}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_backend_cpm()