#!/usr/bin/env python3
"""
Check TikTok ads with proper names
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Database connection
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Get sample of ads with proper names (not starting with 'Ad ')
result = supabase.table("tiktok_ad_data")\
    .select("ad_id, ad_name, campaign_name, category, amount_spent_usd, website_purchases, roas")\
    .not_.like("ad_name", "Ad %")\
    .order("amount_spent_usd", desc=True)\
    .limit(20)\
    .execute()

if result.data:
    print(f"Found {len(result.data)} TikTok ads with proper names")
    print("\nTop spending ads:")
    
    for ad in result.data:
        print(f"\n{'='*80}")
        print(f"Ad ID: {ad['ad_id']}")
        print(f"Ad Name: {ad['ad_name']}")
        print(f"Campaign: {ad['campaign_name']}")
        print(f"Category: {ad['category']}")
        print(f"Spend: ${ad['amount_spent_usd']:,.2f}")
        print(f"Purchases: {ad['website_purchases']}")
        print(f"ROAS: {ad['roas']:.2f}")

# Check category distribution
category_result = supabase.table("tiktok_ad_data")\
    .select("category")\
    .not_.like("ad_name", "Ad %")\
    .execute()

if category_result.data:
    categories = {}
    for row in category_result.data:
        cat = row['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n\n{'='*80}")
    print("Category distribution for ads with names:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count} ads")