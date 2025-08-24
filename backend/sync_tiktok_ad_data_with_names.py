#!/usr/bin/env python3
"""
Update TikTok ad data with proper ad names and campaign names
"""

import os
import json
import requests
from datetime import date
from loguru import logger
from dotenv import load_dotenv
from supabase import create_client
from typing import List, Dict, Any
import time

# Load environment variables
load_dotenv()

class TikTokAdUpdater:
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
        
        logger.info("TikTok Ad Updater initialized")
    
    def get_ads_to_update(self) -> List[Dict[str, Any]]:
        """Get all ads that need name updates"""
        # Get ads where ad_name is like 'Ad %'
        result = self.supabase.table("tiktok_ad_data")\
            .select("ad_id, campaign_id")\
            .like("ad_name", "Ad %")\
            .execute()
        
        # Get unique ad_id/campaign_id combinations
        unique_ads = {}
        for record in result.data:
            ad_id = record['ad_id']
            campaign_id = record['campaign_id']
            unique_ads[ad_id] = campaign_id
        
        logger.info(f"Found {len(unique_ads)} unique ads to update")
        return unique_ads
    
    def fetch_ad_details(self, ad_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch ad details including names"""
        try:
            endpoint = f"{self.base_url}/ad/get/"
            params = {
                "advertiser_id": self.advertiser_id,
                "ad_ids": json.dumps(ad_ids),
                "fields": json.dumps([
                    "ad_id", "ad_name", "campaign_id", "campaign_name", 
                    "adgroup_id", "adgroup_name", "operation_status"
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
                            "campaign_name": ad.get("campaign_name", "Unknown Campaign"),
                            "status": ad.get("operation_status", "UNKNOWN")
                        }
                        for ad in ads
                    }
                else:
                    logger.error(f"API error: {data.get('message')}")
            else:
                logger.error(f"HTTP error: {response.status_code}")
            
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching ad details: {e}")
            return {}
    
    def update_database(self, ad_updates: Dict[str, Dict[str, Any]]) -> int:
        """Update ad names and campaign names in database"""
        updated_count = 0
        
        for ad_id, details in ad_updates.items():
            try:
                # Update all records for this ad_id
                result = self.supabase.table("tiktok_ad_data")\
                    .update({
                        "ad_name": details["ad_name"],
                        "campaign_name": details["campaign_name"]
                    })\
                    .eq("ad_id", ad_id)\
                    .execute()
                
                if result.data:
                    updated_count += len(result.data)
                    
            except Exception as e:
                logger.error(f"Error updating ad {ad_id}: {e}")
        
        return updated_count
    
    def run(self):
        """Main update process"""
        # Get ads that need updating
        ads_to_update = self.get_ads_to_update()
        
        if not ads_to_update:
            logger.info("No ads need updating")
            return
        
        # Process in batches of 50 to avoid API limits
        ad_ids = list(ads_to_update.keys())
        total_updated = 0
        
        for i in range(0, len(ad_ids), 50):
            batch = ad_ids[i:i+50]
            logger.info(f"Processing batch {i//50 + 1}/{(len(ad_ids) + 49)//50}")
            
            # Fetch ad details
            ad_details = self.fetch_ad_details(batch)
            
            if ad_details:
                # Update database
                updated = self.update_database(ad_details)
                total_updated += updated
                logger.info(f"Updated {updated} records in this batch")
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        logger.info(f"\nUpdate complete! Total records updated: {total_updated}")
        
        # Show sample of updated data
        self.show_sample_data()
    
    def show_sample_data(self):
        """Show sample of updated ad data"""
        result = self.supabase.table("tiktok_ad_data")\
            .select("ad_id, ad_name, campaign_name, amount_spent_usd")\
            .not_.like("ad_name", "Ad %")\
            .order("amount_spent_usd", desc=True)\
            .limit(10)\
            .execute()
        
        if result.data:
            print("\nSample of updated ads (top spenders):")
            for ad in result.data:
                print(f"\nAd ID: {ad['ad_id']}")
                print(f"Ad Name: {ad['ad_name']}")
                print(f"Campaign: {ad['campaign_name']}")
                print(f"Spend: ${ad['amount_spent_usd']}")

if __name__ == "__main__":
    logger.info("Starting TikTok ad name update process")
    
    try:
        updater = TikTokAdUpdater()
        updater.run()
    except KeyboardInterrupt:
        logger.info("\nUpdate interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
    logger.info("\nUpdate script completed")