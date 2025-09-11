#!/usr/bin/env python3
"""
HON Automated Reporting - Business Intelligence Analysis
Comprehensive analysis of advertising performance across Meta, Google, and TikTok platforms
"""

import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

class HONBusinessIntelligenceAgent:
    def __init__(self):
        self.base_url = "http://localhost:8007"
        self.data = {}
        
    def fetch_all_data(self):
        """Fetch comprehensive data from all API endpoints"""
        print("🔄 Fetching comprehensive HON advertising data...")
        
        endpoints = {
            'monthly_campaigns': '/api/reports/monthly',
            'meta_ad_summary': '/api/meta-ad-reports/summary',
            'meta_filters': '/api/meta-ad-reports/filters',
            'google_monthly': '/api/google-reports/monthly',
            'tiktok_monthly': '/api/tiktok-reports/monthly',
            'meta_ads': '/api/meta-ad-reports/ad-data?limit=1000'  # High limit for comprehensive analysis
        }
        
        for key, endpoint in endpoints.items():
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
                if response.status_code == 200:
                    self.data[key] = response.json()
                    print(f"✅ Fetched {key}: {len(self.data[key]) if isinstance(self.data[key], list) else 'success'}")
                else:
                    print(f"❌ Failed to fetch {key}: {response.status_code}")
            except Exception as e:
                print(f"❌ Error fetching {key}: {str(e)}")
    
    def analyze_platform_performance(self):
        """Analyze performance across Meta, Google, and TikTok platforms"""
        print("\n📊 PLATFORM PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        # Meta Ads Analysis (from monthly campaigns - primary platform)
        if 'monthly_campaigns' in self.data:
            meta_data = self.data['monthly_campaigns']['summary']
            print(f"\n🔵 META ADS PERFORMANCE:")
            print(f"   Total Spend: ${meta_data['total_spend']:,.2f}")
            print(f"   Total Revenue: ${meta_data['total_revenue']:,.2f}")
            print(f"   Average ROAS: {meta_data['avg_roas']:.2f}")
            print(f"   Average CPA: ${meta_data['avg_cpa']:.2f}")
            print(f"   Average CPC: ${meta_data['avg_cpc']:.2f}")
            print(f"   Campaign Count: {meta_data['campaign_count']}")
            
        # Google Ads Analysis
        if 'google_monthly' in self.data:
            google_data = self.data['google_monthly']
            total_spend = sum(float(month['spend']) for month in google_data)
            total_revenue = sum(float(month['revenue']) for month in google_data)
            avg_roas = statistics.mean(float(month['roas']) for month in google_data)
            avg_cpa = statistics.mean(float(month['cpa']) for month in google_data)
            
            print(f"\n🟢 GOOGLE ADS PERFORMANCE:")
            print(f"   Total Spend: ${total_spend:,.2f}")
            print(f"   Total Revenue: ${total_revenue:,.2f}")
            print(f"   Average ROAS: {avg_roas:.2f}")
            print(f"   Average CPA: ${avg_cpa:.2f}")
            print(f"   Month Count: {len(google_data)}")
            
        # TikTok Ads Analysis
        if 'tiktok_monthly' in self.data:
            tiktok_data = self.data['tiktok_monthly']
            total_spend = sum(float(month['spend']) for month in tiktok_data)
            total_revenue = sum(float(month['revenue']) for month in tiktok_data)
            avg_roas = statistics.mean(float(month['roas']) for month in tiktok_data)
            avg_cpa = statistics.mean(float(month['cpa']) for month in tiktok_data)
            
            print(f"\n🔴 TIKTOK ADS PERFORMANCE:")
            print(f"   Total Spend: ${total_spend:,.2f}")
            print(f"   Total Revenue: ${total_revenue:,.2f}")
            print(f"   Average ROAS: {avg_roas:.2f}")
            print(f"   Average CPA: ${avg_cpa:.2f}")
            print(f"   Month Count: {len(tiktok_data)}")
    
    def analyze_category_performance(self):
        """Analyze product category performance"""
        print("\n🏷️ PRODUCT CATEGORY ANALYSIS")
        print("=" * 60)
        
        if 'meta_filters' in self.data:
            categories = self.data['meta_filters']['categories']
            print(f"Available Product Categories: {', '.join(categories)}")
            
        if 'meta_ads' in self.data:
            ads_data = self.data['meta_ads']
            category_stats = defaultdict(lambda: {'spend': 0, 'revenue': 0, 'ads': 0, 'roas_list': []})
            
            for ad in ads_data:
                if isinstance(ad, dict):
                    category = ad.get('category', 'Unknown')
                    spend = float(ad.get('total_spend', 0))
                    revenue = float(ad.get('total_revenue', 0))
                    roas = float(ad.get('roas', 0))
                    
                    category_stats[category]['spend'] += spend
                    category_stats[category]['revenue'] += revenue
                    category_stats[category]['ads'] += 1
                    if roas > 0:
                        category_stats[category]['roas_list'].append(roas)
            
            print(f"\n📈 CATEGORY PERFORMANCE (Ad-Level Data):")
            for category, stats in sorted(category_stats.items(), key=lambda x: x[1]['spend'], reverse=True):
                avg_roas = statistics.mean(stats['roas_list']) if stats['roas_list'] else 0
                print(f"\n   {category}:")
                print(f"     Spend: ${stats['spend']:,.2f}")
                print(f"     Revenue: ${stats['revenue']:,.2f}")
                print(f"     Ad Count: {stats['ads']}")
                print(f"     Average ROAS: {avg_roas:.2f}")
                print(f"     Category ROAS: {stats['revenue']/stats['spend']:.2f}" if stats['spend'] > 0 else "     Category ROAS: N/A")
    
    def analyze_temporal_trends(self):
        """Analyze performance trends over time"""
        print("\n📅 TEMPORAL TRENDS ANALYSIS")
        print("=" * 60)
        
        if 'monthly_campaigns' in self.data:
            monthly_breakdown = self.data['monthly_campaigns']['monthly_breakdown']
            
            print(f"\n📊 MONTHLY PERFORMANCE TRENDS:")
            print(f"{'Month':<10} {'Spend':<12} {'Revenue':<12} {'ROAS':<8} {'CPA':<8} {'Purchases'}")
            print("-" * 70)
            
            for month_data in monthly_breakdown[:12]:  # Last 12 months
                month = month_data['month']
                spend = month_data['amount_spent_usd']
                revenue = month_data['purchases_conversion_value']
                roas = month_data['roas']
                cpa = month_data['cpa']
                purchases = month_data['website_purchases']
                
                print(f"{month:<10} ${spend:<11,.0f} ${revenue:<11,.0f} {roas:<7.2f} ${cpa:<7.2f} {purchases}")
            
            # Performance momentum analysis
            recent_months = monthly_breakdown[:3]  # Last 3 months
            if len(recent_months) >= 3:
                roas_trend = [month['roas'] for month in recent_months]
                spend_trend = [month['amount_spent_usd'] for month in recent_months]
                
                print(f"\n🎯 RECENT PERFORMANCE MOMENTUM:")
                print(f"   ROAS Trend (3 months): {roas_trend[2]:.2f} → {roas_trend[1]:.2f} → {roas_trend[0]:.2f}")
                print(f"   Spend Trend (3 months): ${spend_trend[2]:,.0f} → ${spend_trend[1]:,.0f} → ${spend_trend[0]:,.0f}")
                
                roas_momentum = "📈 Improving" if roas_trend[0] > roas_trend[2] else "📉 Declining" if roas_trend[0] < roas_trend[2] else "➡️ Stable"
                spend_momentum = "📈 Increasing" if spend_trend[0] > spend_trend[2] else "📉 Decreasing" if spend_trend[0] < spend_trend[2] else "➡️ Stable"
                
                print(f"   ROAS Momentum: {roas_momentum}")
                print(f"   Spend Momentum: {spend_momentum}")
    
    def analyze_creative_formats(self):
        """Analyze creative format performance"""
        print("\n🎨 CREATIVE FORMAT ANALYSIS")
        print("=" * 60)
        
        if 'meta_filters' in self.data:
            formats = self.data['meta_filters']['formats']
            content_types = self.data['meta_filters']['content_types']
            optimizations = self.data['meta_filters']['campaign_optimizations']
            
            print(f"Available Formats: {', '.join(formats)}")
            print(f"Content Types: {', '.join(content_types)}")
            print(f"Campaign Optimizations: {', '.join(optimizations)}")
            
        if 'meta_ads' in self.data:
            ads_data = self.data['meta_ads']
            format_stats = defaultdict(lambda: {'spend': 0, 'revenue': 0, 'ads': 0, 'roas_list': []})
            content_stats = defaultdict(lambda: {'spend': 0, 'revenue': 0, 'ads': 0, 'roas_list': []})
            
            for ad in ads_data:
                if isinstance(ad, dict):
                    format_type = ad.get('format', 'Unknown')
                    content_type = ad.get('content_type', 'Unknown')
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
            
            print(f"\n📹 FORMAT PERFORMANCE:")
            for format_type, stats in sorted(format_stats.items(), key=lambda x: x[1]['spend'], reverse=True):
                avg_roas = statistics.mean(stats['roas_list']) if stats['roas_list'] else 0
                print(f"   {format_type}: ${stats['spend']:,.0f} spend, {avg_roas:.2f} avg ROAS, {stats['ads']} ads")
                
            print(f"\n📝 CONTENT TYPE PERFORMANCE:")
            for content_type, stats in sorted(content_stats.items(), key=lambda x: x[1]['spend'], reverse=True):
                avg_roas = statistics.mean(stats['roas_list']) if stats['roas_list'] else 0
                print(f"   {content_type}: ${stats['spend']:,.0f} spend, {avg_roas:.2f} avg ROAS, {stats['ads']} ads")
    
    def generate_strategic_recommendations(self):
        """Generate strategic recommendations based on analysis"""
        print("\n💡 STRATEGIC RECOMMENDATIONS")
        print("=" * 60)
        
        recommendations = []
        
        # Platform allocation recommendations
        if 'monthly_campaigns' in self.data and 'google_monthly' in self.data and 'tiktok_monthly' in self.data:
            meta_roas = self.data['monthly_campaigns']['summary']['avg_roas']
            google_roas = statistics.mean(float(month['roas']) for month in self.data['google_monthly'])
            tiktok_roas = statistics.mean(float(month['roas']) for month in self.data['tiktok_monthly'])
            
            platform_performance = [
                ("Meta Ads", meta_roas),
                ("Google Ads", google_roas),
                ("TikTok Ads", tiktok_roas)
            ]
            platform_performance.sort(key=lambda x: x[1], reverse=True)
            
            recommendations.append(f"🎯 PLATFORM OPTIMIZATION:")
            recommendations.append(f"   Best performing platform: {platform_performance[0][0]} (ROAS: {platform_performance[0][1]:.2f})")
            recommendations.append(f"   Consider increasing budget allocation to {platform_performance[0][0]}")
            if platform_performance[2][1] < 4.0:
                recommendations.append(f"   Review {platform_performance[2][0]} strategy (ROAS: {platform_performance[2][1]:.2f} below 4.0 threshold)")
        
        # Temporal recommendations
        if 'monthly_campaigns' in self.data:
            recent_months = self.data['monthly_campaigns']['monthly_breakdown'][:3]
            if len(recent_months) >= 3:
                recent_roas = [month['roas'] for month in recent_months]
                if recent_roas[0] > recent_roas[2]:
                    recommendations.append(f"📈 MOMENTUM OPPORTUNITY:")
                    recommendations.append(f"   ROAS is improving ({recent_roas[2]:.2f} → {recent_roas[0]:.2f})")
                    recommendations.append(f"   Consider scaling spend while maintaining current optimization approach")
                elif recent_roas[0] < recent_roas[2]:
                    recommendations.append(f"⚠️ PERFORMANCE ALERT:")
                    recommendations.append(f"   ROAS is declining ({recent_roas[2]:.2f} → {recent_roas[0]:.2f})")
                    recommendations.append(f"   Review recent creative changes and campaign optimizations")
        
        # Budget efficiency recommendations
        if 'monthly_campaigns' in self.data:
            summary = self.data['monthly_campaigns']['summary']
            if summary['avg_roas'] > 6.0:
                recommendations.append(f"🚀 SCALING OPPORTUNITY:")
                recommendations.append(f"   Strong ROAS ({summary['avg_roas']:.2f}) suggests room for budget increases")
                recommendations.append(f"   Test 20-30% budget increases on top-performing campaigns")
            elif summary['avg_roas'] < 4.0:
                recommendations.append(f"🔧 OPTIMIZATION NEEDED:")
                recommendations.append(f"   ROAS ({summary['avg_roas']:.2f}) below target threshold")
                recommendations.append(f"   Focus on creative refresh and audience optimization")
        
        print("\n".join(recommendations))
        
        # Action items
        print(f"\n🎯 IMMEDIATE ACTION ITEMS:")
        print(f"   1. Review top 10 highest-spending ads for creative patterns")
        print(f"   2. Analyze category performance trends for budget reallocation") 
        print(f"   3. Test creative format variations based on performance data")
        print(f"   4. Implement weekly performance monitoring for quick optimizations")
        print(f"   5. Set up automated alerts for ROAS drops below 4.0 threshold")
    
    def generate_executive_summary(self):
        """Generate executive summary for stakeholders"""
        print("\n📋 EXECUTIVE SUMMARY")
        print("=" * 60)
        
        if 'monthly_campaigns' in self.data:
            summary = self.data['monthly_campaigns']['summary']
            
            print(f"📊 KEY PERFORMANCE INDICATORS (Last 20 Months):")
            print(f"   💰 Total Ad Spend: ${summary['total_spend']:,.0f}")
            print(f"   💵 Total Revenue: ${summary['total_revenue']:,.0f}")
            print(f"   📈 Overall ROAS: {summary['avg_roas']:.2f}x")
            print(f"   🎯 Average CPA: ${summary['avg_cpa']:.2f}")
            print(f"   🖱️ Average CPC: ${summary['avg_cpc']:.2f}")
            print(f"   📱 Total Campaigns: {summary['campaign_count']}")
            print(f"   🛒 Total Purchases: {summary['total_purchases']:,}")
            
            roi_percentage = (summary['avg_roas'] - 1) * 100
            print(f"\n💡 BUSINESS IMPACT:")
            print(f"   📊 Return on Investment: {roi_percentage:.1f}%")
            print(f"   💎 Profit Generated: ${summary['total_revenue'] - summary['total_spend']:,.0f}")
            
            efficiency_score = "Excellent" if summary['avg_roas'] > 6 else "Good" if summary['avg_roas'] > 4 else "Needs Improvement"
            print(f"   🎯 Efficiency Rating: {efficiency_score}")
        
        if 'meta_ad_summary' in self.data:
            meta_summary = self.data['meta_ad_summary']
            print(f"\n🔵 RECENT AD-LEVEL PERFORMANCE ({meta_summary['date_range']}):")
            print(f"   📱 Active Ads: {meta_summary['total_ads']}")
            print(f"   💰 Recent Spend: ${meta_summary['total_spend']:,.0f}")
            print(f"   💵 Recent Revenue: ${meta_summary['total_revenue']:,.0f}")
            print(f"   📈 Recent ROAS: {meta_summary['avg_roas']:.2f}x")
    
    def run_complete_analysis(self):
        """Run complete business intelligence analysis"""
        print("🏢 HON AUTOMATED REPORTING - BUSINESS INTELLIGENCE ANALYSIS")
        print("=" * 80)
        print(f"📅 Analysis Date: {datetime.now().strftime('%B %d, %Y at %H:%M')}")
        
        # Fetch all data
        self.fetch_all_data()
        
        # Run all analyses
        self.generate_executive_summary()
        self.analyze_platform_performance()
        self.analyze_category_performance()
        self.analyze_temporal_trends()
        self.analyze_creative_formats()
        self.generate_strategic_recommendations()
        
        print(f"\n✅ Business Intelligence Analysis Complete")
        print(f"📊 Report generated with {sum(len(v) if isinstance(v, list) else 1 for v in self.data.values())} data points")
        print("=" * 80)

if __name__ == "__main__":
    agent = HONBusinessIntelligenceAgent()
    agent.run_complete_analysis()