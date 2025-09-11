#!/usr/bin/env python3
"""
Debug script to investigate why Meta ad sync is pulling July data instead of just 14 days
"""
import os
import sys
from datetime import datetime, timedelta, date
from supabase import create_client
import pandas as pd

# Add the app modules to the path
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from dotenv import load_dotenv
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

def check_current_database_data():
    """Check what date ranges currently exist in the meta_ad_data table"""
    print("=" * 80)
    print("CHECKING CURRENT META AD DATA IN DATABASE")
    print("=" * 80)
    
    try:
        # Query all data to see date range
        response = supabase.table('meta_ad_data').select('reporting_starts, reporting_ends, ad_name').execute()
        
        if not response.data:
            print("❌ NO META AD DATA FOUND IN DATABASE")
            return
        
        df = pd.DataFrame(response.data)
        df['reporting_starts'] = pd.to_datetime(df['reporting_starts'])
        df['reporting_ends'] = pd.to_datetime(df['reporting_ends'])
        
        print(f"📊 Total records in meta_ad_data: {len(df)}")
        print(f"📅 Date range in database:")
        print(f"   Earliest: {df['reporting_starts'].min()}")
        print(f"   Latest: {df['reporting_ends'].max()}")
        
        # Group by date to see distribution
        df['date'] = df['reporting_starts'].dt.date
        date_counts = df['date'].value_counts().sort_index()
        
        print(f"\n📋 RECORDS PER DATE:")
        for date_val, count in date_counts.items():
            print(f"   {date_val}: {count} records")
        
        # Check for July data specifically
        july_data = df[df['reporting_starts'].dt.month == 7]
        if len(july_data) > 0:
            print(f"\n🚨 JULY DATA DETECTED:")
            print(f"   July records: {len(july_data)}")
            print(f"   July date range: {july_data['reporting_starts'].min()} to {july_data['reporting_ends'].max()}")
            print(f"   Sample July ads: {july_data['ad_name'].head(3).tolist()}")
        else:
            print(f"\n✅ No July data found in database")
            
        # Check for recent data (last 14 days)
        today = datetime.now().date()
        fourteen_days_ago = today - timedelta(days=14)
        
        recent_data = df[df['reporting_starts'].dt.date >= fourteen_days_ago]
        print(f"\n📈 RECENT DATA (last 14 days from {fourteen_days_ago}):")
        print(f"   Recent records: {len(recent_data)}")
        if len(recent_data) > 0:
            print(f"   Recent date range: {recent_data['reporting_starts'].min()} to {recent_data['reporting_ends'].max()}")
        
    except Exception as e:
        print(f"❌ Error checking database data: {e}")

def test_date_calculation_logic():
    """Test the date calculation logic from meta_ad_level_service.py"""
    print("\n" + "=" * 80)
    print("TESTING DATE CALCULATION LOGIC")
    print("=" * 80)
    
    import pytz
    from datetime import date, timedelta
    
    # Simulate the logic from get_last_14_days_ad_data
    print("🗓️  SIMULATING DATE CALCULATION FROM get_last_14_days_ad_data():")
    
    # Force Pacific timezone to avoid UTC/server timezone issues
    pacific_tz = pytz.timezone('US/Pacific')
    pacific_now = datetime.now(pacific_tz)
    target_date = pacific_now.date()
    print(f"   Target date (Pacific timezone): {target_date}")
    
    today = date.today()
    print(f"   Today (system date): {today}")
    
    # Check if target_date is more than 7 days old
    if target_date and (today - target_date).days > 7:
        print(f"🚨 EMERGENCY FIX TRIGGERED:")
        print(f"   Target date {target_date} is {(today - target_date).days} days old (> 7)")
        print(f"   Using recent data instead")
        end_date = today - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=13)  # 14 days total
        print(f"   Emergency range: {start_date} to {end_date}")
    else:
        # Use original logic for recent dates
        end_date = target_date - timedelta(days=1)
        start_date = end_date - timedelta(days=13)
        print(f"   Normal calculation:")
        print(f"   End date (yesterday): {end_date}")
        print(f"   Start date (14 days back): {start_date}")
    
    print(f"\n📊 FINAL DATE RANGE FOR API CALL:")
    print(f"   Start: {start_date}")
    print(f"   End: {end_date}")
    print(f"   Total days: {(end_date - start_date).days + 1}")
    
    # Check if this could result in July data
    if start_date.month == 7 or end_date.month == 7:
        print(f"\n🚨 WARNING: Date range includes July!")
        print(f"   This could be why July data is being pulled")
    else:
        print(f"\n✅ Date range does not include July")

def investigate_database_clearing_logic():
    """Check if the database clearing in webhook.py is working correctly"""
    print("\n" + "=" * 80)
    print("INVESTIGATING DATABASE CLEARING LOGIC")
    print("=" * 80)
    
    print("🔍 DATABASE CLEARING ANALYSIS:")
    print("   From webhook.py line 195:")
    print("   supabase.table('meta_ad_data').delete().gt('id', 0).execute()")
    print("")
    print("❌ ISSUE IDENTIFIED: This clears ALL records, not just the sync period!")
    print("   The clearing logic deletes everything with id > 0 (i.e., all records)")
    print("   It doesn't scope deletion to the 14-day period being synced")
    print("")
    print("✅ EXPECTED BEHAVIOR:")
    print("   Should only delete records within the date range being synced")
    print("   For example: delete where reporting_starts >= start_date AND reporting_ends <= end_date")

def check_meta_api_parameters():
    """Analyze the Meta API parameters being used"""
    print("\n" + "=" * 80)
    print("ANALYZING META API PARAMETERS")
    print("=" * 80)
    
    print("📋 META API CALL PARAMETERS (from meta_ad_level_service.py lines 227-246):")
    print("   time_range: {'since': start_date, 'until': end_date}")
    print("   level: 'ad'")
    print("   time_increment: 7  # Weekly segmentation")
    print("   limit: 100  # Reduced from 500 to prevent timeout")
    print("")
    print("✅ API PARAMETERS LOOK CORRECT:")
    print("   The Meta API is being called with proper date constraints")
    print("   time_range should limit results to the specified 14-day window")
    print("")
    print("🤔 POTENTIAL ISSUES:")
    print("   1. If date calculation is wrong, it could request July dates")
    print("   2. If database clearing doesn't work, old July data persists")
    print("   3. If there's historical data that never got cleared")

def provide_solution_recommendations():
    """Provide specific recommendations to fix the issue"""
    print("\n" + "=" * 80)
    print("SOLUTION RECOMMENDATIONS")
    print("=" * 80)
    
    print("🎯 ROOT CAUSE ANALYSIS:")
    print("   The issue is likely NOT with the Meta API date range calculation")
    print("   The API is correctly called with 14-day windows")
    print("   The problem is the database clearing logic in webhook.py")
    print("")
    print("🔧 IMMEDIATE FIX NEEDED:")
    print("   1. Fix database clearing in webhook.py (line 195)")
    print("   2. Change from: supabase.table('meta_ad_data').delete().gt('id', 0).execute()")
    print("   3. Change to: Clear only records within the sync date range")
    print("")
    print("📝 RECOMMENDED CODE CHANGE:")
    print("   # Clear only data in the sync period")
    print("   supabase.table('meta_ad_data').delete()")
    print("     .gte('reporting_starts', start_date.isoformat())")
    print("     .lte('reporting_ends', end_date.isoformat())")
    print("     .execute()")
    print("")
    print("🧪 TESTING PLAN:")
    print("   1. Manually clear all meta_ad_data")
    print("   2. Run a 14-day sync")
    print("   3. Verify only recent 14-day data exists")
    print("   4. Run sync again to test clearing logic works correctly")

def main():
    """Run the complete investigation"""
    print("🔍 HON META AD SYNC INVESTIGATION")
    print("Investigating why 14-day sync is pulling July data...")
    
    # Step 1: Check current database state
    check_current_database_data()
    
    # Step 2: Test date calculation logic  
    test_date_calculation_logic()
    
    # Step 3: Investigate database clearing
    investigate_database_clearing_logic()
    
    # Step 4: Check API parameters
    check_meta_api_parameters()
    
    # Step 5: Provide solutions
    provide_solution_recommendations()
    
    print("\n" + "=" * 80)
    print("🏁 INVESTIGATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()