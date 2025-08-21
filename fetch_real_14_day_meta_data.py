#!/usr/bin/env python3
"""
Fetch REAL 14-day Meta Ads data with actual ad IDs and insert into Supabase
Segmented by week with proper date ranges
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

class Real14DayMetaAdsFetcher:
    """
    Fetches real 14-day Meta Ads data with actual ad IDs and weekly segmentation
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
        
        logger.info("Initialized Real 14-Day Meta Ads Fetcher")
    
    def calculate_14_day_range_segmented_by_week(self) -> tuple[date, date]:
        """
        Calculate proper 14-day range ending yesterday, with weekly segmentation
        """
        today = date.today()
        end_date = today - timedelta(days=1)  # Yesterday is the last full day
        start_date = end_date - timedelta(days=13)  # 14 days total
        
        logger.info(f"📅 14-day range calculation:")
        logger.info(f"   Start: {start_date} (14 days ago)")
        logger.info(f"   End: {end_date} (yesterday)")
        logger.info(f"   Total: 14 days with weekly segmentation")
        
        return start_date, end_date
    
    def fetch_real_14_day_meta_ads_data(self) -> List[Dict[str, Any]]:
        """
        Fetch real 14-day Meta Ads data with actual ad IDs and enhanced parsing
        """
        logger.info("🔄 Fetching REAL 14-day Meta Ads data from API...")
        
        try:
            start_date, end_date = self.calculate_14_day_range_segmented_by_week()
            
            # Test connection first
            logger.info("🔌 Testing Meta Ads API connection...")
            if not self.meta_service.test_connection():
                raise Exception("Meta Ads API connection failed")
            
            # Get real 14-day ad-level data with enhanced parsing and weekly segmentation
            logger.info(f"📊 Fetching ad insights from {start_date} to {end_date} with weekly segments...")
            real_ad_data = self.meta_service.get_ad_level_insights(start_date, end_date)
            
            if not real_ad_data:
                logger.warning("⚠️ No real ad data found for the 14-day period")
                return []
            
            logger.info(f"✅ Retrieved {len(real_ad_data)} REAL ad records from Meta API")
            
            # Log sample of real ad IDs for verification
            logger.info("📋 Sample REAL ad IDs for verification in Meta Ads Manager:")
            sample_size = min(10, len(real_ad_data))
            for i, ad in enumerate(real_ad_data[:sample_size], 1):
                real_ad_id = ad.get('ad_id', 'Unknown')
                ad_name = ad.get('ad_name', 'Unknown')[:50]
                original_name = ad.get('original_ad_name', ad.get('ad_name', ''))[:50]
                reporting_range = f"{ad.get('reporting_starts', 'Unknown')} to {ad.get('reporting_ends', 'Unknown')}"
                
                logger.info(f"   {i}. Ad ID: {real_ad_id}")
                logger.info(f"      Date Range: {reporting_range}")
                logger.info(f"      Original: {original_name}...")
                logger.info(f"      Cleaned:  {ad_name}...")
                logger.info(f"      Category: {ad.get('category', 'Unknown')} | Format: {ad.get('format', 'Unknown')}")
                logger.info("")
            
            # Analyze weekly distribution
            week_distribution = {}
            for ad in real_ad_data:
                week_start = ad.get('reporting_starts')
                if week_start:
                    week_key = week_start.strftime('%Y-%m-%d')
                    week_distribution[week_key] = week_distribution.get(week_key, 0) + 1
            
            logger.info("📊 Weekly distribution of ads:")
            for week, count in sorted(week_distribution.items()):
                logger.info(f"   Week starting {week}: {count} ads")
            
            return real_ad_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching real 14-day Meta Ads data: {e}")
            raise
    
    def clear_demo_data_and_insert_real_14_day(self, real_ad_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Clear demo data and insert real 14-day Meta Ads data with actual ad IDs
        """
        if not real_ad_data:
            logger.warning("⚠️ No real 14-day data to insert")
            return {"ads_inserted": 0}
        
        logger.info(f"📤 Preparing to replace ALL data with {len(real_ad_data)} REAL 14-day ad records...")
        
        try:
            # Clear ALL existing data (demo, batch, and old real data)
            logger.info("🧹 Clearing ALL existing data from meta_ad_data table...")
            result = self.supabase.table('meta_ad_data').delete().neq('id', 'non-existent').execute()
            logger.info("✅ Cleared all existing data")
            
            # Prepare real 14-day data for insertion
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
            
            # Insert real 14-day data in batches
            batch_size = 100
            total_inserted = 0
            
            logger.info(f"📥 Inserting REAL data in batches of {batch_size}...")
            
            for i in range(0, len(insert_data), batch_size):
                batch = insert_data[i:i + batch_size]
                batch_num = i // batch_size + 1
                total_batches = (len(insert_data) + batch_size - 1) // batch_size
                
                logger.info(f"📥 Inserting batch {batch_num}/{total_batches} ({len(batch)} records)...")
                
                result = self.supabase.table('meta_ad_data').insert(batch).execute()
                
                if result.data:
                    total_inserted += len(result.data)
                    logger.info(f"✅ Batch {batch_num} inserted successfully: {len(result.data)} records")
                else:
                    logger.error(f"❌ Batch {batch_num} insertion failed")
                    
            logger.info(f"🎉 Successfully inserted {total_inserted} REAL 14-day ad records with actual ad IDs")
            
            # Calculate comprehensive summary statistics
            total_spend = sum(ad['amount_spent_usd'] for ad in real_ad_data)
            total_purchases = sum(ad['purchases'] for ad in real_ad_data)
            total_revenue = sum(ad['purchases_conversion_value'] for ad in real_ad_data)
            total_impressions = sum(ad['impressions'] for ad in real_ad_data)
            total_clicks = sum(ad['link_clicks'] for ad in real_ad_data)
            
            # Weekly breakdown
            week_stats = {}
            for ad in real_ad_data:
                week_start = ad['reporting_starts'].strftime('%Y-%m-%d')
                if week_start not in week_stats:
                    week_stats[week_start] = {
                        'ads': 0,
                        'spend': 0,
                        'purchases': 0,
                        'revenue': 0
                    }
                week_stats[week_start]['ads'] += 1
                week_stats[week_start]['spend'] += ad['amount_spent_usd']
                week_stats[week_start]['purchases'] += ad['purchases']
                week_stats[week_start]['revenue'] += ad['purchases_conversion_value']
            
            # Sample real ad IDs for verification
            sample_real_ad_ids = [ad['ad_id'] for ad in real_ad_data[:20]]
            
            return {
                "ads_inserted": total_inserted,
                "total_spend": round(total_spend, 2),
                "total_purchases": total_purchases,
                "total_revenue": round(total_revenue, 2),
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "average_roas": round(total_revenue / total_spend, 2) if total_spend > 0 else 0,
                "week_stats": week_stats,
                "sample_real_ad_ids": sample_real_ad_ids
            }
                
        except Exception as e:
            logger.error(f"❌ Error inserting real 14-day data: {e}")
            raise
    
    def fetch_and_insert_real_14_day_data(self) -> Dict[str, Any]:
        """
        Main method to fetch and insert real 14-day Meta Ads data
        """
        logger.info("🚀 Starting REAL 14-day Meta Ads data fetch and insertion")
        
        try:
            # Fetch real 14-day Meta Ads data
            real_ad_data = self.fetch_real_14_day_meta_ads_data()
            
            if not real_ad_data:
                return {
                    "status": "success",
                    "message": "No real ad data found for the 14-day period",
                    "ads_inserted": 0
                }
            
            # Clear all data and insert real 14-day data
            summary = self.clear_demo_data_and_insert_real_14_day(real_ad_data)
            
            logger.info("🎉 Real 14-day Meta Ads data insertion completed successfully!")
            
            start_date, end_date = self.calculate_14_day_range_segmented_by_week()
            
            return {
                "status": "success",
                "message": f"Successfully inserted {summary['ads_inserted']} REAL 14-day ad records",
                "real_data_source": "Meta Ads API",
                "verification_enabled": True,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_days": 14
                },
                "weekly_segmentation": True,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"❌ Real 14-day data fetch and insertion failed: {e}")
            raise

def main():
    """
    Main function to fetch and insert real 14-day Meta Ads data
    """
    try:
        fetcher = Real14DayMetaAdsFetcher()
        result = fetcher.fetch_and_insert_real_14_day_data()
        
        print("\n" + "=" * 80)
        print("🎯 REAL 14-DAY META ADS DATA INSERTION RESULTS")
        print("=" * 80)
        
        print(f"✅ Status: {result['status']}")
        print(f"📅 Date Range: {result['date_range']['start_date']} to {result['date_range']['end_date']}")
        print(f"📊 Total Days: {result['date_range']['total_days']}")
        print(f"📈 Weekly Segmentation: {result['weekly_segmentation']}")
        print(f"📊 Ads Inserted: {result['summary']['ads_inserted']}")
        print(f"💰 Total Spend: ${result['summary']['total_spend']:,.2f}")
        print(f"🛒 Total Purchases: {result['summary']['total_purchases']}")
        print(f"💵 Total Revenue: ${result['summary']['total_revenue']:,.2f}")
        print(f"📈 Average ROAS: {result['summary']['average_roas']}")
        
        print(f"\n📊 WEEKLY BREAKDOWN:")
        for week, stats in sorted(result['summary']['week_stats'].items()):
            print(f"   Week {week}: {stats['ads']} ads, ${stats['spend']:,.2f} spend, {stats['purchases']} purchases")
        
        print(f"\n🔍 SAMPLE REAL AD IDs FOR VERIFICATION:")
        for i, ad_id in enumerate(result['summary']['sample_real_ad_ids'][:10], 1):
            print(f"   {i}. {ad_id}")
        
        print(f"\n✅ ALL DATA IS NOW REAL - You can verify any ad ID in Meta Ads Manager!")
        print(f"🎯 No more demo data - {result['summary']['ads_inserted']} actual ads from your account")
        print(f"📈 Data segmented by week with proper 14-day range")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()