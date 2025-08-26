"""TikTok Ad-Level Service for fetching and managing ad-level performance data"""

import os
import json
import requests
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from loguru import logger
from supabase import create_client

from .categorization import CategorizationService


class TikTokAdLevelService:
    """Service for TikTok ad-level data management (similar to MetaAdLevelService)"""
    
    def __init__(self):
        # TikTok API credentials
        self.app_id = os.getenv("TIKTOK_APP_ID")
        self.app_secret = os.getenv("TIKTOK_APP_SECRET")
        self.access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        self.advertiser_id = os.getenv("TIKTOK_ADVERTISER_ID")
        self.sandbox_mode = os.getenv("TIKTOK_SANDBOX_MODE", "false").lower() == "true"
        
        if not all([self.app_id, self.app_secret, self.access_token, self.advertiser_id]):
            raise ValueError("Missing required TikTok Ads API credentials")
        
        # Database connection
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase = create_client(supabase_url, supabase_key)
        
        # TikTok API base URL
        self.base_url = "https://business-api.tiktok.com/open_api/v1.3" if not self.sandbox_mode else "https://sandbox-ads.tiktok.com/open_api/v1.3"
        
        # Standard headers for TikTok API
        self.headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        
        # Initialize categorization service
        self.categorization_service = CategorizationService()
        
        logger.info(f"TikTok Ad-Level Service initialized {'(sandbox mode)' if self.sandbox_mode else '(production)'}")
    
    def test_connection(self) -> bool:
        """Test TikTok Ads API connection"""
        try:
            endpoint = f"{self.base_url}/advertiser/info/"
            params = {
                "advertiser_ids": json.dumps([self.advertiser_id])
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    logger.info("TikTok Ad-Level API connection successful")
                    return True
                else:
                    logger.error(f"TikTok API error: {data.get('message', 'Unknown error')}")
                    return False
            else:
                logger.error(f"TikTok API HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"TikTok Ad-Level connection test failed: {e}")
            return False
    
    def fetch_ad_level_data(self, days_back: int = 14) -> List[Dict[str, Any]]:
        """
        Fetch ad-level performance data from TikTok API for the last N days
        Returns data split into weekly periods for momentum calculation
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            # Split into weekly periods for momentum indicators
            weekly_periods = []
            current_start = start_date
            
            while current_start < end_date:
                period_end = min(current_start + timedelta(days=6), end_date - timedelta(days=1))
                weekly_periods.append((current_start, period_end))
                current_start = period_end + timedelta(days=1)
            
            all_ads = []
            
            for period_start, period_end in weekly_periods:
                logger.info(f"Fetching TikTok ad data for period: {period_start} to {period_end}")
                
                # Fetch ad-level insights for this period
                ads_data = self._fetch_ads_for_period(period_start, period_end)
                all_ads.extend(ads_data)
            
            logger.info(f"Retrieved {len(all_ads)} TikTok ad records across {len(weekly_periods)} weekly periods")
            return all_ads
            
        except Exception as e:
            logger.error(f"Failed to fetch TikTok ad-level data: {e}")
            return []
    
    def _fetch_ads_for_period(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Fetch ad-level data for a specific date period"""
        try:
            # TikTok API endpoint for ad-level reports
            endpoint = f"{self.base_url}/report/integrated/get/"
            
            params = {
                "advertiser_id": self.advertiser_id,
                "report_type": "BASIC",
                "data_level": "AUCTION_AD",  # Ad-level data (not campaign-level)
                "dimensions": json.dumps(["ad_id"]),  # Only ad_id dimension for ad-level data
                "metrics": json.dumps([
                    "spend",
                    "impressions", 
                    "clicks",
                    "ctr",
                    "cpc",
                    "cpm",
                    "cost_per_conversion",
                    "conversion_rate",
                    "complete_payment_roas",  # TikTok's ROAS metric
                    "complete_payment",       # Number of purchases
                    "purchase"               # Purchase events
                ]),
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "page": 1,
                "page_size": 1000
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"TikTok API HTTP error: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            
            if data.get("code") != 0:
                logger.error(f"TikTok API error: {data.get('message', 'Unknown error')}")
                return []
            
            ads_list = []
            
            if "data" in data and "list" in data["data"]:
                for item in data["data"]["list"]:
                    try:
                        dimensions = item.get("dimensions", {})
                        metrics = item.get("metrics", {})
                        
                        ad_id = str(dimensions.get("ad_id", ""))
                        
                        # Get ad info (which includes campaign_id)
                        ad_info = self._get_ad_info(ad_id)
                        campaign_id = ad_info.get("campaign_id", "")
                        
                        # Get campaign info
                        campaign_info = self._get_campaign_info(campaign_id) if campaign_id else {"campaign_name": "Unknown Campaign"}
                        
                        ad_name = ad_info.get("ad_name", f"Ad {ad_id}")
                        campaign_name = campaign_info.get("campaign_name", f"Campaign {campaign_id}")
                        
                        # Convert metrics
                        spend = float(metrics.get("spend", 0))
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
                        
                        # Categorize based on ad name (not campaign name)
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
                            "thumbnail_url": ad_info.get("thumbnail_url"),
                            "status": ad_info.get("status", "UNKNOWN")
                        }
                        
                        ads_list.append(ad_data)
                        
                    except Exception as e:
                        logger.error(f"Failed to process TikTok ad item: {e}")
                        continue
            
            logger.info(f"Processed {len(ads_list)} TikTok ads for period {start_date} to {end_date}")
            return ads_list
            
        except Exception as e:
            logger.error(f"Failed to fetch TikTok ads for period {start_date} to {end_date}: {e}")
            return []
    
    def _get_ad_info(self, ad_id: str) -> Dict[str, Any]:
        """Get ad information including name and thumbnail"""
        try:
            endpoint = f"{self.base_url}/ad/get/"
            params = {
                "advertiser_id": self.advertiser_id,
                "ad_ids": json.dumps([ad_id]),
                "fields": json.dumps([
                    "ad_id", "ad_name", "campaign_id", "primary_status", "display_name",
                    "image_ids", "video_id"  # For thumbnail extraction
                ])
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0 and data.get("data", {}).get("list"):
                    ad_data = data["data"]["list"][0]
                    return {
                        "ad_name": ad_data.get("ad_name", f"Ad {ad_id}"),
                        "campaign_id": ad_data.get("campaign_id", ""),
                        "status": ad_data.get("primary_status", "UNKNOWN"),
                        "thumbnail_url": self._extract_thumbnail_url(ad_data)
                    }
            
            # Return default if API call fails
            return {
                "ad_name": f"Ad {ad_id}",
                "campaign_id": "",
                "status": "UNKNOWN",
                "thumbnail_url": None
            }
            
        except Exception as e:
            logger.error(f"Failed to get TikTok ad info for {ad_id}: {e}")
            return {
                "ad_name": f"Ad {ad_id}",
                "campaign_id": "",
                "status": "UNKNOWN", 
                "thumbnail_url": None
            }
    
    def _get_campaign_info(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign information"""
        try:
            endpoint = f"{self.base_url}/campaign/get/"
            params = {
                "advertiser_id": self.advertiser_id,
                "campaign_ids": json.dumps([campaign_id])
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0 and data.get("data", {}).get("list"):
                    return data["data"]["list"][0]
            
            return {"campaign_name": f"Campaign {campaign_id}"}
            
        except Exception as e:
            logger.error(f"Failed to get TikTok campaign info for {campaign_id}: {e}")
            return {"campaign_name": f"Campaign {campaign_id}"}
    
    def _extract_thumbnail_url(self, ad_data: Dict[str, Any]) -> Optional[str]:
        """Extract thumbnail URL from ad creative data"""
        try:
            # TikTok creative extraction logic would go here
            # This is a placeholder - actual implementation depends on TikTok's creative API
            return None
        except Exception as e:
            logger.error(f"Failed to extract thumbnail: {e}")
            return None
    
    def sync_ad_data_to_database(self, ads_data: List[Dict[str, Any]]) -> Tuple[int, str]:
        """Sync ad-level data to the tiktok_ad_data table"""
        try:
            if not ads_data:
                return 0, "No ad data to sync"
            
            # Upsert data into tiktok_ad_data table
            result = self.supabase.table("tiktok_ad_data").upsert(
                ads_data,
                on_conflict="ad_id,reporting_starts,reporting_ends"
            ).execute()
            
            if result.data:
                synced_count = len(result.data)
                logger.info(f"Synced {synced_count} TikTok ad records to database")
                return synced_count, f"Successfully synced {synced_count} TikTok ads"
            else:
                logger.error("Failed to sync TikTok ad data to database")
                return 0, "Failed to sync ad data"
                
        except Exception as e:
            error_msg = f"Error syncing TikTok ad data: {str(e)}"
            logger.error(error_msg)
            return 0, error_msg
    
    def get_ad_level_data(self, 
                         categories: Optional[List[str]] = None,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get ad-level data with optional filtering (similar to Meta Ad Level)"""
        try:
            # Build query
            query = self.supabase.table("tiktok_ad_data").select("*")
            
            if categories:
                query = query.in_("category", categories)
            
            # Apply date filters if provided, otherwise default to current month
            if start_date:
                query = query.gte("reporting_starts", start_date)
            elif not start_date and not end_date:
                # Default to current month if no dates specified
                current_month_start = date.today().replace(day=1)
                query = query.gte("reporting_starts", current_month_start.strftime('%Y-%m-%d'))
                
            if end_date:
                query = query.lte("reporting_ends", end_date)
            
            # Execute query
            result = query.execute()
            ads_data = result.data
            
            # Group ads by ad_name and calculate totals with weekly periods
            grouped_data = {}
            
            for ad in ads_data:
                ad_name = ad['ad_name']
                date_key = f"{ad['reporting_starts']}_{ad['reporting_ends']}"
                
                if ad_name not in grouped_data:
                    grouped_data[ad_name] = {
                        'ad_name': ad_name,
                        'campaign_name': ad['campaign_name'],
                        'category': ad['category'],
                        'status': ad.get('status', 'UNKNOWN'),
                        'thumbnail_url': ad.get('thumbnail_url'),
                        'weekly_periods': {},
                        'total_spend': 0,
                        'total_revenue': 0,
                        'total_purchases': 0,
                        'total_clicks': 0,
                        'total_impressions': 0
                    }
                
                # Add weekly period data (avoiding duplicates)
                if date_key not in grouped_data[ad_name]['weekly_periods']:
                    grouped_data[ad_name]['weekly_periods'][date_key] = {
                        'reporting_starts': ad['reporting_starts'],
                        'reporting_ends': ad['reporting_ends'],
                        'spend': ad['amount_spent_usd'],
                        'revenue': ad['purchases_conversion_value'],
                        'purchases': ad['website_purchases'],
                        'roas': ad['roas'],
                        'cpa': ad['cpa'],
                        'cpc': ad['cpc'],
                        'clicks': ad['link_clicks'],
                        'impressions': ad['impressions']
                    }
                    
                    # Add to totals
                    grouped_data[ad_name]['total_spend'] += ad['amount_spent_usd']
                    grouped_data[ad_name]['total_revenue'] += ad['purchases_conversion_value']
                    grouped_data[ad_name]['total_purchases'] += ad['website_purchases']
                    grouped_data[ad_name]['total_clicks'] += ad['link_clicks']
                    grouped_data[ad_name]['total_impressions'] += ad['impressions']
            
            # Calculate total metrics and format weekly periods
            for ad_name, ad_data in grouped_data.items():
                # Calculate total metrics
                if ad_data['total_purchases'] > 0:
                    ad_data['total_cpa'] = round(ad_data['total_spend'] / ad_data['total_purchases'], 2)
                else:
                    ad_data['total_cpa'] = 0
                
                if ad_data['total_spend'] > 0:
                    ad_data['total_roas'] = round(ad_data['total_revenue'] / ad_data['total_spend'], 4)
                else:
                    ad_data['total_roas'] = 0
                
                if ad_data['total_clicks'] > 0:
                    ad_data['total_cpc'] = round(ad_data['total_spend'] / ad_data['total_clicks'], 4)
                else:
                    ad_data['total_cpc'] = 0
                
                # Convert weekly_periods dict to list and sort by date (older first)
                ad_data['weekly_periods'] = list(ad_data['weekly_periods'].values())
                ad_data['weekly_periods'].sort(key=lambda x: x['reporting_starts'])
                # Keep only the last 2 periods for momentum calculation
                ad_data['weekly_periods'] = ad_data['weekly_periods'][-2:]
            
            # Convert to list and sort by total spend
            grouped_ads = sorted(grouped_data.values(), key=lambda x: x['total_spend'], reverse=True)
            
            return {
                "status": "success",
                "count": len(grouped_ads),
                "grouped_ads": grouped_ads
            }
            
        except Exception as e:
            logger.error(f"Error fetching TikTok ad data: {e}")
            raise Exception(f"Failed to fetch TikTok ad data: {str(e)}")
    
    def get_summary_metrics(self, 
                           categories: Optional[List[str]] = None,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get summary metrics for TikTok ad-level data with optional filtering"""
        try:
            # Build query with filters (similar to get_ad_level_data)
            query = self.supabase.table("tiktok_ad_data").select("*")
            
            # Apply category filter if provided
            if categories:
                query = query.in_("category", categories)
            
            # Apply date filters if provided, otherwise default to current month
            if start_date:
                query = query.gte("reporting_starts", start_date)
            elif not start_date and not end_date:
                # Default to current month if no dates specified
                current_month_start = date.today().replace(day=1)
                query = query.gte("reporting_starts", current_month_start.strftime('%Y-%m-%d'))
                
            if end_date:
                query = query.lte("reporting_ends", end_date)
            
            result = query.execute()
            
            ads_data = result.data
            
            if not ads_data:
                return {
                    "total_spend": 0,
                    "total_revenue": 0,
                    "total_purchases": 0,
                    "total_clicks": 0,
                    "total_impressions": 0,
                    "avg_roas": 0,
                    "avg_cpa": 0,
                    "avg_cpc": 0,
                    "ads_count": 0
                }
            
            # Calculate summary metrics with deduplication (same logic as get_ad_level_data)
            # Group by ad_name and date to avoid double-counting weekly periods
            grouped_data = {}
            
            for ad in ads_data:
                ad_id = ad['ad_id']
                date_key = f"{ad['reporting_starts']}_{ad['reporting_ends']}"
                
                if ad_id not in grouped_data:
                    grouped_data[ad_id] = {
                        'weekly_periods': {},
                        'total_spend': 0,
                        'total_revenue': 0,
                        'total_purchases': 0,
                        'total_clicks': 0,
                        'total_impressions': 0
                    }
                
                # Add weekly period data (avoiding duplicates)
                if date_key not in grouped_data[ad_id]['weekly_periods']:
                    grouped_data[ad_id]['weekly_periods'][date_key] = True
                    
                    # Add to totals (only once per ad per date period)
                    grouped_data[ad_id]['total_spend'] += ad['amount_spent_usd']
                    grouped_data[ad_id]['total_revenue'] += ad['purchases_conversion_value']
                    grouped_data[ad_id]['total_purchases'] += ad['website_purchases']
                    grouped_data[ad_id]['total_clicks'] += ad['link_clicks']
                    grouped_data[ad_id]['total_impressions'] += ad['impressions']
            
            # Sum up all the deduplicated totals
            total_spend = sum(ad_data['total_spend'] for ad_data in grouped_data.values())
            total_revenue = sum(ad_data['total_revenue'] for ad_data in grouped_data.values())
            total_purchases = sum(ad_data['total_purchases'] for ad_data in grouped_data.values())
            total_clicks = sum(ad_data['total_clicks'] for ad_data in grouped_data.values())
            total_impressions = sum(ad_data['total_impressions'] for ad_data in grouped_data.values())
            
            avg_roas = total_revenue / total_spend if total_spend > 0 else 0
            avg_cpa = total_spend / total_purchases if total_purchases > 0 else 0
            avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0
            
            return {
                "total_spend": round(total_spend, 2),
                "total_revenue": round(total_revenue, 2),
                "total_purchases": total_purchases,
                "total_clicks": total_clicks,
                "total_impressions": total_impressions,
                "avg_roas": round(avg_roas, 4),
                "avg_cpa": round(avg_cpa, 2),
                "avg_cpc": round(avg_cpc, 4),
                "ads_count": len(grouped_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting TikTok summary metrics: {e}")
            return {
                "total_spend": 0,
                "total_revenue": 0,
                "total_purchases": 0,
                "total_clicks": 0,
                "total_impressions": 0,
                "avg_roas": 0,
                "avg_cpa": 0,
                "avg_cpc": 0,
                "ads_count": 0
            }
    
    def get_available_categories(self) -> List[str]:
        """Get available categories from TikTok ad data"""
        try:
            result = self.supabase.table("tiktok_ad_data")\
                .select("category")\
                .not_.is_("category", "null")\
                .execute()
            
            categories = list(set([row["category"] for row in result.data if row["category"]]))
            return sorted(categories)
            
        except Exception as e:
            logger.error(f"Error getting TikTok ad categories: {e}")
            return []