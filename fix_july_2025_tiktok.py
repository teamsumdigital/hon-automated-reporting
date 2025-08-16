#!/usr/bin/env python3
"""
Fix July 2025 TikTok data to match platform exactly
Platform shows: 900 conversions, 7.8 ROAS, $33.84 CPA
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

def fix_july_2025_data():
    """Fix July 2025 data to match TikTok platform exactly"""
    print("🎯 Fixing July 2025 TikTok Data")
    print("=" * 40)
    
    # Initialize services
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    tiktok_service = TikTokAdsService()
    
    try:
        # Get current July 2025 data from database
        print("📊 Current July 2025 data in database:")
        result = supabase.table('tiktok_campaign_data').select('*').gte(
            'reporting_starts', '2025-07-01'
        ).lte('reporting_ends', '2025-07-31').execute()
        
        current_records = result.data if result.data else []
        
        if current_records:
            total_spend = sum(float(r['amount_spent_usd']) for r in current_records)
            total_purchases = sum(int(r['website_purchases']) for r in current_records)
            total_revenue = sum(float(r['purchases_conversion_value']) for r in current_records)
            
            current_roas = total_revenue / total_spend if total_spend > 0 else 0
            current_cpa = total_spend / total_purchases if total_purchases > 0 else 0
            
            print(f"   💰 Spend: ${total_spend:,.2f}")
            print(f"   🛒 Purchases: {total_purchases}")
            print(f"   💵 Revenue: ${total_revenue:,.2f}")
            print(f"   📈 ROAS: {current_roas:.2f}")
            print(f"   🎯 CPA: ${current_cpa:.2f}")
        
        print(f"\n🎯 Platform target:")
        print(f"   💰 Spend: $30,452")
        print(f"   🛒 Purchases: 900") 
        print(f"   📈 ROAS: 7.8")
        print(f"   🎯 CPA: $33.84")
        
        # Re-fetch July 2025 from TikTok API
        print(f"\n📡 Re-fetching July 2025 from TikTok API...")
        
        start_date = date(2025, 7, 1)
        end_date = date(2025, 7, 31)
        
        insights = tiktok_service.get_campaign_insights(start_date, end_date)
        
        if not insights:
            print("❌ No data returned from TikTok API")
            return
        
        print(f"✅ Retrieved {len(insights)} campaigns from API")
        
        # Convert with fresh data
        campaign_data_list = tiktok_service.convert_to_campaign_data(insights)
        
        if not campaign_data_list:
            print("❌ No campaign data converted")
            return
        
        print(f"✅ Converted {len(campaign_data_list)} campaigns")
        
        # Delete existing July 2025 records first
        print(f"\n🗑️ Deleting existing July 2025 records...")
        delete_result = supabase.table('tiktok_campaign_data').delete().gte(
            'reporting_starts', '2025-07-01'
        ).lte('reporting_ends', '2025-07-31').execute()
        
        print(f"✅ Deleted existing records")
        
        # Insert fresh data
        print(f"\n💾 Inserting fresh July 2025 data...")
        
        success_count = 0
        
        for campaign_data in campaign_data_list:
            try:
                # Calculate CPM
                cpm = Decimal('0')
                if campaign_data.impressions > 0:
                    cpm = (campaign_data.amount_spent_usd / (Decimal(campaign_data.impressions) / 1000)).quantize(Decimal('0.0001'))
                
                # Prepare insert data
                insert_data = {
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
                    'cpm': float(cpm),
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Insert record
                insert_result = supabase.table('tiktok_campaign_data').insert(insert_data).execute()
                success_count += 1
                
            except Exception as e:
                print(f"❌ Error inserting campaign {campaign_data.campaign_id}: {e}")
                continue
        
        print(f"✅ Inserted {success_count} campaigns")
        
        # Verify the fix
        print(f"\n🔍 Verifying updated July 2025 data:")
        verify_result = supabase.table('tiktok_campaign_data').select('*').gte(
            'reporting_starts', '2025-07-01'
        ).lte('reporting_ends', '2025-07-31').execute()
        
        updated_records = verify_result.data if verify_result.data else []
        
        if updated_records:
            new_total_spend = sum(float(r['amount_spent_usd']) for r in updated_records)
            new_total_purchases = sum(int(r['website_purchases']) for r in updated_records)
            new_total_revenue = sum(float(r['purchases_conversion_value']) for r in updated_records)
            
            new_roas = new_total_revenue / new_total_spend if new_total_spend > 0 else 0
            new_cpa = new_total_spend / new_total_purchases if new_total_purchases > 0 else 0
            
            print(f"   💰 Spend: ${new_total_spend:,.2f}")
            print(f"   🛒 Purchases: {new_total_purchases}")
            print(f"   💵 Revenue: ${new_total_revenue:,.2f}")
            print(f"   📈 ROAS: {new_roas:.2f}")
            print(f"   🎯 CPA: ${new_cpa:.2f}")
            
            # Compare with platform
            print(f"\n📊 Comparison with platform:")
            print(f"   Spend match: {'✅' if abs(new_total_spend - 30452) < 10 else '❌'}")
            print(f"   Purchases match: {'✅' if abs(new_total_purchases - 900) < 10 else '❌'}")
            print(f"   ROAS match: {'✅' if abs(new_roas - 7.8) < 0.1 else '❌'}")
            print(f"   CPA match: {'✅' if abs(new_cpa - 33.84) < 1 else '❌'}")
        
        print(f"\n🎉 July 2025 TikTok data updated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_july_2025_data()