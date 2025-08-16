#!/usr/bin/env python3
"""
Simple TikTok Campaign Data Backfill Script
Backfills data and fixes missing ROAS values
"""

import os
import sys
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import calendar
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.tiktok_ads_service import TikTokAdsService

def backfill_tiktok_data():
    """Simple backfill for TikTok data"""
    print("🚀 Starting TikTok Campaign Data Backfill")
    print("=" * 60)
    
    # Initialize services
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    tiktok_service = TikTokAdsService()
    
    # Test connection
    print("🔗 Testing TikTok API connection...")
    if not tiktok_service.test_connection():
        print("❌ TikTok API connection failed!")
        return
    print("✅ TikTok API connection successful!")
    print()
    
    # Check existing data
    print("📊 Checking existing TikTok data...")
    try:
        result = supabase.table('tiktok_campaign_data').select('*', count='exact').execute()
        existing_count = result.count if hasattr(result, 'count') else len(result.data)
        print(f"   📈 Found {existing_count} existing TikTok campaign records")
        
        # Check for records with zero ROAS but spend > 0
        zero_roas_result = supabase.table('tiktok_campaign_data').select('*').eq(
            'roas', 0
        ).gt('amount_spent_usd', 0).execute()
        
        zero_roas_count = len(zero_roas_result.data) if zero_roas_result.data else 0
        print(f"   ⚠️ Found {zero_roas_count} records with zero ROAS but spend > 0")
        
    except Exception as e:
        print(f"   ❌ Error checking existing data: {e}")
        existing_count = 0
        zero_roas_count = 0
    
    print()
    
    # Define months to backfill (July 2025 as example, you can expand this)
    months_to_process = [
        (2024, 1), (2024, 2), (2024, 3), (2024, 4), (2024, 5), (2024, 6),
        (2024, 7), (2024, 8), (2024, 9), (2024, 10), (2024, 11), (2024, 12),
        (2025, 1), (2025, 2), (2025, 3), (2025, 4), (2025, 5), (2025, 6),
        (2025, 7), (2025, 8)  # Through August 2025
    ]
    
    print(f"📅 Processing {len(months_to_process)} months (Jan 2024 - Aug 2025)")
    print()
    
    total_campaigns_processed = 0
    successful_months = 0
    
    for year, month in months_to_process:
        try:
            # Get month date range
            start_date = date(year, month, 1)
            last_day = calendar.monthrange(year, month)[1]
            
            # For August 2025, only go through the 14th
            if year == 2025 and month == 8:
                end_date = date(year, month, 14)
            else:
                end_date = date(year, month, last_day)
            
            month_name = start_date.strftime("%B %Y")
            print(f"📅 Processing {month_name} ({start_date} to {end_date})")
            
            # Fetch TikTok data
            insights = tiktok_service.get_campaign_insights(start_date, end_date)
            
            if not insights:
                print(f"   ⚠️ No data found for {month_name}")
                continue
            
            print(f"   📡 Retrieved {len(insights)} campaign insights")
            
            # Convert to campaign data
            campaign_data_list = tiktok_service.convert_to_campaign_data(insights)
            
            if not campaign_data_list:
                print(f"   ⚠️ No campaign data converted for {month_name}")
                continue
            
            print(f"   ✅ Converted {len(campaign_data_list)} campaigns")
            
            # Upsert to database
            month_success_count = 0
            month_error_count = 0
            
            for campaign_data in campaign_data_list:
                try:
                    # Prepare data for upsert (without CPM for now)
                    upsert_data = {
                        'campaign_id': campaign_data.campaign_id,
                        'campaign_name': campaign_data.campaign_name,
                        'category': campaign_data.category,
                        'campaign_type': campaign_data.campaign_type,
                        'reporting_starts': campaign_data.reporting_starts.isoformat(),
                        'reporting_ends': campaign_data.reporting_ends.isoformat(),
                        'amount_spent_usd': float(campaign_data.amount_spent_usd),
                        'website_purchases': campaign_data.website_purchases,
                        'purchases_conversion_value': float(campaign_data.purchases_conversion_value),
                        'impressions': campaign_data.impressions,
                        'link_clicks': campaign_data.link_clicks,
                        'cpa': float(campaign_data.cpa),
                        'roas': float(campaign_data.roas),
                        'cpc': float(campaign_data.cpc),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    # Upsert (update if exists, insert if not)
                    result = supabase.table('tiktok_campaign_data').upsert(
                        upsert_data,
                        on_conflict='campaign_id,reporting_starts,reporting_ends'
                    ).execute()
                    
                    month_success_count += 1
                    
                except Exception as e:
                    print(f"   ❌ Failed to upsert campaign {campaign_data.campaign_id}: {e}")
                    month_error_count += 1
                    continue
            
            print(f"   💾 Upserted: {month_success_count} success, {month_error_count} errors")
            print()
            
            total_campaigns_processed += month_success_count
            successful_months += 1
            
        except Exception as e:
            print(f"   ❌ Error processing {month_name}: {e}")
            continue
    
    # Final summary
    print("=" * 60)
    print("🎯 TikTok Backfill Complete!")
    print(f"   ✅ Successful months: {successful_months}/{len(months_to_process)}")
    print(f"   📊 Total campaigns processed: {total_campaigns_processed}")
    print(f"   📅 Date range: January 2024 - August 14, 2025")
    print()
    print("📋 Next steps:")
    print("   1. Run the SQL commands in MANUAL_SQL_COMMANDS.md to add CPM column")
    print("   2. Re-run this script with --update-cpm flag to calculate CPM values")

def update_cpm_values():
    """Update CPM values for existing records"""
    print("🔧 Updating CPM values for existing records...")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        # Get all records with impressions > 0
        result = supabase.table('tiktok_campaign_data').select('*').gt('impressions', 0).execute()
        
        if not result.data:
            print("   ⚠️ No records found with impressions > 0")
            return
        
        print(f"   📊 Found {len(result.data)} records to update")
        
        update_count = 0
        
        for record in result.data:
            try:
                # Calculate CPM
                spend = Decimal(str(record['amount_spent_usd']))
                impressions = Decimal(str(record['impressions']))
                
                if impressions > 0:
                    cpm = (spend / (impressions / 1000)).quantize(Decimal('0.0001'))
                    
                    # Update record (only if CPM column exists)
                    try:
                        update_result = supabase.table('tiktok_campaign_data').update({
                            'cpm': float(cpm)
                        }).eq('id', record['id']).execute()
                        
                        update_count += 1
                        
                    except Exception as e:
                        if 'column "cpm" of relation "tiktok_campaign_data" does not exist' in str(e):
                            print("   ⚠️ CPM column doesn't exist yet. Please run the SQL commands first.")
                            return
                        else:
                            raise e
                
            except Exception as e:
                print(f"   ❌ Error updating record {record['id']}: {e}")
                continue
        
        print(f"   ✅ Updated CPM for {update_count} records")
        
    except Exception as e:
        print(f"   ❌ Error updating CPM values: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple TikTok data backfill')
    parser.add_argument('--update-cpm', action='store_true', 
                       help='Update CPM values for existing records')
    
    args = parser.parse_args()
    
    if args.update_cpm:
        update_cpm_values()
    else:
        backfill_tiktok_data()