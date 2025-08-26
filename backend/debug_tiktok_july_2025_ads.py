#!/usr/bin/env python3
"""
Debug July 2025 TikTok ads to find why service returns fewer than DB
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def debug_july_2025_ads():
    print("DEBUGGING JULY 2025 TIKTOK ADS")
    print("=" * 60)
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    print("\n1. ALL JULY 2025 ADS IN DATABASE")
    print("-" * 40)
    
    # Get ALL July 2025 ads
    july_2025_all = supabase.table("tiktok_ad_data")\
        .select("*")\
        .gte("reporting_starts", "2025-07-01")\
        .lte("reporting_ends", "2025-07-31")\
        .execute()
    
    print(f"Total July 2025 ads: {len(july_2025_all.data)}")
    total_spend = sum(ad.get('amount_spent_usd', 0) for ad in july_2025_all.data)
    print(f"Total spend: ${total_spend:,.2f}")
    
    print("\nFirst 10 ads:")
    for i, ad in enumerate(july_2025_all.data[:10]):
        print(f"{i+1}. Ad {ad.get('ad_id')}: ${ad.get('amount_spent_usd', 0):,.2f} - {ad.get('ad_name', 'No name')[:50]}")
    
    print("\n2. TIKTOK SERVICE QUERY SIMULATION")
    print("-" * 40)
    
    # Simulate the exact query the service makes
    service_query = supabase.table("tiktok_ad_data").select("*")
    service_result = service_query.execute()
    
    print(f"Service gets total ads: {len(service_result.data)}")
    
    # Filter to July 2025 manually (like the service does)
    july_2025_from_service = [ad for ad in service_result.data 
                             if ad.get('reporting_starts', '').startswith('2025-07')]
    
    print(f"July 2025 ads from service data: {len(july_2025_from_service)}")
    service_spend = sum(ad.get('amount_spent_usd', 0) for ad in july_2025_from_service)
    print(f"Service July 2025 spend: ${service_spend:,.2f}")
    
    print("\n3. COMPARING AD SETS")
    print("-" * 40)
    
    # Get ad IDs from both queries
    db_ad_ids = set(ad['ad_id'] for ad in july_2025_all.data)
    service_ad_ids = set(ad['ad_id'] for ad in july_2025_from_service)
    
    print(f"DB ad IDs: {len(db_ad_ids)}")
    print(f"Service ad IDs: {len(service_ad_ids)}")
    
    missing_in_service = db_ad_ids - service_ad_ids
    if missing_in_service:
        print(f"\n🚨 {len(missing_in_service)} ads missing from service:")
        for ad_id in list(missing_in_service)[:5]:
            ad_info = next((ad for ad in july_2025_all.data if ad['ad_id'] == ad_id), None)
            if ad_info:
                print(f"  Ad {ad_id}: ${ad_info.get('amount_spent_usd', 0):,.2f}")
    
    extra_in_service = service_ad_ids - db_ad_ids
    if extra_in_service:
        print(f"\n⚠️ {len(extra_in_service)} extra ads in service:")
        for ad_id in extra_in_service:
            print(f"  Ad {ad_id}")
    
    print("\n4. CHECKING SERVICE DATA COMPLETENESS")
    print("-" * 40)
    
    # Check if service query has any limitations
    print("Testing service query with explicit order and limit...")
    
    test_query = supabase.table("tiktok_ad_data")\
        .select("*")\
        .gte("reporting_starts", "2025-07-01")\
        .lte("reporting_ends", "2025-07-31")\
        .order("ad_id")\
        .execute()
    
    print(f"Explicit July 2025 query returns: {len(test_query.data)} ads")
    test_spend = sum(ad.get('amount_spent_usd', 0) for ad in test_query.data)
    print(f"Explicit query spend: ${test_spend:,.2f}")
    
    if len(test_query.data) == len(july_2025_all.data):
        print("✅ Explicit query matches DB query")
    else:
        print("🚨 Explicit query differs from DB query")
    
    print("\n5. INVESTIGATING THE ROOT CAUSE")
    print("-" * 40)
    
    # Check if there are any NULL values or date issues
    july_ads_with_nulls = [ad for ad in july_2025_all.data 
                          if not ad.get('reporting_starts') or not ad.get('amount_spent_usd')]
    
    if july_ads_with_nulls:
        print(f"Found {len(july_ads_with_nulls)} ads with NULL reporting_starts or spend")
        for ad in july_ads_with_nulls:
            print(f"  Ad {ad.get('ad_id')}: starts={ad.get('reporting_starts')}, spend={ad.get('amount_spent_usd')}")
    else:
        print("No ads with NULL reporting_starts or spend found")
        
    # Check for duplicate ad_ids
    ad_id_counts = {}
    for ad in july_2025_all.data:
        ad_id = ad.get('ad_id')
        ad_id_counts[ad_id] = ad_id_counts.get(ad_id, 0) + 1
    
    duplicates = {ad_id: count for ad_id, count in ad_id_counts.items() if count > 1}
    if duplicates:
        print(f"\nFound {len(duplicates)} duplicate ad_ids:")
        for ad_id, count in list(duplicates.items())[:5]:
            print(f"  Ad {ad_id}: {count} entries")
    else:
        print("No duplicate ad_ids found")

if __name__ == "__main__":
    debug_july_2025_ads()