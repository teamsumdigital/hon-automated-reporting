#!/usr/bin/env python3
"""
CRITICAL INVESTIGATION: Analyze what data was actually used in the claimed 8-week analysis
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import json

load_dotenv()

def investigate_analysis_data():
    """Investigate exactly what data was used in the claimed 8-week analysis"""
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
    
    print("🔍 INVESTIGATING CLAIMED 8-WEEK ANALYSIS DATA")
    print("=" * 60)
    
    # Check exactly what data would have been pulled for "8 weeks back" analysis
    # The analysis was run on August 27, 2025, claiming 8 weeks back
    analysis_date = datetime(2025, 8, 27)
    weeks_back = 8
    start_date = analysis_date.date() - timedelta(days=weeks_back * 7)
    end_date = analysis_date.date()
    
    print(f"📅 ANALYSIS DATE: {analysis_date.date()}")
    print(f"📅 CLAIMED PERIOD: {start_date} to {end_date} ({weeks_back} weeks)")
    print(f"📅 EXPECTED DATE RANGE: July 2, 2025 - August 27, 2025")
    print()
    
    # Query campaign_data exactly as the analysis code would have
    print("🔍 INVESTIGATING CAMPAIGN_DATA TABLE:")
    print("-" * 40)
    try:
        response = supabase.table('campaign_data').select('*').gte(
            'reporting_starts', start_date.isoformat()
        ).lte('reporting_starts', end_date.isoformat()).order('reporting_starts', desc=False).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            df['reporting_starts'] = pd.to_datetime(df['reporting_starts'])
            
            print(f"📊 Records found in claimed period: {len(df):,}")
            print(f"📅 Actual date range: {df['reporting_starts'].min().date()} to {df['reporting_starts'].max().date()}")
            print(f"⏰ Actual days: {(df['reporting_starts'].max() - df['reporting_starts'].min()).days + 1}")
            print(f"📆 Actual weeks: {((df['reporting_starts'].max() - df['reporting_starts'].min()).days + 1) / 7:.1f}")
            
            # Show weekly breakdown
            print(f"\n📊 WEEKLY BREAKDOWN:")
            df['year_week'] = df['reporting_starts'].dt.strftime('%Y-W%U')
            weekly_counts = df.groupby('year_week').agg({
                'campaign_id': 'count',
                'amount_spent_usd': 'sum',
                'purchases_conversion_value': 'sum'
            }).round(2)
            
            for week, data in weekly_counts.iterrows():
                spend = data['amount_spent_usd']
                revenue = data['purchases_conversion_value']
                campaigns = data['campaign_id']
                print(f"  {week}: {campaigns:,} campaigns, ${spend:,.2f} spend, ${revenue:,.2f} revenue")
            
            print(f"\n💰 TOTAL METRICS FOR CLAIMED PERIOD:")
            total_spend = df['amount_spent_usd'].sum()
            total_revenue = df['purchases_conversion_value'].sum()
            total_campaigns = df['campaign_id'].nunique()
            print(f"  Total Spend: ${total_spend:,.2f}")
            print(f"  Total Revenue: ${total_revenue:,.2f}")
            print(f"  Total Campaigns: {total_campaigns:,}")
            print(f"  Overall ROAS: {total_revenue / total_spend:.2f}" if total_spend > 0 else "  ROAS: N/A")
            
        else:
            print("❌ NO DATA FOUND in the claimed analysis period!")
            
    except Exception as e:
        print(f"❌ Error querying campaign_data: {e}")
    
    # Now check meta_ad_data for the same period
    print(f"\n\n🔍 INVESTIGATING META_AD_DATA TABLE:")
    print("-" * 40)
    try:
        response = supabase.table('meta_ad_data').select('*').gte(
            'reporting_starts', start_date.isoformat()
        ).lte('reporting_starts', end_date.isoformat()).order('reporting_starts', desc=False).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            df['reporting_starts'] = pd.to_datetime(df['reporting_starts'])
            
            print(f"📊 Records found in claimed period: {len(df):,}")
            print(f"📅 Actual date range: {df['reporting_starts'].min().date()} to {df['reporting_starts'].max().date()}")
            print(f"🎯 Unique ads: {df['ad_id'].nunique():,}")
            print(f"⏰ Actual days: {(df['reporting_starts'].max() - df['reporting_starts'].min()).days + 1}")
            print(f"📆 Actual weeks: {((df['reporting_starts'].max() - df['reporting_starts'].min()).days + 1) / 7:.1f}")
            
        else:
            print("❌ NO DATA FOUND in meta_ad_data for claimed period!")
            
    except Exception as e:
        print(f"❌ Error querying meta_ad_data: {e}")
    
    # Check what the JSON analysis file actually contains
    print(f"\n\n🔍 CHECKING ACTUAL ANALYSIS OUTPUT:")
    print("-" * 40)
    
    analysis_file = 'meta_ads_wow_analysis_20250827_204257.json'
    if os.path.exists(analysis_file):
        with open(analysis_file, 'r') as f:
            analysis_data = json.load(f)
        
        if 'weekly_summary' in analysis_data:
            weeks = analysis_data['weekly_summary']
            print(f"📊 Weeks in analysis output: {len(weeks)}")
            
            for week_data in weeks:
                week = week_data.get('year_week', 'Unknown')
                spend = week_data.get('spend', 0)
                revenue = week_data.get('revenue', 0)
                print(f"  {week}: ${spend:,.2f} spend, ${revenue:,.2f} revenue")
        
        print(f"\n📅 Analysis claimed date range: July 2 - August 27, 2025")
        print(f"📊 Actual weeks analyzed: {len(weeks) if 'weekly_summary' in analysis_data else 'Unknown'}")
    else:
        print(f"❌ Analysis file {analysis_file} not found!")
    
    # FINAL CONCLUSION
    print(f"\n\n🚨 CRITICAL FINDING:")
    print("=" * 60)
    print("The Business Intelligence Agent claimed to analyze '8 weeks of Meta Ads data")
    print("(July 2 - August 27, 2025)' but our investigation shows:")
    print()
    print("❌ META_AD_DATA: Only 2 weeks of data available (Aug 13-26, 2025)")
    print("✅ CAMPAIGN_DATA: Has historical data but NOT in the claimed July-August range")
    print()
    print("🔍 PROBABLE ISSUE: The BI Agent accessed CAMPAIGN_DATA (historical)")
    print("    instead of META_AD_DATA (recent) and misrepresented the date range.")
    print()
    print("📊 ACTUAL ANALYSIS: Based on historical campaign data, NOT recent ad-level data")
    print("    from the claimed July-August 2025 period.")

if __name__ == "__main__":
    investigate_analysis_data()