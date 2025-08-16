#!/usr/bin/env python3
"""
Google Ads Database Migration Script
Creates the Google Ads tables and triggers in Supabase database
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client
    from loguru import logger
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you have installed the required dependencies:")
    print("pip install supabase loguru python-dotenv")
    sys.exit(1)

def run_google_ads_migration():
    """
    Run the Google Ads database migration
    """
    try:
        # Initialize Supabase client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not url or not key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables")
        
        supabase = create_client(url, key)
        
        # Read migration SQL file
        migration_file = Path(__file__).parent / 'database' / 'migrations' / 'add_google_campaign_data.sql'
        
        if not migration_file.exists():
            raise FileNotFoundError(f"Migration file not found: {migration_file}")
        
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        logger.info("Running Google Ads database migration...")
        
        # Execute migration SQL
        # Note: Supabase Python client doesn't support raw SQL execution directly
        # This would typically be run through the Supabase dashboard or psql
        
        print("=" * 60)
        print("GOOGLE ADS DATABASE MIGRATION")
        print("=" * 60)
        print("\nTo complete the Google Ads integration setup:")
        print("\n1. Go to your Supabase dashboard")
        print("2. Navigate to the SQL Editor")
        print("3. Run the following SQL:")
        print("\n" + "=" * 40)
        print(migration_sql)
        print("=" * 40)
        
        print("\nOR copy and run the migration file directly:")
        print(f"File location: {migration_file}")
        
        print("\n4. After running the migration, you can test the Google Ads integration")
        print("5. Run the historical sync script: python google_historical_resync.py")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to prepare Google Ads migration: {e}")
        return False

def test_google_ads_setup():
    """
    Test if Google Ads tables exist and are properly configured
    """
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        supabase = create_client(url, key)
        
        # Try to query the Google Ads table
        result = supabase.table("google_campaign_data").select("id", count="exact").limit(1).execute()
        
        print(f"✅ Google Ads tables exist and are accessible")
        print(f"   Current record count: {result.count}")
        return True
        
    except Exception as e:
        print(f"❌ Google Ads tables not found or not accessible: {e}")
        print("   Please run the database migration first")
        return False

if __name__ == "__main__":
    print("HON Google Ads Database Migration Setup")
    print("=" * 50)
    
    # Check if tables already exist
    if test_google_ads_setup():
        print("\nGoogle Ads tables already exist. Migration may have been run previously.")
        choice = input("\nDo you want to see the migration instructions anyway? (y/n): ")
        if choice.lower() not in ['y', 'yes']:
            sys.exit(0)
    
    # Run migration setup
    success = run_google_ads_migration()
    
    if success:
        print("\n✅ Google Ads migration setup completed!")
        print("\nNext steps:")
        print("1. Set up Google Ads API credentials in .env file")
        print("2. Run: python google_historical_resync.py")
        print("3. Start the backend server and test the /api/google-reports endpoints")
    else:
        print("\n❌ Google Ads migration setup failed.")
        print("Check the error messages above and try again.")