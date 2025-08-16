#!/usr/bin/env python3
"""Debug campaign types in database"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def debug_campaign_types():
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
    
    print("🔍 Debugging Campaign Types")
    print("=" * 40)
    
    # Check sample campaigns with their types
    result = supabase.table("google_campaign_data").select("campaign_name, category, campaign_type").limit(10).execute()
    
    print("Sample campaigns from database:")
    for i, row in enumerate(result.data, 1):
        print(f"{i:2d}. {row['campaign_name']}")
        print(f"    Category: {row['category']}")
        print(f"    Type: {row['campaign_type']}")
        print()
    
    # Check campaign type distribution
    result = supabase.table("google_campaign_data").select("campaign_type").execute()
    type_counts = {}
    for row in result.data:
        ctype = row['campaign_type'] if row['campaign_type'] is not None else 'NULL'
        type_counts[ctype] = type_counts.get(ctype, 0) + 1
    
    print("Campaign Type Distribution:")
    for ctype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ctype}: {count}")
    
    # Check specific YouTube campaigns
    result = supabase.table("google_campaign_data").select("campaign_name, campaign_type").ilike("campaign_name", "%youtube%").execute()
    print(f"\nYouTube campaigns in database ({len(result.data)}):")
    for row in result.data:
        print(f"  {row['campaign_name']} → {row['campaign_type']}")

if __name__ == "__main__":
    debug_campaign_types()