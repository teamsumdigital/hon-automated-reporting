#!/usr/bin/env python3
"""
Fetch real Meta Ads data for the last 14 days with weekly segmentation
and insert into Supabase using our enhanced ad name parsing logic
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

class MetaAds14DaysSyncer:
    """
    Syncs Meta Ads data for the last 14 days with enhanced parsing to Supabase
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
        
        logger.info("Initialized Meta Ads 14-day syncer with enhanced parsing")
    
    def calculate_date_range(self) -> tuple[date, date]:
        """
        Calculate the last 14 days date range (yesterday as end date)
        """
        today = date.today()
        end_date = today - timedelta(days=1)  # Yesterday is the last full day
        start_date = end_date - timedelta(days=13)  # 14 days total
        
        logger.info(f"📅 Date range: {start_date} to {end_date} (14 days)")
        return start_date, end_date
    
    def fetch_meta_ads_data(self) -> List[Dict[str, Any]]:
        """
        Fetch Meta Ads data for the last 14 days with weekly segmentation
        """
        logger.info("🔄 Fetching Meta Ads data for last 14 days...")
        
        try:
            # Get ad-level data with enhanced parsing
            ad_data = self.meta_service.get_last_14_days_ad_data()
            
            if not ad_data:
                logger.warning("⚠️ No ad data found for the last 14 days")
                return []
            
            logger.info(f"✅ Retrieved {len(ad_data)} ad records from Meta API")
            
            # Log parsing stats
            parsed_categories = {}
            parsed_products = {}
            parsed_formats = {}
            
            for ad in ad_data:
                category = ad.get('category', 'Unknown')
                product = ad.get('product', 'Unknown') 
                format_type = ad.get('format', 'Unknown')
                
                parsed_categories[category] = parsed_categories.get(category, 0) + 1
                parsed_products[product] = parsed_products.get(product, 0) + 1
                parsed_formats[format_type] = parsed_formats.get(format_type, 0) + 1
            
            logger.info("📊 Parsing Statistics:")
            logger.info(f"   Categories: {dict(list(parsed_categories.items())[:5])}")
            logger.info(f"   Products: {dict(list(parsed_products.items())[:5])}")
            logger.info(f"   Formats: {dict(list(parsed_formats.items())[:5])}")
            
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
    
    def prepare_insertion_data(self, ad_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare ad data for insertion into Supabase
        """
        logger.info("📝 Preparing data for insertion...")
        
        insert_data = []
        for ad in ad_data:
            # Convert date objects to ISO format strings for Supabase
            insert_record = {
                'ad_id': ad['ad_id'],
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
                'link_clicks': ad['link_clicks'],
                'week_number': ad['week_number']
            }
            insert_data.append(insert_record)
        
        logger.info(f"✅ Prepared {len(insert_data)} records for insertion")
        return insert_data
    
    def insert_data_to_supabase(self, insert_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Insert data into Supabase and return summary statistics
        """
        if not insert_data:
            logger.warning("⚠️ No data to insert")
            return {"ads_inserted": 0}
        
        logger.info(f"📤 Inserting {len(insert_data)} records into Supabase...")
        
        try:
            # Batch insert
            result = self.supabase.table('meta_ad_data').insert(insert_data).execute()
            
            if result.data:
                inserted_count = len(result.data)
                logger.info(f"✅ Successfully inserted {inserted_count} ad records")
                
                # Calculate summary statistics
                total_spend = sum(ad['amount_spent_usd'] for ad in insert_data)
                total_purchases = sum(ad['purchases'] for ad in insert_data)
                total_revenue = sum(ad['purchases_conversion_value'] for ad in insert_data)
                total_impressions = sum(ad['impressions'] for ad in insert_data)
                total_clicks = sum(ad['link_clicks'] for ad in insert_data)
                
                # Group by week for summary
                weekly_summary = {}
                for ad in insert_data:
                    week = ad['week_number']
                    if week not in weekly_summary:
                        weekly_summary[week] = {
                            'ads_count': 0,
                            'spend': 0,
                            'purchases': 0,
                            'revenue': 0,
                            'impressions': 0,
                            'clicks': 0
                        }
                    weekly_summary[week]['ads_count'] += 1
                    weekly_summary[week]['spend'] += ad['amount_spent_usd']
                    weekly_summary[week]['purchases'] += ad['purchases']
                    weekly_summary[week]['revenue'] += ad['purchases_conversion_value']
                    weekly_summary[week]['impressions'] += ad['impressions']
                    weekly_summary[week]['clicks'] += ad['link_clicks']
                
                return {
                    "ads_inserted": inserted_count,
                    "total_spend": round(total_spend, 2),
                    "total_purchases": total_purchases,
                    "total_revenue": round(total_revenue, 2),
                    "total_impressions": total_impressions,
                    "total_clicks": total_clicks,
                    "average_roas": round(total_revenue / total_spend, 2) if total_spend > 0 else 0,
                    "weekly_breakdown": weekly_summary
                }
            else:
                raise Exception("Failed to insert data - no data returned")
                
        except Exception as e:
            logger.error(f"❌ Error inserting data: {e}")
            raise
    
    def generate_parsing_report(self, ad_data: List[Dict[str, Any]]):
        """
        Generate a detailed report of parsing performance
        """
        if not ad_data:
            return
        
        logger.info("📊 ENHANCED PARSING PERFORMANCE REPORT")
        logger.info("=" * 60)
        
        # Field completion stats
        fields_to_check = ['category', 'product', 'color', 'content_type', 'handle', 'format', 'launch_date']
        field_stats = {}
        
        for field in fields_to_check:
            populated_count = sum(1 for ad in ad_data if ad.get(field) and str(ad[field]).strip())
            field_stats[field] = {
                'populated': populated_count,
                'total': len(ad_data),
                'percentage': (populated_count / len(ad_data)) * 100
            }
        
        for field, stats in field_stats.items():
            logger.info(f"🔸 {field.replace('_', ' ').title()}: {stats['populated']}/{stats['total']} ({stats['percentage']:.1f}%)")
        
        # Category breakdown
        categories = {}
        for ad in ad_data:
            cat = ad.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        logger.info(f"\n📂 Category Distribution:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(ad_data)) * 100
            logger.info(f"   {cat}: {count} ads ({percentage:.1f}%)")
        
        # Format breakdown  
        formats = {}
        for ad in ad_data:
            fmt = ad.get('format', 'Unknown')
            formats[fmt] = formats.get(fmt, 0) + 1
        
        logger.info(f"\n🎨 Format Distribution:")
        for fmt, count in sorted(formats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(ad_data)) * 100
            logger.info(f"   {fmt}: {count} ads ({percentage:.1f}%)")
        
        # Campaign optimization breakdown
        optimizations = {}
        for ad in ad_data:
            opt = ad.get('campaign_optimization', 'Unknown')
            optimizations[opt] = optimizations.get(opt, 0) + 1
        
        logger.info(f"\n⚙️ Campaign Optimization:")
        for opt, count in sorted(optimizations.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(ad_data)) * 100
            logger.info(f"   {opt}: {count} ads ({percentage:.1f}%)")
        
        logger.info("=" * 60)
    
    def sync_14_days_data(self) -> Dict[str, Any]:
        """
        Main method to sync 14 days of Meta Ads data with enhanced parsing
        """
        logger.info("🚀 Starting 14-day Meta Ads sync with enhanced parsing")
        
        try:
            # Calculate date range
            start_date, end_date = self.calculate_date_range()
            
            # Fetch Meta Ads data
            ad_data = self.fetch_meta_ads_data()
            
            if not ad_data:
                return {
                    "status": "success",
                    "message": "No ad data found for the last 14 days",
                    "ads_inserted": 0
                }
            
            # Generate parsing report
            self.generate_parsing_report(ad_data)
            
            # Clear existing data
            self.clear_existing_data(start_date, end_date)
            
            # Prepare data for insertion
            insert_data = self.prepare_insertion_data(ad_data)
            
            # Insert into Supabase
            summary = self.insert_data_to_supabase(insert_data)
            
            logger.info("🎉 14-day sync completed successfully!")
            
            return {
                "status": "success",
                "message": f"Successfully synced {summary['ads_inserted']} ad records for last 14 days",
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "parsing_enhanced": True,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"❌ 14-day sync failed: {e}")
            raise

def main():
    """
    Main function to run the 14-day sync
    """
    try:
        syncer = MetaAds14DaysSyncer()
        result = syncer.sync_14_days_data()
        
        print("\n" + "=" * 80)
        print("🎯 META ADS 14-DAY SYNC RESULTS")
        print("=" * 80)
        
        print(f"✅ Status: {result['status']}")
        print(f"📅 Date Range: {result['date_range']['start_date']} to {result['date_range']['end_date']}")
        print(f"📊 Ads Inserted: {result['summary']['ads_inserted']}")
        print(f"💰 Total Spend: ${result['summary']['total_spend']:,.2f}")
        print(f"🛒 Total Purchases: {result['summary']['total_purchases']}")
        print(f"💵 Total Revenue: ${result['summary']['total_revenue']:,.2f}")
        print(f"📈 Average ROAS: {result['summary']['average_roas']}")
        
        print(f"\n📋 Weekly Breakdown:")
        for week, data in result['summary']['weekly_breakdown'].items():
            roas = round(data['revenue'] / data['spend'], 2) if data['spend'] > 0 else 0
            print(f"   {week}: {data['ads_count']} ads, ${data['spend']:,.2f} spend, ROAS {roas}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()