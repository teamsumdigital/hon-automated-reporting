#!/usr/bin/env python3
"""
Fetch TikTok ad data in MONTHLY increments
January 2024 through July 2024 (full months)
August 1-22, 2024 (partial month)
"""

import os
import json
import requests
from datetime import datetime, date
from calendar import monthrange
from loguru import logger
from dotenv import load_dotenv
from supabase import create_client
from typing import List, Dict, Any
from app.services.categorization import CategorizationService
import time

# Load environment variables
load_dotenv()

class TikTokMonthlyFetcher:
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
        
        logger.info("TikTok Monthly Fetcher initialized")
    
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
    
    def fetch_monthly_performance_data(self, year: int, month: int, last_day: int, ad_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch performance data for a full month with pagination"""
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        
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
        
        logger.info(f"Total ads with spend > 0 for {start_date.strftime('%B %Y')}: {len(all_performance_data)}")
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
    
    def run(self):
        """Main process to fetch all data by month"""
        # First, fetch ALL ad details
        logger.info("Step 1: Fetching all ad details with pagination...")
        ad_details = self.fetch_all_ad_details()
        
        if not ad_details:
            logger.error("Failed to fetch ad details")
            return
        
        # Clear existing data
        logger.info("Clearing existing data...")
        self.supabase.table("tiktok_ad_data").delete().neq("ad_id", "0").execute()
        
        total_synced = 0
        
        # Define months to fetch: January 2024 through July 2025 (19 full months) + August 1-22, 2025 (partial)
        months_to_fetch = [
            # 2024 - 12 months
            (2024, 1, 31),   # January 2024
            (2024, 2, 29),   # February 2024 (leap year)
            (2024, 3, 31),   # March 2024
            (2024, 4, 30),   # April 2024
            (2024, 5, 31),   # May 2024
            (2024, 6, 30),   # June 2024
            (2024, 7, 31),   # July 2024
            (2024, 8, 31),   # August 2024
            (2024, 9, 30),   # September 2024
            (2024, 10, 31),  # October 2024
            (2024, 11, 30),  # November 2024
            (2024, 12, 31),  # December 2024
            # 2025 - 7 full months + 1 partial
            (2025, 1, 31),   # January 2025
            (2025, 2, 28),   # February 2025
            (2025, 3, 31),   # March 2025
            (2025, 4, 30),   # April 2025
            (2025, 5, 31),   # May 2025
            (2025, 6, 30),   # June 2025
            (2025, 7, 31),   # July 2025
            (2025, 8, 22),   # August 2025 (partial month)
        ]
        
        logger.info(f"Step 2: Fetching performance data for {len(months_to_fetch)} months")
        
        for i, (year, month, last_day) in enumerate(months_to_fetch, 1):
            month_name = date(year, month, 1).strftime('%B %Y')
            if year == 2025 and month == 8 and last_day == 22:
                month_name += " (Partial)"
            
            logger.info(f"\nProcessing month {i}/{len(months_to_fetch)}: {month_name}")
            
            # Fetch performance data for the month
            ads_data = self.fetch_monthly_performance_data(year, month, last_day, ad_details)
            
            if ads_data:
                # Sync to database
                synced = self.sync_to_database(ads_data)
                total_synced += synced
                logger.info(f"Synced {synced} ads for {month_name}")
            else:
                logger.info(f"No ads found for {month_name}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Data fetch complete!")
        logger.info(f"Total months processed: {len(months_to_fetch)}")
        logger.info(f"Total ads synced: {total_synced}")
        logger.info(f"Data covers: January 2024 to August 22, 2025")
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
        
        # Monthly breakdown
        if total_count > 0:
            print("\nRecords by month:")
            month_result = self.supabase.table("tiktok_ad_data")\
                .select("reporting_starts")\
                .execute()
            
            month_counts = {}
            for record in month_result.data:
                month_key = record['reporting_starts'][:7]
                month_counts[month_key] = month_counts.get(month_key, 0) + 1
            
            for month in sorted(month_counts.keys()):
                print(f"  {month}: {month_counts[month]:,} records")
        
        print(f"{'='*60}")

if __name__ == "__main__":
    logger.info("Starting TikTok monthly data fetch")
    logger.info("Fetching data by MONTH from January 2024 through August 22, 2025")
    
    try:
        fetcher = TikTokMonthlyFetcher()
        fetcher.run()
    except KeyboardInterrupt:
        logger.info("\nFetch interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("\nFetch script completed")