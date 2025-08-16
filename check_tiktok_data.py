#!/usr/bin/env python3
"""
Check what TikTok data has been backfilled successfully
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def check_tiktok_data():
    """Check TikTok data in Supabase"""
    print("📊 Checking TikTok Campaign Data in Supabase")
    print("=" * 50)
    
    try:
        # Initialize Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        supabase = create_client(supabase_url, supabase_key)
        
        # Get total count
        result = supabase.table('tiktok_campaign_data').select('*', count='exact').execute()
        total_count = result.count if hasattr(result, 'count') else len(result.data)
        
        print(f"📈 Total TikTok campaign records: {total_count}")
        
        if total_count == 0:
            print("⚠️ No TikTok data found in database")
            return
        
        # Get records with spend > 0
        spend_result = supabase.table('tiktok_campaign_data').select('*').gt('amount_spent_usd', 0).execute()
        spend_campaigns = len(spend_result.data) if spend_result.data else 0
        
        print(f"💰 Campaigns with spend > 0: {spend_campaigns}")
        
        # Get records with ROAS > 0
        roas_result = supabase.table('tiktok_campaign_data').select('*').gt('roas', 0).execute()
        roas_campaigns = len(roas_result.data) if roas_result.data else 0
        
        print(f"📈 Campaigns with ROAS > 0: {roas_campaigns}")
        
        # Get date range
        date_result = supabase.table('tiktok_campaign_data').select('reporting_starts', 'reporting_ends').order('reporting_starts', desc=False).execute()
        
        if date_result.data:
            earliest = date_result.data[0]['reporting_starts']
            latest = date_result.data[-1]['reporting_ends']
            print(f"📅 Date range: {earliest} to {latest}")
        
        # Show sample of recent records with spend
        print("\n📋 Sample records with spend > 0:")
        print("-" * 80)
        
        sample_result = supabase.table('tiktok_campaign_data').select(
            'campaign_name', 'amount_spent_usd', 'roas', 'website_purchases', 'reporting_starts'
        ).gt('amount_spent_usd', 0).order('reporting_starts', desc=True).limit(5).execute()
        
        if sample_result.data:
            for record in sample_result.data:
                print(f"🎯 {record['campaign_name'][:40]:40} | ${record['amount_spent_usd']:8.2f} | ROAS: {record['roas']:6.2f} | Purchases: {record['website_purchases']:3d} | {record['reporting_starts']}")
        
        # Check for zero ROAS with spend
        zero_roas_result = supabase.table('tiktok_campaign_data').select('*').eq('roas', 0).gt('amount_spent_usd', 0).execute()
        zero_roas_count = len(zero_roas_result.data) if zero_roas_result.data else 0
        
        print(f"\n⚠️ Records with zero ROAS but spend > 0: {zero_roas_count}")
        
        # Check totals
        if spend_result.data:
            total_spend = sum(float(record['amount_spent_usd']) for record in spend_result.data)
            total_purchases = sum(int(record['website_purchases']) for record in spend_result.data)
            total_revenue = sum(float(record['purchases_conversion_value']) for record in spend_result.data)
            
            overall_roas = total_revenue / total_spend if total_spend > 0 else 0
            
            print(f"\n📊 TOTALS SUMMARY:")
            print(f"   💰 Total Spend: ${total_spend:,.2f}")
            print(f"   🛒 Total Purchases: {total_purchases:,}")
            print(f"   💵 Total Revenue: ${total_revenue:,.2f}")
            print(f"   📈 Overall ROAS: {overall_roas:.2f}")
        
        # Check if CPM column exists
        try:
            cpm_result = supabase.table('tiktok_campaign_data').select('cpm').limit(1).execute()
            print(f"\n✅ CPM column exists and accessible")
        except Exception as e:
            if 'column "cpm" does not exist' in str(e).lower():
                print(f"\n⚠️ CPM column does not exist yet - run MANUAL_SQL_COMMANDS.md")
            else:
                print(f"\n❌ Error checking CPM column: {e}")
        
    except Exception as e:
        print(f"❌ Error checking TikTok data: {e}")

if __name__ == "__main__":
    check_tiktok_data()