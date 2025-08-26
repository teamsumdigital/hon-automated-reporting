#!/usr/bin/env python3
"""
Debug why TikTok table is empty but KPIs show data
"""

import requests
import json

def test_tiktok_dashboard():
    print("🔍 DEBUGGING TIKTOK TABLE ISSUE")
    print("=" * 50)
    
    # Test the dashboard endpoint with current month filter
    response = requests.get('http://localhost:8007/api/tiktok-reports/dashboard?start_date=2025-08-01&_t=123')
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        return
    
    data = response.json()
    
    print("📊 SUMMARY DATA:")
    summary = data.get('summary', {})
    print(f"  Total Spend: ${summary.get('total_spend', 0):,.2f}")
    print(f"  Total Revenue: ${summary.get('total_revenue', 0):,.2f}")
    print(f"  Campaigns Count: {summary.get('campaigns_count', 0)}")
    
    print("\n📅 PIVOT DATA (Table Data):")
    pivot_data = data.get('pivot_data', [])
    print(f"  Pivot data count: {len(pivot_data)}")
    
    if pivot_data:
        for item in pivot_data:
            print(f"  {item.get('month')}: ${item.get('spend', 0):,.2f}")
    else:
        print("  ❌ NO PIVOT DATA - This is why table is empty!")
    
    print(f"\n📂 CATEGORIES: {data.get('categories', [])}")
    
    # Test without date filter to see if data exists
    print("\n" + "=" * 50)
    print("🔍 TESTING WITHOUT DATE FILTER")
    
    response2 = requests.get('http://localhost:8007/api/tiktok-reports/dashboard?_t=456')
    if response2.status_code == 200:
        data2 = response2.json()
        pivot_data2 = data2.get('pivot_data', [])
        print(f"  Pivot data without filter: {len(pivot_data2)} items")
        
        for item in pivot_data2[:5]:  # Show first 5
            print(f"  {item.get('month')}: ${item.get('spend', 0):,.2f}")
    
    # Check raw campaign data
    print("\n" + "=" * 50)
    print("🔍 RAW CAMPAIGN DATA")
    
    campaigns = data.get('campaigns', [])
    print(f"  Raw campaigns count: {len(campaigns)}")
    
    if campaigns:
        print("  Sample campaigns:")
        for campaign in campaigns[:3]:
            print(f"    Date: {campaign.get('reporting_starts')} - Spend: ${campaign.get('amount_spent_usd', 0):,.2f}")

if __name__ == "__main__":
    test_tiktok_dashboard()