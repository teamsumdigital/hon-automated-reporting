#!/usr/bin/env python3
"""
Debug script to investigate Standing Mats filtering issue in TikTok ad level dashboard
"""

import os
import sys
from datetime import datetime, date
from supabase import create_client
from decimal import Decimal

# Add the backend path to import services
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def setup_supabase():
    """Setup Supabase connection"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return None
        
    return create_client(supabase_url, supabase_key)

def test_category_filtering():
    """Test TikTok category filtering to debug Standing Mats issue"""
    
    supabase = setup_supabase()
    if not supabase:
        return
    
    print("🔍 Debugging Standing Mats filtering issue...")
    print("=" * 60)
    
    # First, let's get all TikTok ad data for July 2025
    july_start = "2025-07-01"
    july_end = "2025-07-31"
    
    print(f"📅 Getting all TikTok ad data for July 2025 ({july_start} to {july_end})")
    
    try:
        # Get all data for July 2025
        all_july_result = supabase.table("tiktok_ad_data")\
            .select("*")\
            .gte("reporting_starts", july_start)\
            .lte("reporting_ends", july_end)\
            .execute()
        
        all_july_data = all_july_result.data
        print(f"📊 Total July 2025 records: {len(all_july_data)}")
        
        # Group by category and sum spend
        category_totals = {}
        for record in all_july_data:
            category = record.get('category', 'Unknown')
            spend = float(record.get('amount_spent_usd', 0))
            
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += spend
        
        print("\n💰 Spend by Category (July 2025):")
        total_spend = 0
        for category, spend in sorted(category_totals.items()):
            print(f"   {category}: ${spend:,.2f}")
            total_spend += spend
        print(f"   TOTAL: ${total_spend:,.2f}")
        
        print("\n" + "=" * 60)
        
        # Test individual category filters
        test_categories = ['Play Furniture', 'Tumbling Mats', 'Play Mats', 'Bath Mats', 'Standing Mats']
        
        print("🔬 Testing individual category filters:")
        individual_totals = {}
        
        for category in test_categories:
            result = supabase.table("tiktok_ad_data")\
                .select("*")\
                .gte("reporting_starts", july_start)\
                .lte("reporting_ends", july_end)\
                .eq("category", category)\
                .execute()
            
            data = result.data
            spend = sum(float(record.get('amount_spent_usd', 0)) for record in data)
            individual_totals[category] = spend
            
            print(f"   {category}: ${spend:,.2f} ({len(data)} records)")
        
        print(f"   Individual totals sum: ${sum(individual_totals.values()):,.2f}")
        
        print("\n" + "=" * 60)
        
        # Test the exact filter combination that works (without Standing Mats)
        working_categories = ['Play Furniture', 'Tumbling Mats', 'Play Mats', 'Bath Mats']
        
        print("✅ Testing working combination (without Standing Mats):")
        working_result = supabase.table("tiktok_ad_data")\
            .select("*")\
            .gte("reporting_starts", july_start)\
            .lte("reporting_ends", july_end)\
            .in_("category", working_categories)\
            .execute()
        
        working_data = working_result.data
        working_spend = sum(float(record.get('amount_spent_usd', 0)) for record in working_data)
        
        print(f"   Combined filter result: ${working_spend:,.2f} ({len(working_data)} records)")
        print(f"   Expected (sum of individual): ${sum(individual_totals[cat] for cat in working_categories):,.2f}")
        
        # Test the problematic combination (with Standing Mats)
        all_categories = ['Play Furniture', 'Tumbling Mats', 'Play Mats', 'Bath Mats', 'Standing Mats']
        
        print("\n❌ Testing problematic combination (with Standing Mats):")
        problematic_result = supabase.table("tiktok_ad_data")\
            .select("*")\
            .gte("reporting_starts", july_start)\
            .lte("reporting_ends", july_end)\
            .in_("category", all_categories)\
            .execute()
        
        problematic_data = problematic_result.data
        problematic_spend = sum(float(record.get('amount_spent_usd', 0)) for record in problematic_data)
        
        print(f"   Combined filter result: ${problematic_spend:,.2f} ({len(problematic_data)} records)")
        print(f"   Expected (sum of individual): ${sum(individual_totals.values()):,.2f}")
        
        print("\n" + "=" * 60)
        
        # Let's examine the data more closely
        print("🔍 Examining Standing Mats records in detail:")
        
        standing_result = supabase.table("tiktok_ad_data")\
            .select("*")\
            .gte("reporting_starts", july_start)\
            .lte("reporting_ends", july_end)\
            .eq("category", "Standing Mats")\
            .execute()
        
        standing_data = standing_result.data
        
        print(f"Standing Mats records: {len(standing_data)}")
        
        if standing_data:
            print("First few Standing Mats records:")
            for i, record in enumerate(standing_data[:5]):  # Show first 5
                print(f"   {i+1}. Ad: {record.get('ad_name', 'N/A')[:50]}...")
                print(f"      Spend: ${record.get('amount_spent_usd', 0)}")
                print(f"      Category: {record.get('category', 'N/A')}")
                print(f"      Date: {record.get('reporting_starts', 'N/A')} to {record.get('reporting_ends', 'N/A')}")
                print()
        
        print("\n" + "=" * 60)
        
        # Check for any duplicate ad_id + date combinations
        print("🔍 Checking for duplicate ad records...")
        
        # Group by ad_id and date to check for duplicates
        ad_date_combinations = {}
        
        for record in all_july_data:
            ad_id = record.get('ad_id', 'unknown')
            start_date = record.get('reporting_starts', 'unknown')
            end_date = record.get('reporting_ends', 'unknown')
            key = f"{ad_id}_{start_date}_{end_date}"
            
            if key not in ad_date_combinations:
                ad_date_combinations[key] = []
            ad_date_combinations[key].append(record)
        
        duplicates = {k: v for k, v in ad_date_combinations.items() if len(v) > 1}
        
        if duplicates:
            print(f"⚠️  Found {len(duplicates)} duplicate ad+date combinations:")
            for key, records in list(duplicates.items())[:3]:  # Show first 3
                print(f"   {key}: {len(records)} records")
                for record in records:
                    print(f"      Category: {record.get('category', 'N/A')}, Spend: ${record.get('amount_spent_usd', 0)}")
        else:
            print("✅ No duplicate ad+date combinations found")
        
        print("\n" + "=" * 60)
        
        # Final analysis
        print("📋 ANALYSIS SUMMARY:")
        print(f"1. Total spend from database query: ${total_spend:,.2f}")
        print(f"2. Sum of individual categories: ${sum(individual_totals.values()):,.2f}")
        print(f"3. Working filter combination: ${working_spend:,.2f}")
        print(f"4. Problematic filter combination: ${problematic_spend:,.2f}")
        print(f"5. Difference when adding Standing Mats: ${problematic_spend - working_spend:+,.2f}")
        print(f"6. Expected difference (Standing Mats alone): ${individual_totals.get('Standing Mats', 0):+,.2f}")
        
        if problematic_spend != sum(individual_totals.values()):
            print("\n🚨 ISSUE IDENTIFIED:")
            print("   The combined filter with Standing Mats is NOT returning the expected total!")
            print("   This suggests there may be an issue with:")
            print("   - Database query logic")
            print("   - Data integrity (duplicate records)")
            print("   - Category assignment inconsistencies")
        else:
            print("\n✅ No database-level filtering issue detected.")
            print("   The problem may be in the frontend processing or API response handling.")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_category_filtering()