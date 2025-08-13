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
        
        if not all([self.app_id, self.app_secret, self.access_token, self.account_id]):
            raise ValueError("Missing required Meta Ads API credentials")
        
        FacebookAdsApi.init(access_token=self.access_token)
        self.ad_account = AdAccount(f"act_{self.account_id}")
    
    def get_campaign_insights(
        self, 
        start_date: date, 
        end_date: date,
        campaigns: Optional[List[str]] = None
    ) -> List[MetaAdsInsight]:
        """
        Fetch campaign insights from Meta Ads API for the specified date range
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
            
            insights = self.ad_account.get_insights(params=params)
            
            results = []
            for insight in insights:
                # Extract purchases from actions array
                purchases = "0"
                purchase_value = "0"
                
                if 'actions' in insight and insight['actions']:
                    for action in insight['actions']:
                        if action.get('action_type') == 'purchase':
                            purchases = action.get('value', '0')
                            break
                
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
                    cpm=insight.get('cpm', '0'),
                    cpc=insight.get('cpc', '0'),
                    ctr=insight.get('ctr', '0'),
                    date_start=start_date.strftime('%Y-%m-%d'),
                    date_stop=end_date.strftime('%Y-%m-%d')
                )
                results.append(meta_insight)
            
            logger.info(f"Retrieved {len(results)} campaign insights for {start_date} to {end_date}")
            return results
            
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
                clicks = int(insight.clicks) if insight.clicks else 0
                
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
                
                # Calculate CPC
                cpc = (spend / clicks).quantize(Decimal('0.0001')) if clicks > 0 else Decimal('0')
                
                campaign_data = CampaignData(
                    campaign_id=insight.campaign_id,
                    campaign_name=insight.campaign_name,
                    reporting_starts=datetime.strptime(insight.date_start, '%Y-%m-%d').date(),
                    reporting_ends=datetime.strptime(insight.date_stop, '%Y-%m-%d').date(),
                    amount_spent_usd=spend,
                    website_purchases=purchases,
                    purchases_conversion_value=revenue,
                    impressions=impressions,
                    link_clicks=clicks,
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
        Test the Meta Ads API connection
        """
        try:
            # Simple test to get account info
            account_info = self.ad_account.api_get(fields=['name', 'account_status'])
            logger.info(f"Connected to account: {account_info.get('name', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False