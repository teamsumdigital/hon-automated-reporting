#!/usr/bin/env python3
"""
Fetch Meta Ads data for the last 7 days and insert into Supabase
Shorter timeframe to avoid API timeout issues
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

class MetaAds7DaysSyncer:
    """
    Syncs Meta Ads data for the last 7 days with enhanced parsing to Supabase
    """
    
    def __init__(self):
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        
        self.supabase = create_client(supabase_url, supabase_key)
        
        # Initialize Meta Ads service with enhanced parser
        self.meta_service = MetaAdLevelService()
        
        logger.info("Initialized Meta Ads 7-day syncer with enhanced parsing")
    
    def calculate_date_range(self) -> tuple[date, date]:
        """
        Calculate the last 7 days date range (yesterday as end date)
        """
        today = date.today()
        end_date = today - timedelta(days=1)  # Yesterday is the last full day
        start_date = end_date - timedelta(days=6)  # 7 days total
        
        logger.info(f"📅 Date range: {start_date} to {end_date} (7 days)")
        return start_date, end_date
    
    def fetch_meta_ads_data(self) -> List[Dict[str, Any]]:
        """
        Fetch Meta Ads data for the last 7 days
        """
        logger.info("🔄 Fetching Meta Ads data for last 7 days...")
        
        try:
            start_date, end_date = self.calculate_date_range()
            
            # Get ad-level data with enhanced parsing
            ad_data = self.meta_service.get_ad_level_insights(start_date, end_date)
            
            if not ad_data:
                logger.warning("⚠️ No ad data found for the last 7 days")
                return []
            
            logger.info(f"✅ Retrieved {len(ad_data)} ad records from Meta API")
            
            return ad_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching Meta Ads data: {e}")
            raise
    
    def clear_existing_data(self, start_date: date, end_date: date):
        """
        Clear existing data from the database for the date range
        """
        logger.info(f"🧹 Clearing existing data from {start_date} to {end_date}")
        
        try:
            result = (self.supabase.table('meta_ad_data')
                     .delete()
                     .gte('reporting_starts', start_date.isoformat())
                     .lte('reporting_ends', end_date.isoformat())
                     .execute())
            
            logger.info(f"✅ Cleared existing data for date range")
            
        except Exception as e:
            logger.error(f"❌ Error clearing existing data: {e}")
            raise
    
    def insert_data_to_supabase(self, ad_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Insert data into Supabase in smaller batches
        """
        if not ad_data:
            logger.warning("⚠️ No data to insert")
            return {"ads_inserted": 0}
        
        logger.info(f"📤 Preparing to insert {len(ad_data)} records into Supabase...")
        
        # Prepare data for insertion
        insert_data = []
        for ad in ad_data:
            # Convert date objects to ISO format strings for Supabase
            insert_record = {
                'ad_id': ad['ad_id'],
                'in_platform_ad_name': ad.get('original_ad_name', ad['ad_name']),  # Original from Meta platform
                'ad_name': ad['ad_name'],  # Cleaned version from our parser
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
                'link_clicks': ad['link_clicks'],
                'week_number': ad.get('week_number', f"Week {ad['reporting_starts'].strftime('%m/%d')}-{ad['reporting_ends'].strftime('%m/%d')}")
            }
            insert_data.append(insert_record)
        
        try:
            # Insert in smaller batches to avoid timeouts
            batch_size = 100
            total_inserted = 0
            
            for i in range(0, len(insert_data), batch_size):
                batch = insert_data[i:i + batch_size]
                logger.info(f"📥 Inserting batch {i//batch_size + 1} ({len(batch)} records)...")
                
                result = self.supabase.table('meta_ad_data').insert(batch).execute()
                
                if result.data:
                    total_inserted += len(result.data)
                    logger.info(f"✅ Batch inserted successfully: {len(result.data)} records")
                else:
                    logger.error(f"❌ Batch insertion failed")
                    
            logger.info(f"🎉 Successfully inserted {total_inserted} total ad records")
            
            # Calculate summary statistics
            total_spend = sum(ad['amount_spent_usd'] for ad in ad_data)
            total_purchases = sum(ad['purchases'] for ad in ad_data)
            total_revenue = sum(ad['purchases_conversion_value'] for ad in ad_data)
            total_impressions = sum(ad['impressions'] for ad in ad_data)
            total_clicks = sum(ad['link_clicks'] for ad in ad_data)
            
            return {
                "ads_inserted": total_inserted,
                "total_spend": round(total_spend, 2),
                "total_purchases": total_purchases,
                "total_revenue": round(total_revenue, 2),
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "average_roas": round(total_revenue / total_spend, 2) if total_spend > 0 else 0
            }
                
        except Exception as e:
            logger.error(f"❌ Error inserting data: {e}")
            raise
    
    def sync_7_days_data(self) -> Dict[str, Any]:
        """
        Main method to sync 7 days of Meta Ads data with enhanced parsing
        """
        logger.info("🚀 Starting 7-day Meta Ads sync with enhanced parsing")
        
        try:
            # Calculate date range
            start_date, end_date = self.calculate_date_range()
            
            # Fetch Meta Ads data
            ad_data = self.fetch_meta_ads_data()
            
            if not ad_data:
                return {
                    "status": "success",
                    "message": "No ad data found for the last 7 days",
                    "ads_inserted": 0
                }
            
            # Clear existing data
            self.clear_existing_data(start_date, end_date)
            
            # Insert into Supabase
            summary = self.insert_data_to_supabase(ad_data)
            
            logger.info("🎉 7-day sync completed successfully!")
            
            return {
                "status": "success",
                "message": f"Successfully synced {summary['ads_inserted']} ad records for last 7 days",
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "parsing_enhanced": True,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"❌ 7-day sync failed: {e}")
            raise

def main():
    """
    Main function to run the 7-day sync
    """
    try:
        syncer = MetaAds7DaysSyncer()
        result = syncer.sync_7_days_data()
        
        print("\n" + "=" * 80)
        print("🎯 META ADS 7-DAY SYNC RESULTS")
        print("=" * 80)
        
        print(f"✅ Status: {result['status']}")
        print(f"📅 Date Range: {result['date_range']['start_date']} to {result['date_range']['end_date']}")
        print(f"📊 Ads Inserted: {result['summary']['ads_inserted']}")
        print(f"💰 Total Spend: ${result['summary']['total_spend']:,.2f}")
        print(f"🛒 Total Purchases: {result['summary']['total_purchases']}")
        print(f"💵 Total Revenue: ${result['summary']['total_revenue']:,.2f}")
        print(f"📈 Average ROAS: {result['summary']['average_roas']}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()