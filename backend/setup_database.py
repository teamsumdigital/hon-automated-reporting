#!/usr/bin/env python3
"""
Setup the Supabase database schema for HON Automated Reporting
"""

import os
from dotenv import load_dotenv
from supabase import create_client

def setup_database():
    """Setup database tables and initial data"""
    load_dotenv()
    
    print("🔗 Connecting to Supabase...")
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    try:
        supabase = create_client(url, key)
        print("✅ Connected to Supabase")
        
        # Read schema file
        schema_path = "../database/schema.sql"
        if not os.path.exists(schema_path):
            print(f"❌ Schema file not found: {schema_path}")
            return False
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        print("📝 Reading schema file...")
        
        # Split into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        print(f"🔨 Executing {len(statements)} SQL statements...")
        
        success_count = 0
        for i, statement in enumerate(statements, 1):
            try:
                # Skip comments and empty statements
                if statement.startswith('--') or not statement:
                    continue
                
                # Execute via raw SQL (for CREATE statements)
                result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                print(f"   ✅ Statement {i}: {statement[:50]}...")
                success_count += 1
                
            except Exception as e:
                # Some statements might fail if tables already exist - that's OK
                if "already exists" in str(e).lower():
                    print(f"   ⚠️  Statement {i}: Already exists")
                else:
                    print(f"   ❌ Statement {i}: {e}")
        
        print(f"\n🎉 Database setup complete! {success_count} statements executed successfully.")
        
        # Test that tables were created
        try:
            result = supabase.table("category_rules").select("*").limit(1).execute()
            print("✅ Tables accessible and ready")
            return True
        except Exception as e:
            print(f"❌ Tables not accessible: {e}")
            print("\n💡 Manual setup required:")
            print("1. Go to your Supabase dashboard")
            print("2. Open the SQL Editor")
            print("3. Copy and paste the contents of database/schema.sql")
            print("4. Click 'Run' to execute the schema")
            return False
            
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_database()