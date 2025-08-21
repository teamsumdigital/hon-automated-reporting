#!/usr/bin/env python3
"""
Run the EXACT same process as the backend - one API call with weekly segmentation
This is the production approach that will be used ongoing
"""

import os
import sys
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client

# Load environment variables
load_dotenv()

# Add the backend app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

from services.meta_ad_level_service import MetaAdLevelService

class BackendSyncProcess:
    """
    Runs the exact same sync process as the backend will use ongoing
    """
    
    def __init__(self):
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        
        self.supabase = create_client(supabase_url, supabase_key)
        
        # Initialize Meta Ads service
        self.meta_service = MetaAdLevelService()
        
        logger.info("Initialized Backend Sync Process (Production Approach)")
    
    def run_production_sync(self) -> Dict[str, Any]:
        """
        Run the exact same sync process as the backend
        Single API call with weekly segmentation - this is the production approach
        """
        logger.info("🚀 Running PRODUCTION sync process (same as backend)")
        
        try:
            # Use the exact same method as backend: get_last_14_days_ad_data()
            logger.info("📊 Fetching 14-day data with weekly segments (single API call)...")
            
            real_ad_data = self.meta_service.get_last_14_days_ad_data()
            
            if not real_ad_data:
                logger.warning("⚠️ No ad data found")
                return {"status": "no_data", "ads_inserted": 0}
            
            logger.info(f"✅ Retrieved {len(real_ad_data)} ad records (production method)")
            
            # Filter out ads with $0 spend AND 0 purchases (but keep $0 spend with purchases > 0)
            filtered_ad_data = []
            zero_spend_zero_purchase_count = 0
            zero_spend_with_purchases_count = 0
            
            for ad in real_ad_data:
                spend = ad.get('amount_spent_usd', 0)
                purchases = ad.get('purchases', 0)
                
                if spend == 0 and purchases == 0:
                    # Skip ads with no spend and no purchases
                    zero_spend_zero_purchase_count += 1
                    continue
                elif spend == 0 and purchases > 0:
                    # Keep interesting edge case: $0 spend but got purchases
                    zero_spend_with_purchases_count += 1
                    filtered_ad_data.append(ad)
                else:
                    # Keep all other ads (normal cases with spend)
                    filtered_ad_data.append(ad)
            
            logger.info(f"🔍 Filtering results:")
            logger.info(f"   📊 Original ads: {len(real_ad_data)}")
            logger.info(f"   ❌ Filtered out (£0 spend + 0 purchases): {zero_spend_zero_purchase_count}")
            logger.info(f"   💡 Kept interesting cases ($0 spend + purchases): {zero_spend_with_purchases_count}")
            logger.info(f"   ✅ Final ads to insert: {len(filtered_ad_data)}")
            
            if not filtered_ad_data:
                logger.warning("⚠️ No ads remaining after filtering")
                return {"status": "no_data_after_filtering", "ads_inserted": 0}
            
            # Clear ALL existing data (handle empty database gracefully)
            logger.info("🧹 Clearing existing data if any...")
            try:
                result = self.supabase.table('meta_ad_data').delete().gt('id', 0).execute()
                logger.info("✅ Cleared existing data")
            except Exception as e:
                logger.info("ℹ️ Database already empty or clear operation not needed")
            
            # Prepare data for insertion using EXACT same format as backend
            insert_data = []
            for ad in filtered_ad_data:
                insert_record = {
                    'ad_id': ad['ad_id'],  # REAL Meta Ads ad ID
                    'in_platform_ad_name': ad.get('original_ad_name', ad['ad_name']),
                    'ad_name': ad['ad_name'],
                    'campaign_name': ad['campaign_name'],
                    'reporting_starts': ad['reporting_starts'].isoformat(),
                    'reporting_ends': ad['reporting_ends'].isoformat(),
                    'launch_date': ad['launch_date'].isoformat() if ad['launch_date'] else None,
                    'days_live': ad['days_live'],
                    'category': ad['category'],
                    'product': ad['product'],
                    'color': ad['color'],
                    'content_type': ad['content_type'],
                    'handle': ad['handle'],
                    'format': ad['format'],
                    'campaign_optimization': ad['campaign_optimization'],
                    'amount_spent_usd': ad['amount_spent_usd'],
                    'purchases': ad['purchases'],
                    'purchases_conversion_value': ad['purchases_conversion_value'],
                    'impressions': ad['impressions'],
                    'link_clicks': ad['link_clicks']
                    # Note: week_number column will be added by you in Supabase
                }
                insert_data.append(insert_record)
            
            # Insert in batches (same as backend)
            batch_size = 100
            total_inserted = 0
            
            logger.info(f"📥 Inserting {len(insert_data)} records in batches...")
            
            for i in range(0, len(insert_data), batch_size):
                batch = insert_data[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                logger.info(f"📥 Inserting batch {batch_num} ({len(batch)} records)...")
                
                result = self.supabase.table('meta_ad_data').insert(batch).execute()
                
                if result.data:
                    total_inserted += len(result.data)
                    logger.info(f"✅ Batch {batch_num} inserted: {len(result.data)} records")
            
            # Calculate summary (using filtered data)
            total_spend = sum(ad['amount_spent_usd'] for ad in filtered_ad_data)
            total_purchases = sum(ad['purchases'] for ad in filtered_ad_data)
            total_revenue = sum(ad['purchases_conversion_value'] for ad in filtered_ad_data)
            total_impressions = sum(ad['impressions'] for ad in filtered_ad_data)
            total_clicks = sum(ad['link_clicks'] for ad in filtered_ad_data)
            
            # Weekly breakdown
            week_stats = {}
            for ad in filtered_ad_data:
                week_key = f"{ad['reporting_starts']} to {ad['reporting_ends']}"
                if week_key not in week_stats:
                    week_stats[week_key] = 0
                week_stats[week_key] += 1
            
            sample_real_ad_ids = [ad['ad_id'] for ad in filtered_ad_data[:10]]
            
            return {
                "status": "success",
                "message": f"Production sync completed - {total_inserted} real ads inserted",
                "method": "Single API call with weekly segmentation (production approach)",
                "ads_inserted": total_inserted,
                "ads_filtered_out": zero_spend_zero_purchase_count,
                "zero_spend_with_purchases": zero_spend_with_purchases_count,
                "total_spend": round(total_spend, 2),
                "total_purchases": total_purchases,
                "total_revenue": round(total_revenue, 2),
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "average_roas": round(total_revenue / total_spend, 2) if total_spend > 0 else 0,
                "weekly_segments": len(week_stats),
                "week_breakdown": week_stats,
                "sample_real_ad_ids": sample_real_ad_ids
            }
            
        except Exception as e:
            logger.error(f"❌ Production sync failed: {e}")
            raise

def main():
    """
    Main function - runs production sync process
    """
    try:
        syncer = BackendSyncProcess()
        result = syncer.run_production_sync()
        
        print("\n" + "=" * 80)
        print("🎯 PRODUCTION SYNC RESULTS (Backend Method)")
        print("=" * 80)
        
        print(f"✅ Status: {result['status']}")
        print(f"⚡ Method: {result['method']}")
        print(f"📊 Ads Inserted: {result['ads_inserted']}")
        print(f"❌ Ads Filtered Out ($0 spend + 0 purchases): {result['ads_filtered_out']}")
        print(f"💡 Interesting Cases ($0 spend + purchases): {result['zero_spend_with_purchases']}")
        print(f"📈 Weekly Segments: {result['weekly_segments']}")
        print(f"💰 Total Spend: ${result['total_spend']:,.2f}")
        print(f"🛒 Total Purchases: {result['total_purchases']}")
        print(f"💵 Total Revenue: ${result['total_revenue']:,.2f}")
        print(f"📈 Average ROAS: {result['average_roas']}")
        
        print(f"\n📊 WEEKLY BREAKDOWN:")
        for week, count in result['week_breakdown'].items():
            print(f"   {week}: {count} ad records")
        
        print(f"\n🔍 SAMPLE REAL AD IDs FOR VERIFICATION:")
        for i, ad_id in enumerate(result['sample_real_ad_ids'], 1):
            print(f"   {i}. {ad_id}")
        
        print(f"\n✅ This is the EXACT process your backend will use ongoing!")
        print(f"🚀 Fast, efficient, weekly segmented - production ready")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Production sync failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()