#!/usr/bin/env python3
"""
Debug the backend aggregation logic for Google Ads Multi Category CPM
"""

import requests
import json
from collections import defaultdict

def debug_backend_aggregation():
    """Debug where the backend CPM calculation goes wrong"""
    
    backend_url = "http://localhost:8007"
    
    print("🔍 Deep Debug: Backend Multi Category CPM Aggregation")
    print("=" * 65)
    
    try:
        # Step 1: Get raw campaign data for Multi Category
        print("📊 STEP 1: Raw Individual Campaigns")
        campaigns_response = requests.get(f"{backend_url}/api/google-reports/campaigns?categories=Multi Category", timeout=10)
        campaigns = campaigns_response.json()
        
        # Group by month manually to replicate backend logic
        monthly_manual = defaultdict(lambda: {
            'spend': 0, 'impressions': 0, 'campaigns': []
        })
        
        for campaign in campaigns[:20]:  # Limit for readability
            date_str = campaign['reporting_starts']
            month = date_str[:7]  # YYYY-MM
            spend = float(campaign['amount_spent_usd'])
            impressions = int(campaign['impressions'])
            
            monthly_manual[month]['spend'] += spend
            monthly_manual[month]['impressions'] += impressions
            monthly_manual[month]['campaigns'].append(campaign['campaign_id'])
        
        print(f"Found {len(campaigns)} Multi Category campaigns")
        print("Manual Monthly Aggregation:")
        print("-" * 50)
        
        for month, data in sorted(monthly_manual.items())[:3]:
            manual_cpm = (data['spend'] / data['impressions']) * 1000 if data['impressions'] > 0 else 0
            print(f"{month}: ${data['spend']:.0f} spend, {data['impressions']:,} impressions = ${manual_cpm:.2f} CPM")
        
        # Step 2: Compare with backend monthly API
        print(f"\n📊 STEP 2: Backend Monthly API Results")
        monthly_response = requests.get(f"{backend_url}/api/google-reports/monthly?categories=Multi Category", timeout=10)
        monthly_data = monthly_response.json()
        
        print("Backend Monthly API:")
        print("-" * 50)
        for month_data in monthly_data[:3]:
            month = month_data['month']
            backend_spend = float(month_data['spend'])
            backend_impressions = int(month_data['impressions'])
            backend_cpm = float(month_data['cpm'])
            expected_cpm = (backend_spend / backend_impressions) * 1000 if backend_impressions > 0 else 0
            
            print(f"{month}: ${backend_spend:.0f} spend, {backend_impressions:,} impressions")
            print(f"  Backend CPM: ${backend_cpm:.2f}")
            print(f"  Expected CPM: ${expected_cpm:.2f}")
            
            # Check if they match our manual calculation
            if month in monthly_manual:
                manual_spend = monthly_manual[month]['spend']
                manual_impressions = monthly_manual[month]['impressions']
                manual_cpm = (manual_spend / manual_impressions) * 1000 if manual_impressions > 0 else 0
                
                spend_match = abs(backend_spend - manual_spend) < 10
                impressions_match = abs(backend_impressions - manual_impressions) < 1000
                
                print(f"  Manual matches: Spend={spend_match}, Impressions={impressions_match}")
                
                if not spend_match or not impressions_match:
                    print(f"  ❌ DISCREPANCY FOUND!")
                    print(f"    Manual: ${manual_spend:.0f}, {manual_impressions:,} imp")
                    print(f"    Backend: ${backend_spend:.0f}, {backend_impressions:,} imp")
            print()
        
        # Step 3: Check if backend is including wrong data
        print("📊 STEP 3: Data Consistency Check")
        print("-" * 40)
        
        # Check if backend monthly totals make sense vs individual campaigns
        total_manual_spend = sum(float(c['amount_spent_usd']) for c in campaigns)
        total_manual_impressions = sum(int(c['impressions']) for c in campaigns)
        
        total_backend_spend = sum(float(m['spend']) for m in monthly_data)
        total_backend_impressions = sum(int(m['impressions']) for m in monthly_data)
        
        print(f"Total Spend - Manual: ${total_manual_spend:.0f}, Backend: ${total_backend_spend:.0f}")
        print(f"Total Impressions - Manual: {total_manual_impressions:,}, Backend: {total_backend_impressions:,}")
        
        if abs(total_manual_spend - total_backend_spend) > 100 or abs(total_manual_impressions - total_backend_impressions) > 10000:
            print("❌ MAJOR DISCREPANCY: Backend is aggregating different data!")
        else:
            print("✅ Totals match - issue is in CPM calculation logic")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    debug_backend_aggregation()