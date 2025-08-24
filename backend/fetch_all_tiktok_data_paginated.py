#!/usr/bin/env python3
"""
Fetch ALL TikTok ad data with proper pagination handling
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
import time

# Load environment variables
load_dotenv()

class TikTokCompleteFetcher:
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
        
        logger.info("TikTok Complete Fetcher initialized")
    
    def fetch_all_ad_details(self) -> Dict[str, Any]:
        """Fetch ALL ad details with pagination"""
        logger.info("Fetching all ad details...")
        all_ads = {}
        page = 1
        total_fetched = 0
        
        while True:
            try:
                endpoint = f"{self.base_url}/ad/get/"
                params = {
                    "advertiser_id": self.advertiser_id,
                    "fields": json.dumps([
                        "ad_id", "ad_name", "campaign_id", "campaign_name", "operation_status"
                    ]),
                    "page": page,
                    "page_size": 1000
                }
                
                response = requests.get(endpoint, headers=self.headers, params=params)
                
                if response.status_code != 200:
                    logger.error(f"Failed to fetch ad details page {page}: {response.status_code}")
                    break
                
                data = response.json()
                if data.get("code") != 0:
                    logger.error(f"API error on page {page}: {data.get('message')}")
                    break
                
                page_data = data.get("data", {})
                ads_list = page_data.get("list", [])
                
                if not ads_list:
                    logger.info(f"No more ads on page {page}, stopping")
                    break
                
                # Add ads to lookup
                for ad in ads_list:
                    all_ads[str(ad["ad_id"])] = {
                        "ad_name": ad.get("ad_name", f"Ad {ad['ad_id']}"),
                        "campaign_id": str(ad.get("campaign_id", "")),
                        "campaign_name": ad.get("campaign_name", "Unknown Campaign"),
                        "status": ad.get("operation_status", "UNKNOWN")
                    }
                
                total_fetched += len(ads_list)
                logger.info(f"Fetched page {page} with {len(ads_list)} ads (total: {total_fetched})")
                
                # Check if there are more pages
                page_info = page_data.get("page_info", {})
                total_pages = page_info.get("total_page", 1)
                
                if page >= total_pages:
                    logger.info(f"Reached last page ({total_pages})")
                    break
                
                page += 1
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error fetching ad details page {page}: {e}")
                break
        
        logger.info(f"Total ad details fetched: {len(all_ads)}")
        return all_ads
    
    def fetch_performance_data_paginated(self, start_date: date, end_date: date, ad_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch performance data with pagination"""
        all_performance_data = []
        page = 1
        total_ads_with_spend = 0
        
        logger.info(f"Fetching performance data for {start_date} to {end_date}")
        
        while True:
            try:
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
                    "page": page,
                    "page_size": 1000
                }
                
                response = requests.get(endpoint, headers=self.headers, params=params)
                
                if response.status_code != 200:
                    logger.error(f"API HTTP error on page {page}: {response.status_code}")
                    break
                
                data = response.json()
                if data.get("code") != 0:
                    logger.error(f"API error on page {page}: {data.get('message')}")
                    break
                
                page_data = data.get("data", {})
                performance_list = page_data.get("list", [])
                
                if not performance_list:
                    logger.info(f"No more performance data on page {page}")
                    break
                
                # Process performance data
                for item in performance_list:
                    try:
                        ad_id = str(item["dimensions"]["ad_id"])
                        metrics = item["metrics"]
                        
                        # Convert metrics
                        spend = float(metrics.get("spend", 0))
                        
                        # Only include ads with spend > 0
                        if spend <= 0:
                            continue
                        
                        total_ads_with_spend += 1
                        
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
                        
                        all_performance_data.append(ad_data)
                        
                    except Exception as e:
                        logger.error(f"Failed to process ad: {e}")
                        continue
                
                logger.info(f"Page {page}: {len(performance_list)} ads, {total_ads_with_spend} with spend > 0")
                
                # Check if there are more pages
                page_info = page_data.get("page_info", {})
                total_pages = page_info.get("total_page", 1)
                
                if page >= total_pages:
                    logger.info(f"Reached last page ({total_pages})")
                    break
                
                page += 1
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Failed to fetch performance page {page}: {e}")
                break
        
        logger.info(f"Total ads with spend > 0: {len(all_performance_data)}")
        return all_performance_data
    
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
    
    def generate_date_ranges(self, start_date: date, end_date: date) -> List[tuple]:
        """Generate weekly date ranges"""
        date_ranges = []
        current_start = start_date
        
        while current_start <= end_date:
            period_end = min(current_start + timedelta(days=6), end_date)
            date_ranges.append((current_start, period_end))
            current_start = period_end + timedelta(days=1)
        
        return date_ranges
    
    def run(self):
        """Main process to fetch all data"""
        # First, fetch ALL ad details
        logger.info("Step 1: Fetching all ad details with pagination...")
        ad_details = self.fetch_all_ad_details()
        
        if not ad_details:
            logger.error("Failed to fetch ad details")
            return
        
        # Clear existing data
        logger.info("Clearing existing data...")
        self.supabase.table("tiktok_ad_data").delete().neq("ad_id", "0").execute()
        
        # Define date range
        start_date = date(2024, 1, 1)
        end_date = date(2024, 8, 22)
        
        # Generate weekly date ranges
        date_ranges = self.generate_date_ranges(start_date, end_date)
        
        logger.info(f"Step 2: Fetching performance data for {len(date_ranges)} weekly periods")
        
        total_synced = 0
        
        for i, (period_start, period_end) in enumerate(date_ranges, 1):
            logger.info(f"\nProcessing period {i}/{len(date_ranges)}: {period_start} to {period_end}")
            
            # Fetch performance data with pagination
            ads_data = self.fetch_performance_data_paginated(period_start, period_end, ad_details)
            
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
        logger.info(f"Data covers: {start_date} to {end_date}")
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
        
        # Category breakdown
        category_result = self.supabase.table("tiktok_ad_data").select("category").execute()
        categories = {}
        if category_result.data:
            for row in category_result.data:
                cat = row['category']
                categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n{'='*60}")
        print("FINAL DATABASE STATISTICS")
        print(f"{'='*60}")
        print(f"Total ad records: {total_count:,}")
        if earliest and latest:
            print(f"Date range: {earliest['reporting_starts']} to {latest['reporting_ends']}")
        print(f"Total spend: ${total_spend:,.2f}")
        
        print("\nCategory breakdown:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count:,} ads")
        
        # Check unnamed ads
        unnamed_result = self.supabase.table("tiktok_ad_data")\
            .select("ad_id")\
            .like("ad_name", "Ad %")\
            .execute()
        
        unnamed_count = len(unnamed_result.data) if unnamed_result.data else 0
        named_count = total_count - unnamed_count
        
        print(f"\nData quality:")
        print(f"  Ads with proper names: {named_count:,} ({named_count/total_count*100:.1f}%)")
        print(f"  Ads with generic names: {unnamed_count:,} ({unnamed_count/total_count*100:.1f}%)")
        
        print(f"{'='*60}")

if __name__ == "__main__":
    logger.info("Starting TikTok complete data fetch with pagination")
    logger.info("This will fetch ALL data, not just the first 1000 records")
    
    try:
        fetcher = TikTokCompleteFetcher()
        fetcher.run()
    except KeyboardInterrupt:
        logger.info("\nFetch interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("\nFetch script completed")