#!/usr/bin/env python3
"""
Examine HON Database Schema for Meta Ads Analysis
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd

load_dotenv()

def examine_schema():
    """Examine the database schema and sample data"""
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
    
    print("🔍 EXAMINING HON DATABASE SCHEMA")
    print("=" * 50)
    
    # Check campaign_data table
    try:
        print("\n📊 CAMPAIGN_DATA TABLE:")
        response = supabase.table('campaign_data').select('*').limit(3).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            print(f"Columns: {list(df.columns)}")
            print(f"Sample data shape: {df.shape}")
            print("\nSample records:")
            print(df.head(2).to_string())
        else:
            print("No data found in campaign_data")
    except Exception as e:
        print(f"Error accessing campaign_data: {e}")
    
    # Check meta_ad_data table
    try:
        print("\n\n📈 META_AD_DATA TABLE:")
        response = supabase.table('meta_ad_data').select('*').limit(3).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            print(f"Columns: {list(df.columns)}")
            print(f"Sample data shape: {df.shape}")
            print("\nSample records:")
            print(df.head(2).to_string())
        else:
            print("No data found in meta_ad_data")
    except Exception as e:
        print(f"Error accessing meta_ad_data: {e}")
    
    # Check if there are other relevant tables
    print("\n\n🗃️ CHECKING FOR OTHER META TABLES:")
    
    # Try some potential table names
    potential_tables = [
        'meta_campaign_data',
        'meta_ads_data', 
        'facebook_campaign_data',
        'meta_reporting_data',
        'ad_performance_data'
    ]
    
    for table_name in potential_tables:
        try:
            response = supabase.table(table_name).select('*').limit(1).execute()
            if response.data:
                df = pd.DataFrame(response.data)
                print(f"\n✅ Found table '{table_name}' with columns: {list(df.columns)}")
        except Exception as e:
            if "does not exist" not in str(e):
                print(f"❌ Error checking {table_name}: {e}")

if __name__ == "__main__":
    examine_schema()