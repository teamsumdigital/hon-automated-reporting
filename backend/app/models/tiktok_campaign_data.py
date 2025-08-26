from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class TikTokCampaignData(BaseModel):
    """TikTok Ads campaign data model - mirrors CampaignData structure"""
    campaign_id: str
    campaign_name: str
    category: Optional[str] = None
    campaign_type: Optional[str] = None
    reporting_starts: date
    reporting_ends: date
    amount_spent_usd: Decimal = Field(default=0, decimal_places=2)
    website_purchases: int = 0
    purchases_conversion_value: Decimal = Field(default=0, decimal_places=2)
    impressions: int = 0
    link_clicks: int = 0
    cpa: Decimal = Field(default=0, decimal_places=2)
    roas: Decimal = Field(default=0, decimal_places=4)
    cpc: Decimal = Field(default=0, decimal_places=4)

    class Config:
        from_attributes = True

class TikTokCampaignDataResponse(TikTokCampaignData):
    """TikTok Ads campaign data response with database fields"""
    id: int
    created_at: datetime
    updated_at: datetime

class TikTokAdsInsight(BaseModel):
    """TikTok Ads API insight data structure"""
    campaign_id: str
    campaign_name: str
    spend: str  # TikTok returns cost in dollars (unlike Google's micros)
    impressions: str = "0"
    clicks: str = "0"  # TikTok destination clicks (similar to link clicks)
    date_start: str
    date_stop: str
    
    # TikTok specific metrics
    ctr: Optional[str] = "0"  # Click-through rate
    cpc: Optional[str] = "0"  # Cost per click
    cpm: Optional[str] = "0"  # Cost per mille (thousand impressions)
    cost_per_conversion: Optional[str] = "0"  # Cost per conversion
    conversion_rate: Optional[str] = "0"  # Conversion rate
    
    # Payment Complete metrics (correct ROAS source)
    complete_payment_roas: Optional[str] = "0"  # Payment Complete ROAS (website)
    complete_payment: Optional[str] = "0"  # Number of complete payments
    purchase: Optional[str] = "0"  # Purchase events
    
    # Legacy fields for backward compatibility
    conversions: Optional[str] = "0"  # Use complete_payment instead
    conversion_value: Optional[str] = "0"  # Calculate from complete_payment_roas
    reach: Optional[str] = "0"  # Unique users reached
    frequency: Optional[str] = "0"  # Average frequency per user

class TikTokMonthlyReport(BaseModel):
    """TikTok Ads monthly report model"""
    report_month: date
    report_date: date
    total_spend: Decimal = Field(default=0, decimal_places=2)
    total_purchases: int = 0
    total_revenue: Decimal = Field(default=0, decimal_places=2)
    total_impressions: int = 0
    total_clicks: int = 0
    avg_cpa: Decimal = Field(default=0, decimal_places=2)
    avg_roas: Decimal = Field(default=0, decimal_places=4)
    avg_cpc: Decimal = Field(default=0, decimal_places=4)

class TikTokPivotTableData(BaseModel):
    """TikTok Ads pivot table data structure"""
    month: str
    spend: Decimal
    link_clicks: int
    purchases: int
    revenue: Decimal
    cpa: Decimal
    roas: Decimal
    cpc: Decimal

    def model_dump(self, **kwargs):
        """Convert Decimal fields to float for JSON serialization"""
        data = super().model_dump(**kwargs)
        data['spend'] = float(self.spend)
        data['revenue'] = float(self.revenue)
        data['cpa'] = float(self.cpa)
        data['roas'] = float(self.roas)
        data['cpc'] = float(self.cpc)
        return data

class TikTokDashboardFilters(BaseModel):
    """Filters for TikTok Ads dashboard - same as Meta/Google"""
    categories: Optional[List[str]] = None
    campaign_types: Optional[List[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    month: Optional[str] = None

class TikTokCredentials(BaseModel):
    """TikTok Ads API credentials configuration"""
    app_id: str
    app_secret: str
    access_token: str
    advertiser_id: str
    client_key: str
    sandbox_mode: bool = False  # For testing

class TikTokQuery(BaseModel):
    """TikTok Ads query configuration"""
    start_date: date
    end_date: date
    campaign_ids: Optional[List[str]] = None
    metrics: List[str] = Field(default_factory=lambda: [
        'spend',
        'impressions',
        'clicks', 
        'conversions',
        'conversion_value',
        'ctr',
        'cpc',
        'cpm',
        'cost_per_conversion'
    ])
    dimensions: List[str] = Field(default_factory=lambda: [
        'campaign_id',
        'campaign_name'
    ])
    
class TikTokApiResponse(BaseModel):
    """Wrapper for TikTok Ads API responses"""
    success: bool
    data: Optional[List[TikTokAdsInsight]] = None
    error: Optional[str] = None
    total_results: int = 0
    request_id: Optional[str] = None  # TikTok provides request IDs for debugging

class TikTokReportRequest(BaseModel):
    """TikTok Ads report request structure"""
    advertiser_id: str
    report_type: str = "BASIC"  # TikTok report types: BASIC, AUCTION, ATTRIBUTION
    data_level: str = "AUCTION_CAMPAIGN"  # Campaign level reporting
    dimensions: List[str]
    metrics: List[str]
    start_date: str
    end_date: str
    filters: Optional[List[dict]] = None
    page: int = 1
    page_size: int = 1000

class TikTokCampaignSummary(BaseModel):
    """Summary statistics for TikTok campaigns"""
    total_campaigns: int
    active_campaigns: int
    paused_campaigns: int
    total_spend: Decimal
    total_impressions: int
    total_clicks: int
    total_conversions: int
    average_cpc: Decimal
    average_cpm: Decimal
    average_ctr: Decimal
    overall_roas: Decimal