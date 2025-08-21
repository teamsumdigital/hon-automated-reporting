#!/usr/bin/env python3
"""
Apply thumbnail_url column migration to Supabase database
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
        
        print("Applying thumbnail_url column migration...")
        
        # Add the column using raw SQL
        result = supabase.rpc('exec_sql', {
            'sql': 'ALTER TABLE meta_ad_data ADD COLUMN IF NOT EXISTS thumbnail_url TEXT;'
        }).execute()
        
        print("✅ Migration applied successfully")
        
        # Test the column exists
        test_result = supabase.table('meta_ad_data').select('thumbnail_url').limit(1).execute()
        print("✅ thumbnail_url column confirmed to exist")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("Try running this SQL manually in Supabase SQL editor:")
        print("ALTER TABLE meta_ad_data ADD COLUMN IF NOT EXISTS thumbnail_url TEXT;")

if __name__ == "__main__":
    apply_migration()