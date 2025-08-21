#!/usr/bin/env python3
"""
Debug script to test thumbnail fetching from Meta Ads API
"""
import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.insert(0, '/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

load_dotenv()

# Test imports
try:
    from app.services.meta_ad_level_service import MetaAdLevelService
    from supabase import create_client
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test database connection
try:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    # Check if thumbnail_url column exists
    result = supabase.table('meta_ad_data').select('*').limit(1).execute()
    if result.data and len(result.data) > 0:
        sample_record = result.data[0]
        if 'thumbnail_url' in sample_record:
            print("✅ thumbnail_url column exists in database")
            print(f"Sample thumbnail_url: {sample_record.get('thumbnail_url')}")
        else:
            print("❌ thumbnail_url column missing from database")
    else:
        print("❌ No data in meta_ad_data table")
        
except Exception as e:
    print(f"❌ Database error: {e}")

# Test Meta API connection and thumbnail fetching
try:
    meta_service = MetaAdLevelService()
    print("✅ Meta API service initialized")
    
    # Test with a few ad IDs from recent data
    result = supabase.table('meta_ad_data').select('ad_id').limit(3).execute()
    if result.data:
        ad_ids = [record['ad_id'] for record in result.data if record.get('ad_id')]
        print(f"Testing thumbnail fetch for ad IDs: {ad_ids}")
        
        thumbnails = meta_service.get_ad_thumbnails(ad_ids)
        print(f"✅ Fetched {len(thumbnails)} thumbnails out of {len(ad_ids)} ads")
        
        for ad_id, url in thumbnails.items():
            print(f"  {ad_id}: {url}")
            
        if not thumbnails:
            print("❌ No thumbnails retrieved - check API permissions")
    else:
        print("❌ No ad_ids found in database")
        
except Exception as e:
    print(f"❌ Meta API error: {e}")