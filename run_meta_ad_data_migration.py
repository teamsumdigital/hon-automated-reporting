#!/usr/bin/env python3
"""
Migration script to create the meta_ad_data table in Supabase
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the meta_ad_data table migration"""
    
    # Initialize Supabase client
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")
        return False
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # Read the migration SQL
        migration_file = "database/migrations/create_meta_ad_data_table.sql"
        
        if not os.path.exists(migration_file):
            print(f"❌ Error: Migration file not found: {migration_file}")
            return False
        
        with open(migration_file, 'r') as f:
            sql_content = f.read()
        
        print("📝 Running meta_ad_data table migration...")
        
        # Execute the migration
        # Note: Supabase Python client doesn't directly support raw SQL execution
        # This migration should be run in the Supabase SQL editor
        print("⚠️  Please run the following SQL in your Supabase SQL editor:")
        print("-" * 80)
        print(sql_content)
        print("-" * 80)
        
        # Alternative: Test table creation by attempting to query it
        try:
            result = supabase.table('meta_ad_data').select('*').limit(1).execute()
            print("✅ meta_ad_data table already exists and is accessible")
            return True
        except Exception as e:
            print(f"ℹ️  Table doesn't exist yet. Please run the SQL above in Supabase dashboard.")
            print(f"   Then run this script again to verify the table creation.")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {str(e)}")
        return False

def verify_table_structure():
    """Verify the meta_ad_data table exists and has correct structure"""
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        
        # Test basic table access
        result = supabase.table('meta_ad_data').select('*').limit(1).execute()
        print("✅ meta_ad_data table exists and is accessible")
        
        # Try inserting a test record to verify structure
        test_data = {
            'ad_id': 'test_ad_123',
            'ad_name': 'Test Ad',
            'campaign_name': 'Test Campaign',
            'reporting_starts': '2024-01-01',
            'reporting_ends': '2024-01-01',
            'amount_spent_usd': 0,
            'purchases': 0,
            'purchases_conversion_value': 0,
            'impressions': 0,
            'link_clicks': 0
        }
        
        # Insert and immediately delete test record
        insert_result = supabase.table('meta_ad_data').insert(test_data).execute()
        if insert_result.data:
            test_id = insert_result.data[0]['id']
            supabase.table('meta_ad_data').delete().eq('id', test_id).execute()
            print("✅ Table structure verified - all required fields present")
            return True
            
    except Exception as e:
        print(f"❌ Table structure verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 HON Meta Ad Data Migration")
    print("=" * 50)
    
    if run_migration():
        print("\n🎉 Migration completed successfully!")
        if verify_table_structure():
            print("✅ Table structure verified and ready for ad-level data")
        else:
            print("⚠️  Please check table structure manually")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")