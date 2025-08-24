#!/usr/bin/env python3
"""
Resync TikTok ad data with proper names for the existing date ranges
"""

import os
import json
import requests
from datetime import datetime, date
from loguru import logger
from dotenv import load_dotenv
from supabase import create_client
from typing import List, Dict, Any
from app.services.categorization import CategorizationService

# Load environment variables
load_dotenv()

class TikTokAdResync:
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
        
        logger.info("TikTok Ad Resync initialized")
    
    def get_date_ranges(self) -> List[tuple]:
        """Get all unique date ranges from existing data"""
        result = self.supabase.table("tiktok_ad_data")\
            .select("reporting_starts, reporting_ends")\
            .execute()
        
        # Get unique date ranges
        date_ranges = set()
        for record in result.data:
            date_ranges.add((record['reporting_starts'], record['reporting_ends']))
        
        # Sort by date
        sorted_ranges = sorted(list(date_ranges))
        logger.info(f"Found {len(sorted_ranges)} unique date ranges to resync")
        return sorted_ranges
    
    def fetch_ads_with_names(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch ad performance data with names for a specific date range"""
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
                "start_date": start_date,
                "end_date": end_date,
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
            
            # Get all ads with details (including names)
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
            
            # Combine performance data with ad details
            ads_list = []
            for item in performance_data:
                try:
                    ad_id = str(item["dimensions"]["ad_id"])
                    metrics = item["metrics"]
                    
                    # Get ad details
                    details = ad_details.get(ad_id, {
                        "ad_name": f"Ad {ad_id}",
                        "campaign_id": "",
                        "campaign_name": "Unknown Campaign",
                        "status": "UNKNOWN"
                    })
                    
                    # Convert metrics
                    spend = float(metrics.get("spend", 0))
                    
                    # Only include ads with spend > 0
                    if spend <= 0:
                        continue
                    
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
                        "reporting_starts": start_date,
                        "reporting_ends": end_date,
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
            
            logger.info(f"Processed {len(ads_list)} ads for period {start_date} to {end_date}")
            return ads_list
            
        except Exception as e:
            logger.error(f"Failed to fetch ads: {e}")
            return []
    
    def update_database(self, ads_data: List[Dict[str, Any]]) -> int:
        """Update ads in database"""
        if not ads_data:
            return 0
        
        try:
            # Update using upsert
            result = self.supabase.table("tiktok_ad_data").upsert(
                ads_data,
                on_conflict="ad_id,reporting_starts,reporting_ends"
            ).execute()
            
            if result.data:
                return len(result.data)
            return 0
            
        except Exception as e:
            logger.error(f"Error updating database: {e}")
            return 0
    
    def run(self):
        """Main resync process"""
        # Get date ranges
        date_ranges = self.get_date_ranges()
        
        if not date_ranges:
            logger.info("No date ranges found to resync")
            return
        
        total_updated = 0
        
        # Process each date range
        for i, (start_date, end_date) in enumerate(date_ranges, 1):
            logger.info(f"\nProcessing range {i}/{len(date_ranges)}: {start_date} to {end_date}")
            
            # Fetch ads with names
            ads_data = self.fetch_ads_with_names(start_date, end_date)
            
            if ads_data:
                # Update database
                updated = self.update_database(ads_data)
                total_updated += updated
                logger.info(f"Updated {updated} ads for this period")
            else:
                logger.info("No ads found for this period")
        
        logger.info(f"\nResync complete! Total ads updated: {total_updated}")
        
        # Show sample data
        self.show_sample_data()
    
    def show_sample_data(self):
        """Show sample of updated data"""
        result = self.supabase.table("tiktok_ad_data")\
            .select("ad_id, ad_name, campaign_name, category, amount_spent_usd")\
            .not_.like("ad_name", "Ad %")\
            .order("amount_spent_usd", desc=True)\
            .limit(10)\
            .execute()
        
        if result.data:
            print("\nSample of updated ads (top spenders with names):")
            for ad in result.data:
                print(f"\nAd ID: {ad['ad_id']}")
                print(f"Ad Name: {ad['ad_name']}")
                print(f"Campaign: {ad['campaign_name']}")
                print(f"Category: {ad['category']}")
                print(f"Spend: ${ad['amount_spent_usd']}")

if __name__ == "__main__":
    logger.info("Starting TikTok ad data resync with proper names")
    
    try:
        resyncer = TikTokAdResync()
        resyncer.run()
    except KeyboardInterrupt:
        logger.info("\nResync interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
    logger.info("\nResync script completed")