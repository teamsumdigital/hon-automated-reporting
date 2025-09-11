#!/usr/bin/env python3
"""
HON Meta Ads Week-over-Week Business Intelligence Analysis
=========================================================

Performs comprehensive week-over-week performance analysis focusing on:
- Weekly performance trends and momentum
- Performance drivers and growth analysis
- Category and campaign performance
- Strategic recommendations for optimization

Author: Business Intelligence Agent
Date: August 28, 2025
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from supabase import create_client, Client
from loguru import logger
import json

# Load environment variables
load_dotenv()

class MetaAdsWoWAnalyzer:
    """Week-over-Week Meta Ads Performance Analyzer"""
    
    def __init__(self):
        """Initialize the analyzer with database connection"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials not found in environment variables")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Configure logging
        logger.add("logs/meta_ads_wow_analysis.log", rotation="1 day", retention="7 days")
        logger.info("🚀 Meta Ads WoW Analyzer initialized")
    
    def get_meta_campaign_data(self, weeks_back: int = 8) -> pd.DataFrame:
        """Fetch Meta campaign data for recent weeks"""
        try:
            # Calculate date range for analysis
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=weeks_back * 7)
            
            logger.info(f"📅 Fetching Meta campaign data from {start_date} to {end_date}")
            
            # Query campaign data using reporting_starts as the date field
            response = self.supabase.table('campaign_data').select('*').gte(
                'reporting_starts', start_date.isoformat()
            ).lte('reporting_starts', end_date.isoformat()).order('reporting_starts', desc=False).execute()
            
            if not response.data:
                logger.warning("⚠️ No campaign data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(response.data)
            logger.info(f"✅ Retrieved {len(df)} campaign records")
            
            # Map column names to standard format for analysis
            column_mapping = {
                'reporting_starts': 'date',
                'amount_spent_usd': 'spend',
                'purchases_conversion_value': 'revenue',
                'website_purchases': 'purchases',
                'link_clicks': 'clicks'
            }
            
            # Rename columns to standard format
            df = df.rename(columns=column_mapping)
            
            # Convert date column and add week calculations
            df['date'] = pd.to_datetime(df['date'])
            df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.dayofweek, unit='D')
            df['week_number'] = df['date'].dt.isocalendar().week
            df['year_week'] = df['date'].dt.strftime('%Y-W%U')
            
            # Ensure numeric columns are properly typed
            numeric_columns = ['spend', 'revenue', 'purchases', 'clicks', 'impressions', 'cpm', 'cpc', 'roas', 'cpa']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error fetching campaign data: {str(e)}")
            return pd.DataFrame()
    
    def get_meta_ad_level_data(self, weeks_back: int = 8) -> pd.DataFrame:
        """Fetch Meta ad-level data for detailed analysis"""
        try:
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=weeks_back * 7)
            
            logger.info(f"📊 Fetching Meta ad-level data from {start_date} to {end_date}")
            
            # Query ad-level data using reporting_starts as the date field
            response = self.supabase.table('meta_ad_data').select('*').gte(
                'reporting_starts', start_date.isoformat()
            ).lte('reporting_starts', end_date.isoformat()).order('reporting_starts', desc=False).execute()
            
            if not response.data:
                logger.warning("⚠️ No ad-level data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(response.data)
            logger.info(f"✅ Retrieved {len(df)} ad-level records")
            
            # Map column names to standard format for analysis
            column_mapping = {
                'reporting_starts': 'date',
                'amount_spent_usd': 'spend',
                'purchases_conversion_value': 'revenue',
                'purchases': 'purchases',
                'link_clicks': 'clicks'
            }
            
            # Rename columns to standard format
            df = df.rename(columns=column_mapping)
            
            # Add week calculations
            df['date'] = pd.to_datetime(df['date'])
            df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.dayofweek, unit='D')
            df['year_week'] = df['date'].dt.strftime('%Y-W%U')
            
            # Ensure numeric columns are properly typed
            numeric_columns = ['spend', 'revenue', 'purchases', 'clicks', 'impressions']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Calculate ROAS and other derived metrics
            df['roas'] = np.where(df['spend'] > 0, df['revenue'] / df['spend'], 0)
            df['cpa'] = np.where(df['purchases'] > 0, df['spend'] / df['purchases'], 0)
            df['cpc'] = np.where(df['clicks'] > 0, df['spend'] / df['clicks'], 0)
            df['cpm'] = np.where(df['impressions'] > 0, (df['spend'] / df['impressions']) * 1000, 0)
            df['ctr'] = np.where(df['impressions'] > 0, (df['clicks'] / df['impressions']) * 100, 0)
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error fetching ad-level data: {str(e)}")
            return pd.DataFrame()
    
    def calculate_weekly_aggregates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate weekly performance aggregates"""
        if df.empty:
            return pd.DataFrame()
        
        logger.info("📈 Calculating weekly aggregates")
        
        # Define aggregation dict based on available columns
        agg_dict = {
            'spend': 'sum',
            'revenue': 'sum',
            'purchases': 'sum'
        }
        
        # Add optional columns if they exist
        optional_columns = {
            'impressions': 'sum',
            'clicks': 'sum',
            'cpm': 'mean',
            'cpc': 'mean',
            'ctr': 'mean',
            'roas': 'mean',
            'cpa': 'mean'
        }
        
        for col, agg_func in optional_columns.items():
            if col in df.columns:
                agg_dict[col] = agg_func
        
        # Weekly aggregation
        weekly_metrics = df.groupby(['year_week', 'week_start']).agg(agg_dict).reset_index()
        
        # Calculate derived metrics if base columns exist
        if 'spend' in weekly_metrics.columns and 'revenue' in weekly_metrics.columns:
            weekly_metrics['roas'] = np.where(
                weekly_metrics['spend'] > 0,
                weekly_metrics['revenue'] / weekly_metrics['spend'],
                0
            )
        
        if 'spend' in weekly_metrics.columns and 'purchases' in weekly_metrics.columns:
            weekly_metrics['cpa'] = np.where(
                weekly_metrics['purchases'] > 0,
                weekly_metrics['spend'] / weekly_metrics['purchases'],
                0
            )
        
        if 'spend' in weekly_metrics.columns and 'clicks' in weekly_metrics.columns:
            weekly_metrics['cpc'] = np.where(
                weekly_metrics['clicks'] > 0,
                weekly_metrics['spend'] / weekly_metrics['clicks'],
                0
            )
        
        if 'impressions' in weekly_metrics.columns and 'spend' in weekly_metrics.columns:
            weekly_metrics['cpm'] = np.where(
                weekly_metrics['impressions'] > 0,
                (weekly_metrics['spend'] / weekly_metrics['impressions']) * 1000,
                0
            )
        
        if 'impressions' in weekly_metrics.columns and 'clicks' in weekly_metrics.columns:
            weekly_metrics['ctr'] = np.where(
                weekly_metrics['impressions'] > 0,
                (weekly_metrics['clicks'] / weekly_metrics['impressions']) * 100,
                0
            )
        
        # Sort by week
        weekly_metrics = weekly_metrics.sort_values('week_start')
        
        # Calculate week-over-week changes for available metrics
        metrics_to_track = ['spend', 'revenue', 'purchases']
        if 'roas' in weekly_metrics.columns:
            metrics_to_track.append('roas')
        if 'cpm' in weekly_metrics.columns:
            metrics_to_track.append('cpm')
        if 'cpc' in weekly_metrics.columns:
            metrics_to_track.append('cpc')
        if 'cpa' in weekly_metrics.columns:
            metrics_to_track.append('cpa')
        
        for metric in metrics_to_track:
            weekly_metrics[f'{metric}_wow_change'] = weekly_metrics[metric].pct_change()
            weekly_metrics[f'{metric}_wow_abs_change'] = weekly_metrics[metric].diff()
        
        logger.info(f"✅ Calculated aggregates for {len(weekly_metrics)} weeks")
        return weekly_metrics
    
    def analyze_category_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze category performance week-over-week"""
        if df.empty:
            return {}
        
        logger.info("🏷️ Analyzing category performance")
        
        # Get recent 2 weeks for comparison
        recent_weeks = df['year_week'].unique()[-2:]
        if len(recent_weeks) < 2:
            return {"error": "Insufficient data for category analysis"}
        
        current_week, previous_week = recent_weeks[-1], recent_weeks[-2]
        
        # Filter data for these weeks
        current_data = df[df['year_week'] == current_week]
        previous_data = df[df['year_week'] == previous_week]
        
        # Category analysis
        category_performance = {}
        
        # Get all categories
        categories = df['category'].unique() if 'category' in df.columns else []
        
        for category in categories:
            if pd.isna(category) or category == 'Unknown':
                continue
                
            current_cat = current_data[current_data['category'] == category]
            previous_cat = previous_data[previous_data['category'] == category]
            
            current_metrics = {
                'spend': current_cat['spend'].sum(),
                'revenue': current_cat['revenue'].sum(),
                'purchases': current_cat['purchases'].sum(),
                'roas': current_cat['revenue'].sum() / current_cat['spend'].sum() if current_cat['spend'].sum() > 0 else 0
            }
            
            previous_metrics = {
                'spend': previous_cat['spend'].sum(),
                'revenue': previous_cat['revenue'].sum(),
                'purchases': previous_cat['purchases'].sum(),
                'roas': previous_cat['revenue'].sum() / previous_cat['spend'].sum() if previous_cat['spend'].sum() > 0 else 0
            }
            
            # Calculate changes
            changes = {}
            for metric in ['spend', 'revenue', 'purchases', 'roas']:
                if previous_metrics[metric] > 0:
                    changes[f'{metric}_change'] = ((current_metrics[metric] - previous_metrics[metric]) / previous_metrics[metric]) * 100
                else:
                    changes[f'{metric}_change'] = 100 if current_metrics[metric] > 0 else 0
            
            category_performance[category] = {
                'current': current_metrics,
                'previous': previous_metrics,
                'changes': changes
            }
        
        return category_performance
    
    def identify_top_performers(self, df: pd.DataFrame, top_n: int = 10) -> Dict[str, List[Dict]]:
        """Identify top performing campaigns and ads"""
        if df.empty:
            return {}
        
        logger.info(f"🏆 Identifying top {top_n} performers")
        
        # Get recent week data
        latest_week = df['year_week'].max()
        latest_data = df[df['year_week'] == latest_week]
        
        # Top campaigns by revenue
        top_revenue = latest_data.nlargest(top_n, 'revenue')[
            ['campaign_name', 'revenue', 'spend', 'roas', 'purchases', 'category']
        ].to_dict('records')
        
        # Top campaigns by ROAS (min $100 spend)
        high_spend = latest_data[latest_data['spend'] >= 100]
        top_roas = high_spend.nlargest(top_n, 'roas')[
            ['campaign_name', 'revenue', 'spend', 'roas', 'purchases', 'category']
        ].to_dict('records')
        
        # Top campaigns by spend
        top_spend = latest_data.nlargest(top_n, 'spend')[
            ['campaign_name', 'revenue', 'spend', 'roas', 'purchases', 'category']
        ].to_dict('records')
        
        return {
            'top_revenue': top_revenue,
            'top_roas': top_roas,
            'top_spend': top_spend,
            'week': latest_week
        }
    
    def calculate_momentum_indicators(self, weekly_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate performance momentum indicators"""
        if len(weekly_data) < 3:
            return {"error": "Insufficient data for momentum calculation"}
        
        logger.info("📊 Calculating momentum indicators")
        
        # Get last 4 weeks for trend analysis
        recent_weeks = weekly_data.tail(4)
        
        momentum = {}
        
        for metric in ['revenue', 'spend', 'roas', 'purchases']:
            values = recent_weeks[metric].values
            
            # Calculate trend (simple linear regression slope)
            x = np.arange(len(values))
            slope = np.polyfit(x, values, 1)[0]
            
            # Calculate acceleration (change in slope)
            if len(values) >= 4:
                first_half_slope = np.polyfit(x[:2], values[:2], 1)[0]
                second_half_slope = np.polyfit(x[2:], values[2:], 1)[0]
                acceleration = second_half_slope - first_half_slope
            else:
                acceleration = 0
            
            # Performance consistency (coefficient of variation)
            consistency = np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
            
            momentum[metric] = {
                'trend_slope': float(slope),
                'acceleration': float(acceleration),
                'consistency': float(consistency),
                'recent_values': values.tolist()
            }
        
        return momentum
    
    def generate_strategic_recommendations(self, 
                                        weekly_data: pd.DataFrame, 
                                        category_performance: Dict, 
                                        top_performers: Dict,
                                        momentum: Dict) -> List[Dict[str, Any]]:
        """Generate strategic recommendations based on analysis"""
        recommendations = []
        
        if weekly_data.empty:
            return recommendations
        
        logger.info("💡 Generating strategic recommendations")
        
        # Get latest week metrics
        latest_week = weekly_data.tail(1).iloc[0]
        
        # Revenue momentum recommendation
        if 'revenue' in momentum and momentum['revenue']['trend_slope'] > 0:
            recommendations.append({
                'type': 'Growth Opportunity',
                'priority': 'High',
                'title': 'Revenue Momentum Detected',
                'description': f"Revenue shows positive trend with slope of {momentum['revenue']['trend_slope']:.2f}. Consider increasing budget on high-performing campaigns.",
                'action': 'Scale top revenue-generating campaigns by 20-30%'
            })
        elif 'revenue' in momentum and momentum['revenue']['trend_slope'] < 0:
            recommendations.append({
                'type': 'Performance Alert',
                'priority': 'High',
                'title': 'Declining Revenue Trend',
                'description': f"Revenue declining with slope of {momentum['revenue']['trend_slope']:.2f}. Review campaign performance and creative fatigue.",
                'action': 'Audit underperforming campaigns and refresh creative assets'
            })
        
        # ROAS optimization recommendation
        if latest_week['roas'] < 2.0:
            recommendations.append({
                'type': 'Efficiency Alert',
                'priority': 'Medium',
                'title': 'ROAS Below Benchmark',
                'description': f"Current ROAS of {latest_week['roas']:.2f} is below optimal threshold of 2.0.",
                'action': 'Focus budget on campaigns with ROAS > 2.5 and pause those below 1.5'
            })
        
        # Category performance recommendations
        if category_performance:
            best_category = None
            best_roas_change = float('-inf')
            
            for category, data in category_performance.items():
                roas_change = data['changes'].get('roas_change', 0)
                if roas_change > best_roas_change:
                    best_roas_change = roas_change
                    best_category = category
            
            if best_category and best_roas_change > 10:
                recommendations.append({
                    'type': 'Category Opportunity',
                    'priority': 'Medium',
                    'title': f'{best_category} Category Performing Well',
                    'description': f"{best_category} shows {best_roas_change:.1f}% ROAS improvement week-over-week.",
                    'action': f'Increase budget allocation to {best_category} campaigns by 15-25%'
                })
        
        # Top performer scaling recommendation
        if 'top_roas' in top_performers and top_performers['top_roas']:
            top_roas_campaign = top_performers['top_roas'][0]
            if top_roas_campaign['roas'] > 3.0:
                recommendations.append({
                    'type': 'Scaling Opportunity',
                    'priority': 'High',
                    'title': 'High ROAS Campaign Ready for Scaling',
                    'description': f"Campaign '{top_roas_campaign['campaign_name']}' has ROAS of {top_roas_campaign['roas']:.2f}.",
                    'action': 'Scale this campaign by 50% and create similar creative variations'
                })
        
        # Spend efficiency recommendation
        total_spend_change = latest_week.get('spend_wow_change', 0)
        revenue_change = latest_week.get('revenue_wow_change', 0)
        
        if total_spend_change > 0.1 and revenue_change < total_spend_change * 0.8:
            recommendations.append({
                'type': 'Efficiency Warning',
                'priority': 'Medium',
                'title': 'Spend Increasing Faster Than Revenue',
                'description': f"Spend increased {total_spend_change:.1%} but revenue only {revenue_change:.1%}.",
                'action': 'Review campaign targeting and bid strategies for efficiency improvements'
            })
        
        logger.info(f"✅ Generated {len(recommendations)} recommendations")
        return recommendations
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """Run the complete week-over-week analysis"""
        logger.info("🔍 Starting comprehensive Meta Ads WoW analysis")
        
        analysis_results = {
            'analysis_date': datetime.now().isoformat(),
            'status': 'success',
            'data_sources': []
        }
        
        try:
            # 1. Fetch campaign data
            campaign_df = self.get_meta_campaign_data()
            if not campaign_df.empty:
                analysis_results['data_sources'].append('campaign_data')
            
            # 2. Fetch ad-level data  
            ad_level_df = self.get_meta_ad_level_data()
            if not ad_level_df.empty:
                analysis_results['data_sources'].append('meta_ad_data')
            
            # Use campaign data as primary source, fall back to ad-level if needed
            primary_df = campaign_df if not campaign_df.empty else ad_level_df
            
            if primary_df.empty:
                analysis_results['status'] = 'error'
                analysis_results['error'] = 'No data available for analysis'
                return analysis_results
            
            # 3. Calculate weekly aggregates
            weekly_data = self.calculate_weekly_aggregates(primary_df)
            analysis_results['weekly_summary'] = weekly_data.to_dict('records')
            
            # 4. Analyze category performance
            category_performance = self.analyze_category_performance(primary_df)
            analysis_results['category_analysis'] = category_performance
            
            # 5. Identify top performers
            top_performers = self.identify_top_performers(primary_df)
            analysis_results['top_performers'] = top_performers
            
            # 6. Calculate momentum indicators
            momentum = self.calculate_momentum_indicators(weekly_data)
            analysis_results['momentum_indicators'] = momentum
            
            # 7. Generate recommendations
            recommendations = self.generate_strategic_recommendations(
                weekly_data, category_performance, top_performers, momentum
            )
            analysis_results['recommendations'] = recommendations
            
            # 8. Generate executive summary
            analysis_results['executive_summary'] = self.generate_executive_summary(
                weekly_data, category_performance, recommendations
            )
            
            logger.info("✅ Meta Ads WoW analysis completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {str(e)}")
            analysis_results['status'] = 'error'
            analysis_results['error'] = str(e)
        
        return analysis_results
    
    def generate_executive_summary(self, weekly_data: pd.DataFrame, 
                                 category_performance: Dict, 
                                 recommendations: List) -> Dict[str, Any]:
        """Generate executive summary of findings"""
        if weekly_data.empty:
            return {"error": "No data for executive summary"}
        
        latest_week = weekly_data.tail(1).iloc[0]
        previous_week = weekly_data.tail(2).head(1).iloc[0] if len(weekly_data) >= 2 else None
        
        summary = {
            'period': f"Week ending {latest_week['week_start'].strftime('%Y-%m-%d')}",
            'key_metrics': {
                'total_spend': float(latest_week['spend']),
                'total_revenue': float(latest_week['revenue']),
                'roas': float(latest_week['roas']),
                'purchases': int(latest_week['purchases']),
                'cpm': float(latest_week['cpm']),
                'cpc': float(latest_week['cpc'])
            }
        }
        
        if previous_week is not None:
            summary['week_over_week_changes'] = {
                'spend_change': float(latest_week.get('spend_wow_change', 0)) * 100,
                'revenue_change': float(latest_week.get('revenue_wow_change', 0)) * 100,
                'roas_change': float(latest_week.get('roas_wow_change', 0)) * 100,
                'purchases_change': float(latest_week.get('purchases_wow_change', 0)) * 100
            }
        
        # Performance status
        roas = latest_week['roas']
        if roas >= 2.5:
            performance_status = "Excellent"
        elif roas >= 2.0:
            performance_status = "Good"
        elif roas >= 1.5:
            performance_status = "Fair"
        else:
            performance_status = "Needs Improvement"
        
        summary['performance_status'] = performance_status
        summary['total_recommendations'] = len(recommendations)
        summary['high_priority_actions'] = len([r for r in recommendations if r.get('priority') == 'High'])
        
        return summary

def main():
    """Main analysis execution"""
    try:
        analyzer = MetaAdsWoWAnalyzer()
        results = analyzer.run_complete_analysis()
        
        # Save results to JSON file
        output_file = f"meta_ads_wow_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n🎯 META ADS WEEK-OVER-WEEK ANALYSIS COMPLETE")
        print(f"📄 Results saved to: {output_file}")
        print(f"📊 Analysis Status: {results.get('status', 'unknown')}")
        
        if results.get('status') == 'success':
            summary = results.get('executive_summary', {})
            print(f"\n📈 EXECUTIVE SUMMARY:")
            print(f"   Period: {summary.get('period', 'N/A')}")
            print(f"   Performance Status: {summary.get('performance_status', 'N/A')}")
            if 'key_metrics' in summary:
                metrics = summary['key_metrics']
                print(f"   Total Spend: ${metrics.get('total_spend', 0):,.2f}")
                print(f"   Total Revenue: ${metrics.get('total_revenue', 0):,.2f}")
                print(f"   ROAS: {metrics.get('roas', 0):.2f}")
            print(f"   Recommendations: {summary.get('total_recommendations', 0)} total, {summary.get('high_priority_actions', 0)} high priority")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Main execution failed: {str(e)}")
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    results = main()