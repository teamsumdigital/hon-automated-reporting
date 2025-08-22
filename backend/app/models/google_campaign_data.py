from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class GoogleCampaignData(BaseModel):
    """Google Ads campaign data model - mirrors CampaignData structure"""
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

class GoogleCampaignDataResponse(GoogleCampaignData):
    """Google Ads campaign data response with database fields"""
    id: int
    created_at: datetime
    updated_at: datetime

class GoogleAdsInsight(BaseModel):
    """Google Ads API insight data structure"""
    campaign_id: str
    campaign_name: str
    cost_micros: str  # Google Ads returns cost in micros (1,000,000 = $1)
    conversions: str = "0"
    conversions_value: str = "0"
    impressions: str = "0"
    clicks: str = "0"  # Google Ads clicks are website clicks by default
    date_start: str
    date_stop: str
    
    # Additional Google Ads specific metrics that might be useful
    ctr: Optional[str] = "0"
    average_cpc: Optional[str] = "0"
    cost_per_conversion: Optional[str] = "0"

class GoogleMonthlyReport(BaseModel):
    """Google Ads monthly report model"""
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

class GooglePivotTableData(BaseModel):
    """Google Ads pivot table data structure"""
    month: str
    spend: Decimal
    link_clicks: int
    purchases: int
    revenue: Decimal
    impressions: int
    cpa: Decimal
    roas: Decimal
    cpc: Decimal
    cpm: Decimal

class GoogleDashboardFilters(BaseModel):
    """Filters for Google Ads dashboard - same as Meta"""
    categories: Optional[List[str]] = None
    campaign_types: Optional[List[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    month: Optional[str] = None

class GoogleAdsCredentials(BaseModel):
    """Google Ads API credentials configuration"""
    developer_token: str
    client_id: str
    client_secret: str
    refresh_token: str
    customer_id: str
    login_customer_id: Optional[str] = None  # For manager accounts
    
class GoogleAdsQuery(BaseModel):
    """Google Ads query configuration"""
    start_date: date
    end_date: date
    campaign_ids: Optional[List[str]] = None
    fields: List[str] = Field(default_factory=lambda: [
        'campaign.id',
        'campaign.name',
        'metrics.cost_micros',
        'metrics.conversions',
        'metrics.conversions_value',
        'metrics.impressions', 
        'metrics.clicks',
        'metrics.ctr',
        'metrics.average_cpc'
    ])
    
class GoogleAdsApiResponse(BaseModel):
    """Wrapper for Google Ads API responses"""
    success: bool
    data: Optional[List[GoogleAdsInsight]] = None
    error: Optional[str] = None
    total_results: int = 0