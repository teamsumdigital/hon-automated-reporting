#!/usr/bin/env python3
"""
Fetch remaining TikTok ad data from July 22, 2024 through August 22, 2024
"""

import os
import json
import requests
from datetime import datetime, date, timedelta
from loguru import logger
from dotenv import load_dotenv
from supabase import create_client
from typing import List, Dict, Any
from app.services.categorization import CategorizationService

# Load environment variables
load_dotenv()

class TikTokRemainingDataFetcher:
    def __init__(self):
        # TikTok API credentials
        self.access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        self.advertiser_id = os.getenv("TIKTOK_ADVERTISER_ID")
        
        # Database connection
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.supabase = create_client(supabase_url, supabase_key)
        
        # TikTok API base URL
        self.base_url = "https://business-api.tiktok.com/open_api/v1.3"
        
        # Standard headers for TikTok API
        self.headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        
        # Initialize categorization service
        self.categorization_service = CategorizationService()
        
        logger.info("TikTok Remaining Data Fetcher initialized")
    
    def check_existing_data(self):
        """Check what data we already have"""
        result = self.supabase.table("tiktok_ad_data")\
            .select("reporting_starts, reporting_ends")\
            .order("reporting_ends", desc=True)\
            .limit(1)\
            .execute()
        
        if result.data:
            latest_date = result.data[0]['reporting_ends']
            logger.info(f"Latest data in database ends on: {latest_date}")
            return datetime.strptime(latest_date, '%Y-%m-%d').date()
        else:
            logger.warning("No existing data found")
            return None
    
    def generate_date_ranges(self, start_date: date, end_date: date) -> List[tuple]:
        """Generate weekly date ranges"""
        date_ranges = []
        current_start = start_date
        
        while current_start <= end_date:
            period_end = min(current_start + timedelta(days=6), end_date)
            date_ranges.append((current_start, period_end))
            current_start = period_end + timedelta(days=1)
        
        return date_ranges
    
    def fetch_ads_for_period(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Fetch ad data for a specific period with names"""
        try:
            # Get performance data
            endpoint = f"{self.base_url}/report/integrated/get/"
            params = {
                "advertiser_id": self.advertiser_id,
                "report_type": "BASIC",
                "data_level": "AUCTION_AD",
                "dimensions": json.dumps(["ad_id"]),
                "metrics": json.dumps([
                    "spend", "impressions", "clicks", "ctr", "cpc", "cpm",
                    "cost_per_conversion", "conversion_rate", 
                    "complete_payment_roas", "complete_payment", "purchase"
                ]),
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "page": 1,
                "page_size": 1000
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"API HTTP error: {response.status_code}")
                return []
            
            data = response.json()
            if data.get("code") != 0:
                logger.error(f"API error: {data.get('message')}")
                return []
            
            performance_data = data.get("data", {}).get("list", [])
            
            if not performance_data:
                logger.info(f"No ads found for period {start_date} to {end_date}")
                return []
            
            logger.info(f"Found {len(performance_data)} ads with data for {start_date} to {end_date}")
            
            # Get all ads with details (including names) - get current active ads
            all_ads_endpoint = f"{self.base_url}/ad/get/"
            all_ads_params = {
                "advertiser_id": self.advertiser_id,
                "fields": json.dumps([
                    "ad_id", "ad_name", "campaign_id", "campaign_name", "operation_status"
                ]),
                "page": 1,
                "page_size": 1000
            }
            
            ads_response = requests.get(all_ads_endpoint, headers=self.headers, params=all_ads_params)
            
            if ads_response.status_code != 200 or ads_response.json().get("code") != 0:
                logger.error("Failed to fetch ad details")
                return []
            
            # Create lookup for ad details
            ad_details = {}
            for ad in ads_response.json().get("data", {}).get("list", []):
                ad_details[str(ad["ad_id"])] = {
                    "ad_name": ad.get("ad_name", f"Ad {ad['ad_id']}"),
                    "campaign_id": str(ad.get("campaign_id", "")),
                    "campaign_name": ad.get("campaign_name", "Unknown Campaign"),
                    "status": ad.get("operation_status", "UNKNOWN")
                }
            
            logger.info(f"Fetched details for {len(ad_details)} ads")
            
            # Combine performance data with ad details
            ads_list = []
            ads_with_spend = 0
            
            for item in performance_data:
                try:
                    ad_id = str(item["dimensions"]["ad_id"])
                    metrics = item["metrics"]
                    
                    # Convert metrics
                    spend = float(metrics.get("spend", 0))
                    
                    # Only include ads with spend > 0
                    if spend <= 0:
                        continue
                    
                    ads_with_spend += 1
                    
                    # Get ad details
                    details = ad_details.get(ad_id, {
                        "ad_name": f"Ad {ad_id}",
                        "campaign_id": "",
                        "campaign_name": "Unknown Campaign",
                        "status": "UNKNOWN"
                    })
                    
                    purchases = int(metrics.get("complete_payment", 0))
                    impressions = int(metrics.get("impressions", 0))
                    clicks = int(metrics.get("clicks", 0))
                    roas = float(metrics.get("complete_payment_roas", 0))
                    
                    # Calculate revenue from ROAS and spend
                    revenue = spend * roas if spend > 0 and roas > 0 else 0
                    
                    # Calculate derived metrics
                    cpa = spend / purchases if purchases > 0 else 0
                    cpc = spend / clicks if clicks > 0 else 0
                    cpm = float(metrics.get("cpm", 0))
                    
                    # Categorize based on ad name
                    category = self.categorization_service.categorize_ad(
                        details["ad_name"], ad_id, "tiktok"
                    )
                    
                    ad_data = {
                        "ad_id": ad_id,
                        "ad_name": details["ad_name"],
                        "campaign_id": details["campaign_id"],
                        "campaign_name": details["campaign_name"],
                        "category": category,
                        "reporting_starts": start_date.strftime('%Y-%m-%d'),
                        "reporting_ends": end_date.strftime('%Y-%m-%d'),
                        "amount_spent_usd": round(spend, 2),
                        "website_purchases": purchases,
                        "purchases_conversion_value": round(revenue, 2),
                        "impressions": impressions,
                        "link_clicks": clicks,
                        "cpa": round(cpa, 2),
                        "roas": round(roas, 4),
                        "cpc": round(cpc, 4),
                        "cpm": round(cpm, 2),
                        "thumbnail_url": None,
                        "status": details["status"]
                    }
                    
                    ads_list.append(ad_data)
                    
                except Exception as e:
                    logger.error(f"Failed to process ad: {e}")
                    continue
            
            logger.info(f"Processed {len(ads_list)} ads with spend > 0 for period {start_date} to {end_date}")
            return ads_list
            
        except Exception as e:
            logger.error(f"Failed to fetch ads: {e}")
            return []
    
    def sync_to_database(self, ads_data: List[Dict[str, Any]]) -> int:
        """Sync ads to database"""
        if not ads_data:
            return 0
        
        try:
            # Upsert in batches
            batch_size = 500
            total_synced = 0
            
            for i in range(0, len(ads_data), batch_size):
                batch = ads_data[i:i+batch_size]
                result = self.supabase.table("tiktok_ad_data").upsert(
                    batch,
                    on_conflict="ad_id,reporting_starts,reporting_ends"
                ).execute()
                
                if result.data:
                    total_synced += len(result.data)
                    logger.info(f"Synced batch of {len(result.data)} records")
            
            return total_synced
            
        except Exception as e:
            logger.error(f"Error syncing to database: {e}")
            return 0
    
    def run(self):
        """Main process to fetch remaining data"""
        # Check existing data
        latest_date = self.check_existing_data()
        
        if latest_date:
            # Start from the day after our latest data
            start_date = latest_date + timedelta(days=1)
        else:
            # If no data, start from July 22, 2024
            start_date = date(2024, 7, 22)
        
        # End date is August 22, 2024
        end_date = date(2024, 8, 22)
        
        if start_date > end_date:
            logger.info("Already have data through August 22, 2024")
            return
        
        # Generate date ranges
        date_ranges = self.generate_date_ranges(start_date, end_date)
        
        logger.info(f"Fetching data from {start_date} to {end_date}")
        logger.info(f"Processing {len(date_ranges)} weekly periods")
        
        total_synced = 0
        
        for i, (period_start, period_end) in enumerate(date_ranges, 1):
            logger.info(f"\nProcessing period {i}/{len(date_ranges)}: {period_start} to {period_end}")
            
            # Fetch ads for this period
            ads_data = self.fetch_ads_for_period(period_start, period_end)
            
            if ads_data:
                # Sync to database
                synced = self.sync_to_database(ads_data)
                total_synced += synced
                logger.info(f"Synced {synced} ads for this period")
            else:
                logger.info("No ads found for this period")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Data fetch complete!")
        logger.info(f"Total periods processed: {len(date_ranges)}")
        logger.info(f"Total ads synced: {total_synced}")
        logger.info(f"Data now covers through: {end_date}")
        logger.info('='*60)
        
        # Show final statistics
        self.show_final_stats()
    
    def show_final_stats(self):
        """Show final database statistics"""
        # Total records
        count_result = self.supabase.table("tiktok_ad_data").select("*", count="exact").execute()
        total_count = count_result.count
        
        # Date range
        date_result = self.supabase.table("tiktok_ad_data")\
            .select("reporting_starts, reporting_ends")\
            .order("reporting_starts")\
            .limit(1)\
            .execute()
        
        earliest = date_result.data[0] if date_result.data else None
        
        date_result = self.supabase.table("tiktok_ad_data")\
            .select("reporting_starts, reporting_ends")\
            .order("reporting_ends", desc=True)\
            .limit(1)\
            .execute()
        
        latest = date_result.data[0] if date_result.data else None
        
        # Spend summary
        spend_result = self.supabase.table("tiktok_ad_data").select("amount_spent_usd").execute()
        total_spend = sum(d['amount_spent_usd'] for d in spend_result.data) if spend_result.data else 0
        
        print(f"\n{'='*60}")
        print("FINAL DATABASE STATISTICS")
        print(f"{'='*60}")
        print(f"Total ad records: {total_count:,}")
        if earliest and latest:
            print(f"Date range: {earliest['reporting_starts']} to {latest['reporting_ends']}")
        print(f"Total spend: ${total_spend:,.2f}")
        print(f"{'='*60}")

if __name__ == "__main__":
    logger.info("Starting TikTok remaining data fetch")
    logger.info("Target: Complete data through August 22, 2024")
    
    try:
        fetcher = TikTokRemainingDataFetcher()
        fetcher.run()
    except KeyboardInterrupt:
        logger.info("\nFetch interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("\nFetch script completed")