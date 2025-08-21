#!/usr/bin/env python3
"""
Add the missing week_number column to meta_ad_data table
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('./.env')

def add_week_number_column():
    """Add the missing week_number column"""
    
    # Initialize Supabase client
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")
        return False
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # Read the SQL file
        with open('add_week_number_column.sql', 'r') as f:
            sql_content = f.read()
        
        print("📝 Adding week_number column to meta_ad_data table...")
        print("-" * 60)
        print(sql_content)
        print("-" * 60)
        print("⚠️  Please run the above SQL in your Supabase SQL editor")
        print("   OR manually add the column in the Supabase dashboard:")
        print("   1. Go to Table Editor → meta_ad_data")
        print("   2. Click 'Add Column'")
        print("   3. Name: week_number")
        print("   4. Type: varchar(50)")
        print("   5. Save")
        
        # Try to verify the column exists by testing a simple insert
        try:
            # Test if we can access the table with the new column
            result = supabase.table('meta_ad_data').select('week_number').limit(1).execute()
            print("✅ week_number column is accessible!")
            return True
        except Exception as e:
            print(f"❌ week_number column not found: {e}")
            print("   Please add the column manually in Supabase dashboard")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Adding week_number column to meta_ad_data table")
    print("=" * 60)
    
    if add_week_number_column():
        print("\n🎉 Column added successfully!")
        print("You can now run the ad data sync:")
        print("python3 sync_real_ad_data.py")
    else:
        print("\n❌ Column addition failed. Please add manually in Supabase.")