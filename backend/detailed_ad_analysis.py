#!/usr/bin/env python3
"""
Detailed Ad-Level Analysis for Category and Creative Performance
"""

import requests
import json
from collections import defaultdict
import statistics

def fetch_detailed_ad_data():
    """Fetch comprehensive ad-level data"""
    try:
        response = requests.get("http://localhost:8007/api/meta-ad-reports/ad-data", timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to fetch ad data: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching ad data: {str(e)}")
        return []

def analyze_category_performance(ads_data):
    """Detailed category performance analysis"""
    print("\n🏷️ DETAILED CATEGORY PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    category_stats = defaultdict(lambda: {
        'spend': 0, 'revenue': 0, 'ads': 0, 'purchases': 0,
        'roas_list': [], 'cpa_list': [], 'high_performers': []
    })
    
    total_analyzed = 0
    for ad in ads_data:
        if isinstance(ad, dict):
            total_analyzed += 1
            category = ad.get('category', 'Uncategorized')
            spend = float(ad.get('total_spend', 0))
            revenue = float(ad.get('total_revenue', 0))
            roas = float(ad.get('roas', 0))
            purchases = int(ad.get('total_purchases', 0))
            cpa = float(ad.get('cpa', 0))
            ad_name = ad.get('ad_name', 'Unknown')
            
            category_stats[category]['spend'] += spend
            category_stats[category]['revenue'] += revenue
            category_stats[category]['ads'] += 1
            category_stats[category]['purchases'] += purchases
            
            if roas > 0:
                category_stats[category]['roas_list'].append(roas)
            if cpa > 0:
                category_stats[category]['cpa_list'].append(cpa)
                
            # Track high performers (spend > $1000 and ROAS > 5)
            if spend > 1000 and roas > 5:
                category_stats[category]['high_performers'].append({
                    'name': ad_name[:50], 'spend': spend, 'roas': roas
                })
    
    print(f"📊 Total Ads Analyzed: {total_analyzed}")
    print(f"\n{'Category':<20} {'Spend':<12} {'Revenue':<12} {'ROAS':<8} {'CPA':<8} {'Ads':<6} {'Purchases'}")
    print("-" * 90)
    
    # Sort by spend descending
    for category, stats in sorted(category_stats.items(), key=lambda x: x[1]['spend'], reverse=True):
        if stats['spend'] > 0:
            avg_roas = statistics.mean(stats['roas_list']) if stats['roas_list'] else 0
            avg_cpa = statistics.mean(stats['cpa_list']) if stats['cpa_list'] else 0
            
            print(f"{category:<20} ${stats['spend']:<11,.0f} ${stats['revenue']:<11,.0f} "
                  f"{avg_roas:<7.2f} ${avg_cpa:<7.2f} {stats['ads']:<6} {stats['purchases']}")
    
    # High performers by category
    print(f"\n🌟 HIGH-PERFORMING ADS BY CATEGORY (Spend > $1000, ROAS > 5):")
    for category, stats in category_stats.items():
        if stats['high_performers']:
            print(f"\n   {category} ({len(stats['high_performers'])} ads):")
            for ad in sorted(stats['high_performers'], key=lambda x: x['spend'], reverse=True)[:3]:
                print(f"     • {ad['name']}... - ${ad['spend']:.0f} spend, {ad['roas']:.2f} ROAS")

def analyze_format_performance(ads_data):
    """Detailed format and content type analysis"""
    print(f"\n🎨 DETAILED CREATIVE FORMAT ANALYSIS")
    print("=" * 80)
    
    format_stats = defaultdict(lambda: {'spend': 0, 'revenue': 0, 'ads': 0, 'roas_list': []})
    content_stats = defaultdict(lambda: {'spend': 0, 'revenue': 0, 'ads': 0, 'roas_list': []})
    optimization_stats = defaultdict(lambda: {'spend': 0, 'revenue': 0, 'ads': 0, 'roas_list': []})
    
    for ad in ads_data:
        if isinstance(ad, dict):
            format_type = ad.get('format', 'Unknown')
            content_type = ad.get('content_type', 'Unknown')  
            optimization = ad.get('campaign_optimization', 'Unknown')
            spend = float(ad.get('total_spend', 0))
            revenue = float(ad.get('total_revenue', 0))
            roas = float(ad.get('roas', 0))
            
            # Format analysis
            format_stats[format_type]['spend'] += spend
            format_stats[format_type]['revenue'] += revenue
            format_stats[format_type]['ads'] += 1
            if roas > 0:
                format_stats[format_type]['roas_list'].append(roas)
            
            # Content type analysis
            content_stats[content_type]['spend'] += spend
            content_stats[content_type]['revenue'] += revenue
            content_stats[content_type]['ads'] += 1
            if roas > 0:
                content_stats[content_type]['roas_list'].append(roas)
                
            # Optimization type analysis
            optimization_stats[optimization]['spend'] += spend
            optimization_stats[optimization]['revenue'] += revenue
            optimization_stats[optimization]['ads'] += 1
            if roas > 0:
                optimization_stats[optimization]['roas_list'].append(roas)
    
    # Format performance
    print(f"📹 AD FORMAT PERFORMANCE:")
    print(f"{'Format':<15} {'Spend':<12} {'Revenue':<12} {'ROAS':<8} {'Ads':<6}")
    print("-" * 65)
    for format_type, stats in sorted(format_stats.items(), key=lambda x: x[1]['spend'], reverse=True):
        if stats['spend'] > 0:
            avg_roas = statistics.mean(stats['roas_list']) if stats['roas_list'] else 0
            print(f"{format_type:<15} ${stats['spend']:<11,.0f} ${stats['revenue']:<11,.0f} "
                  f"{avg_roas:<7.2f} {stats['ads']:<6}")
    
    # Content type performance
    print(f"\n📝 CONTENT TYPE PERFORMANCE:")
    print(f"{'Content Type':<15} {'Spend':<12} {'Revenue':<12} {'ROAS':<8} {'Ads':<6}")
    print("-" * 65)
    for content_type, stats in sorted(content_stats.items(), key=lambda x: x[1]['spend'], reverse=True):
        if stats['spend'] > 0:
            avg_roas = statistics.mean(stats['roas_list']) if stats['roas_list'] else 0
            print(f"{content_type:<15} ${stats['spend']:<11,.0f} ${stats['revenue']:<11,.0f} "
                  f"{avg_roas:<7.2f} {stats['ads']:<6}")
    
    # Optimization type performance
    print(f"\n⚡ CAMPAIGN OPTIMIZATION PERFORMANCE:")
    print(f"{'Optimization':<15} {'Spend':<12} {'Revenue':<12} {'ROAS':<8} {'Ads':<6}")
    print("-" * 65)
    for optimization, stats in sorted(optimization_stats.items(), key=lambda x: x[1]['spend'], reverse=True):
        if stats['spend'] > 0:
            avg_roas = statistics.mean(stats['roas_list']) if stats['roas_list'] else 0
            print(f"{optimization:<15} ${stats['spend']:<11,.0f} ${stats['revenue']:<11,.0f} "
                  f"{avg_roas:<7.2f} {stats['ads']:<6}")

def analyze_top_performers(ads_data):
    """Analyze top performing ads"""
    print(f"\n🏆 TOP PERFORMING ADS ANALYSIS")
    print("=" * 80)
    
    # Filter and sort ads
    valid_ads = [ad for ad in ads_data if isinstance(ad, dict) and float(ad.get('total_spend', 0)) > 0]
    
    # Top by spend
    top_by_spend = sorted(valid_ads, key=lambda x: float(x.get('total_spend', 0)), reverse=True)[:10]
    print(f"💰 TOP 10 ADS BY SPEND:")
    for i, ad in enumerate(top_by_spend, 1):
        name = ad.get('ad_name', 'Unknown')[:40]
        spend = float(ad.get('total_spend', 0))
        roas = float(ad.get('roas', 0))
        category = ad.get('category', 'Unknown')
        print(f"   {i:2}. {name}... - ${spend:,.0f} (ROAS: {roas:.2f}) [{category}]")
    
    # Top by ROAS (min $500 spend)
    high_spend_ads = [ad for ad in valid_ads if float(ad.get('total_spend', 0)) >= 500]
    top_by_roas = sorted(high_spend_ads, key=lambda x: float(x.get('roas', 0)), reverse=True)[:10]
    print(f"\n📈 TOP 10 ADS BY ROAS (Min $500 spend):")
    for i, ad in enumerate(top_by_roas, 1):
        name = ad.get('ad_name', 'Unknown')[:40]
        spend = float(ad.get('total_spend', 0))
        roas = float(ad.get('roas', 0))
        category = ad.get('category', 'Unknown')
        print(f"   {i:2}. {name}... - ROAS: {roas:.2f} (${spend:,.0f} spend) [{category}]")

def main():
    print("🔍 DETAILED AD-LEVEL ANALYSIS")
    print("=" * 80)
    print("Fetching comprehensive ad-level data...")
    
    ads_data = fetch_detailed_ad_data()
    
    if ads_data:
        print(f"✅ Fetched {len(ads_data)} ad records")
        analyze_category_performance(ads_data)
        analyze_format_performance(ads_data)
        analyze_top_performers(ads_data)
    else:
        print("❌ No ad data available for analysis")
    
    print("\n✅ Detailed analysis complete")

if __name__ == "__main__":
    main()