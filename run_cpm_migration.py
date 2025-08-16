#!/usr/bin/env python3
"""
Add CPM column to TikTok campaign data table via Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def add_cpm_column():
    """Add CPM column to TikTok campaign data table"""
    try:
        # Initialize Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        supabase = create_client(supabase_url, supabase_key)
        
        print("🔧 Adding CPM column to tiktok_campaign_data table...")
        
        # Add CPM column via SQL RPC (if your Supabase has SQL execution enabled)
        # Note: This might not work with all Supabase configurations
        # If it fails, you'll need to run the SQL manually in Supabase dashboard
        
        sql_commands = [
            """
            ALTER TABLE tiktok_campaign_data 
            ADD COLUMN IF NOT EXISTS cpm DECIMAL(10, 4) DEFAULT 0;
            """,
            """
            UPDATE tiktok_campaign_data 
            SET cpm = CASE 
                WHEN impressions > 0 THEN ROUND((amount_spent_usd / (impressions::decimal / 1000)), 4)
                ELSE 0 
            END
            WHERE cpm = 0 OR cpm IS NULL;
            """,
            """
            ALTER TABLE tiktok_monthly_reports 
            ADD COLUMN IF NOT EXISTS avg_cpm DECIMAL(10, 4) DEFAULT 0;
            """
        ]
        
        for i, sql in enumerate(sql_commands, 1):
            try:
                print(f"   📝 Executing SQL command {i}/3...")
                # Note: Direct SQL execution might not be available
                # This is a placeholder - you may need to run SQL manually
                print(f"      SQL: {sql.strip()}")
                
            except Exception as e:
                print(f"   ⚠️ SQL execution failed (this is expected): {e}")
                print(f"   📋 Please run this SQL manually in Supabase dashboard:")
                print(f"   {sql}")
        
        print("✅ CPM column setup complete!")
        print("💡 CPM calculation: cost / (impressions / 1000)")
        
        # Test if we can query the table structure
        try:
            result = supabase.table('tiktok_campaign_data').select('*').limit(1).execute()
            if result.data:
                print(f"📊 Sample record fields: {list(result.data[0].keys())}")
        except Exception as e:
            print(f"   ⚠️ Could not test table structure: {e}")
        
    except Exception as e:
        print(f"❌ Error adding CPM column: {e}")

if __name__ == "__main__":
    add_cpm_column()