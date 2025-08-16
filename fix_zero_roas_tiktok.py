#!/usr/bin/env python3
"""
Fix TikTok records with zero ROAS but spend > 0
Re-fetch with correct Payment Complete ROAS
"""

import os
import sys
from datetime import date, datetime
from decimal import Decimal
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.tiktok_ads_service import TikTokAdsService

def fix_zero_roas_records():
    """Fix records with zero ROAS but spend > 0"""
    print("🔧 Fixing TikTok Records with Zero ROAS")
    print("=" * 50)
    
    # Initialize services
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    tiktok_service = TikTokAdsService()
    
    try:
        # Get records with zero ROAS but spend > 0
        print("🔍 Finding records with zero ROAS but spend > 0...")
        result = supabase.table('tiktok_campaign_data').select('*').eq(
            'roas', 0
        ).gt('amount_spent_usd', 0).order('amount_spent_usd', desc=True).execute()
        
        zero_roas_records = result.data if result.data else []
        
        if not zero_roas_records:
            print("✅ No records found with zero ROAS and spend > 0")
            return
        
        print(f"📊 Found {len(zero_roas_records)} records to fix")
        print()
        
        fixed_count = 0
        error_count = 0
        
        # Group records by date range to minimize API calls
        date_ranges = {}
        for record in zero_roas_records:
            start_date = record['reporting_starts']
            end_date = record['reporting_ends']
            date_key = f"{start_date}_{end_date}"
            
            if date_key not in date_ranges:
                date_ranges[date_key] = []
            date_ranges[date_key].append(record)
        
        print(f"📅 Processing {len(date_ranges)} unique date ranges...")
        print()
        
        for i, (date_key, records) in enumerate(date_ranges.items(), 1):
            try:
                start_date_str, end_date_str = date_key.split('_')
                start_date = datetime.fromisoformat(start_date_str).date()
                end_date = datetime.fromisoformat(end_date_str).date()
                
                print(f"📅 {i}/{len(date_ranges)}: {start_date} to {end_date} ({len(records)} campaigns)")
                
                # Get campaign IDs for this date range
                campaign_ids = [record['campaign_id'] for record in records]
                
                # Re-fetch from TikTok API with correct ROAS
                print(f"   📡 Fetching fresh data from TikTok API...")
                insights = tiktok_service.get_campaign_insights(
                    start_date, end_date, campaign_ids=campaign_ids
                )
                
                if not insights:
                    print(f"   ⚠️ No insights returned from API")
                    continue
                
                print(f"   📈 Retrieved {len(insights)} insights")
                
                # Convert to campaign data with correct ROAS
                campaign_data_list = tiktok_service.convert_to_campaign_data(insights)
                
                if not campaign_data_list:
                    print(f"   ⚠️ No campaign data converted")
                    continue
                
                print(f"   ✅ Converted {len(campaign_data_list)} campaigns")
                
                # Update each record
                range_fixed = 0
                range_errors = 0
                
                for campaign_data in campaign_data_list:
                    try:
                        # Find the corresponding database record
                        db_record = next(
                            (r for r in records if r['campaign_id'] == campaign_data.campaign_id), 
                            None
                        )
                        
                        if not db_record:
                            continue
                        
                        # Calculate CPM (if we can)
                        cpm = Decimal('0')
                        if campaign_data.impressions > 0:
                            cpm = (campaign_data.amount_spent_usd / (Decimal(campaign_data.impressions) / 1000)).quantize(Decimal('0.0001'))
                        
                        # Prepare update data
                        update_data = {
                            'roas': float(campaign_data.roas),
                            'purchases_conversion_value': float(campaign_data.purchases_conversion_value),
                            'website_purchases': campaign_data.website_purchases,
                            'cpa': float(campaign_data.cpa),
                            'updated_at': datetime.now().isoformat()
                        }
                        
                        # Try to add CPM if column exists
                        try:
                            update_data['cpm'] = float(cpm)
                        except:
                            pass  # CPM column doesn't exist yet
                        
                        # Update the record
                        update_result = supabase.table('tiktok_campaign_data').update(
                            update_data
                        ).eq('id', db_record['id']).execute()
                        
                        range_fixed += 1
                        
                        if campaign_data.roas > 0:
                            print(f"   ✅ Fixed {campaign_data.campaign_name[:30]:30} | ROAS: {campaign_data.roas:6.2f} | Revenue: ${campaign_data.purchases_conversion_value:8.2f}")
                        
                    except Exception as e:
                        print(f"   ❌ Error updating campaign {campaign_data.campaign_id}: {e}")
                        range_errors += 1
                        continue
                
                print(f"   💾 Updated: {range_fixed} success, {range_errors} errors")
                print()
                
                fixed_count += range_fixed
                error_count += range_errors
                
            except Exception as e:
                print(f"   ❌ Error processing date range {date_key}: {e}")
                error_count += len(records)
                continue
        
        # Final summary
        print("=" * 50)
        print("🎯 Zero ROAS Fix Complete!")
        print(f"   ✅ Records fixed: {fixed_count}")
        print(f"   ❌ Errors: {error_count}")
        print(f"   📊 Total processed: {len(zero_roas_records)}")
        
        # Check remaining zero ROAS records
        final_check = supabase.table('tiktok_campaign_data').select('*').eq(
            'roas', 0
        ).gt('amount_spent_usd', 0).execute()
        
        remaining_zero = len(final_check.data) if final_check.data else 0
        print(f"   ⚠️ Remaining zero ROAS records: {remaining_zero}")
        
    except Exception as e:
        print(f"❌ Error fixing zero ROAS records: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_zero_roas_records()