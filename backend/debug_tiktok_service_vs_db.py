#!/usr/bin/env python3
"""
Compare TikTok service output vs direct database queries
"""

import os
import sys
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def debug_service_vs_db():
    print("COMPARING TIKTOK SERVICE VS DATABASE")
    print("=" * 60)
    
    # Direct database connection
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    # Initialize TikTok service manually
    from app.services.tiktok_service import TikTokService
    tiktok_service = TikTokService()
    
    print("\n1. DIRECT DATABASE QUERY - NO FILTERS")
    print("-" * 40)
    
    # Direct DB query - all July 2025 data
    july_2025_db = supabase.table("tiktok_ad_data")\
        .select("*")\
        .gte("reporting_starts", "2025-07-01")\
        .lte("reporting_ends", "2025-07-31")\
        .execute()
    
    july_2025_db_spend = sum(ad.get('amount_spent_usd', 0) for ad in july_2025_db.data)
    print(f"DB July 2025 total: ${july_2025_db_spend:,.2f} ({len(july_2025_db.data)} ads)")
    
    print("\n2. TIKTOK SERVICE QUERY - NO FILTERS")
    print("-" * 40)
    
    # TikTok service - no filters
    service_data_no_filter = tiktok_service.get_dashboard_data()
    july_2025_service = None
    for pivot in service_data_no_filter.get('pivot_data', []):
        if pivot.get('month') == '2025-07':
            july_2025_service = pivot
            break
    
    if july_2025_service:
        print(f"Service July 2025 total: ${july_2025_service['spend']:,.2f}")
        print(f"Service data: {july_2025_service}")
    else:
        print("Service did not return July 2025 data")
        print("Available months:", [p.get('month') for p in service_data_no_filter.get('pivot_data', [])])
    
    print("\n3. CHECKING SERVICE RAW DATA")
    print("-" * 40)
    
    # Check what raw data the service is working with
    query = supabase.table("tiktok_ad_data").select("*")
    result = query.execute()
    all_campaigns = result.data
    
    # Filter to July 2025 manually
    july_2025_campaigns = [c for c in all_campaigns if c.get('reporting_starts', '').startswith('2025-07')]
    july_2025_raw_spend = sum(c.get('amount_spent_usd', 0) for c in july_2025_campaigns)
    
    print(f"Service raw data July 2025: ${july_2025_raw_spend:,.2f} ({len(july_2025_campaigns)} ads)")
    
    if july_2025_raw_spend != july_2025_db_spend:
        print("🚨 MISMATCH between service raw data and direct DB query!")
        print("This indicates a query issue in the service.")
    else:
        print("✅ Service raw data matches direct DB query")
    
    # Test the pivot generation directly
    print("\n4. TESTING PIVOT GENERATION DIRECTLY")
    print("-" * 40)
    
    pivot_data = tiktok_service._generate_pivot_data(july_2025_campaigns)
    july_2025_pivot = None
    for pivot in pivot_data:
        if pivot.get('month') == '2025-07':
            july_2025_pivot = pivot
            break
    
    if july_2025_pivot:
        print(f"Direct pivot calculation July 2025: ${july_2025_pivot['spend']:,.2f}")
    else:
        print("Direct pivot calculation did not produce July 2025 data")
        print("Pivot months:", [p.get('month') for p in pivot_data])
    
    print("\n5. INVESTIGATING JULY 2025 AD DATES")
    print("-" * 40)
    
    # Check the actual reporting dates
    for ad in july_2025_campaigns[:5]:
        print(f"Ad {ad.get('ad_id')}: {ad.get('reporting_starts')} to {ad.get('reporting_ends')} - ${ad.get('amount_spent_usd', 0):,.2f}")
    
    print(f"\nAll July 2025 reporting_starts dates:")
    dates = list(set(ad.get('reporting_starts') for ad in july_2025_campaigns))
    print(sorted(dates))

if __name__ == "__main__":
    debug_service_vs_db()