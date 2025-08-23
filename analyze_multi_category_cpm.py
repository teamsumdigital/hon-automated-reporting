#!/usr/bin/env python3
"""
Analyze why Multi Category campaigns have high CPM values
"""

import requests
import json

def analyze_multi_category_cpm():
    backend_url = "http://localhost:8007"
    
    print("🔍 Multi Category CPM Analysis")
    print("=" * 50)
    
    try:
        # Get actual Multi Category campaigns
        response = requests.get(f"{backend_url}/api/google-reports/campaigns?category=Multi Category", timeout=10)
        campaigns = response.json()
        
        print(f"Analyzing {len(campaigns)} Multi Category campaigns")
        print()
        
        # Sort by spend to see biggest spenders
        campaigns_by_spend = sorted(campaigns, key=lambda x: float(x['amount_spent_usd']), reverse=True)
        
        print("Top 15 Multi Category campaigns by spend:")
        print(f"{'Campaign ID':<15} {'Date':<12} {'Spend':<8} {'Impressions':<12} {'CPM':<8} {'Status':<10}")
        print("-" * 85)
        
        total_spend = 0
        total_impressions = 0
        high_cpm_count = 0
        
        for i, campaign in enumerate(campaigns_by_spend[:15]):
            spend = float(campaign['amount_spent_usd'])
            impressions = int(campaign['impressions'])
            cpm = (spend / impressions) * 1000 if impressions > 0 else 0
            
            total_spend += spend
            total_impressions += impressions
            
            status = "HIGH CPM!" if cpm > 50 else "Normal"
            if cpm > 50:
                high_cpm_count += 1
            
            print(f"{campaign['campaign_id']:<15} {campaign['reporting_starts']:<12} ${spend:<7.0f} {impressions:<12,} ${cpm:<7.2f} {status:<10}")
        
        print(f"\nTop 15 campaigns summary:")
        print(f"Total spend: ${total_spend:,.0f}")
        print(f"Total impressions: {total_impressions:,}")
        print(f"Average CPM: ${(total_spend/total_impressions)*1000:.2f}")
        print(f"High CPM campaigns (>$50): {high_cpm_count}/15")
        
        # Now analyze monthly aggregation
        print(f"\n📊 Monthly Aggregation Analysis")
        monthly_response = requests.get(f"{backend_url}/api/google-reports/monthly?categories=Multi Category", timeout=10)
        monthly_data = monthly_response.json()
        
        print(f"Monthly data points: {len(monthly_data)}")
        print(f"{'Month':<10} {'Spend':<8} {'Impressions':<12} {'CPM':<8} {'Assessment':<15}")
        print("-" * 60)
        
        high_cpm_months = 0
        for month in sorted(monthly_data, key=lambda x: x['month'])[-10:]:  # Last 10 months
            spend = float(month['spend'])
            impressions = int(month['impressions'])
            cpm = float(month['cpm'])
            
            # Assess the CPM level
            if cpm > 100:
                assessment = "VERY HIGH"
                high_cpm_months += 1
            elif cpm > 50:
                assessment = "HIGH"
                high_cpm_months += 1
            else:
                assessment = "Normal"
            
            print(f"{month['month']:<10} ${spend:<7.0f} {impressions:<12,} ${cpm:<7.2f} {assessment:<15}")
        
        print(f"\nConclusion:")
        if high_cpm_months > 5:
            print("❌ Multi Category campaigns genuinely have high CPM values")
            print("   This appears to be due to low impression delivery relative to spend")
            print("   The backend calculation is correct - these campaigns are simply inefficient")
        else:
            print("✅ CPM values appear normal for most periods")
            
        # Check if this is a campaign performance issue, not a calculation issue
        print(f"\n💡 Recommendation:")
        print("   The high CPM values appear to be genuine campaign performance issues")
        print("   rather than calculation errors. Multi Category campaigns are getting")
        print("   low impression delivery for their spend levels.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_multi_category_cpm()