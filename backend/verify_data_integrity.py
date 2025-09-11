#!/usr/bin/env python3
"""
CRITICAL DATA INTEGRITY VERIFICATION
Verify actual Meta Ads data availability vs claimed 8 weeks analysis
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import json

load_dotenv()

def verify_data_integrity():
    """Comprehensive data integrity check"""
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
    
    print("🚨 CRITICAL DATA INTEGRITY INVESTIGATION")
    print("=" * 60)
    print("❓ CLAIMED: 8 weeks of Meta Ads data (July 2 - August 27, 2025)")
    print("❓ USER STATES: Only 2 weeks of data exist")
    print("🔍 INVESTIGATING ACTUAL DATABASE CONTENTS...")
    print("=" * 60)
    
    results = {}
    
    # Check campaign_data table
    print("\n📊 CAMPAIGN_DATA TABLE ANALYSIS:")
    print("-" * 40)
    try:
        # Get all campaign data
        response = supabase.table('campaign_data').select('*').execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df['reporting_starts'] = pd.to_datetime(df['reporting_starts'])
            df['reporting_ends'] = pd.to_datetime(df['reporting_ends'])
            
            min_date = df['reporting_starts'].min()
            max_date = df['reporting_ends'].max()
            total_records = len(df)
            date_range_days = (max_date - min_date).days + 1
            
            print(f"📅 Date Range: {min_date.date()} to {max_date.date()}")
            print(f"📊 Total Records: {total_records:,}")
            print(f"⏰ Days Covered: {date_range_days}")
            print(f"📆 Weeks Covered: {date_range_days / 7:.1f}")
            
            # Show date distribution
            print(f"\n🗓️ DATE DISTRIBUTION:")
            date_counts = df.groupby('reporting_starts').size().sort_index()
            for date, count in date_counts.head(10).items():
                print(f"  {date.date()}: {count:,} records")
            if len(date_counts) > 10:
                print(f"  ... and {len(date_counts) - 10} more dates")
            
            results['campaign_data'] = {
                'min_date': str(min_date.date()),
                'max_date': str(max_date.date()),
                'total_records': total_records,
                'days_covered': date_range_days,
                'weeks_covered': round(date_range_days / 7, 1)
            }
        else:
            print("❌ NO DATA FOUND in campaign_data")
            results['campaign_data'] = {'error': 'No data found'}
    except Exception as e:
        print(f"❌ ERROR accessing campaign_data: {e}")
        results['campaign_data'] = {'error': str(e)}
    
    # Check meta_ad_data table
    print("\n\n📈 META_AD_DATA TABLE ANALYSIS:")
    print("-" * 40)
    try:
        # Get all meta ad data
        response = supabase.table('meta_ad_data').select('*').execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df['reporting_starts'] = pd.to_datetime(df['reporting_starts'])
            df['reporting_ends'] = pd.to_datetime(df['reporting_ends'])
            
            min_date = df['reporting_starts'].min()
            max_date = df['reporting_ends'].max()
            total_records = len(df)
            date_range_days = (max_date - min_date).days + 1
            unique_ads = df['ad_id'].nunique()
            
            print(f"📅 Date Range: {min_date.date()} to {max_date.date()}")
            print(f"📊 Total Records: {total_records:,}")
            print(f"🎯 Unique Ads: {unique_ads:,}")
            print(f"⏰ Days Covered: {date_range_days}")
            print(f"📆 Weeks Covered: {date_range_days / 7:.1f}")
            
            # Show date distribution
            print(f"\n🗓️ DATE DISTRIBUTION:")
            date_counts = df.groupby('reporting_starts').size().sort_index()
            for date, count in date_counts.head(10).items():
                print(f"  {date.date()}: {count:,} records")
            if len(date_counts) > 10:
                print(f"  ... and {len(date_counts) - 10} more dates")
            
            # Check for July/August 2025 data specifically
            print(f"\n🔍 JULY/AUGUST 2025 SPECIFIC CHECK:")
            july_start = datetime(2025, 7, 1)
            august_end = datetime(2025, 8, 31)
            july_aug_data = df[(df['reporting_starts'] >= july_start) & 
                              (df['reporting_starts'] <= august_end)]
            print(f"  Records in July-August 2025: {len(july_aug_data):,}")
            if len(july_aug_data) > 0:
                july_aug_min = july_aug_data['reporting_starts'].min()
                july_aug_max = july_aug_data['reporting_ends'].max()
                july_aug_days = (july_aug_max - july_aug_min).days + 1
                print(f"  July-Aug Date Range: {july_aug_min.date()} to {july_aug_max.date()}")
                print(f"  July-Aug Days: {july_aug_days}")
                print(f"  July-Aug Weeks: {july_aug_days / 7:.1f}")
            
            results['meta_ad_data'] = {
                'min_date': str(min_date.date()),
                'max_date': str(max_date.date()),
                'total_records': total_records,
                'unique_ads': unique_ads,
                'days_covered': date_range_days,
                'weeks_covered': round(date_range_days / 7, 1),
                'july_aug_2025_records': len(july_aug_data)
            }
        else:
            print("❌ NO DATA FOUND in meta_ad_data")
            results['meta_ad_data'] = {'error': 'No data found'}
    except Exception as e:
        print(f"❌ ERROR accessing meta_ad_data: {e}")
        results['meta_ad_data'] = {'error': str(e)}
    
    # Check if there are any analysis files that might show what was analyzed
    print("\n\n🔍 CHECKING RECENT ANALYSIS FILES:")
    print("-" * 40)
    
    analysis_files = [
        'meta_ads_wow_analysis_20250827_204143.json',
        'meta_ads_wow_analysis_20250827_204236.json', 
        'meta_ads_wow_analysis_20250827_204257.json',
        'META_ADS_WOW_ANALYSIS_COMPLETE.md',
        'HON_Meta_Ads_WoW_Business_Intelligence_Report.md'
    ]
    
    for file in analysis_files:
        if os.path.exists(file):
            print(f"✅ Found: {file}")
            # Check file size and modification time
            stat = os.stat(file)
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            size_kb = stat.st_size / 1024
            print(f"   📁 Size: {size_kb:.1f} KB, Modified: {mod_time}")
        else:
            print(f"❌ Missing: {file}")
    
    # FINAL VERDICT
    print("\n\n🚨 DATA INTEGRITY VERDICT:")
    print("=" * 60)
    
    if 'campaign_data' in results and 'weeks_covered' in results['campaign_data']:
        campaign_weeks = results['campaign_data']['weeks_covered']
        print(f"📊 CAMPAIGN DATA: {campaign_weeks} weeks")
    
    if 'meta_ad_data' in results and 'weeks_covered' in results['meta_ad_data']:
        ad_weeks = results['meta_ad_data']['weeks_covered']
        print(f"📈 META AD DATA: {ad_weeks} weeks")
        
        if ad_weeks < 8:
            print(f"🚨 CRITICAL ISSUE: Only {ad_weeks} weeks of data exist, NOT 8 weeks!")
            print("❌ The claimed '8 weeks of Meta Ads data (July 2 - August 27, 2025)' appears to be INACCURATE")
        else:
            print(f"✅ 8+ weeks of data confirmed")
    
    # Save results
    with open('data_integrity_investigation.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Full results saved to: data_integrity_investigation.json")
    return results

if __name__ == "__main__":
    verify_data_integrity()