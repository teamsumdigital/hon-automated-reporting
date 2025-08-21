#!/usr/bin/env python3
"""
Fetch REAL 14-day Meta Ads data with rate limiting and retry logic
Uses smaller batches and delays to avoid API limits
"""

import os
import sys
import time
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

class RateLimited14DayMetaAdsFetcher:
    """
    Fetches real 14-day Meta Ads data with rate limiting and smaller batches
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
        
        logger.info("Initialized Rate-Limited 14-Day Meta Ads Fetcher")
    
    def calculate_daily_ranges(self) -> List[tuple[date, date]]:
        """
        Calculate 14 daily ranges to fetch data in smaller chunks
        """
        today = date.today()
        end_date = today - timedelta(days=1)  # Yesterday
        
        daily_ranges = []
        for days_ago in range(14):
            current_date = end_date - timedelta(days=days_ago)
            daily_ranges.append((current_date, current_date))
        
        daily_ranges.reverse()  # Oldest to newest
        
        logger.info(f"📅 Created {len(daily_ranges)} daily ranges from {daily_ranges[0][0]} to {daily_ranges[-1][1]}")
        return daily_ranges
    
    def fetch_daily_data_with_retry(self, start_date: date, end_date: date, max_retries: int = 3) -> List[Dict[str, Any]]:
        """
        Fetch data for a single day with retry logic
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"📊 Fetching data for {start_date} (attempt {attempt + 1}/{max_retries})")
                
                # Add delay between attempts
                if attempt > 0:
                    delay = 30 * attempt  # 30, 60 seconds
                    logger.info(f"⏱️ Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                
                # Fetch data for this single day
                daily_data = self.meta_service.get_ad_level_insights(start_date, end_date)
                
                if daily_data:
                    logger.info(f"✅ Retrieved {len(daily_data)} ads for {start_date}")
                else:
                    logger.info(f"ℹ️ No ads found for {start_date}")
                
                # Add delay after successful call to respect rate limits
                time.sleep(2)  # 2 second delay between calls
                
                return daily_data or []
                
            except Exception as e:
                if "Application request limit reached" in str(e):
                    wait_time = 60 * (attempt + 1)  # 60, 120, 180 seconds
                    logger.warning(f"⚠️ Rate limit hit for {start_date}. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Error fetching data for {start_date}: {e}")
                    if attempt == max_retries - 1:
                        raise
        
        return []
    
    def fetch_14_day_data_in_batches(self) -> List[Dict[str, Any]]:
        """
        Fetch 14 days of data in daily batches to avoid rate limits
        """
        logger.info("🔄 Fetching 14-day Meta Ads data in daily batches...")
        
        daily_ranges = self.calculate_daily_ranges()
        all_ad_data = []
        
        for i, (start_date, end_date) in enumerate(daily_ranges, 1):
            logger.info(f"📅 Processing day {i}/14: {start_date}")
            
            try:
                daily_data = self.fetch_daily_data_with_retry(start_date, end_date)
                all_ad_data.extend(daily_data)
                
                logger.info(f"✅ Day {i} complete. Total ads so far: {len(all_ad_data)}")
                
            except Exception as e:
                logger.error(f"❌ Failed to fetch data for {start_date}: {e}")
                logger.info("⏭️ Continuing with next day...")
                continue
        
        logger.info(f"🎉 Completed 14-day fetch. Total ads retrieved: {len(all_ad_data)}")
        
        # Log sample of real ad IDs for verification
        if all_ad_data:
            logger.info("📋 Sample REAL ad IDs for verification:")
            sample_size = min(5, len(all_ad_data))
            for i, ad in enumerate(all_ad_data[:sample_size], 1):
                real_ad_id = ad.get('ad_id', 'Unknown')
                ad_name = ad.get('ad_name', 'Unknown')[:50]
                reporting_range = f"{ad.get('reporting_starts', 'Unknown')} to {ad.get('reporting_ends', 'Unknown')}"
                
                logger.info(f"   {i}. Ad ID: {real_ad_id}")
                logger.info(f"      Date: {reporting_range}")
                logger.info(f"      Name: {ad_name}...")
        
        return all_ad_data
    
    def insert_real_14_day_data(self, real_ad_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Insert real 14-day data into Supabase
        """
        if not real_ad_data:
            logger.warning("⚠️ No data to insert")
            return {"ads_inserted": 0}
        
        logger.info(f"📤 Preparing to insert {len(real_ad_data)} REAL ad records...")
        
        try:
            # Clear ALL existing data
            logger.info("🧹 Clearing all existing data...")
            result = self.supabase.table('meta_ad_data').delete().neq('id', 'non-existent').execute()
            logger.info("✅ Cleared all existing data")
            
            # Prepare data for insertion
            insert_data = []
            for ad in real_ad_data:
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
                }
                insert_data.append(insert_record)
            
            # Insert in batches
            batch_size = 100
            total_inserted = 0
            
            for i in range(0, len(insert_data), batch_size):
                batch = insert_data[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                logger.info(f"📥 Inserting batch {batch_num} ({len(batch)} records)...")
                
                result = self.supabase.table('meta_ad_data').insert(batch).execute()
                
                if result.data:
                    total_inserted += len(result.data)
                    logger.info(f"✅ Batch {batch_num} inserted: {len(result.data)} records")
            
            # Calculate summary
            total_spend = sum(ad['amount_spent_usd'] for ad in real_ad_data)
            total_purchases = sum(ad['purchases'] for ad in real_ad_data)
            total_revenue = sum(ad['purchases_conversion_value'] for ad in real_ad_data)
            
            sample_real_ad_ids = [ad['ad_id'] for ad in real_ad_data[:10]]
            
            return {
                "ads_inserted": total_inserted,
                "total_spend": round(total_spend, 2),
                "total_purchases": total_purchases,
                "total_revenue": round(total_revenue, 2),
                "average_roas": round(total_revenue / total_spend, 2) if total_spend > 0 else 0,
                "sample_real_ad_ids": sample_real_ad_ids
            }
                
        except Exception as e:
            logger.error(f"❌ Error inserting data: {e}")
            raise
    
    def run_rate_limited_14_day_fetch(self) -> Dict[str, Any]:
        """
        Main method with rate limiting
        """
        logger.info("🚀 Starting rate-limited 14-day Meta Ads fetch")
        
        try:
            # Fetch data in daily batches
            real_ad_data = self.fetch_14_day_data_in_batches()
            
            if not real_ad_data:
                return {
                    "status": "success",
                    "message": "No ad data found for the 14-day period",
                    "ads_inserted": 0
                }
            
            # Insert data
            summary = self.insert_real_14_day_data(real_ad_data)
            
            return {
                "status": "success",
                "message": f"Successfully inserted {summary['ads_inserted']} REAL ads with rate limiting",
                "real_data_source": "Meta Ads API (rate-limited)",
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"❌ Rate-limited fetch failed: {e}")
            raise

def main():
    """
    Main function with rate limiting
    """
    try:
        fetcher = RateLimited14DayMetaAdsFetcher()
        result = fetcher.run_rate_limited_14_day_fetch()
        
        print("\n" + "=" * 80)
        print("🎯 RATE-LIMITED 14-DAY META ADS RESULTS")
        print("=" * 80)
        
        print(f"✅ Status: {result['status']}")
        print(f"📊 Ads Inserted: {result['summary']['ads_inserted']}")
        print(f"💰 Total Spend: ${result['summary']['total_spend']:,.2f}")
        print(f"🛒 Total Purchases: {result['summary']['total_purchases']}")
        print(f"💵 Total Revenue: ${result['summary']['total_revenue']:,.2f}")
        print(f"📈 Average ROAS: {result['summary']['average_roas']}")
        
        print(f"\n🔍 REAL AD IDs FOR VERIFICATION:")
        for i, ad_id in enumerate(result['summary']['sample_real_ad_ids'], 1):
            print(f"   {i}. {ad_id}")
        
        print(f"\n✅ All data is REAL - fetched with rate limiting!")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()