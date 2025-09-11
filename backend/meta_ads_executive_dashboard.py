#!/usr/bin/env python3
"""
Meta Ads Executive Dashboard Generator
Creates a concise executive summary for leadership review
"""

import json
from datetime import datetime

def create_executive_dashboard():
    """Generate executive dashboard summary"""
    
    # Read the analysis results
    try:
        with open('meta_ads_wow_analysis_20250827_204257.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Analysis file not found. Run the WoW analysis first.")
        return
    
    # Extract key metrics
    summary = data['executive_summary']
    recommendations = data['recommendations']
    top_performers = data['top_performers']
    
    print("🎯 HON META ADS EXECUTIVE DASHBOARD")
    print("=" * 50)
    print(f"📅 Period: {summary['period']}")
    print(f"⭐ Performance Status: {summary['performance_status']}")
    print()
    
    # Key metrics section
    print("📊 KEY PERFORMANCE METRICS")
    print("-" * 30)
    metrics = summary['key_metrics']
    changes = summary['week_over_week_changes']
    
    print(f"💰 Revenue:    ${metrics['total_revenue']:,.0f}  (+{changes['revenue_change']:+.1f}%)")
    print(f"💸 Spend:      ${metrics['total_spend']:,.0f}   (+{changes['spend_change']:+.1f}%)")
    print(f"📈 ROAS:       {metrics['roas']:.2f}          (+{changes['roas_change']:+.1f}%)")
    print(f"🛒 Purchases:  {metrics['purchases']:,}       (+{changes['purchases_change']:+.1f}%)")
    print(f"💰 CPM:        ${metrics['cpm']:.2f}")
    print(f"💰 CPC:        ${metrics['cpc']:.2f}")
    print()
    
    # Top performers section
    print("🏆 TOP PERFORMERS")
    print("-" * 20)
    print("🥇 Highest ROAS:")
    top_roas = top_performers['top_roas'][0]
    print(f"   {top_roas['campaign_name'][:40]}...")
    print(f"   ROAS: {top_roas['roas']:.2f} | Revenue: ${top_roas['revenue']:,.0f}")
    print()
    
    print("💰 Highest Revenue:")
    top_revenue = top_performers['top_revenue'][0]
    print(f"   {top_revenue['campaign_name'][:40]}...")
    print(f"   Revenue: ${top_revenue['revenue']:,.0f} | ROAS: {top_revenue['roas']:.2f}")
    print()
    
    # Recommendations section
    print("⚡ PRIORITY ACTIONS")
    print("-" * 18)
    high_priority = [r for r in recommendations if r['priority'] == 'High']
    for i, rec in enumerate(high_priority, 1):
        print(f"{i}. {rec['title']}")
        print(f"   Action: {rec['action']}")
        print()
    
    # Summary insights
    print("💡 KEY INSIGHTS")
    print("-" * 15)
    print("✅ ROAS of 8.15 is 325% above benchmark (2.0)")
    print("✅ Creative Testing campaigns showing 23.72 ROAS")
    print("✅ Tumbling Mats category +56.7% ROAS improvement")
    print("⚠️  Revenue trend showing volatility - monitor closely")
    print("🚀 Ready for aggressive scaling on high-ROAS campaigns")
    print()
    
    print("📋 NEXT 7 DAYS")
    print("-" * 14)
    print("1. Scale Creative Testing - Tumbling Mat by 50%")
    print("2. Increase Tumbling Mats budget by 25%")  
    print("3. Create 3 new creative variations")
    print("4. Audit Play Furniture for scaling opportunities")
    print()
    
    print(f"📈 Performance Trend: {'🟢 EXCELLENT' if summary['performance_status'] == 'Excellent' else '🟡 GOOD'}")
    print(f"🎯 Total Recommendations: {summary['total_recommendations']} ({summary['high_priority_actions']} high priority)")
    
    # Export summary for easy sharing
    dashboard_summary = {
        "period": summary['period'],
        "status": summary['performance_status'],
        "roas": metrics['roas'],
        "revenue": metrics['total_revenue'],
        "wow_revenue_change": changes['revenue_change'],
        "top_campaign_roas": top_roas['roas'],
        "high_priority_actions": len(high_priority),
        "key_actions": [r['title'] for r in high_priority]
    }
    
    with open('executive_dashboard_summary.json', 'w') as f:
        json.dump(dashboard_summary, f, indent=2)
    
    print("\n📄 Executive summary saved to: executive_dashboard_summary.json")

if __name__ == "__main__":
    create_executive_dashboard()