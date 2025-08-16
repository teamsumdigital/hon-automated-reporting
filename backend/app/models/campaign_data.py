from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class CampaignData(BaseModel):
    campaign_id: str
    campaign_name: str
    category: Optional[str] = None
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
    cpm: Decimal = Field(default=0, decimal_places=4)

    class Config:
        from_attributes = True

class CampaignDataResponse(CampaignData):
    id: int
    created_at: datetime
    updated_at: datetime

class MetaAdsInsight(BaseModel):
    campaign_id: str
    campaign_name: str
    spend: str
    purchases: str = "0"
    purchase_roas: List[dict] = []
    impressions: str = "0"
    clicks: str = "0"
    link_clicks: str = "0"  # Add link_clicks field
    cpm: str = "0"
    cpc: str = "0"
    ctr: str = "0"
    date_start: str
    date_stop: str

class CategoryRule(BaseModel):
    rule_name: str
    pattern: str
    category: str
    priority: int = 0
    is_active: bool = True

class CategoryOverride(BaseModel):
    campaign_id: str
    category: str
    created_by: Optional[str] = None

class MonthlyReport(BaseModel):
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

class PivotTableData(BaseModel):
    month: str
    spend: Decimal
    revenue: Decimal
    roas: Decimal
    cpa: Decimal
    cpc: Decimal
    cpm: Decimal

class DashboardFilters(BaseModel):
    categories: Optional[List[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    month: Optional[str] = None