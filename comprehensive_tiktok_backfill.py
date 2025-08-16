#!/usr/bin/env python3
"""
Comprehensive TikTok Backfill for ALL months with zero ROAS
Fixes all historical data from January 2024 through August 14, 2025
"""

import os
import sys
from datetime import date, datetime, timedelta
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

def comprehensive_backfill():
    """Comprehensive backfill for all TikTok months"""
    print("🚀 Comprehensive TikTok Backfill - All Months")
    print("=" * 60)
    
    # Initialize services
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    tiktok_service = TikTokAdsService()
    
    try:
        # Test connection first
        print("🔗 Testing TikTok API connection...")
        if not tiktok_service.test_connection():
            print("❌ TikTok API connection failed!")
            return
        print("✅ TikTok API connection successful!")
        print()
        
        # Get all records with zero ROAS but spend > 0
        print("📊 Finding records with zero ROAS...")
        zero_roas_result = supabase.table('tiktok_campaign_data').select('*').eq(
            'roas', 0
        ).gt('amount_spent_usd', 0).order('reporting_starts', desc=False).execute()
        
        zero_roas_records = zero_roas_result.data if zero_roas_result.data else []
        
        print(f"⚠️ Found {len(zero_roas_records)} records with zero ROAS but spend > 0")
        
        if not zero_roas_records:
            print("✅ No records need fixing!")
            return
        
        # Group by month for efficient processing
        months_to_fix = {}
        for record in zero_roas_records:
            month_key = record['reporting_starts'][:7]  # YYYY-MM format
            if month_key not in months_to_fix:
                months_to_fix[month_key] = []
            months_to_fix[month_key].append(record)
        
        print(f"📅 Need to fix {len(months_to_fix)} months:")
        for month_key, records in months_to_fix.items():
            total_spend = sum(float(r['amount_spent_usd']) for r in records)
            print(f"   • {month_key}: {len(records)} records, ${total_spend:,.2f} spend")
        print()
        
        # Process each month
        fixed_months = 0
        total_fixed_records = 0
        
        for i, (month_key, records) in enumerate(months_to_fix.items(), 1):
            try:
                year, month = map(int, month_key.split('-'))
                
                # Determine date range
                start_date = date(year, month, 1)
                
                if year == 2025 and month == 8:
                    # August 2025: only through the 14th
                    end_date = date(year, month, 14)
                else:
                    # Full month
                    last_day = calendar.monthrange(year, month)[1]
                    end_date = date(year, month, last_day)
                
                month_name = start_date.strftime("%B %Y")
                month_spend = sum(float(r['amount_spent_usd']) for r in records)
                
                print(f"📅 {i}/{len(months_to_fix)}: {month_name} ({len(records)} records, ${month_spend:,.2f} spend)")
                
                # Fetch fresh data from TikTok API
                print(f"   📡 Fetching from TikTok API...")
                insights = tiktok_service.get_campaign_insights(start_date, end_date)
                
                if not insights:
                    print(f"   ⚠️ No data returned from API")
                    continue
                
                print(f"   📈 Retrieved {len(insights)} campaigns")
                
                # Convert to campaign data
                campaign_data_list = tiktok_service.convert_to_campaign_data(insights)
                
                if not campaign_data_list:
                    print(f"   ⚠️ No campaign data converted")
                    continue
                
                print(f"   ✅ Converted {len(campaign_data_list)} campaigns")
                
                # Update each record that has zero ROAS
                month_fixed = 0
                month_errors = 0
                
                for campaign_data in campaign_data_list:
                    try:
                        # Find corresponding zero ROAS record
                        matching_record = next(
                            (r for r in records if r['campaign_id'] == campaign_data.campaign_id),
                            None
                        )
                        
                        if not matching_record:
                            continue
                        
                        # Only update if the record actually has zero ROAS
                        if float(matching_record['roas']) > 0:
                            continue
                        
                        # Calculate CPM
                        cpm = Decimal('0')
                        if campaign_data.impressions > 0:
                            cpm = (campaign_data.amount_spent_usd / (Decimal(campaign_data.impressions) / 1000)).quantize(Decimal('0.0001'))
                        
                        # Update the record with fresh TikTok data
                        update_data = {
                            'roas': float(campaign_data.roas),
                            'purchases_conversion_value': float(campaign_data.purchases_conversion_value),
                            'website_purchases': campaign_data.website_purchases,
                            'cpa': float(campaign_data.cpa),
                            'cpm': float(cpm),
                            'updated_at': datetime.now().isoformat()
                        }
                        
                        update_result = supabase.table('tiktok_campaign_data').update(
                            update_data
                        ).eq('id', matching_record['id']).execute()
                        
                        month_fixed += 1
                        
                        if campaign_data.roas > 0:
                            print(f"   ✅ Fixed {campaign_data.campaign_name[:25]:25} | ROAS: {campaign_data.roas:6.2f} | Revenue: ${campaign_data.purchases_conversion_value:8.2f}")
                        
                    except Exception as e:
                        print(f"   ❌ Error updating campaign {campaign_data.campaign_id}: {e}")
                        month_errors += 1
                        continue
                
                print(f"   💾 Month result: {month_fixed} fixed, {month_errors} errors")
                print()
                
                total_fixed_records += month_fixed
                if month_fixed > 0:
                    fixed_months += 1
                
            except Exception as e:
                print(f"   ❌ Error processing {month_key}: {e}")
                continue
        
        # Final summary
        print("=" * 60)
        print("🎯 Comprehensive Backfill Complete!")
        print(f"   ✅ Months processed: {len(months_to_fix)}")
        print(f"   ✅ Months with fixes: {fixed_months}")
        print(f"   ✅ Records fixed: {total_fixed_records}")
        
        # Check final status
        final_check = supabase.table('tiktok_campaign_data').select('*').eq(
            'roas', 0
        ).gt('amount_spent_usd', 0).execute()
        
        remaining_zero = len(final_check.data) if final_check.data else 0
        improvement = len(zero_roas_records) - remaining_zero
        
        print(f"   ⚠️ Remaining zero ROAS: {remaining_zero} (improved by {improvement})")
        
        # Show overall stats
        total_result = supabase.table('tiktok_campaign_data').select('*').execute()
        total_records = len(total_result.data) if total_result.data else 0
        
        roas_records = supabase.table('tiktok_campaign_data').select('*').gt('roas', 0).execute()
        roas_count = len(roas_records.data) if roas_records.data else 0
        
        print(f"   📊 Total records: {total_records}")
        print(f"   📈 Records with ROAS > 0: {roas_count}")
        print(f"   📈 ROAS coverage: {(roas_count/total_records)*100:.1f}%")
        
        # Calculate final totals
        spend_records = supabase.table('tiktok_campaign_data').select('*').gt('amount_spent_usd', 0).execute()
        
        if spend_records.data:
            total_spend = sum(float(r['amount_spent_usd']) for r in spend_records.data)
            total_revenue = sum(float(r['purchases_conversion_value']) for r in spend_records.data)
            total_purchases = sum(int(r['website_purchases']) for r in spend_records.data)
            
            overall_roas = total_revenue / total_spend if total_spend > 0 else 0
            
            print(f"\n📊 FINAL TOTALS:")
            print(f"   💰 Total Spend: ${total_spend:,.2f}")
            print(f"   🛒 Total Purchases: {total_purchases:,}")
            print(f"   💵 Total Revenue: ${total_revenue:,.2f}")
            print(f"   📈 Overall ROAS: {overall_roas:.2f}")
        
    except Exception as e:
        print(f"❌ Error in comprehensive backfill: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    comprehensive_backfill()