#!/usr/bin/env python3
"""
Apply thumbnail_url column migrations to Supabase database
Ensures both the lightweight and high-resolution thumbnail URLs exist
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def apply_migration():
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        supabase = create_client(supabase_url, supabase_key)
        
        print("Applying thumbnail_url columns migration...")

        # Add the columns using raw SQL
        result = supabase.rpc('exec_sql', {
            'sql': (
                'ALTER TABLE meta_ad_data '
                'ADD COLUMN IF NOT EXISTS thumbnail_url TEXT, '
                'ADD COLUMN IF NOT EXISTS thumbnail_url_high_res TEXT;'
            )
        }).execute()
        
        print("✅ Migration applied successfully")
        
        # Test the columns exist
        supabase.table('meta_ad_data').select('thumbnail_url,thumbnail_url_high_res').limit(1).execute()
        print("✅ thumbnail_url and thumbnail_url_high_res columns confirmed to exist")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("Try running this SQL manually in Supabase SQL editor:")
        print('''ALTER TABLE meta_ad_data \
ADD COLUMN IF NOT EXISTS thumbnail_url TEXT, \
ADD COLUMN IF NOT EXISTS thumbnail_url_high_res TEXT;''')

if __name__ == "__main__":
    apply_migration()