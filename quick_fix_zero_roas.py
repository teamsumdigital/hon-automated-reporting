#!/usr/bin/env python3
"""
Quick fix for zero ROAS records - processes in small batches
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

def quick_fix_zero_roas():
    """Quick fix for zero ROAS records in small batches"""
    print("🚀 Quick Fix for Zero ROAS Records")
    print("=" * 50)
    
    # Initialize services
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    tiktok_service = TikTokAdsService()
    
    try:
        # Get records with zero ROAS but spend > 0, limit to top 10 by spend
        print("🔍 Getting top 10 records with zero ROAS but highest spend...")
        result = supabase.table('tiktok_campaign_data').select('*').eq(
            'roas', 0
        ).gt('amount_spent_usd', 100).order('amount_spent_usd', desc=True).limit(10).execute()
        
        zero_roas_records = result.data if result.data else []
        
        if not zero_roas_records:
            print("✅ No high-spend records found with zero ROAS")
            return
        
        print(f"📊 Processing {len(zero_roas_records)} high-value records:")
        for record in zero_roas_records:
            print(f"   💰 {record['campaign_name'][:40]:40} | ${record['amount_spent_usd']:8.2f} | {record['reporting_starts']}")
        print()
        
        fixed_count = 0
        
        # Process each record individually for better control
        for i, record in enumerate(zero_roas_records, 1):
            try:
                start_date = datetime.fromisoformat(record['reporting_starts']).date()
                end_date = datetime.fromisoformat(record['reporting_ends']).date()
                campaign_id = record['campaign_id']
                
                print(f"📅 {i}/{len(zero_roas_records)}: Processing {record['campaign_name'][:30]}")
                print(f"   📡 Fetching {start_date} to {end_date}...")
                
                # Fetch single campaign data
                insights = tiktok_service.get_campaign_insights(
                    start_date, end_date, campaign_ids=[campaign_id]
                )
                
                if not insights:
                    print(f"   ⚠️ No data returned from API")
                    continue
                
                # Convert to campaign data
                campaign_data_list = tiktok_service.convert_to_campaign_data(insights)
                
                if not campaign_data_list:
                    print(f"   ⚠️ No campaign data converted")
                    continue
                
                campaign_data = campaign_data_list[0]
                
                # Calculate CPM
                cpm = Decimal('0')
                if campaign_data.impressions > 0:
                    cpm = (campaign_data.amount_spent_usd / (Decimal(campaign_data.impressions) / 1000)).quantize(Decimal('0.0001'))
                
                # Update the record
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
                ).eq('id', record['id']).execute()
                
                print(f"   ✅ Updated: ROAS {campaign_data.roas:.2f} | Revenue ${campaign_data.purchases_conversion_value:.2f} | CPM ${cpm:.2f}")
                fixed_count += 1
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        print()
        print("=" * 50)
        print(f"🎯 Quick Fix Complete: {fixed_count}/{len(zero_roas_records)} records updated")
        
        # Check remaining zero ROAS records
        final_check = supabase.table('tiktok_campaign_data').select('*').eq(
            'roas', 0
        ).gt('amount_spent_usd', 0).execute()
        
        remaining_zero = len(final_check.data) if final_check.data else 0
        print(f"⚠️ Remaining zero ROAS records: {remaining_zero}")
        
        # Show sample of what was fixed
        print("\n📊 Sample of updated records:")
        updated_result = supabase.table('tiktok_campaign_data').select(
            'campaign_name', 'amount_spent_usd', 'roas', 'purchases_conversion_value', 'cpm'
        ).gt('roas', 0).gt('amount_spent_usd', 100).order('amount_spent_usd', desc=True).limit(5).execute()
        
        if updated_result.data:
            for record in updated_result.data:
                print(f"✅ {record['campaign_name'][:30]:30} | ${record['amount_spent_usd']:8.2f} | ROAS: {record['roas']:6.2f} | Revenue: ${record['purchases_conversion_value']:8.2f} | CPM: ${record['cpm']:6.2f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_fix_zero_roas()