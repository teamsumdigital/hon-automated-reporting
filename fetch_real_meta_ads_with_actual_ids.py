#!/usr/bin/env python3
"""
Fetch REAL Meta Ads data with actual ad IDs from Meta Ads API
This will allow verification of ads in Meta Ads Manager
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

class RealMetaAdsFetcher:
    """
    Fetches real Meta Ads data with actual ad IDs for verification
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
        
        logger.info("Initialized Real Meta Ads Fetcher")
    
    def calculate_proper_14_day_range(self) -> tuple[date, date]:
        """
        Calculate proper 14-day range ending yesterday, segmented by week
        """
        today = date.today()
        end_date = today - timedelta(days=1)  # Yesterday is the last full day
        start_date = end_date - timedelta(days=13)  # 14 days total
        
        # Adjust to start on Monday for proper weekly segmentation
        days_since_monday = start_date.weekday()
        adjusted_start = start_date - timedelta(days=days_since_monday)
        adjusted_end = adjusted_start + timedelta(days=13)  # 14 days from adjusted start
        
        logger.info(f"📅 Calculated 14-day range:")
        logger.info(f"   Original: {start_date} to {end_date}")
        logger.info(f"   Adjusted: {adjusted_start} to {adjusted_end} (Monday to Sunday alignment)")
        
        return adjusted_start, adjusted_end
    
    def fetch_real_meta_ads_data(self) -> List[Dict[str, Any]]:
        """
        Fetch real Meta Ads data with actual ad IDs
        """
        logger.info("🔄 Fetching REAL Meta Ads data from API...")
        
        try:
            start_date, end_date = self.calculate_proper_14_day_range()
            
            # Test connection first
            if not self.meta_service.test_connection():
                raise Exception("Meta Ads API connection failed")
            
            # Get real ad-level data with enhanced parsing
            real_ad_data = self.meta_service.get_ad_level_insights(start_date, end_date)
            
            if not real_ad_data:
                logger.warning("⚠️ No real ad data found for the 14-day period")
                return []
            
            logger.info(f"✅ Retrieved {len(real_ad_data)} REAL ad records from Meta API")
            
            # Log some sample real ad IDs for verification
            sample_ads = real_ad_data[:5]
            logger.info("📋 Sample REAL ad IDs for verification in Meta Ads Manager:")
            for i, ad in enumerate(sample_ads, 1):
                real_ad_id = ad.get('ad_id', 'Unknown')
                ad_name = ad.get('ad_name', 'Unknown')[:50]
                original_name = ad.get('original_ad_name', ad.get('ad_name', ''))[:50]
                logger.info(f"   {i}. Ad ID: {real_ad_id}")
                logger.info(f"      Original: {original_name}...")
                logger.info(f"      Cleaned:  {ad_name}...")
                logger.info(f"      Category: {ad.get('category', 'Unknown')}")
            
            return real_ad_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching real Meta Ads data: {e}")
            raise
    
    def clear_demo_data_and_insert_real(self, real_ad_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Clear demo data and insert real Meta Ads data with actual ad IDs
        """
        if not real_ad_data:
            logger.warning("⚠️ No real data to insert")
            return {"ads_inserted": 0}
        
        logger.info(f"📤 Preparing to replace demo data with {len(real_ad_data)} REAL ad records...")
        
        try:
            # Clear all demo/batch data first
            logger.info("🧹 Clearing ALL demo and batch data...")
            demo_patterns = ['demo_%', 'batch_%', 'week%_%']
            
            for pattern in demo_patterns:
                result = self.supabase.table('meta_ad_data').delete().like('ad_id', pattern).execute()
                logger.info(f"   Cleared ads matching pattern: {pattern}")
            
            # Prepare real data for insertion
            insert_data = []
            for ad in real_ad_data:
                # Convert date objects to ISO format strings for Supabase
                insert_record = {
                    'ad_id': ad['ad_id'],  # REAL Meta Ads ad ID
                    'in_platform_ad_name': ad.get('original_ad_name', ad['ad_name']),  # Original from Meta platform
                    'ad_name': ad['ad_name'],  # Cleaned version from parser
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
                }
                insert_data.append(insert_record)
            
            # Insert real data in batches
            batch_size = 50
            total_inserted = 0
            
            for i in range(0, len(insert_data), batch_size):
                batch = insert_data[i:i + batch_size]
                logger.info(f"📥 Inserting REAL data batch {i//batch_size + 1} ({len(batch)} records)...")
                
                result = self.supabase.table('meta_ad_data').insert(batch).execute()
                
                if result.data:
                    total_inserted += len(result.data)
                    logger.info(f"✅ Real data batch inserted successfully: {len(result.data)} records")
                else:
                    logger.error(f"❌ Real data batch insertion failed")
                    
            logger.info(f"🎉 Successfully inserted {total_inserted} REAL ad records with actual ad IDs")
            
            # Calculate summary statistics
            total_spend = sum(ad['amount_spent_usd'] for ad in real_ad_data)
            total_purchases = sum(ad['purchases'] for ad in real_ad_data)
            total_revenue = sum(ad['purchases_conversion_value'] for ad in real_ad_data)
            total_impressions = sum(ad['impressions'] for ad in real_ad_data)
            total_clicks = sum(ad['link_clicks'] for ad in real_ad_data)
            
            # Show real ad IDs for verification
            real_ad_ids = [ad['ad_id'] for ad in real_ad_data[:10]]
            
            return {
                "ads_inserted": total_inserted,
                "total_spend": round(total_spend, 2),
                "total_purchases": total_purchases,
                "total_revenue": round(total_revenue, 2),
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "average_roas": round(total_revenue / total_spend, 2) if total_spend > 0 else 0,
                "sample_real_ad_ids": real_ad_ids
            }
                
        except Exception as e:
            logger.error(f"❌ Error inserting real data: {e}")
            raise
    
    def fetch_and_replace_with_real_data(self) -> Dict[str, Any]:
        """
        Main method to fetch real Meta Ads data and replace demo data
        """
        logger.info("🚀 Starting REAL Meta Ads data fetch and replacement")
        
        try:
            # Fetch real Meta Ads data
            real_ad_data = self.fetch_real_meta_ads_data()
            
            if not real_ad_data:
                return {
                    "status": "success",
                    "message": "No real ad data found for the 14-day period",
                    "ads_inserted": 0
                }
            
            # Clear demo data and insert real data
            summary = self.clear_demo_data_and_insert_real(real_ad_data)
            
            logger.info("🎉 Real Meta Ads data replacement completed successfully!")
            
            return {
                "status": "success",
                "message": f"Successfully replaced demo data with {summary['ads_inserted']} REAL ad records",
                "real_data_source": "Meta Ads API",
                "verification_enabled": True,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"❌ Real data fetch and replacement failed: {e}")
            raise

def main():
    """
    Main function to fetch and insert real Meta Ads data
    """
    try:
        fetcher = RealMetaAdsFetcher()
        result = fetcher.fetch_and_replace_with_real_data()
        
        print("\n" + "=" * 80)
        print("🎯 REAL META ADS DATA REPLACEMENT RESULTS")
        print("=" * 80)
        
        print(f"✅ Status: {result['status']}")
        print(f"📊 Ads Inserted: {result['summary']['ads_inserted']}")
        print(f"💰 Total Spend: ${result['summary']['total_spend']:,.2f}")
        print(f"🛒 Total Purchases: {result['summary']['total_purchases']}")
        print(f"💵 Total Revenue: ${result['summary']['total_revenue']:,.2f}")
        print(f"📈 Average ROAS: {result['summary']['average_roas']}")
        
        print(f"\n🔍 REAL AD IDs FOR VERIFICATION IN META ADS MANAGER:")
        for i, ad_id in enumerate(result['summary']['sample_real_ad_ids'], 1):
            print(f"   {i}. {ad_id}")
        
        print(f"\n✅ You can now search for these REAL ad IDs in Meta Ads Manager!")
        print(f"🎯 No more fake demo data - these are actual ads from your account")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()