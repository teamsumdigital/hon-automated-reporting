import os
from typing import List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from loguru import logger

try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    GOOGLE_ADS_AVAILABLE = True
except ImportError:
    GOOGLE_ADS_AVAILABLE = False
    logger.warning("Google Ads library not available. Install with: pip install google-ads")

try:
    from ..models.google_campaign_data import (
        GoogleAdsInsight, 
        GoogleCampaignData
    )
except ImportError:
    # Create basic models inline if imports fail
    from pydantic import BaseModel
    
    class GoogleAdsInsight(BaseModel):
        campaign_id: str
        campaign_name: str
        cost: str = "0"
        cost_micros: str = "0"
        conversions: str = "0"
        conversions_value: str = "0"
        impressions: str = "0"
        clicks: str = "0"
        date_start: str
        date_stop: str
    
    class GoogleCampaignData(BaseModel):
        campaign_id: str
        campaign_name: str
        category: Optional[str] = None
        campaign_type: Optional[str] = None
        reporting_starts: date
        reporting_ends: date
        amount_spent_usd: Decimal = Decimal('0')
        website_purchases: int = 0
        purchases_conversion_value: Decimal = Decimal('0')
        impressions: int = 0
        link_clicks: int = 0
        cpa: Decimal = Decimal('0')
        roas: Decimal = Decimal('0')
        cpc: Decimal = Decimal('0')

try:
    from ..services.categorization import CategorizationService
    from ..services.campaign_type_service import CampaignTypeService
except ImportError:
    # Mock categorization service
    class CategorizationService:
        def categorize_campaign(self, campaign_name: str) -> str:
            return "Uncategorized"
    
    # Mock campaign type service
    class CampaignTypeService:
        def classify_campaign_type(self, campaign_name: str) -> str:
            return "Unclassified"

class GoogleAdsService:
    """Service for Google Ads API integration"""
    
    def __init__(self):
        if not GOOGLE_ADS_AVAILABLE:
            raise ImportError("Google Ads library not available. Install with: pip install google-ads")
            
        self.developer_token = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
        self.client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID") 
        self.client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
        self.refresh_token = os.getenv("GOOGLE_OAUTH_REFRESH_TOKEN")
        self.customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
        self.login_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")  # Optional for manager accounts
        
        if not all([self.developer_token, self.client_id, self.client_secret, self.refresh_token, self.customer_id]):
            raise ValueError("Missing required Google Ads API credentials")
        
        # Initialize Google Ads client
        try:
            # Create client configuration
            client_config = {
                "developer_token": self.developer_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "use_proto_plus": True  # Required by Google Ads client library
            }
            
            # Add login_customer_id only if provided
            if self.login_customer_id:
                client_config["login_customer_id"] = self.login_customer_id
            
            self.client = GoogleAdsClient.load_from_dict(client_config)
            self.categorization_service = CategorizationService()
            self.campaign_type_service = CampaignTypeService()
            
            logger.info(f"Initialized Google Ads client for customer ID: {self.customer_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Ads client: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test Google Ads API connection"""
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Simple query to test connection
            query = f"""
                SELECT customer.id, customer.descriptive_name
                FROM customer
                WHERE customer.id = {self.customer_id}
                LIMIT 1
            """
            
            response = ga_service.search(customer_id=self.customer_id, query=query)
            
            # Try to get at least one result
            for row in response:
                account_name = row.customer.descriptive_name or "Unknown"
                logger.info(f"Connected to Google Ads account: {account_name} (ID: {self.customer_id})")
                return True
                
            logger.warning(f"No results found for customer ID: {self.customer_id}")
            return False
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error: {ex}")
            for error in ex.failure.errors:
                logger.error(f"  Error: {error.error_code}: {error.message}")
            return False
        except Exception as e:
            logger.error(f"Google Ads connection test failed: {e}")
            return False
    
    def get_campaign_insights(
        self, 
        start_date: date, 
        end_date: date,
        campaigns: Optional[List[str]] = None
    ) -> List[GoogleAdsInsight]:
        """Fetch campaign insights from Google Ads API"""
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Build query for campaign performance data
            query = f"""
                SELECT 
                    campaign.id,
                    campaign.name,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value,
                    metrics.impressions,
                    metrics.clicks,
                    segments.date
                FROM campaign
                WHERE segments.date >= '{start_date.strftime('%Y-%m-%d')}'
                AND segments.date <= '{end_date.strftime('%Y-%m-%d')}'
            """
            
            if campaigns:
                campaign_ids = "', '".join(campaigns)
                query += f" AND campaign.id IN ('{campaign_ids}')"
            
            query += " ORDER BY campaign.id"
            
            response = ga_service.search(customer_id=self.customer_id, query=query)
            
            insights = []
            for row in response:
                # Convert micros to dollars
                cost = str(row.metrics.cost_micros / 1_000_000)
                
                insight = GoogleAdsInsight(
                    campaign_id=str(row.campaign.id),
                    campaign_name=row.campaign.name,
                    cost=cost,
                    cost_micros=str(row.metrics.cost_micros),
                    conversions=str(row.metrics.conversions),
                    conversions_value=str(row.metrics.conversions_value),
                    impressions=str(row.metrics.impressions),
                    clicks=str(row.metrics.clicks),
                    date_start=start_date.strftime('%Y-%m-%d'),
                    date_stop=end_date.strftime('%Y-%m-%d')
                )
                insights.append(insight)
            
            logger.info(f"Retrieved {len(insights)} Google Ads insights for {start_date} to {end_date}")
            return insights
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error fetching insights: {ex}")
            for error in ex.failure.errors:
                logger.error(f"  Error: {error.error_code}: {error.message}")
            raise
        except Exception as e:
            logger.error(f"Error fetching Google Ads insights: {e}")
            raise
    
    def convert_to_campaign_data(self, insights: List[GoogleAdsInsight]) -> List[GoogleCampaignData]:
        """Convert Google Ads insights to campaign data"""
        campaign_data_list = []
        
        for insight in insights:
            try:
                # Calculate metrics - use cost_micros and convert to dollars
                spend = Decimal(insight.cost_micros) / Decimal('1000000')
                spend = spend.quantize(Decimal('0.01'))
                conversions = int(float(insight.conversions)) if insight.conversions else 0
                conversion_value = Decimal(insight.conversions_value).quantize(Decimal('0.01'))
                impressions = int(insight.impressions) if insight.impressions else 0
                clicks = int(insight.clicks) if insight.clicks else 0
                
                # Calculate derived metrics
                cpa = (spend / conversions).quantize(Decimal('0.01')) if conversions > 0 else Decimal('0')
                roas = (conversion_value / spend).quantize(Decimal('0.0001')) if spend > 0 else Decimal('0')
                cpc = (spend / clicks).quantize(Decimal('0.0001')) if clicks > 0 else Decimal('0')
                
                # Get category
                category = self.categorization_service.categorize_campaign(insight.campaign_name, insight.campaign_id)
                
                # Get campaign type
                campaign_type = self.campaign_type_service.classify_campaign_type(insight.campaign_name)
                
                # For daily insights, both dates should be the actual insight date (not query range)
                insight_date = datetime.strptime(insight.date_start, '%Y-%m-%d').date()
                
                campaign_data = GoogleCampaignData(
                    campaign_id=insight.campaign_id,
                    campaign_name=insight.campaign_name,
                    category=category,
                    campaign_type=campaign_type,
                    reporting_starts=insight_date,
                    reporting_ends=insight_date,
                    amount_spent_usd=spend,
                    website_purchases=conversions,
                    purchases_conversion_value=conversion_value,
                    impressions=impressions,
                    link_clicks=clicks,
                    cpa=cpa,
                    roas=roas,
                    cpc=cpc
                )
                campaign_data_list.append(campaign_data)
                
            except Exception as e:
                logger.error(f"Error converting Google Ads insight for campaign {insight.campaign_id}: {e}")
                continue
        
        return campaign_data_list
    
    def get_campaigns(self, enabled_only: bool = False) -> List[dict]:
        """Get list of campaigns from Google Ads account"""
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            query_parts = [
                "SELECT campaign.id, campaign.name, campaign.status",
                "FROM campaign"
            ]
            
            if enabled_only:
                query_parts.append("WHERE campaign.status = 'ENABLED'")
            
            query = " ".join(query_parts)
            
            response = ga_service.search(customer_id=self.customer_id, query=query)
            
            campaigns = []
            for row in response:
                campaigns.append({
                    'id': str(row.campaign.id),
                    'name': row.campaign.name,
                    'status': row.campaign.status.name
                })
            
            logger.info(f"Retrieved {len(campaigns)} Google Ads campaigns")
            return campaigns
            
        except GoogleAdsException as ex:
            logger.error(f"Failed to get Google Ads campaigns: {ex}")
            return []
        except Exception as e:
            logger.error(f"Failed to get Google Ads campaigns: {e}")
            return []
    
    def get_monthly_campaign_insights(
        self, 
        start_date: date, 
        end_date: date,
        campaigns: Optional[List[str]] = None
    ) -> List[GoogleAdsInsight]:
        """Fetch monthly aggregated campaign insights from Google Ads API"""
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Build query for campaign performance data using date range
            # Google Ads API requires segments.date, not segments.month
            query = f"""
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    segments.date,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value,
                    metrics.impressions,
                    metrics.clicks
                FROM campaign
                WHERE segments.date >= '{start_date.strftime('%Y-%m-%d')}'
                AND segments.date <= '{end_date.strftime('%Y-%m-%d')}'
            """
            
            if campaigns:
                campaign_ids = "', '".join(campaigns)
                query += f" AND campaign.id IN ('{campaign_ids}')"
            
            query += " ORDER BY campaign.id, segments.date"
            
            response = ga_service.search(customer_id=self.customer_id, query=query)
            
            # Aggregate daily data into monthly totals by campaign
            monthly_aggregated = {}
            
            for row in response:
                campaign_id = str(row.campaign.id)
                campaign_name = row.campaign.name
                
                # Create key for this campaign
                if campaign_id not in monthly_aggregated:
                    monthly_aggregated[campaign_id] = {
                        'campaign_id': campaign_id,
                        'campaign_name': campaign_name,
                        'cost_micros': 0,
                        'conversions': 0,
                        'conversions_value': 0,
                        'impressions': 0,
                        'clicks': 0
                    }
                
                # Aggregate metrics
                monthly_aggregated[campaign_id]['cost_micros'] += row.metrics.cost_micros
                monthly_aggregated[campaign_id]['conversions'] += row.metrics.conversions
                monthly_aggregated[campaign_id]['conversions_value'] += row.metrics.conversions_value
                monthly_aggregated[campaign_id]['impressions'] += row.metrics.impressions
                monthly_aggregated[campaign_id]['clicks'] += row.metrics.clicks
            
            # Convert aggregated data to insights
            insights = []
            for campaign_data in monthly_aggregated.values():
                # Convert micros to dollars
                cost = str(campaign_data['cost_micros'] / 1_000_000)
                
                insight = GoogleAdsInsight(
                    campaign_id=campaign_data['campaign_id'],
                    campaign_name=campaign_data['campaign_name'],
                    cost=cost,
                    cost_micros=str(campaign_data['cost_micros']),
                    conversions=str(campaign_data['conversions']),
                    conversions_value=str(campaign_data['conversions_value']),
                    impressions=str(campaign_data['impressions']),
                    clicks=str(campaign_data['clicks']),
                    date_start=start_date.strftime('%Y-%m-%d'),
                    date_stop=end_date.strftime('%Y-%m-%d')
                )
                insights.append(insight)
            
            logger.info(f"Retrieved and aggregated {len(insights)} monthly Google Ads insights for {start_date} to {end_date}")
            return insights
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error fetching monthly insights: {ex}")
            for error in ex.failure.errors:
                logger.error(f"  Error: {error.error_code}: {error.message}")
            raise
        except Exception as e:
            logger.error(f"Error fetching monthly Google Ads insights: {e}")
            raise