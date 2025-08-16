import os
import json
import requests
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from loguru import logger

try:
    # Try importing official TikTok Business API if available
    from tiktok_business_api_sdk import TikTokBusinessClient
    TIKTOK_SDK_AVAILABLE = True
except ImportError:
    TIKTOK_SDK_AVAILABLE = False
    logger.warning("TikTok Business API SDK not available. Install with: pip install TikTok-Business-API")

from ..models.tiktok_campaign_data import (
    TikTokAdsInsight,
    TikTokCampaignData,
    TikTokCredentials,
    TikTokQuery,
    TikTokApiResponse,
    TikTokReportRequest
)
from ..services.categorization import CategorizationService

class TikTokAdsService:
    """Service for TikTok Ads API integration"""
    
    def __init__(self):
        self.app_id = os.getenv("TIKTOK_APP_ID")
        self.app_secret = os.getenv("TIKTOK_APP_SECRET")
        self.access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        self.advertiser_id = os.getenv("TIKTOK_ADVERTISER_ID")
        self.client_key = os.getenv("TIKTOK_CLIENT_KEY")
        self.sandbox_mode = os.getenv("TIKTOK_SANDBOX_MODE", "false").lower() == "true"
        
        if not all([self.app_id, self.app_secret, self.access_token, self.advertiser_id]):
            raise ValueError("Missing required TikTok Ads API credentials")
        
        # Base API URLs
        self.base_url = "https://business-api.tiktok.com/open_api/v1.3" if not self.sandbox_mode else "https://sandbox-ads.tiktok.com/open_api/v1.3"
        self.oauth_url = "https://business-api.tiktok.com/open_api/v1.3/oauth2"
        
        # Initialize categorization service
        self.categorization_service = CategorizationService()
        
        # Set up session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            "Access-Token": self.access_token,
            "Content-Type": "application/json"
        })
        
        logger.info(f"TikTok Ads Service initialized {'(sandbox mode)' if self.sandbox_mode else '(production)'}")
    
    def test_connection(self) -> bool:
        """Test TikTok Ads API connection"""
        try:
            # Use advertiser info endpoint to test connection
            endpoint = f"{self.base_url}/advertiser/info/"
            params = {
                "advertiser_ids": json.dumps([self.advertiser_id])
            }
            
            response = self.session.get(endpoint, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:  # TikTok API success code
                    logger.info("TikTok Ads API connection successful")
                    return True
                else:
                    logger.error(f"TikTok API error: {data.get('message', 'Unknown error')}")
                    return False
            else:
                logger.error(f"TikTok API HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"TikTok Ads connection test failed: {e}")
            return False
    
    def get_campaign_insights(
        self, 
        start_date: date, 
        end_date: date,
        campaign_ids: Optional[List[str]] = None
    ) -> List[TikTokAdsInsight]:
        """
        Fetch campaign insights from TikTok Ads API for the specified date range
        """
        try:
            endpoint = f"{self.base_url}/report/integrated/get/"
            
            # Build request payload
            request_data = {
                "advertiser_id": self.advertiser_id,
                "report_type": "BASIC",
                "data_level": "AUCTION_CAMPAIGN",
                "dimensions": ["campaign_id"],
                "metrics": [
                    "spend",
                    "impressions", 
                    "clicks",
                    "ctr",
                    "cpc",
                    "cpm",
                    "cost_per_conversion",
                    "conversion_rate",
                    "complete_payment_roas",  # Payment Complete ROAS (website)
                    "complete_payment",       # Number of complete payments
                    "purchase"               # Purchase events
                ],
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "page": 1,
                "page_size": 1000
            }
            
            # Add campaign filter if specified
            if campaign_ids:
                request_data["filters"] = [{
                    "field_name": "campaign_id",
                    "filter_type": "IN",
                    "filter_value": campaign_ids
                }]
            
            logger.info(f"Fetching TikTok campaign insights for {start_date} to {end_date}")
            logger.debug(f"Request payload: {request_data}")
            
            # Convert to query parameters for GET request
            params = {}
            for key, value in request_data.items():
                if isinstance(value, list):
                    params[key] = json.dumps(value)
                else:
                    params[key] = value
            
            response = self.session.get(endpoint, params=params)
            
            if response.status_code != 200:
                logger.error(f"TikTok API HTTP error: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            
            if data.get("code") != 0:
                logger.error(f"TikTok API error: {data.get('message', 'Unknown error')}")
                return []
            
            insights = []
            
            # Process the response data
            if "data" in data and "list" in data["data"]:
                for item in data["data"]["list"]:
                    try:
                        # Get campaign info - may need separate API call
                        campaign_info = self._get_campaign_info(item.get("dimensions", {}).get("campaign_id"))
                        campaign_name = campaign_info.get("campaign_name", f"Campaign {item.get('dimensions', {}).get('campaign_id')}")
                        
                        # Extract metrics
                        metrics = item.get("metrics", {})
                        
                        insight = TikTokAdsInsight(
                            campaign_id=str(item.get("dimensions", {}).get("campaign_id", "")),
                            campaign_name=campaign_name,
                            spend=str(metrics.get("spend", 0)),
                            impressions=str(metrics.get("impressions", 0)),
                            clicks=str(metrics.get("clicks", 0)),
                            date_start=start_date.strftime('%Y-%m-%d'),
                            date_stop=end_date.strftime('%Y-%m-%d'),
                            ctr=str(metrics.get("ctr", 0)),
                            cpc=str(metrics.get("cpc", 0)),
                            cpm=str(metrics.get("cpm", 0)),
                            cost_per_conversion=str(metrics.get("cost_per_conversion", 0)),
                            conversion_rate=str(metrics.get("conversion_rate", 0)),
                            # Payment Complete ROAS (website) - the correct ROAS metric
                            complete_payment_roas=str(metrics.get("complete_payment_roas", 0)),
                            complete_payment=str(metrics.get("complete_payment", 0)),
                            purchase=str(metrics.get("purchase", 0)),
                            # Legacy compatibility
                            conversions=str(metrics.get("complete_payment", 0)),  # Use complete_payment as conversions
                            conversion_value="0"  # Will calculate from ROAS and spend
                        )
                        insights.append(insight)
                        
                    except Exception as e:
                        logger.error(f"Failed to process TikTok insight item: {e}")
                        continue
            
            logger.info(f"Retrieved {len(insights)} TikTok campaigns for {start_date} to {end_date}")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get TikTok campaign insights: {e}")
            return []
    
    def _get_campaign_info(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign information including name"""
        try:
            endpoint = f"{self.base_url}/campaign/get/"
            params = {
                "advertiser_id": self.advertiser_id,
                "campaign_ids": json.dumps([campaign_id])
            }
            
            response = self.session.get(endpoint, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0 and data.get("data", {}).get("list"):
                    return data["data"]["list"][0]
            
            # Return default if API call fails
            return {"campaign_name": f"Campaign {campaign_id}"}
            
        except Exception as e:
            logger.error(f"Failed to get TikTok campaign info for {campaign_id}: {e}")
            return {"campaign_name": f"Campaign {campaign_id}"}
    
    def convert_to_campaign_data(self, insights: List[TikTokAdsInsight]) -> List[TikTokCampaignData]:
        """
        Convert TikTok Ads insights to standardized campaign data format
        """
        campaign_data_list = []
        
        for insight in insights:
            try:
                # Parse metrics (TikTok returns in dollars, not micros like Google)
                amount_spent = Decimal(insight.spend)
                purchases = int(float(insight.complete_payment))  # Use complete_payment instead of conversions
                impressions = int(insight.impressions)
                clicks = int(insight.clicks)  # TikTok clicks are destination clicks
                
                # Use Payment Complete ROAS (website) - the correct TikTok ROAS metric
                roas = Decimal(insight.complete_payment_roas)
                
                # Calculate purchase value from ROAS and spend
                purchase_value = (roas * amount_spent).quantize(Decimal('0.01')) if amount_spent > 0 else Decimal('0')
                
                # Calculate derived metrics with proper rounding
                cpa = (amount_spent / purchases).quantize(Decimal('0.01')) if purchases > 0 else Decimal('0')
                cpc = (amount_spent / clicks).quantize(Decimal('0.0001')) if clicks > 0 else Decimal('0')
                
                # Auto-categorize campaign using existing system
                category = self.categorization_service.categorize_campaign(
                    insight.campaign_name, 
                    insight.campaign_id
                )
                
                campaign_data = TikTokCampaignData(
                    campaign_id=insight.campaign_id,
                    campaign_name=insight.campaign_name,
                    category=category,
                    reporting_starts=datetime.strptime(insight.date_start, '%Y-%m-%d').date(),
                    reporting_ends=datetime.strptime(insight.date_stop, '%Y-%m-%d').date(),
                    amount_spent_usd=amount_spent,
                    website_purchases=purchases,
                    purchases_conversion_value=purchase_value,
                    impressions=impressions,
                    link_clicks=clicks,  # TikTok destination clicks = link clicks
                    cpa=cpa,
                    roas=roas,
                    cpc=cpc
                )
                
                campaign_data_list.append(campaign_data)
                
            except Exception as e:
                logger.error(f"Failed to convert TikTok insight for campaign {insight.campaign_id}: {e}")
                continue
        
        logger.info(f"Converted {len(campaign_data_list)} TikTok campaigns to campaign data")
        return campaign_data_list
    
    def get_campaigns(self, enabled_only: bool = True) -> List[dict]:
        """Get list of campaigns from TikTok Ads account"""
        try:
            endpoint = f"{self.base_url}/campaign/get/"
            params = {
                "advertiser_id": self.advertiser_id,
                "page": 1,
                "page_size": 1000
            }
            
            if enabled_only:
                params["filters"] = json.dumps([{
                    "field_name": "primary_status",
                    "filter_type": "EQUALS",
                    "filter_value": "STATUS_ENABLE"
                }])
            
            response = self.session.get(endpoint, params=params)
            
            if response.status_code != 200:
                logger.error(f"Failed to get TikTok campaigns: HTTP {response.status_code}")
                return []
            
            data = response.json()
            
            if data.get("code") != 0:
                logger.error(f"TikTok API error: {data.get('message', 'Unknown error')}")
                return []
            
            campaigns = []
            
            if "data" in data and "list" in data["data"]:
                for campaign in data["data"]["list"]:
                    campaigns.append({
                        'id': str(campaign.get('campaign_id', '')),
                        'name': campaign.get('campaign_name', ''),
                        'status': campaign.get('primary_status', 'UNKNOWN'),
                        'objective': campaign.get('objective_type', ''),
                        'budget': campaign.get('budget', 0)
                    })
            
            logger.info(f"Retrieved {len(campaigns)} TikTok campaigns")
            return campaigns
            
        except Exception as e:
            logger.error(f"Failed to get TikTok campaigns: {e}")
            return []
    
    def refresh_access_token(self) -> bool:
        """Refresh TikTok access token if needed"""
        try:
            # TikTok token refresh logic would go here
            # This depends on your specific OAuth implementation
            logger.warning("TikTok token refresh not implemented - tokens need manual renewal")
            return False
        except Exception as e:
            logger.error(f"Failed to refresh TikTok token: {e}")
            return False