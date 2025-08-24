#!/usr/bin/env python3
"""
Sync TikTok Ad-Level Historical Data with Batch Processing
Fetches TikTok ad-level data from January 2024 to August 22, 2024
and populates the tiktok_ad_data table with optimized batch requests
"""

import os
import sys
import json
import requests
from datetime import date, timedelta
from loguru import logger
from dotenv import load_dotenv
from typing import List, Dict, Any

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.categorization import CategorizationService
from supabase import create_client

# Load environment variables
load_dotenv()

class BatchTikTokAdSync:
    def __init__(self):
        # TikTok API credentials
        self.app_id = os.getenv("TIKTOK_APP_ID")
        self.app_secret = os.getenv("TIKTOK_APP_SECRET")
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
        
        logger.info("Batch TikTok Ad Sync initialized")
    
    def fetch_ads_batch(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Fetch ad performance data and enrich with batch ad/campaign info"""
        try:
            # First, get the performance report for all ads
            logger.info(f"Fetching ad performance data for {start_date} to {end_date}")
            
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
                logger.error(f"API HTTP error: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            if data.get("code") != 0:
                logger.error(f"API error: {data.get('message', 'Unknown error')}")
                return []
            
            performance_data = data.get("data", {}).get("list", [])
            
            if not performance_data:
                logger.info(f"No ads with spend found for period {start_date} to {end_date}")
                return []
            
            # Extract all ad IDs
            ad_ids = [str(item["dimensions"]["ad_id"]) for item in performance_data]
            logger.info(f"Found {len(ad_ids)} ads with spend > 0")
            
            # Batch fetch ad details (process in chunks of 100)
            ad_details = {}
            for i in range(0, len(ad_ids), 100):
                chunk = ad_ids[i:i+100]
                chunk_details = self._fetch_ad_details_batch(chunk)
                ad_details.update(chunk_details)
            
            # Get unique campaign IDs
            campaign_ids = list(set([
                ad["campaign_id"] for ad in ad_details.values() 
                if ad.get("campaign_id")
            ]))
            
            # Batch fetch campaign details
            campaign_details = {}
            if campaign_ids:
                for i in range(0, len(campaign_ids), 100):
                    chunk = campaign_ids[i:i+100]
                    chunk_details = self._fetch_campaign_details_batch(chunk)
                    campaign_details.update(chunk_details)
            
            # Combine all data
            ads_list = []
            for item in performance_data:
                try:
                    ad_id = str(item["dimensions"]["ad_id"])
                    metrics = item["metrics"]
                    
                    ad_info = ad_details.get(ad_id, {})
                    campaign_id = ad_info.get("campaign_id", "")
                    campaign_info = campaign_details.get(campaign_id, {})
                    
                    ad_name = ad_info.get("ad_name", f"Ad {ad_id}")
                    campaign_name = campaign_info.get("campaign_name", "Unknown Campaign")
                    
                    # Convert metrics
                    spend = float(metrics.get("spend", 0))
                    purchases = int(metrics.get("complete_payment", 0))
                    impressions = int(metrics.get("impressions", 0))
                    clicks = int(metrics.get("clicks", 0))
                    roas = float(metrics.get("complete_payment_roas", 0))
                    
                    # Only include ads with spend > 0
                    if spend <= 0:
                        continue
                    
                    # Calculate revenue from ROAS and spend
                    revenue = spend * roas if spend > 0 and roas > 0 else 0
                    
                    # Calculate derived metrics
                    cpa = spend / purchases if purchases > 0 else 0
                    cpc = spend / clicks if clicks > 0 else 0
                    cpm = float(metrics.get("cpm", 0))
                    
                    # Categorize based on ad name
                    category = self.categorization_service.categorize_ad(ad_name, ad_id, "tiktok")
                    
                    ad_data = {
                        "ad_id": ad_id,
                        "ad_name": ad_name,
                        "campaign_id": campaign_id,
                        "campaign_name": campaign_name,
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
                        "thumbnail_url": None,  # Would need separate API call
                        "status": ad_info.get("status", "UNKNOWN")
                    }
                    
                    ads_list.append(ad_data)
                    
                except Exception as e:
                    logger.error(f"Failed to process ad item: {e}")
                    continue
            
            logger.info(f"Processed {len(ads_list)} ads for period {start_date} to {end_date}")
            return ads_list
            
        except Exception as e:
            logger.error(f"Failed to fetch ads batch: {e}")
            return []
    
    def _fetch_ad_details_batch(self, ad_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch ad details in batch"""
        try:
            endpoint = f"{self.base_url}/ad/get/"
            params = {
                "advertiser_id": self.advertiser_id,
                "ad_ids": json.dumps(ad_ids),
                "fields": json.dumps([
                    "ad_id", "ad_name", "campaign_id", "primary_status"
                ])
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    ads = data.get("data", {}).get("list", [])
                    return {
                        str(ad["ad_id"]): {
                            "ad_name": ad.get("ad_name", f"Ad {ad['ad_id']}"),
                            "campaign_id": str(ad.get("campaign_id", "")),
                            "status": ad.get("primary_status", "UNKNOWN")
                        }
                        for ad in ads
                    }
            
            logger.error(f"Failed to fetch ad details batch")
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching ad details batch: {e}")
            return {}
    
    def _fetch_campaign_details_batch(self, campaign_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch campaign details in batch"""
        try:
            endpoint = f"{self.base_url}/campaign/get/"
            params = {
                "advertiser_id": self.advertiser_id,
                "campaign_ids": json.dumps(campaign_ids)
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    campaigns = data.get("data", {}).get("list", [])
                    return {
                        str(campaign["campaign_id"]): {
                            "campaign_name": campaign.get("campaign_name", f"Campaign {campaign['campaign_id']}")
                        }
                        for campaign in campaigns
                    }
            
            logger.error(f"Failed to fetch campaign details batch")
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching campaign details batch: {e}")
            return {}
    
    def sync_to_database(self, ads_data: List[Dict[str, Any]]) -> int:
        """Sync ads to database"""
        try:
            if not ads_data:
                return 0
            
            # Upsert in batches of 500
            total_synced = 0
            for i in range(0, len(ads_data), 500):
                batch = ads_data[i:i+500]
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

def generate_date_ranges(start_date: date, end_date: date, days_per_period: int = 7) -> list:
    """Generate weekly date ranges for the sync period"""
    date_ranges = []
    current_start = start_date
    
    while current_start <= end_date:
        period_end = min(current_start + timedelta(days=days_per_period - 1), end_date)
        date_ranges.append((current_start, period_end))
        current_start = period_end + timedelta(days=1)
    
    return date_ranges

def main():
    """Main sync function"""
    syncer = BatchTikTokAdSync()
    
    # Define date range
    start_date = date(2024, 1, 1)
    end_date = date(2024, 8, 22)
    
    # Generate weekly periods
    date_ranges = generate_date_ranges(start_date, end_date, days_per_period=7)
    
    logger.info(f"Processing {len(date_ranges)} weekly periods from {start_date} to {end_date}")
    
    total_synced = 0
    
    for period_num, (period_start, period_end) in enumerate(date_ranges, 1):
        logger.info(f"\nProcessing period {period_num}/{len(date_ranges)}: {period_start} to {period_end}")
        
        try:
            # Fetch ads for this period
            ads_data = syncer.fetch_ads_batch(period_start, period_end)
            
            if ads_data:
                # Sync to database
                synced = syncer.sync_to_database(ads_data)
                total_synced += synced
                logger.info(f"Synced {synced} ads for this period")
            else:
                logger.info("No ads found for this period")
        
        except Exception as e:
            logger.error(f"Error processing period: {e}")
            continue
    
    logger.info("\n" + "="*60)
    logger.info(f"Historical sync completed!")
    logger.info(f"Total periods processed: {len(date_ranges)}")
    logger.info(f"Total records synced: {total_synced}")
    logger.info("="*60)

if __name__ == "__main__":
    logger.info("Starting TikTok Ad-Level Historical Data Sync (Batch Mode)")
    logger.info("Date range: January 1, 2024 to August 22, 2024")
    
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nSync interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
    logger.info("\nSync script completed")