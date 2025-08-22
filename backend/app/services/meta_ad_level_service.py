import os
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.exceptions import FacebookRequestError
from loguru import logger
from decimal import Decimal
import re
from .ad_name_parser import AdNameParser
from .categorization import CategorizationService

class MetaAdLevelService:
    """
    Service for fetching ad-level data from Meta Ads API
    """
    
    def __init__(self):
        self.app_id = os.getenv("META_APP_ID")
        self.app_secret = os.getenv("META_APP_SECRET")
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.account_id = os.getenv("META_ACCOUNT_ID")
        self.secondary_account_id = os.getenv("META_ACCOUNT_ID_SECONDARY")
        
        if not all([self.app_id, self.app_secret, self.access_token, self.account_id]):
            raise ValueError("Missing required Meta Ads API credentials")
        
        FacebookAdsApi.init(access_token=self.access_token)
        self.ad_account = AdAccount(f"act_{self.account_id}")
        
        # Initialize the advanced ad name parser
        self.ad_parser = AdNameParser()
        
        # Initialize the main categorization service for consistent categories
        self.categorization_service = CategorizationService()
        
        # Initialize secondary account if configured
        self.secondary_ad_account = None
        if self.secondary_account_id:
            self.secondary_ad_account = AdAccount(f"act_{self.secondary_account_id}")
            logger.info(f"Initialized dual Meta Ads accounts for ad-level data: {self.account_id} and {self.secondary_account_id}")
        else:
            logger.info(f"Initialized single Meta Ads account for ad-level data: {self.account_id}")
    
    def categorize_campaign(self, campaign_name: str) -> str:
        """
        Categorize campaign based on name patterns
        """
        campaign_lower = campaign_name.lower()
        
        # Play Mats - must have both 'play' and 'mat'
        if 'play' in campaign_lower and 'mat' in campaign_lower:
            return 'Play Mats'
        
        # Standing Mats
        if any(keyword in campaign_lower for keyword in ['standing', 'desk']):
            return 'Standing Mats'
        
        # Bath Mats
        if 'bath' in campaign_lower and 'mat' in campaign_lower:
            return 'Bath Mats'
        
        # Tumbling Mats
        if 'tumbling' in campaign_lower:
            return 'Tumbling Mats'
        
        # Play Furniture
        if 'play' in campaign_lower and 'furniture' in campaign_lower:
            return 'Play Furniture'
        
        # Multi Category
        if 'multi' in campaign_lower:
            return 'Multi Category'
        
        return 'Uncategorized'
    
    def extract_product_info(self, ad_name: str, campaign_name: str = "") -> Dict[str, Any]:
        """
        Extract product information from ad name using advanced parser
        Returns dict with product, color, handle, etc.
        """
        # Use the advanced parser to extract all information
        parsed_data = self.ad_parser.parse_ad_name(ad_name, campaign_name)
        
        # Return the data in the format expected by the service
        return {
            'product': parsed_data.get('product', ''),
            'color': parsed_data.get('color', ''),
            'handle': parsed_data.get('handle', ''),
            'content_type': parsed_data.get('content_type', ''),
            'format': parsed_data.get('format', ''),
            'launch_date': parsed_data.get('launch_date'),
            'days_live': parsed_data.get('days_live', 0),
            'category': parsed_data.get('category', ''),
            'campaign_optimization': parsed_data.get('campaign_optimization', 'Standard'),
            'ad_name_clean': parsed_data.get('ad_name_clean', ad_name)
        }
    
    def _get_week_number(self, start_date: date, end_date: date) -> str:
        """
        Generate a week identifier for the date range
        """
        return f"Week {start_date.strftime('%m/%d')}-{end_date.strftime('%m/%d')}"
    
    def get_ad_creation_date(self, ad_id: str, ad_account: AdAccount) -> Optional[date]:
        """
        Get the creation date of an ad
        """
        try:
            ad = Ad(ad_id)
            ad_info = ad.api_get(fields=['created_time'])
            if 'created_time' in ad_info:
                created_datetime = datetime.strptime(ad_info['created_time'], '%Y-%m-%dT%H:%M:%S%z')
                return created_datetime.date()
        except Exception as e:
            logger.warning(f"Could not get creation date for ad {ad_id}: {e}")
        return None
    
    def calculate_days_live(self, launch_date: Optional[date], end_date: date) -> int:
        """
        Calculate number of days the ad has been live
        """
        if launch_date:
            return (end_date - launch_date).days + 1
        return 0
    
    def _fetch_ad_insights_for_account(
        self,
        ad_account: AdAccount,
        account_name: str,
        start_date: date,
        end_date: date,
        campaigns: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch ad-level insights for a specific account with weekly segmentation
        """
        try:
            params = {
                'time_range': {
                    'since': start_date.strftime('%Y-%m-%d'),
                    'until': end_date.strftime('%Y-%m-%d')
                },
                'fields': [
                    'ad_id',
                    'ad_name',
                    'campaign_id',
                    'campaign_name',
                    'spend',
                    'actions',
                    'action_values',
                    'impressions',
                    'clicks',
                    'cpm',
                    'cpc',
                    'ctr',
                    'objective',
                    'date_start',
                    'date_stop'
                ],
                'level': 'ad',
                'time_increment': 7,  # Weekly segments (7 days)
                'breakdowns': [],
                'limit': 1000
            }
            
            if campaigns:
                params['filtering'] = [
                    {
                        'field': 'campaign.id',
                        'operator': 'IN',
                        'value': campaigns
                    }
                ]
            
            insights = ad_account.get_insights(params=params)
            
            results = []
            for insight in insights:
                # Extract purchases and link_clicks from actions array
                purchases = 0
                purchase_value = 0.0
                link_clicks = 0
                
                if 'actions' in insight and insight['actions']:
                    for action in insight['actions']:
                        if action.get('action_type') == 'purchase':
                            purchases = int(float(action.get('value', '0')))
                        elif action.get('action_type') == 'link_click':
                            link_clicks = int(float(action.get('value', '0')))
                
                if 'action_values' in insight and insight['action_values']:
                    for action_value in insight['action_values']:
                        if action_value.get('action_type') == 'purchase':
                            purchase_value = float(action_value.get('value', '0'))
                            break
                
                # Get ad creation date from API
                ad_id = insight.get('ad_id', '')
                api_launch_date = self.get_ad_creation_date(ad_id, ad_account)
                
                # Extract product information from ad name (includes parsing launch date from name)
                campaign_name = insight.get('campaign_name', '')
                ad_name = insight.get('ad_name', '')
                product_info = self.extract_product_info(ad_name, campaign_name)
                
                # Use parsed launch date if available, otherwise fall back to API date
                launch_date = product_info['launch_date'] or api_launch_date
                
                # Calculate days live using parsed data if available, otherwise use API data
                days_live = product_info['days_live'] if product_info['launch_date'] else self.calculate_days_live(launch_date, end_date)
                
                # Use main categorization service for consistency with other dashboards
                # Try ad name first (more specific), fallback to campaign name
                category = self.categorization_service.categorize_ad(ad_name, ad_id, platform="meta") or \
                          self.categorize_campaign(campaign_name)
                
                # Use parsed campaign optimization, fallback to API objective
                campaign_optimization = product_info['campaign_optimization'] or insight.get('objective', 'Standard')
                
                # Use the actual date range from the insight (for weekly segmentation)
                insight_start = datetime.strptime(insight.get('date_start', start_date.strftime('%Y-%m-%d')), '%Y-%m-%d').date()
                insight_end = datetime.strptime(insight.get('date_stop', end_date.strftime('%Y-%m-%d')), '%Y-%m-%d').date()
                
                ad_data = {
                    'ad_id': ad_id,
                    'original_ad_name': ad_name,  # Original from Meta platform
                    'ad_name': product_info['ad_name_clean'],  # Cleaned version from parser
                    'campaign_name': campaign_name,
                    'reporting_starts': insight_start,
                    'reporting_ends': insight_end,
                    'launch_date': launch_date,
                    'days_live': days_live,
                    'category': category,
                    'product': product_info['product'],
                    'color': product_info['color'],
                    'content_type': product_info['content_type'],
                    'handle': product_info['handle'],
                    'format': product_info['format'],
                    'campaign_optimization': campaign_optimization,
                    'amount_spent_usd': float(insight.get('spend', '0')),
                    'purchases': purchases,
                    'purchases_conversion_value': purchase_value,
                    'impressions': int(insight.get('impressions', '0')),
                    'link_clicks': link_clicks,
                    'week_number': self._get_week_number(insight_start, insight_end)
                }
                
                results.append(ad_data)
            
            logger.info(f"Retrieved {len(results)} ad-level insights from {account_name} for {start_date} to {end_date}")
            return results
            
        except FacebookRequestError as e:
            logger.error(f"Facebook API error for ad-level data from account {account_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching ad-level insights from {account_name}: {e}")
            raise
    
    def get_ad_level_insights(
        self,
        start_date: date,
        end_date: date,
        campaigns: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch ad-level insights from Meta Ads API for the specified date range
        """
        try:
            # Fetch from primary account
            primary_results = self._fetch_ad_insights_for_account(
                self.ad_account,
                f"Primary ({self.account_id})",
                start_date,
                end_date,
                campaigns
            )
            
            # Fetch from secondary account if configured
            secondary_results = []
            if self.secondary_ad_account:
                secondary_results = self._fetch_ad_insights_for_account(
                    self.secondary_ad_account,
                    f"Secondary ({self.secondary_account_id})",
                    start_date,
                    end_date,
                    campaigns
                )
            
            # Combine results from both accounts
            all_results = primary_results + secondary_results
            
            logger.info(f"Retrieved {len(primary_results)} ad insights from primary account, {len(secondary_results)} from secondary account (total: {len(all_results)})")
            return all_results
            
        except FacebookRequestError as e:
            logger.error(f"Facebook API error fetching ad-level data: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching ad-level insights: {e}")
            raise
    
    def get_last_14_days_ad_data(self, target_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Get ad-level data for the last 14 days with weekly segmentation
        Yesterday is the last full day in the 14-day period
        """
        if target_date is None:
            target_date = date.today()
        
        # Yesterday is the end date (last full day)
        end_date = target_date - timedelta(days=1)
        # Start date is 14 days before yesterday
        start_date = end_date - timedelta(days=13)
        
        logger.info(f"Fetching last 14 days of ad-level data from {start_date} to {end_date} (weekly segments)")
        
        # Get ad insights data
        ad_data = self.get_ad_level_insights(start_date, end_date)
        
        # Extract unique ad IDs and fetch thumbnails
        ad_ids = list(set([ad['ad_id'] for ad in ad_data if ad.get('ad_id')]))
        logger.info(f"🖼️ THUMBNAIL DEBUG: Found {len(ad_ids)} unique ad IDs from {len(ad_data)} ad records")
        
        if ad_ids:
            logger.info(f"🖼️ Fetching thumbnails for {len(ad_ids)} unique ads")
            logger.info(f"🖼️ First 5 ad IDs: {ad_ids[:5]}")
            thumbnails = self.get_ad_thumbnails(ad_ids)
            
            # Add thumbnail URLs to ad data
            for ad in ad_data:
                ad_id = ad.get('ad_id')
                if ad_id and ad_id in thumbnails:
                    ad['thumbnail_url'] = thumbnails[ad_id]
                else:
                    ad['thumbnail_url'] = None
        else:
            logger.info("No ad IDs found, skipping thumbnail fetch")
        
        return ad_data
    
    def get_month_to_date_ad_data(self, target_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Get month-to-date ad-level data for the specified date (or current date)
        """
        if target_date is None:
            target_date = date.today()
        
        # Calculate start of month and end date
        start_of_month = target_date.replace(day=1)
        end_date = target_date - timedelta(days=1)
        
        logger.info(f"Fetching month-to-date ad-level data from {start_of_month} to {end_date}")
        
        return self.get_ad_level_insights(start_of_month, end_date)
    
    def test_connection(self) -> bool:
        """
        Test the Meta Ads API connection for ad-level data access
        """
        try:
            # Test primary account
            primary_account_info = self.ad_account.api_get(fields=['name', 'account_status'])
            logger.info(f"Ad-level service connected to primary account: {primary_account_info.get('name', 'Unknown')} (ID: {self.account_id})")
            
            # Test secondary account if configured
            if self.secondary_ad_account:
                secondary_account_info = self.secondary_ad_account.api_get(fields=['name', 'account_status'])
                logger.info(f"Ad-level service connected to secondary account: {secondary_account_info.get('name', 'Unknown')} (ID: {self.secondary_account_id})")
            
            # Test ad-level access by fetching a small sample
            today = date.today()
            yesterday = today - timedelta(days=1)
            test_ads = self.get_ad_level_insights(yesterday, yesterday)
            logger.info(f"Ad-level access test successful: retrieved {len(test_ads)} ads for {yesterday}")
            
            return True
        except Exception as e:
            logger.error(f"Ad-level service connection test failed: {e}")
            return False
    
    def get_ad_thumbnails(self, ad_ids: List[str]) -> Dict[str, str]:
        """
        Fetch thumbnail URLs for a list of ad IDs
        Returns dict mapping ad_id to thumbnail_url
        """
        thumbnails = {}
        
        # Process in batches to avoid rate limits
        batch_size = 10
        for i in range(0, len(ad_ids), batch_size):
            batch = ad_ids[i:i + batch_size]
            
            for ad_id in batch:
                try:
                    ad = Ad(ad_id)
                    
                    # Get ad creatives for this ad
                    creatives = ad.get_ad_creatives(fields=[
                        AdCreative.Field.thumbnail_url,
                        AdCreative.Field.image_url,
                        AdCreative.Field.object_story_spec
                    ])
                    
                    if creatives and len(creatives) > 0:
                        creative = creatives[0]  # Use first creative
                        
                        # Try thumbnail_url first, fallback to image_url
                        thumbnail_url = creative.get('thumbnail_url')
                        if not thumbnail_url:
                            thumbnail_url = creative.get('image_url')
                        
                        # If still no URL, try extracting from object_story_spec
                        if not thumbnail_url and 'object_story_spec' in creative:
                            object_story = creative['object_story_spec']
                            if 'link_data' in object_story and 'picture' in object_story['link_data']:
                                thumbnail_url = object_story['link_data']['picture']
                        
                        if thumbnail_url:
                            thumbnails[ad_id] = thumbnail_url
                            logger.debug(f"Found thumbnail for ad {ad_id}: {thumbnail_url}")
                        else:
                            logger.debug(f"No thumbnail found for ad {ad_id}")
                    else:
                        logger.debug(f"No creatives found for ad {ad_id}")
                        
                except FacebookRequestError as e:
                    logger.warning(f"Facebook API error fetching creative for ad {ad_id}: {e}")
                except Exception as e:
                    logger.warning(f"Error fetching creative for ad {ad_id}: {e}")
        
        logger.info(f"Retrieved {len(thumbnails)} thumbnails out of {len(ad_ids)} requested ads")
        return thumbnails