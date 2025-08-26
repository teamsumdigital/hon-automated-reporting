#!/usr/bin/env python3
"""
Debug TikTok KPI Mismatch Issue

This script identifies the discrepancy between:
1. Summary endpoint KPI values (what API calculates server-side)
2. Frontend aggregation of ad data (what frontend would calculate from ad list)
"""

import requests
import json
from collections import defaultdict

def fetch_tiktok_data():
    """Fetch both summary and ad data from TikTok endpoints"""
    try:
        # Fetch summary
        summary_response = requests.get('http://localhost:8007/api/tiktok-ad-reports/summary')
        if summary_response.status_code != 200:
            print(f"❌ Summary endpoint error: {summary_response.status_code}")
            return None, None
        
        summary_data = summary_response.json()['summary']
        
        # Fetch ad data
        ad_response = requests.get('http://localhost:8007/api/tiktok-ad-reports/ad-data')
        if ad_response.status_code != 200:
            print(f"❌ Ad data endpoint error: {ad_response.status_code}")
            return None, None
        
        ad_data = ad_response.json()['grouped_ads']
        
        return summary_data, ad_data
    
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None, None

def calculate_frontend_totals(ad_data):
    """Calculate totals as frontend would from ad list"""
    totals = {
        'total_spend': 0,
        'total_revenue': 0,
        'total_purchases': 0,
        'total_clicks': 0,
        'total_impressions': 0,
        'ads_count': len(ad_data)
    }
    
    for ad in ad_data:
        totals['total_spend'] += ad.get('total_spend', 0)
        totals['total_revenue'] += ad.get('total_revenue', 0)
        totals['total_purchases'] += ad.get('total_purchases', 0)
        totals['total_clicks'] += ad.get('total_clicks', 0)
        totals['total_impressions'] += ad.get('total_impressions', 0)
    
    # Calculate averages
    totals['avg_roas'] = totals['total_revenue'] / totals['total_spend'] if totals['total_spend'] > 0 else 0
    totals['avg_cpa'] = totals['total_spend'] / totals['total_purchases'] if totals['total_purchases'] > 0 else 0
    totals['avg_cpc'] = totals['total_spend'] / totals['total_clicks'] if totals['total_clicks'] > 0 else 0
    
    return totals

def analyze_weekly_periods_data(ad_data):
    """Analyze if weekly periods are being double-counted"""
    period_analysis = {
        'ads_with_multiple_periods': 0,
        'total_periods': 0,
        'period_distribution': defaultdict(int)
    }
    
    for ad in ad_data:
        weekly_periods = ad.get('weekly_periods', [])
        period_count = len(weekly_periods)
        
        period_analysis['total_periods'] += period_count
        period_analysis['period_distribution'][period_count] += 1
        
        if period_count > 1:
            period_analysis['ads_with_multiple_periods'] += 1
    
    return period_analysis

def main():
    print("🔍 TikTok KPI Mismatch Analysis")
    print("=" * 50)
    
    # Fetch data
    summary_data, ad_data = fetch_tiktok_data()
    if not summary_data or not ad_data:
        return
    
    # Calculate frontend totals
    frontend_totals = calculate_frontend_totals(ad_data)
    
    # Analyze weekly periods
    period_analysis = analyze_weekly_periods_data(ad_data)
    
    # Compare values
    print("📊 COMPARISON RESULTS:")
    print("-" * 30)
    
    metrics = ['total_spend', 'total_revenue', 'total_purchases', 'total_clicks', 'total_impressions', 'ads_count']
    
    for metric in metrics:
        api_value = summary_data.get(metric, 0)
        frontend_value = frontend_totals.get(metric, 0)
        difference = abs(api_value - frontend_value)
        
        status = "✅ MATCH" if difference < 0.01 else "❌ MISMATCH"
        
        print(f"{metric}:")
        print(f"  API Summary: {api_value:,.2f}")
        print(f"  Frontend Calc: {frontend_value:,.2f}")
        print(f"  Difference: {difference:,.2f} {status}")
        print()
    
    # Compare calculated averages
    print("📈 CALCULATED AVERAGES:")
    print("-" * 30)
    
    avg_metrics = ['avg_roas', 'avg_cpa', 'avg_cpc']
    for metric in avg_metrics:
        api_value = summary_data.get(metric, 0)
        frontend_value = frontend_totals.get(metric, 0)
        difference = abs(api_value - frontend_value)
        
        status = "✅ MATCH" if difference < 0.01 else "❌ MISMATCH"
        
        print(f"{metric}:")
        print(f"  API Summary: {api_value:.4f}")
        print(f"  Frontend Calc: {frontend_value:.4f}")
        print(f"  Difference: {difference:.4f} {status}")
        print()
    
    # Weekly periods analysis
    print("📅 WEEKLY PERIODS ANALYSIS:")
    print("-" * 30)
    print(f"Total ads: {len(ad_data)}")
    print(f"Ads with multiple periods: {period_analysis['ads_with_multiple_periods']}")
    print(f"Total periods across all ads: {period_analysis['total_periods']}")
    print("\nPeriod distribution:")
    for period_count, ad_count in sorted(period_analysis['period_distribution'].items()):
        print(f"  {period_count} period(s): {ad_count} ads")
    
    # Check for potential data source issues
    print("\n🔍 POTENTIAL ISSUES:")
    print("-" * 30)
    
    if period_analysis['ads_with_multiple_periods'] > 0:
        print(f"⚠️  {period_analysis['ads_with_multiple_periods']} ads have multiple weekly periods")
        print("   This could indicate weekly data is being aggregated correctly in frontend")
        print("   but summary endpoint may be using different aggregation logic")
    
    if frontend_totals['ads_count'] != summary_data.get('ads_count', 0):
        print(f"⚠️  Ad count mismatch: Frontend sees {frontend_totals['ads_count']} ads, API reports {summary_data.get('ads_count', 0)}")
        print("   This suggests different grouping/counting logic between endpoints")
    
    # Check for highest spending ads
    print("\n💰 TOP 5 SPENDING ADS (Frontend Calculation):")
    print("-" * 30)
    top_ads = sorted(ad_data, key=lambda x: x.get('total_spend', 0), reverse=True)[:5]
    for i, ad in enumerate(top_ads, 1):
        print(f"{i}. {ad.get('ad_name', 'Unknown')[:50]}...")
        print(f"   Spend: ${ad.get('total_spend', 0):,.2f}, Revenue: ${ad.get('total_revenue', 0):,.2f}")
        print(f"   Periods: {len(ad.get('weekly_periods', []))}")

if __name__ == "__main__":
    main()