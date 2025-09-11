#!/usr/bin/env python3
"""
Comprehensive Business Intelligence Report for HON Automated Reporting
Final analysis with complete data access and strategic insights
"""

import requests
import json
from datetime import datetime
from collections import defaultdict
import statistics

class HONComprehensiveBI:
    def __init__(self):
        self.base_url = "http://localhost:8007"
        self.data = {}
        
    def fetch_comprehensive_data(self):
        """Fetch all available data from HON reporting system"""
        print("🔄 Fetching comprehensive HON data across all platforms...")
        
        endpoints = {
            'monthly_summary': '/api/reports/monthly',
            'meta_ad_data': '/api/meta-ad-reports/ad-data',
            'meta_summary': '/api/meta-ad-reports/summary',
            'filters': '/api/meta-ad-reports/filters',
            'google_monthly': '/api/google-reports/monthly',
            'tiktok_monthly': '/api/tiktok-reports/monthly'
        }
        
        for key, endpoint in endpoints.items():
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=60)
                if response.status_code == 200:
                    self.data[key] = response.json()
                    
                    # Log data structure
                    if key == 'meta_ad_data':
                        count = self.data[key].get('count', 0)
                        ads = self.data[key].get('grouped_ads', [])
                        print(f"✅ Fetched {key}: {count} total ads, {len(ads)} grouped ad entries")
                    elif isinstance(self.data[key], list):
                        print(f"✅ Fetched {key}: {len(self.data[key])} records")
                    elif isinstance(self.data[key], dict) and 'summary' in self.data[key]:
                        print(f"✅ Fetched {key}: summary data")
                    else:
                        print(f"✅ Fetched {key}: success")
                else:
                    print(f"❌ Failed to fetch {key}: {response.status_code}")
            except Exception as e:
                print(f"❌ Error fetching {key}: {str(e)}")
    
    def analyze_platform_comparison(self):
        """Compare performance across Meta, Google, and TikTok"""
        print("\\n📊 CROSS-PLATFORM PERFORMANCE COMPARISON")
        print("=" * 80)
        
        platforms = []
        
        # Meta Ads (from monthly summary)
        if 'monthly_summary' in self.data and 'summary' in self.data['monthly_summary']:
            meta = self.data['monthly_summary']['summary']
            platforms.append({
                'name': 'Meta Ads',
                'spend': meta['total_spend'],
                'revenue': meta['total_revenue'],
                'roas': meta['avg_roas'],
                'cpa': meta['avg_cpa'],
                'cpc': meta['avg_cpc'],
                'campaigns': meta['campaign_count'],
                'purchases': meta['total_purchases']
            })
        
        # Google Ads
        if 'google_monthly' in self.data:
            google_data = self.data['google_monthly']
            total_spend = sum(float(m['spend']) for m in google_data)
            total_revenue = sum(float(m['revenue']) for m in google_data)
            avg_roas = statistics.mean(float(m['roas']) for m in google_data)
            avg_cpa = statistics.mean(float(m['cpa']) for m in google_data)
            total_purchases = sum(int(m['purchases']) for m in google_data)
            
            platforms.append({
                'name': 'Google Ads',
                'spend': total_spend,
                'revenue': total_revenue,
                'roas': avg_roas,
                'cpa': avg_cpa,
                'cpc': statistics.mean(float(m['cpc']) for m in google_data),
                'campaigns': len(google_data),
                'purchases': total_purchases
            })
        
        # TikTok Ads
        if 'tiktok_monthly' in self.data:
            tiktok_data = self.data['tiktok_monthly']
            total_spend = sum(float(m['spend']) for m in tiktok_data)
            total_revenue = sum(float(m['revenue']) for m in tiktok_data)
            avg_roas = statistics.mean(float(m['roas']) for m in tiktok_data)
            avg_cpa = statistics.mean(float(m['cpa']) for m in tiktok_data)
            total_purchases = sum(int(m['purchases']) for m in tiktok_data)
            
            platforms.append({
                'name': 'TikTok Ads',
                'spend': total_spend,
                'revenue': total_revenue,
                'roas': avg_roas,
                'cpa': avg_cpa,
                'cpc': statistics.mean(float(m['cpc']) for m in tiktok_data),
                'campaigns': len(tiktok_data),
                'purchases': total_purchases
            })
        
        # Display comparison table
        print(f"{'Platform':<12} {'Spend':<12} {'Revenue':<12} {'ROAS':<8} {'CPA':<8} {'CPC':<8} {'Purchases'}")
        print("-" * 85)
        
        total_spend = 0
        total_revenue = 0
        
        for platform in platforms:
            print(f"{platform['name']:<12} ${platform['spend']:<11,.0f} ${platform['revenue']:<11,.0f} "
                  f"{platform['roas']:<7.2f} ${platform['cpa']:<7.2f} ${platform['cpc']:<7.2f} {platform['purchases']:,}")
            total_spend += platform['spend']
            total_revenue += platform['revenue']
        
        print("-" * 85)
        print(f"{'TOTAL':<12} ${total_spend:<11,.0f} ${total_revenue:<11,.0f} "
              f"{total_revenue/total_spend:<7.2f} {'N/A':<7} {'N/A':<7} {sum(p['purchases'] for p in platforms):,}")
        
        # Platform efficiency analysis
        print(f"\\n🏆 PLATFORM EFFICIENCY RANKING:")
        platforms_by_roas = sorted(platforms, key=lambda x: x['roas'], reverse=True)
        for i, platform in enumerate(platforms_by_roas, 1):
            efficiency = "🥇 Excellent" if platform['roas'] > 8 else "🥈 Good" if platform['roas'] > 5 else "🥉 Moderate"
            print(f"   {i}. {platform['name']}: {platform['roas']:.2f}x ROAS {efficiency}")
    
    def analyze_meta_ad_performance(self):
        """Deep dive into Meta ad-level performance"""
        print("\\n🔵 META ADS - DETAILED AD-LEVEL ANALYSIS")
        print("=" * 80)
        
        if 'meta_ad_data' not in self.data:
            print("❌ No Meta ad data available")
            return
            
        ad_data = self.data['meta_ad_data']
        grouped_ads = ad_data.get('grouped_ads', [])
        
        if not grouped_ads:
            print("❌ No grouped ads data available")
            return
        
        print(f"📊 Analyzing {len(grouped_ads)} Meta ad groups ({ad_data.get('count', 0)} total ads)")
        
        # Category performance analysis
        category_stats = defaultdict(lambda: {
            'spend': 0, 'revenue': 0, 'ads': 0, 'roas_list': []
        })
        
        format_stats = defaultdict(lambda: {
            'spend': 0, 'revenue': 0, 'ads': 0, 'roas_list': []
        })
        
        all_ads = []
        
        for ad_group in grouped_ads:
            if 'weekly_data' in ad_group:
                for week in ad_group['weekly_data']:
                    spend = float(week.get('spend', 0))
                    revenue = float(week.get('revenue', 0))
                    roas = float(week.get('roas', 0))
                    category = week.get('category', 'Unknown')
                    format_type = week.get('format', 'Unknown')
                    
                    # Category stats
                    category_stats[category]['spend'] += spend
                    category_stats[category]['revenue'] += revenue
                    category_stats[category]['ads'] += 1
                    if roas > 0:
                        category_stats[category]['roas_list'].append(roas)
                    
                    # Format stats
                    format_stats[format_type]['spend'] += spend
                    format_stats[format_type]['revenue'] += revenue
                    format_stats[format_type]['ads'] += 1
                    if roas > 0:
                        format_stats[format_type]['roas_list'].append(roas)
                    
                    # Store for top performers
                    all_ads.append({
                        'name': ad_group.get('ad_name', 'Unknown'),
                        'spend': spend,
                        'revenue': revenue,
                        'roas': roas,
                        'category': category,
                        'format': format_type,
                        'week_start': week.get('week_start')
                    })
        
        # Category performance table
        print(f"\\n🏷️ CATEGORY PERFORMANCE:")
        print(f"{'Category':<20} {'Spend':<12} {'Revenue':<12} {'ROAS':<8} {'Ads':<6}")
        print("-" * 70)
        
        for category, stats in sorted(category_stats.items(), key=lambda x: x[1]['spend'], reverse=True):
            if stats['spend'] > 0:
                avg_roas = statistics.mean(stats['roas_list']) if stats['roas_list'] else 0
                print(f"{category:<20} ${stats['spend']:<11,.0f} ${stats['revenue']:<11,.0f} "
                      f"{avg_roas:<7.2f} {stats['ads']}")
        
        # Format performance table
        print(f"\\n🎨 CREATIVE FORMAT PERFORMANCE:")
        print(f"{'Format':<15} {'Spend':<12} {'Revenue':<12} {'ROAS':<8} {'Ads':<6}")
        print("-" * 65)
        
        for format_type, stats in sorted(format_stats.items(), key=lambda x: x[1]['spend'], reverse=True):
            if stats['spend'] > 0:
                avg_roas = statistics.mean(stats['roas_list']) if stats['roas_list'] else 0
                print(f"{format_type:<15} ${stats['spend']:<11,.0f} ${stats['revenue']:<11,.0f} "
                      f"{avg_roas:<7.2f} {stats['ads']}")
        
        # Top performing ads
        high_spend_ads = [ad for ad in all_ads if ad['spend'] > 500]
        top_by_spend = sorted(all_ads, key=lambda x: x['spend'], reverse=True)[:10]
        top_by_roas = sorted(high_spend_ads, key=lambda x: x['roas'], reverse=True)[:10]
        
        print(f"\\n💰 TOP 10 ADS BY SPEND:")
        for i, ad in enumerate(top_by_spend, 1):
            print(f"   {i:2}. {ad['name'][:45]}... - ${ad['spend']:,.0f} (ROAS: {ad['roas']:.2f}) [{ad['category']}]")
        
        if high_spend_ads:
            print(f"\\n📈 TOP 10 ADS BY ROAS (Min $500 spend):")
            for i, ad in enumerate(top_by_roas, 1):
                print(f"   {i:2}. {ad['name'][:45]}... - ROAS: {ad['roas']:.2f} (${ad['spend']:,.0f}) [{ad['category']}]")
    
    def analyze_temporal_trends(self):
        """Analyze performance trends over time"""
        print("\\n📅 TEMPORAL PERFORMANCE TRENDS")
        print("=" * 80)
        
        if 'monthly_summary' not in self.data or 'monthly_breakdown' not in self.data['monthly_summary']:
            print("❌ No monthly trend data available")
            return
        
        monthly_data = self.data['monthly_summary']['monthly_breakdown']
        
        # Recent performance (last 6 months)
        print(f"\\n📊 RECENT 6-MONTH PERFORMANCE TREND:")
        print(f"{'Month':<10} {'Spend':<12} {'Revenue':<12} {'ROAS':<8} {'CPA':<8} {'Purchases':<10} {'Momentum'}")
        print("-" * 85)
        
        recent_months = monthly_data[:6]
        for i, month in enumerate(recent_months):
            momentum = ""
            if i > 0:
                prev_roas = recent_months[i-1]['roas']
                curr_roas = month['roas']
                if curr_roas > prev_roas * 1.1:
                    momentum = "📈"
                elif curr_roas < prev_roas * 0.9:
                    momentum = "📉"
                else:
                    momentum = "➡️"
            
            print(f"{month['month']:<10} ${month['amount_spent_usd']:<11,.0f} "
                  f"${month['purchases_conversion_value']:<11,.0f} "
                  f"{month['roas']:<7.2f} ${month['cpa']:<7.2f} "
                  f"{month['website_purchases']:<10} {momentum}")
        
        # Performance insights
        if len(recent_months) >= 3:
            roas_trend = [m['roas'] for m in recent_months[:3]]
            spend_trend = [m['amount_spent_usd'] for m in recent_months[:3]]
            
            print(f"\\n🎯 PERFORMANCE INSIGHTS:")
            print(f"   Recent 3-month ROAS: {roas_trend[2]:.2f} → {roas_trend[1]:.2f} → {roas_trend[0]:.2f}")
            print(f"   Recent 3-month spend: ${spend_trend[2]:,.0f} → ${spend_trend[1]:,.0f} → ${spend_trend[0]:,.0f}")
            
            # Trend analysis
            if roas_trend[0] > roas_trend[2]:
                print(f"   📈 ROAS trending upward: +{((roas_trend[0]/roas_trend[2])-1)*100:.1f}% vs 3 months ago")
            elif roas_trend[0] < roas_trend[2]:
                print(f"   📉 ROAS trending downward: {((roas_trend[0]/roas_trend[2])-1)*100:.1f}% vs 3 months ago")
            else:
                print(f"   ➡️ ROAS stable over last 3 months")
    
    def generate_strategic_recommendations(self):
        """Generate actionable strategic recommendations"""
        print("\\n💡 STRATEGIC RECOMMENDATIONS & ACTION PLAN")
        print("=" * 80)
        
        recommendations = []
        
        # Platform allocation recommendations
        if 'monthly_summary' in self.data and 'google_monthly' in self.data and 'tiktok_monthly' in self.data:
            meta_roas = self.data['monthly_summary']['summary']['avg_roas']
            google_roas = statistics.mean(float(m['roas']) for m in self.data['google_monthly'])
            tiktok_roas = statistics.mean(float(m['roas']) for m in self.data['tiktok_monthly'])
            
            platforms = [('Meta', meta_roas), ('Google', google_roas), ('TikTok', tiktok_roas)]
            platforms.sort(key=lambda x: x[1], reverse=True)
            
            recommendations.extend([
                "🎯 PLATFORM BUDGET ALLOCATION:",
                f"   1. {platforms[0][0]} Ads (ROAS: {platforms[0][1]:.2f}) - INCREASE budget by 15-20%",
                f"   2. {platforms[1][0]} Ads (ROAS: {platforms[1][1]:.2f}) - MAINTAIN current levels",
                f"   3. {platforms[2][0]} Ads (ROAS: {platforms[2][1]:.2f}) - {'OPTIMIZE' if platforms[2][1] < 4 else 'STABLE'} campaigns"
            ])
        
        # Performance momentum recommendations
        if 'monthly_summary' in self.data:
            recent = self.data['monthly_summary']['monthly_breakdown'][:3]
            if len(recent) >= 3:
                current_roas = recent[0]['roas']
                if current_roas > 6:
                    recommendations.extend([
                        "🚀 SCALING OPPORTUNITY:",
                        f"   Current ROAS ({current_roas:.2f}) indicates strong performance",
                        "   → Test 25-30% budget increases on top campaigns",
                        "   → Expand to similar audience segments"
                    ])
                elif current_roas < 4:
                    recommendations.extend([
                        "⚠️ OPTIMIZATION URGENT:",
                        f"   Current ROAS ({current_roas:.2f}) below profitability threshold",
                        "   → Immediate creative refresh needed",
                        "   → Review audience targeting",
                        "   → Consider reducing budget until ROAS improves"
                    ])
        
        # Category-specific recommendations
        recommendations.extend([
            "🏷️ CATEGORY OPTIMIZATION:",
            "   → Focus on highest ROAS product categories for expansion",
            "   → Develop category-specific landing pages",
            "   → Create seasonal category campaigns",
            "",
            "🎨 CREATIVE STRATEGY:",
            "   → A/B test top-performing ad formats",
            "   → Refresh creative assets monthly",
            "   → Test User-Generated Content (UGC) vs Brand content",
            "",
            "📊 MONITORING & OPTIMIZATION:",
            "   → Set up weekly ROAS alerts (threshold: 4.0)",
            "   → Implement daily budget pacing checks",
            "   → Monthly competitive analysis",
            "   → Quarterly strategic review sessions"
        ])
        
        for rec in recommendations:
            print(rec)
        
        # Action timeline
        print(f"\\n⏰ IMMEDIATE ACTION TIMELINE:")
        print(f"   📅 Week 1: Implement budget reallocation based on platform performance")
        print(f"   📅 Week 2: Launch creative refresh for underperforming categories")  
        print(f"   📅 Week 3: Set up automated monitoring and alert systems")
        print(f"   📅 Week 4: Begin scaling tests on top-performing campaigns")
        print(f"   📅 Month 2: Full strategic review and optimization cycle")
    
    def generate_executive_summary(self):
        """Generate executive summary for leadership"""
        print("\\n📋 EXECUTIVE SUMMARY")
        print("=" * 80)
        
        if 'monthly_summary' in self.data:
            summary = self.data['monthly_summary']['summary']
            
            print(f"🏢 HOUSE OF NOA - ADVERTISING PERFORMANCE OVERVIEW")
            print(f"📅 Analysis Period: January 2024 - August 2025 (20 months)")
            print(f"📊 Data Sources: Meta Ads, Google Ads, TikTok Ads")
            print(f"")
            print(f"💰 FINANCIAL PERFORMANCE:")
            print(f"   Total Investment: ${summary['total_spend']:,.0f}")
            print(f"   Total Revenue Generated: ${summary['total_revenue']:,.0f}")
            print(f"   Net Profit: ${summary['total_revenue'] - summary['total_spend']:,.0f}")
            print(f"   Return on Ad Spend (ROAS): {summary['avg_roas']:.2f}x")
            print(f"   Return on Investment (ROI): {((summary['avg_roas'] - 1) * 100):.1f}%")
            print(f"")
            print(f"🎯 KEY METRICS:")
            print(f"   Average Cost Per Acquisition: ${summary['avg_cpa']:.2f}")
            print(f"   Average Cost Per Click: ${summary['avg_cpc']:.2f}")
            print(f"   Total Customer Acquisitions: {summary['total_purchases']:,}")
            print(f"   Active Campaigns: {summary['campaign_count']}")
            print(f"")
            
            # Business health indicators
            health_score = "EXCELLENT" if summary['avg_roas'] > 6 else "GOOD" if summary['avg_roas'] > 4 else "NEEDS ATTENTION"
            print(f"📈 BUSINESS HEALTH SCORE: {health_score}")
            
            if summary['avg_roas'] > 5:
                print(f"   ✅ Strong profitability across advertising channels")
                print(f"   ✅ Efficient customer acquisition costs")
                print(f"   ✅ Sustainable growth trajectory")
            elif summary['avg_roas'] > 4:
                print(f"   ✅ Profitable advertising performance")
                print(f"   ⚠️ Room for optimization improvements")
                print(f"   ➡️ Monitor performance trends closely")
            else:
                print(f"   ⚠️ Below profitability threshold - immediate action needed")
                print(f"   🔧 Urgent optimization required")
                print(f"   📉 Consider budget reduction until ROAS improves")
        
        print(f"\\n🎯 STRATEGIC PRIORITY: Maintain strong ROAS while scaling successful campaigns")
    
    def run_comprehensive_analysis(self):
        """Run the complete business intelligence analysis"""
        print("🏢 HON AUTOMATED REPORTING - COMPREHENSIVE BUSINESS INTELLIGENCE")
        print("=" * 90)
        print(f"📅 Report Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}")
        print(f"🔬 Analysis Type: Cross-Platform Performance & Strategic Recommendations")
        
        # Fetch all data
        self.fetch_comprehensive_data()
        
        # Run all analyses
        self.generate_executive_summary()
        self.analyze_platform_comparison()
        self.analyze_meta_ad_performance()
        self.analyze_temporal_trends()
        self.generate_strategic_recommendations()
        
        print(f"\\n✅ COMPREHENSIVE BUSINESS INTELLIGENCE ANALYSIS COMPLETE")
        print("=" * 90)

if __name__ == "__main__":
    bi_agent = HONComprehensiveBI()
    bi_agent.run_comprehensive_analysis()