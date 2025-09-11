#!/usr/bin/env python3
"""
Check the actual structure of google_campaign_data table
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

def check_table_structure():
    """Check the actual columns in google_campaign_data table"""
    try:
        # Get a sample row to see actual column names
        response = supabase.table('google_campaign_data').select('*').limit(1).execute()
        
        if response.data:
            print("📋 Google Campaign Data Table Columns:")
            print("=" * 50)
            sample_row = response.data[0]
            for column, value in sample_row.items():
                print(f"   {column}: {type(value).__name__} = {value}")
        else:
            print("❌ No data found in google_campaign_data table")
            
    except Exception as e:
        print(f"❌ Error checking table structure: {e}")

def check_available_tables():
    """Check what Google Ads related tables exist"""
    try:
        # Check different possible table names
        table_names = [
            'google_campaign_data',
            'google_ads_campaign_data', 
            'google_ads_data',
            'campaign_data',
            'google_campaigns'
        ]
        
        print("\n🔍 Checking available tables:")
        for table_name in table_names:
            try:
                response = supabase.table(table_name).select('*').limit(1).execute()
                if response.data:
                    print(f"   ✅ {table_name} exists with {len(response.data)} sample records")
                    # Show first row structure
                    sample = response.data[0]
                    date_columns = [col for col in sample.keys() if 'date' in col.lower()]
                    if date_columns:
                        print(f"      📅 Date columns: {date_columns}")
                else:
                    print(f"   ⚠️  {table_name} exists but empty")
            except Exception as table_error:
                print(f"   ❌ {table_name} not found")
                
    except Exception as e:
        print(f"❌ Error checking tables: {e}")

if __name__ == "__main__":
    check_table_structure()
    check_available_tables()