import os
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from supabase import create_client, Client
from loguru import logger

from ..models.tiktok_campaign_data import (
    TikTokCampaignData,
    TikTokCampaignDataResponse,
    TikTokPivotTableData,
    TikTokDashboardFilters,
    TikTokMonthlyReport
)

class TikTokReportingService:
    """Service for TikTok Ads reporting and data management"""
    
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase: Client = create_client(url, key)
    
    def store_campaign_data(self, campaign_data_list: List[TikTokCampaignData]) -> bool:
        """
        Store TikTok Ads campaign data in database with upsert logic
        """
        try:
            for campaign_data in campaign_data_list:
                data = {
                    "campaign_id": campaign_data.campaign_id,
                    "campaign_name": campaign_data.campaign_name,
                    "category": campaign_data.category,
                    "reporting_starts": campaign_data.reporting_starts.isoformat(),
                    "reporting_ends": campaign_data.reporting_ends.isoformat(),
                    "amount_spent_usd": float(campaign_data.amount_spent_usd),
                    "website_purchases": campaign_data.website_purchases,
                    "purchases_conversion_value": float(campaign_data.purchases_conversion_value),
                    "impressions": campaign_data.impressions,
                    "link_clicks": campaign_data.link_clicks,
                    "cpa": float(campaign_data.cpa),
                    "roas": float(campaign_data.roas),
                    "cpc": float(campaign_data.cpc)
                }
                
                # Use upsert to handle duplicates
                result = self.supabase.table("tiktok_campaign_data").upsert(data).execute()
                
            logger.info(f"Stored {len(campaign_data_list)} TikTok campaigns")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store TikTok campaign data: {e}")
            return False
    
    def get_campaign_data(
        self, 
        filters: Optional[TikTokDashboardFilters] = None
    ) -> List[TikTokCampaignDataResponse]:
        """
        Get TikTok campaign data with optional filters
        """
        try:
            query = self.supabase.table("tiktok_campaign_data").select("*")
            
            if filters:
                if filters.categories:
                    query = query.in_("category", filters.categories)
                if filters.start_date:
                    query = query.gte("reporting_starts", filters.start_date.isoformat())
                if filters.end_date:
                    query = query.lte("reporting_ends", filters.end_date.isoformat())
            
            result = query.order("reporting_starts", desc=False).execute()  # Excel-style: oldest first
            
            campaigns = []
            for row in result.data:
                campaign = TikTokCampaignDataResponse(
                    id=row["id"],
                    campaign_id=row["campaign_id"],
                    campaign_name=row["campaign_name"],
                    category=row["category"],
                    reporting_starts=datetime.fromisoformat(row["reporting_starts"]).date(),
                    reporting_ends=datetime.fromisoformat(row["reporting_ends"]).date(),
                    amount_spent_usd=Decimal(str(row["amount_spent_usd"])),
                    website_purchases=row["website_purchases"],
                    purchases_conversion_value=Decimal(str(row["purchases_conversion_value"])),
                    impressions=row["impressions"],
                    link_clicks=row["link_clicks"],
                    cpa=Decimal(str(row["cpa"])),
                    roas=Decimal(str(row["roas"])),
                    cpc=Decimal(str(row["cpc"])),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"])
                )
                campaigns.append(campaign)
            
            return campaigns
            
        except Exception as e:
            logger.error(f"Failed to get TikTok campaign data: {e}")
            return []
    
    def generate_pivot_table_data(
        self, 
        filters: Optional[TikTokDashboardFilters] = None
    ) -> List[TikTokPivotTableData]:
        """
        Generate pivot table data grouped by month for TikTok Ads
        """
        try:
            campaigns = self.get_campaign_data(filters)
            
            # Group by month
            monthly_data = {}
            
            for campaign in campaigns:
                month_key = campaign.reporting_starts.strftime("%Y-%m")
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        "month": month_key,
                        "spend": Decimal('0'),
                        "link_clicks": 0,
                        "purchases": 0,
                        "revenue": Decimal('0'),
                        "campaign_count": 0
                    }
                
                monthly_data[month_key]["spend"] += campaign.amount_spent_usd
                monthly_data[month_key]["link_clicks"] += campaign.link_clicks
                monthly_data[month_key]["purchases"] += campaign.website_purchases
                monthly_data[month_key]["revenue"] += campaign.purchases_conversion_value
                monthly_data[month_key]["campaign_count"] += 1
            
            # Calculate derived metrics and create pivot data
            pivot_data = []
            for month_key, data in monthly_data.items():
                cpa = data["spend"] / data["purchases"] if data["purchases"] > 0 else Decimal('0')
                roas = data["revenue"] / data["spend"] if data["spend"] > 0 else Decimal('0')
                cpc = data["spend"] / data["link_clicks"] if data["link_clicks"] > 0 else Decimal('0')
                
                pivot_item = TikTokPivotTableData(
                    month=month_key,
                    spend=data["spend"],
                    link_clicks=data["link_clicks"],
                    purchases=data["purchases"],
                    revenue=data["revenue"],
                    cpa=cpa,
                    roas=roas,
                    cpc=cpc
                )
                pivot_data.append(pivot_item)
            
            # Sort by month ascending (oldest first, Excel style)
            pivot_data.sort(key=lambda x: x.month, reverse=False)
            
            return pivot_data
            
        except Exception as e:
            logger.error(f"Failed to generate TikTok pivot table data: {e}")
            return []
    
    def get_month_to_date_summary(self) -> Dict:
        """
        Get month-to-date summary for TikTok Ads
        """
        try:
            current_date = date.today()
            month_start = current_date.replace(day=1)
            
            # Get current month data
            campaigns = self.get_campaign_data(
                TikTokDashboardFilters(start_date=month_start, end_date=current_date)
            )
            
            total_spend = sum(campaign.amount_spent_usd for campaign in campaigns)
            total_clicks = sum(campaign.link_clicks for campaign in campaigns)
            total_purchases = sum(campaign.website_purchases for campaign in campaigns)
            total_revenue = sum(campaign.purchases_conversion_value for campaign in campaigns)
            
            avg_cpa = total_spend / total_purchases if total_purchases > 0 else Decimal('0')
            avg_roas = total_revenue / total_spend if total_spend > 0 else Decimal('0')
            avg_cpc = total_spend / total_clicks if total_clicks > 0 else Decimal('0')
            
            return {
                "period": f"{current_date.strftime('%B %Y')} (Month-to-Date)",
                "total_spend": float(total_spend),
                "total_clicks": total_clicks,
                "total_purchases": total_purchases,
                "total_revenue": float(total_revenue),
                "avg_cpa": float(avg_cpa),
                "avg_roas": float(avg_roas),
                "avg_cpc": float(avg_cpc),
                "campaigns_count": len(campaigns)
            }
            
        except Exception as e:
            logger.error(f"Failed to get TikTok month-to-date summary: {e}")
            return {}
    
    def get_available_categories(self) -> List[str]:
        """
        Get all unique categories from TikTok campaign data
        """
        try:
            result = self.supabase.table("tiktok_campaign_data").select("category").execute()
            
            categories = list(set([
                row["category"] for row in result.data 
                if row["category"] and row["category"] != "Uncategorized"
            ]))
            categories.sort()
            
            return categories
            
        except Exception as e:
            logger.error(f"Failed to get TikTok categories: {e}")
            return []
    
    def get_data_stats(self) -> Dict:
        """
        Get statistics about TikTok data in database
        """
        try:
            # Get total campaigns
            campaigns_result = self.supabase.table("tiktok_campaign_data").select("id", count="exact").execute()
            total_campaigns = campaigns_result.count
            
            # Get date range
            date_result = self.supabase.table("tiktok_campaign_data").select("reporting_starts, reporting_ends").order("reporting_starts").execute()
            
            earliest_date = None
            latest_date = None
            
            if date_result.data:
                earliest_date = date_result.data[0]["reporting_starts"]
                latest_date = date_result.data[-1]["reporting_ends"]
            
            # Get unique categories
            categories_result = self.supabase.table("tiktok_campaign_data").select("category").execute()
            unique_categories = len(set([row["category"] for row in categories_result.data if row["category"]]))
            
            return {
                "total_campaigns": total_campaigns,
                "earliest_date": earliest_date,
                "latest_date": latest_date,
                "unique_categories": unique_categories,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get TikTok data stats: {e}")
            return {}
    
    def delete_campaign_data(
        self,
        start_date: date,
        end_date: date,
        campaign_ids: Optional[List[str]] = None
    ) -> bool:
        """
        Delete TikTok campaign data for specified date range
        """
        try:
            query = self.supabase.table("tiktok_campaign_data").delete()
            query = query.gte("reporting_starts", start_date.isoformat())
            query = query.lte("reporting_ends", end_date.isoformat())
            
            if campaign_ids:
                query = query.in_("campaign_id", campaign_ids)
            
            result = query.execute()
            deleted_count = len(result.data) if result.data else 0
            
            logger.info(f"Deleted {deleted_count} TikTok campaign records from {start_date} to {end_date}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete TikTok campaign data: {e}")
            return False
    
    def get_performance_comparison(self, months: int = 6) -> Dict:
        """
        Get performance comparison for the last N months
        """
        try:
            end_date = date.today()
            start_date = end_date.replace(month=end_date.month - months + 1)
            
            filters = TikTokDashboardFilters(start_date=start_date, end_date=end_date)
            pivot_data = self.generate_pivot_table_data(filters)
            
            if len(pivot_data) < 2:
                return {}
            
            current_month = pivot_data[-1]
            previous_month = pivot_data[-2]
            
            # Calculate month-over-month changes
            spend_change = ((current_month.spend - previous_month.spend) / previous_month.spend * 100) if previous_month.spend > 0 else 0
            roas_change = ((current_month.roas - previous_month.roas) / previous_month.roas * 100) if previous_month.roas > 0 else 0
            cpc_change = ((current_month.cpc - previous_month.cpc) / previous_month.cpc * 100) if previous_month.cpc > 0 else 0
            
            return {
                "current_month": {
                    "spend": float(current_month.spend),
                    "roas": float(current_month.roas),
                    "cpc": float(current_month.cpc)
                },
                "previous_month": {
                    "spend": float(previous_month.spend),
                    "roas": float(previous_month.roas),
                    "cpc": float(previous_month.cpc)
                },
                "changes": {
                    "spend_change": float(spend_change),
                    "roas_change": float(roas_change),
                    "cpc_change": float(cpc_change)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get TikTok performance comparison: {e}")
            return {}