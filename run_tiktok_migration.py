#!/usr/bin/env python3
"""Run TikTok database migration"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def run_tiktok_migration():
    """Run the TikTok campaign data migration"""
    
    print("🚀 Running TikTok Database Migration...")
    
    # Connect to Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Read migration file
    migration_file = "database/migrations/add_tiktok_campaign_data.sql"
    
    try:
        with open(migration_file, 'r') as file:
            migration_sql = file.read()
        
        print(f"📄 Loaded migration from {migration_file}")
        
        # Execute migration (note: Supabase Python client doesn't directly support raw SQL)
        # We'll need to execute this manually in Supabase dashboard or use the CLI
        print("⚠️  Please run this migration manually in Supabase:")
        print(f"1. Go to Supabase dashboard → SQL Editor")
        print(f"2. Copy the contents of {migration_file}")
        print(f"3. Paste and execute the SQL")
        
        # Alternative: Check if tables exist by querying
        try:
            result = supabase.table("tiktok_campaign_data").select("id").limit(1).execute()
            print("✅ TikTok campaign data table already exists")
            return True
        except Exception as e:
            print(f"❌ TikTok campaign data table does not exist yet")
            print(f"🔍 Run the migration SQL manually in Supabase dashboard")
            return False
            
    except FileNotFoundError:
        print(f"❌ Migration file not found: {migration_file}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 TikTok Database Migration")
    print("=" * 40)
    
    success = run_tiktok_migration()
    
    if success:
        print("\n✅ TikTok database structure ready!")
    else:
        print("\n❌ Manual migration required")
        print("📋 Next steps:")
        print("  1. Open Supabase dashboard")
        print("  2. Go to SQL Editor")
        print("  3. Run database/migrations/add_tiktok_campaign_data.sql")
    
    print("=" * 40)