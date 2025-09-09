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
import time
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
    
    def fetch_ad_status_batch(self, ad_ids: List[str], ad_account: AdAccount) -> Dict[str, str]:
        """
        Fetch effective_status for a batch of ads using bulk Ad object queries
        """
        status_map = {}
        try:
            if not ad_ids:
                return status_map
                
            logger.info(f"🔍 Fetching status for {len(ad_ids)} ads (optimized bulk query)...")
            
            # Use bulk query approach - much faster than individual calls
            batch_size = 100  # Larger batches for efficiency
            for i in range(0, len(ad_ids), batch_size):
                batch_ids = ad_ids[i:i + batch_size]
                
                try:
                    # Query ads in bulk using the account endpoint
                    ads_data = ad_account.get_ads(
                        fields=['id', 'effective_status'],
                        params={'ids': batch_ids}
                    )
                    
                    # Process bulk results
                    for ad_data in ads_data:
                        ad_id = ad_data.get('id', '')
                        status = ad_data.get('effective_status', 'UNKNOWN')
                        status_map[ad_id] = status
                        
                    logger.info(f"✅ Batch {i//batch_size + 1}: Got status for {len(batch_ids)} ads")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Batch {i//batch_size + 1} failed: {e}")
                    # Fallback: mark all ads in this batch as UNKNOWN
                    for ad_id in batch_ids:
                        status_map[ad_id] = 'UNKNOWN'
                
                # Small delay between batches to be respectful of API limits
                if i + batch_size < len(ad_ids):
                    time.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"❌ Error fetching ad status batch: {e}")
            # Fallback: mark all ads as UNKNOWN if bulk fails
            for ad_id in ad_ids:
                status_map[ad_id] = 'UNKNOWN'
            
        logger.info(f"📊 Status fetch complete: {len(status_map)} ads processed")
        return status_map
    
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
        Fetch ad-level insights for a specific account with weekly segmentation and rate limit handling
        """
        import time
        from facebook_business.exceptions import FacebookRequestError
        
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
                'limit': 500  # Reduced from 1000 to avoid rate limits
            }
            
            if campaigns:
                params['filtering'] = [
                    {
                        'field': 'campaign.id',
                        'operator': 'IN',
                        'value': campaigns
                    }
                ]
            
            # Rate limit handling with exponential backoff
            max_retries = 3
            base_delay = 60  # Start with 1 minute
            
            for attempt in range(max_retries + 1):
                try:
                    logger.info(f"🔄 API REQUEST: Fetching insights from {account_name} (attempt {attempt + 1})")
                    insights = ad_account.get_insights(params=params)
                    break  # Success, exit retry loop
                    
                except FacebookRequestError as e:
                    error_code = getattr(e, 'api_error_code', None)
                    error_subcode = getattr(e, 'api_error_subcode', None)
                    
                    # Rate limit error codes: 4, 17, 32, 613, 80004
                    if error_code in [4, 17, 32, 613, 80004] or 'rate limit' in str(e).lower():
                        if attempt < max_retries:
                            delay = base_delay * (2 ** attempt)  # Exponential backoff
                            logger.warning(f"⚠️ RATE LIMIT HIT: {account_name} - waiting {delay}s before retry {attempt + 1}/{max_retries}")
                            logger.warning(f"⚠️ Error details: Code {error_code}, Subcode {error_subcode}")
                            time.sleep(delay)
                            continue
                        else:
                            logger.error(f"❌ RATE LIMIT EXHAUSTED: {account_name} - all {max_retries} retries failed")
                            raise
                    else:
                        # Non-rate-limit error, don't retry
                        raise
            
            # TODO: Temporarily disable status fetching to avoid deployment timeouts
            # Will re-enable with better optimization after core sync is working
            logger.info(f"⏭️ Skipping status fetch for now - focusing on core sync performance")
            status_map = {}  # Empty status map - automation will use UNKNOWN status
            
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
                    'week_number': self._get_week_number(insight_start, insight_end),
                    'effective_status': status_map.get(ad_id, 'UNKNOWN')
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
        Fetch ad-level insights from Meta Ads API for the specified date range with rate limit protection
        """
        import time
        
        try:
            # Fetch from primary account
            logger.info("🔄 FETCHING PRIMARY ACCOUNT DATA")
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
                # Add delay between accounts to respect rate limits
                account_delay = 10  # 10 second delay between accounts
                logger.info(f"⏱️ ACCOUNT DELAY: Waiting {account_delay}s before fetching secondary account...")
                time.sleep(account_delay)
                
                logger.info("🔄 FETCHING SECONDARY ACCOUNT DATA")
                secondary_results = self._fetch_ad_insights_for_account(
                    self.secondary_ad_account,
                    f"Secondary ({self.secondary_account_id})",
                    start_date,
                    end_date,
                    campaigns
                )
            
            # Combine results from both accounts
            all_results = primary_results + secondary_results
            
            logger.info(f"✅ ACCOUNT DATA COMPLETE: {len(primary_results)} from primary, {len(secondary_results)} from secondary (total: {len(all_results)})")
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
        # Force Pacific timezone to avoid UTC/server timezone issues
        import pytz
        
        if target_date is None:
            # Get current date in Pacific timezone (where business operates)
            pacific_tz = pytz.timezone('US/Pacific')
            pacific_now = datetime.now(pacific_tz)
            target_date = pacific_now.date()
        
        # Yesterday is the end date (last full day) 
        end_date = target_date - timedelta(days=1)
        # Start date: 13 days before end_date (gives us 14 total days)
        start_date = end_date - timedelta(days=13)
        
        # Add explicit logging to debug date calculation
        logger.info(f"🗓️ DATE CALCULATION DEBUG:")
        logger.info(f"🗓️ Target date (today): {target_date}")
        logger.info(f"🗓️ End date (yesterday): {end_date}") 
        logger.info(f"🗓️ Start date (14 days back): {start_date}")
        logger.info(f"🗓️ Total days in range: {(end_date - start_date).days + 1}")
        logger.info(f"🗓️ Fetching last 14 days of ad-level data from {start_date} to {end_date} (weekly segments)")
        
        # Get ad insights data
        ad_data = self.get_ad_level_insights(start_date, end_date)
        
        # Extract unique ad IDs and fetch thumbnails
        ad_ids = list(set([ad['ad_id'] for ad in ad_data if ad.get('ad_id')]))
        logger.info(f"🖼️ THUMBNAIL DEBUG: Found {len(ad_ids)} unique ad IDs from {len(ad_data)} ad records")
        
        if ad_ids:
            logger.info(f"🖼️ Fetching thumbnails for {len(ad_ids)} unique ads")
            logger.info(f"🖼️ First 5 ad IDs: {ad_ids[:5]}")
            thumbnails = self.get_ad_thumbnails(ad_ids)
            
            # Add thumbnail data to ad data (enhanced structure)
            for ad in ad_data:
                ad_id = ad.get('ad_id')
                if ad_id and ad_id in thumbnails:
                    thumbnail_data = thumbnails[ad_id]
                    ad['thumbnail_url'] = thumbnail_data.get('thumbnail_url')  # For table display
                    ad['permalink_url'] = thumbnail_data.get('permalink_url')  # For hover high-res
                    ad['creative_type'] = thumbnail_data.get('creative_type', 'unknown')
                    ad['original_width'] = thumbnail_data.get('original_width', 0)
                    ad['original_height'] = thumbnail_data.get('original_height', 0)
                else:
                    ad['thumbnail_url'] = None
                    ad['permalink_url'] = None
                    ad['creative_type'] = 'unknown'
                    ad['original_width'] = 0
                    ad['original_height'] = 0
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
    
    def _upgrade_thumbnail_url(self, original_url: str, ad_id: str) -> str:
        """
        Try to upgrade a Facebook thumbnail URL to a larger size by manipulating URL parameters
        """
        import re
        
        try:
            # Facebook CDN URLs have size parameters we can modify
            # Common patterns:
            # 1. stp=dst-emg0_p64x64_q75 -> stp=dst-emg0_p320x320_q75 (increase size)
            # 2. _nc_ht=scontent-X.xx.fbcdn.net/v/...&oh=... -> try larger variants
            
            upgraded_url = original_url
            
            # Method 1: Replace p64x64 with larger sizes in stp parameter (most common)
            if 'p64x64' in original_url:
                # Try progressively larger sizes
                for target_size in ['p400x400', 'p320x320', 'p200x200']:
                    test_url = original_url.replace('p64x64', target_size)
                    if test_url != original_url:
                        logger.info(f"🔧 URL upgrade for ad {ad_id}: p64x64 → {target_size}")
                        upgraded_url = test_url
                        break
            
            # Method 2: For scontent URLs with dst-emg0 pattern
            elif 'scontent-' in original_url and 'dst-emg0_p64x64' in original_url:
                upgraded_url = re.sub(r'dst-emg0_p64x64_q\d+', 'dst-emg0_p400x400_q75', original_url)
                if upgraded_url != original_url:
                    logger.info(f"🔧 URL upgrade for ad {ad_id}: dst-emg0 p64x64 → p400x400")
            
            # Method 3: Handle the specific pattern from your URL
            elif 'stp=c0.5000x0.5000f_dst-emg0_p64x64' in original_url:
                upgraded_url = original_url.replace('stp=c0.5000x0.5000f_dst-emg0_p64x64', 'stp=c0.5000x0.5000f_dst-emg0_p400x400')
                if upgraded_url != original_url:
                    logger.info(f"🔧 URL upgrade for ad {ad_id}: stp parameter p64x64 → p400x400")
            
            # Method 4: Generic p64x64 replacement in stp parameters
            elif 'stp=' in original_url and 'p64x64' in original_url:
                upgraded_url = re.sub(r'p64x64', 'p400x400', original_url)
                if upgraded_url != original_url:
                    logger.info(f"🔧 URL upgrade for ad {ad_id}: generic p64x64 → p400x400")
            
            # Method 5: For other Facebook CDN patterns, try adding size parameters
            elif '.fbcdn.net' in original_url:
                if '&stp=' not in original_url and '?stp=' not in original_url:
                    separator = '&' if '?' in original_url else '?'
                    upgraded_url = f"{original_url}{separator}stp=dst-jpg_p400x400"
                    logger.info(f"🔧 URL upgrade for ad {ad_id}: added size parameter")
            
            return upgraded_url
            
        except Exception as e:
            logger.warning(f"Failed to upgrade thumbnail URL for ad {ad_id}: {e}")
            return original_url
    
    def get_ad_thumbnails(self, ad_ids: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Enhanced thumbnail system using ChatGPT's solution
        Fetches true high-resolution originals via AdImage permalink_url
        Returns dict mapping ad_id to {thumbnail_url, permalink_url, creative_type}
        """
        import time
        from facebook_business.exceptions import FacebookRequestError
        from facebook_business.adobjects.adimage import AdImage
        
        thumbnails = {}
        
        # STEP 1: Get account images with permalink_url (permanent high-res CDN URLs)
        account_images = {}
        try:
            logger.info(f"🖼️ Fetching account images with permalink_url for true high-res...")
            images = self.ad_account.get_ad_images(fields=[
                'id', 'hash', 'url', 'permalink_url', 'original_width', 'original_height'
            ], params={'limit': 500})
            
            for img in images:
                if 'hash' in img:
                    account_images[img['hash']] = {
                        'url': img.get('url'),  # Standard URL for table display
                        'permalink_url': img.get('permalink_url', img.get('url')),  # True high-res CDN
                        'original_width': img.get('original_width', 0),
                        'original_height': img.get('original_height', 0)
                    }
                    
            logger.info(f"✅ Loaded {len(account_images)} account images with permalink URLs")
        except Exception as e:
            logger.warning(f"⚠️ Could not load account images: {e}")
        
        # STEP 2: Process ads in batches with rate limit handling
        batch_size = 5
        batch_delay = 2
        
        for i in range(0, len(ad_ids), batch_size):
            batch = ad_ids[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(ad_ids) + batch_size - 1) // batch_size
            
            logger.info(f"🖼️ THUMBNAIL BATCH {batch_num}/{total_batches}: Processing {len(batch)} ads")
            
            for ad_id in batch:
                max_retries = 2
                base_delay = 30
                
                for attempt in range(max_retries + 1):
                    try:
                        ad = Ad(ad_id)
                        
                        # Get ad creatives with comprehensive fields for enhanced thumbnail system
                        creatives = ad.get_ad_creatives(fields=[
                            AdCreative.Field.thumbnail_url,      # Small thumbnail for table display
                            AdCreative.Field.image_hash,         # Key for permalink_url lookup
                            AdCreative.Field.object_story_spec,  # Video ID and link data detection
                            AdCreative.Field.video_id,           # For video thumbnail endpoint
                            AdCreative.Field.image_url,          # Alternative image source
                            AdCreative.Field.image_crops,        # Multiple size variants
                            'object_story_id',                   # Story post details
                            'effective_object_story_id',         # Effective story details  
                            'call_to_action_type',               # CTA indicates ad type
                            'asset_feed_spec',                   # Dynamic ads/catalog
                            'degrees_of_freedom_spec',           # Creative flexibility
                            'template_url',                      # Dynamic template
                            'title',                             # Ad title
                            'body'                               # Ad body text
                        ])
                        
                        if creatives and len(creatives) > 0:
                            creative = creatives[0]
                            
                            # DEBUG: Log available fields to understand what Facebook returns
                            available_fields = list(creative.keys())
                            logger.debug(f"🔍 Ad {ad_id} creative fields: {available_fields}")
                            
                            thumbnail_data = {
                                'thumbnail_url': None,     # For table display
                                'permalink_url': None,     # For hover high-res
                                'creative_type': 'unknown',
                                'original_width': 0,
                                'original_height': 0
                            }
                            resolution_info = "unknown"
                            
                            # STEP 1: Detect creative type (EXPANDED DETECTION)
                            creative_type_detected = False
                            
                            # Check for video first
                            if 'video_id' in creative and creative['video_id']:
                                thumbnail_data['creative_type'] = 'video'
                                logger.debug(f"🎬 Ad {ad_id} is VIDEO type (video_id: {creative['video_id']})")
                                creative_type_detected = True
                            elif 'object_story_spec' in creative:
                                story_spec = creative['object_story_spec']
                                # Check for video data first
                                if any(key in story_spec for key in ['video_data', 'video']):
                                    thumbnail_data['creative_type'] = 'video'
                                    logger.debug(f"🎬 Ad {ad_id} is VIDEO type from story_spec")
                                    creative_type_detected = True
                                # Check for carousel/collection (link_data with child_attachments)
                                elif ('link_data' in story_spec and 
                                      'child_attachments' in story_spec['link_data'] and 
                                      len(story_spec['link_data']['child_attachments']) > 1):
                                    thumbnail_data['creative_type'] = 'carousel'
                                    logger.debug(f"🎠 Ad {ad_id} is CAROUSEL type ({len(story_spec['link_data']['child_attachments'])} items)")
                                    creative_type_detected = True
                                # Check for single collection/dynamic product
                                elif 'link_data' in story_spec:
                                    thumbnail_data['creative_type'] = 'dynamic_product' 
                                    logger.debug(f"🏪 Ad {ad_id} is DYNAMIC_PRODUCT type")
                                    creative_type_detected = True
                            
                            # Check for dynamic/catalog ads using asset_feed_spec
                            if not creative_type_detected and 'asset_feed_spec' in creative:
                                thumbnail_data['creative_type'] = 'dynamic_product'
                                logger.debug(f"🏪 Ad {ad_id} is DYNAMIC_PRODUCT type (asset_feed_spec)")
                                creative_type_detected = True
                            
                            # Check template_url for dynamic ads
                            if not creative_type_detected and 'template_url' in creative and creative['template_url']:
                                thumbnail_data['creative_type'] = 'dynamic_product'
                                logger.debug(f"🏪 Ad {ad_id} is DYNAMIC_PRODUCT type (template_url)")
                                creative_type_detected = True
                                
                            # Fallback to static_image
                            if not creative_type_detected:
                                thumbnail_data['creative_type'] = 'static_image'
                                logger.debug(f"🖼️ Ad {ad_id} is STATIC_IMAGE type (fallback - no video/dynamic indicators found)")
                            
                            # STEP 2: Get permalink_url for static images (ChatGPT's solution)
                            if thumbnail_data['creative_type'] == 'static_image' and 'image_hash' in creative:
                                image_hash = creative['image_hash']
                                if image_hash in account_images:
                                    account_image = account_images[image_hash]
                                    thumbnail_data['thumbnail_url'] = account_image['url']  # Table display
                                    thumbnail_data['permalink_url'] = account_image['permalink_url']  # Hover high-res
                                    thumbnail_data['original_width'] = account_image['original_width']
                                    thumbnail_data['original_height'] = account_image['original_height']
                                    resolution_info = f"permalink_url_{account_image['original_width']}x{account_image['original_height']}"
                                    logger.info(f"✅ PERMALINK: Using permalink_url for static ad {ad_id} ({account_image['original_width']}x{account_image['original_height']})")
                            
                            # STEP 3: Fallback to image_crops for enhanced resolution
                            if not thumbnail_data['thumbnail_url'] and 'image_crops' in creative and creative['image_crops']:
                                image_crops = creative['image_crops']
                                available_sizes = list(image_crops.keys())
                                logger.debug(f"🎯 Ad {ad_id} image_crops available: {available_sizes}")
                                
                                # Try progressively larger sizes
                                for target_size in ['1080x1080', '600x600', '400x400', '320x320', '192x192']:
                                    if target_size in image_crops:
                                        thumbnail_data['thumbnail_url'] = image_crops[target_size]['source']
                                        resolution_info = f"image_crops_{target_size}"
                                        logger.info(f"✅ HIGH-RES CROPS: Using {target_size} crop for ad {ad_id}")
                                        break
                            
                            # STEP 4: Video thumbnail fetching (ChatGPT's solution)
                            if thumbnail_data['creative_type'] == 'video' and 'video_id' in creative and creative['video_id']:
                                try:
                                    from facebook_business.adobjects.advideo import AdVideo
                                    video = AdVideo(creative['video_id'])
                                    video_thumbnails = video.get_thumbnails()
                                    
                                    if video_thumbnails:
                                        # Find the largest thumbnail
                                        best_thumbnail = None
                                        max_size = 0
                                        
                                        for thumb in video_thumbnails:
                                            width = thumb.get('width', 0)
                                            height = thumb.get('height', 0)
                                            size = width * height
                                            
                                            if size > max_size:
                                                max_size = size
                                                best_thumbnail = thumb
                                        
                                        if best_thumbnail:
                                            thumbnail_data['thumbnail_url'] = best_thumbnail.get('uri')
                                            thumbnail_data['permalink_url'] = best_thumbnail.get('uri')  # Same for video
                                            thumbnail_data['original_width'] = best_thumbnail.get('width', 0)
                                            thumbnail_data['original_height'] = best_thumbnail.get('height', 0)
                                            resolution_info = f"video_thumbnail_{thumbnail_data['original_width']}x{thumbnail_data['original_height']}"
                                            logger.info(f"✅ VIDEO: Using video thumbnail for ad {ad_id} ({thumbnail_data['original_width']}x{thumbnail_data['original_height']})")
                                
                                except Exception as e:
                                    logger.warning(f"⚠️ Could not fetch video thumbnail for ad {ad_id}: {e}")
                            
                            # STEP 4B: Carousel/Dynamic Product thumbnail handling
                            if thumbnail_data['creative_type'] in ['carousel', 'dynamic_product'] and 'object_story_spec' in creative:
                                story_spec = creative['object_story_spec']
                                if 'link_data' in story_spec:
                                    link_data = story_spec['link_data']
                                    
                                    # Try to get the best thumbnail from carousel/collection
                                    if 'child_attachments' in link_data and len(link_data['child_attachments']) > 0:
                                        # Use first child attachment thumbnail
                                        first_child = link_data['child_attachments'][0]
                                        if 'picture' in first_child:
                                            thumbnail_data['thumbnail_url'] = first_child['picture']
                                            thumbnail_data['permalink_url'] = first_child['picture']  # Same URL for collections
                                            resolution_info = f"carousel_child_thumbnail"
                                            logger.info(f"🎠 CAROUSEL: Using child thumbnail for ad {ad_id}")
                                    elif 'picture' in link_data:
                                        # Single collection/dynamic product
                                        thumbnail_data['thumbnail_url'] = link_data['picture']
                                        thumbnail_data['permalink_url'] = link_data['picture']
                                        resolution_info = f"dynamic_product_thumbnail"
                                        logger.info(f"🏪 DYNAMIC_PRODUCT: Using link_data picture for ad {ad_id}")
                            
                            # STEP 4C: Enhanced image_crops handling for all types
                            if not thumbnail_data['thumbnail_url'] and 'image_crops' in creative and creative['image_crops']:
                                image_crops = creative['image_crops']
                                available_sizes = list(image_crops.keys())
                                logger.debug(f"🎯 Ad {ad_id} image_crops available: {available_sizes}")
                                
                                # Find the largest available crop
                                best_size = None
                                max_pixels = 0
                                
                                for size_key in image_crops.keys():
                                    try:
                                        # Parse dimensions from size key (e.g., "1080x1080")
                                        if 'x' in size_key:
                                            w, h = map(int, size_key.split('x'))
                                            pixels = w * h
                                            if pixels > max_pixels:
                                                max_pixels = pixels
                                                best_size = size_key
                                    except:
                                        continue
                                
                                if best_size and best_size in image_crops:
                                    crop_data = image_crops[best_size]
                                    thumbnail_data['thumbnail_url'] = crop_data['source']
                                    thumbnail_data['permalink_url'] = crop_data['source']  # Use same high-res source
                                    
                                    # Try to extract dimensions
                                    try:
                                        w, h = map(int, best_size.split('x'))
                                        thumbnail_data['original_width'] = w
                                        thumbnail_data['original_height'] = h
                                    except:
                                        pass
                                    
                                    resolution_info = f"image_crops_{best_size}"
                                    logger.info(f"✅ HIGH-RES CROPS: Using {best_size} crop for ad {ad_id} ({max_pixels:,} pixels)")
                                else:
                                    logger.debug(f"⚠️ No valid image_crops found for ad {ad_id}")
                            
                            # STEP 5: object_story_spec.link_data.picture (often high-res)
                            if not thumbnail_data['thumbnail_url'] and 'object_story_spec' in creative:
                                story_spec = creative['object_story_spec']
                                if 'link_data' in story_spec and 'picture' in story_spec['link_data']:
                                    thumbnail_data['thumbnail_url'] = story_spec['link_data']['picture']
                                    thumbnail_data['permalink_url'] = story_spec['link_data']['picture']  # Same for dynamic products
                                    resolution_info = "story_spec_picture"
                                    logger.info(f"✅ STORY: Using object_story_spec picture for ad {ad_id}")
                            
                            # STEP 6: image_url fallback (may be larger than thumbnail_url)
                            if not thumbnail_data['thumbnail_url'] and 'image_url' in creative:
                                thumbnail_data['thumbnail_url'] = creative['image_url']
                                thumbnail_data['permalink_url'] = creative['image_url']
                                resolution_info = "image_url"
                                logger.info(f"✅ IMAGE_URL: Using image_url for ad {ad_id}")
                            
                            # STEP 7: thumbnail_url (64x64 fallback) - NO URL PARAMETER MODIFICATION
                            if not thumbnail_data['thumbnail_url'] and 'thumbnail_url' in creative:
                                thumbnail_data['thumbnail_url'] = creative['thumbnail_url']
                                # Use same URL for both - avoid signature mismatch by not modifying URLs
                                thumbnail_data['permalink_url'] = creative['thumbnail_url']
                                resolution_info = "thumbnail_url_64x64_safe"
                                logger.warning(f"⚠️ FALLBACK: Using original 64x64 thumbnail_url for ad {ad_id} (no enhancement possible)")
                            
                            if thumbnail_data['thumbnail_url']:
                                thumbnails[ad_id] = thumbnail_data
                                logger.debug(f"📸 Ad {ad_id} thumbnail ({resolution_info}): {thumbnail_data['thumbnail_url'][:100]}...")
                            else:
                                logger.warning(f"❌ No thumbnail found for ad {ad_id}")
                        else:
                            logger.warning(f"❌ No creatives found for ad {ad_id}")
                        
                        break  # Success, exit retry loop
                        
                    except FacebookRequestError as e:
                        error_code = getattr(e, 'api_error_code', None)
                        
                        # Rate limit error codes
                        if error_code in [4, 17, 32, 613, 80004] or 'rate limit' in str(e).lower():
                            if attempt < max_retries:
                                delay = base_delay * (2 ** attempt)
                                logger.warning(f"⚠️ THUMBNAIL RATE LIMIT: ad {ad_id} - waiting {delay}s (attempt {attempt + 1})")
                                time.sleep(delay)
                                continue
                            else:
                                logger.warning(f"❌ THUMBNAIL RATE LIMIT EXHAUSTED: ad {ad_id} - skipping")
                                break
                        else:
                            logger.warning(f"Facebook API error fetching creative for ad {ad_id}: {e}")
                            break
                    except Exception as e:
                        logger.warning(f"Error fetching creative for ad {ad_id}: {e}")
                        break
            
            # Add delay between batches to respect rate limits
            if i + batch_size < len(ad_ids):  # Don't delay after the last batch
                logger.info(f"⏱️ Waiting {batch_delay}s between thumbnail batches...")
                time.sleep(batch_delay)
        
        logger.info(f"Retrieved {len(thumbnails)} thumbnails out of {len(ad_ids)} requested ads")
        return thumbnails