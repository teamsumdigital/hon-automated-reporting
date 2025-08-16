import os
from typing import List, Optional
from datetime import date, datetime, timedelta
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.exceptions import FacebookRequestError
from loguru import logger
from ..models.campaign_data import MetaAdsInsight, CampaignData
from decimal import Decimal

class MetaAdsService:
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
        
        # Initialize secondary account if configured
        self.secondary_ad_account = None
        if self.secondary_account_id:
            self.secondary_ad_account = AdAccount(f"act_{self.secondary_account_id}")
            logger.info(f"Initialized dual Meta Ads accounts: {self.account_id} and {self.secondary_account_id}")
        else:
            logger.info(f"Initialized single Meta Ads account: {self.account_id}")
    
    def _apply_august_2025_limit(self, start_date: date, end_date: date) -> tuple[date, date]:
        """
        Apply August 11, 2025 limit for backfill testing
        """
        # If we're fetching August 2025 data, limit to August 11
        if start_date.year == 2025 and start_date.month == 8:
            august_11_2025 = date(2025, 8, 11)
            if end_date > august_11_2025:
                logger.info(f"Limiting August 2025 backfill from {end_date} to {august_11_2025} for testing")
                end_date = august_11_2025
        return start_date, end_date
    
    def _fetch_account_insights(
        self,
        ad_account: AdAccount,
        account_name: str,
        start_date: date,
        end_date: date,
        campaigns: Optional[List[str]] = None
    ) -> List[MetaAdsInsight]:
        """
        Fetch insights for a specific ad account
        """
        try:
            params = {
                'time_range': {
                    'since': start_date.strftime('%Y-%m-%d'),
                    'until': end_date.strftime('%Y-%m-%d')
                },
                'fields': [
                    'campaign_id',
                    'campaign_name',
                    'spend',
                    'actions',
                    'action_values',
                    'impressions',
                    'clicks',
                    'cpm',
                    'cpc',
                    'ctr'
                ],
                'level': 'campaign',
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
                purchases = "0"
                purchase_value = "0"
                link_clicks = "0"
                
                if 'actions' in insight and insight['actions']:
                    for action in insight['actions']:
                        if action.get('action_type') == 'purchase':
                            purchases = action.get('value', '0')
                        elif action.get('action_type') == 'link_click':
                            link_clicks = action.get('value', '0')
                
                if 'action_values' in insight and insight['action_values']:
                    for action_value in insight['action_values']:
                        if action_value.get('action_type') == 'purchase':
                            purchase_value = action_value.get('value', '0')
                            break
                
                # Calculate ROAS from spend and revenue
                spend_val = float(insight.get('spend', '0'))
                revenue_val = float(purchase_value)
                roas_value = revenue_val / spend_val if spend_val > 0 else 0
                
                meta_insight = MetaAdsInsight(
                    campaign_id=insight.get('campaign_id', ''),
                    campaign_name=insight.get('campaign_name', ''),
                    spend=insight.get('spend', '0'),
                    purchases=purchases,
                    purchase_roas=[{'value': str(roas_value)}] if roas_value > 0 else [],
                    impressions=insight.get('impressions', '0'),
                    clicks=insight.get('clicks', '0'),
                    link_clicks=link_clicks,
                    cpm=insight.get('cpm', '0'),
                    cpc=insight.get('cpc', '0'),
                    ctr=insight.get('ctr', '0'),
                    date_start=start_date.strftime('%Y-%m-%d'),
                    date_stop=end_date.strftime('%Y-%m-%d')
                )
                results.append(meta_insight)
            
            logger.info(f"Retrieved {len(results)} campaign insights from {account_name} for {start_date} to {end_date}")
            return results
            
        except FacebookRequestError as e:
            logger.error(f"Facebook API error for account {account_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching campaign insights from {account_name}: {e}")
            raise
    
    def get_campaign_insights(
        self, 
        start_date: date, 
        end_date: date,
        campaigns: Optional[List[str]] = None
    ) -> List[MetaAdsInsight]:
        """
        Fetch campaign insights from Meta Ads API for the specified date range
        Now supports dual accounts and August 2025 testing limitations
        """
        try:
            # Apply August 2025 limitation for testing
            start_date, end_date = self._apply_august_2025_limit(start_date, end_date)
            
            # Fetch from primary account
            primary_results = self._fetch_account_insights(
                self.ad_account, 
                f"Primary ({self.account_id})", 
                start_date, 
                end_date, 
                campaigns
            )
            
            # Fetch from secondary account if configured
            secondary_results = []
            if self.secondary_ad_account:
                secondary_results = self._fetch_account_insights(
                    self.secondary_ad_account,
                    f"Secondary ({self.secondary_account_id})",
                    start_date,
                    end_date,
                    campaigns
                )
            
            # Combine results from both accounts
            all_results = primary_results + secondary_results
            
            logger.info(f"Retrieved {len(primary_results)} insights from primary account, {len(secondary_results)} from secondary account (total: {len(all_results)})")
            return all_results
            
        except FacebookRequestError as e:
            logger.error(f"Facebook API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching campaign insights: {e}")
            raise
    
    def convert_to_campaign_data(self, insights: List[MetaAdsInsight]) -> List[CampaignData]:
        """
        Convert Meta Ads insights to CampaignData models
        """
        campaign_data_list = []
        
        for insight in insights:
            try:
                # Calculate metrics
                spend = Decimal(insight.spend).quantize(Decimal('0.01')) if insight.spend else Decimal('0')
                purchases = int(float(insight.purchases)) if insight.purchases else 0
                impressions = int(insight.impressions) if insight.impressions else 0
                
                # Get link clicks from the insight object
                link_clicks = int(insight.link_clicks) if insight.link_clicks else 0
                
                # Calculate ROAS from purchase_roas
                roas = Decimal('0')
                if insight.purchase_roas:
                    roas_data = insight.purchase_roas[0] if isinstance(insight.purchase_roas, list) else insight.purchase_roas
                    if isinstance(roas_data, dict) and 'value' in roas_data:
                        roas = Decimal(str(roas_data['value'])).quantize(Decimal('0.0001'))
                
                # Calculate revenue from ROAS and spend
                revenue = (spend * roas).quantize(Decimal('0.01')) if roas > 0 else Decimal('0')
                
                # Calculate CPA
                cpa = (spend / purchases).quantize(Decimal('0.01')) if purchases > 0 else Decimal('0')
                
                # Calculate CPC using link clicks
                cpc = (spend / link_clicks).quantize(Decimal('0.0001')) if link_clicks > 0 else Decimal('0')
                
                campaign_data = CampaignData(
                    campaign_id=insight.campaign_id,
                    campaign_name=insight.campaign_name,
                    reporting_starts=datetime.strptime(insight.date_start, '%Y-%m-%d').date(),
                    reporting_ends=datetime.strptime(insight.date_stop, '%Y-%m-%d').date(),
                    amount_spent_usd=spend,
                    website_purchases=purchases,
                    purchases_conversion_value=revenue,
                    impressions=impressions,
                    link_clicks=link_clicks,
                    cpa=cpa,
                    roas=roas,
                    cpc=cpc
                )
                campaign_data_list.append(campaign_data)
                
            except Exception as e:
                logger.error(f"Error converting insight for campaign {insight.campaign_id}: {e}")
                continue
        
        return campaign_data_list
    
    def get_month_to_date_data(self, target_date: Optional[date] = None) -> List[CampaignData]:
        """
        Get month-to-date campaign data for the specified date (or current date)
        """
        if target_date is None:
            target_date = date.today()
        
        # Calculate start of month and end date (target_date - 1 day for weekly reports)
        start_of_month = target_date.replace(day=1)
        end_date = target_date - timedelta(days=1)
        
        logger.info(f"Fetching month-to-date data from {start_of_month} to {end_date}")
        
        insights = self.get_campaign_insights(start_of_month, end_date)
        return self.convert_to_campaign_data(insights)
    
    def test_connection(self) -> bool:
        """
        Test the Meta Ads API connection for both accounts
        """
        try:
            # Test primary account
            primary_account_info = self.ad_account.api_get(fields=['name', 'account_status'])
            logger.info(f"Connected to primary account: {primary_account_info.get('name', 'Unknown')} (ID: {self.account_id})")
            
            # Test secondary account if configured
            if self.secondary_ad_account:
                secondary_account_info = self.secondary_ad_account.api_get(fields=['name', 'account_status'])
                logger.info(f"Connected to secondary account: {secondary_account_info.get('name', 'Unknown')} (ID: {self.secondary_account_id})")
            
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False