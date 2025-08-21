#!/usr/bin/env python3
"""
Check if data was successfully inserted into Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def check_data():
    # Initialize Supabase client
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return
    
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        # Check recent data
        result = (supabase.table('meta_ad_data')
                 .select('*')
                 .order('reporting_starts', desc=True)
                 .limit(10)
                 .execute())
        
        if result.data:
            print(f"✅ Found {len(result.data)} recent ad records")
            print("\n📊 Recent Records:")
            for i, record in enumerate(result.data[:5], 1):
                print(f"  {i}. {record.get('ad_name', 'Unknown')[:50]}...")
                print(f"     Date: {record.get('reporting_starts')} | Category: {record.get('category')} | Format: {record.get('format')}")
            
            # Check date range
            date_result = (supabase.table('meta_ad_data')
                          .select('reporting_starts, reporting_ends')
                          .order('reporting_starts', desc=True)
                          .limit(1)
                          .execute())
            
            if date_result.data:
                latest = date_result.data[0]
                print(f"\n📅 Latest data: {latest.get('reporting_starts')} to {latest.get('reporting_ends')}")
            
            # Check total count
            count_result = (supabase.table('meta_ad_data')
                           .select('id', count='exact')
                           .execute())
            
            print(f"📈 Total records in database: {count_result.count}")
            
        else:
            print("⚠️ No data found in meta_ad_data table")
            
    except Exception as e:
        print(f"❌ Error checking data: {e}")

if __name__ == "__main__":
    check_data()