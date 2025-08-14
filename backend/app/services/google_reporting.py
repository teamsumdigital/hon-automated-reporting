import os
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from supabase import create_client, Client
from loguru import logger

from ..models.google_campaign_data import (
    GoogleCampaignData,
    GoogleCampaignDataResponse,
    GooglePivotTableData,
    GoogleDashboardFilters,
    GoogleMonthlyReport
)

class GoogleReportingService:
    """Service for Google Ads reporting and data management"""
    
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase: Client = create_client(url, key)
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string with variable microsecond precision"""
        try:
            return datetime.fromisoformat(timestamp_str)
        except ValueError:
            # Handle microseconds with less than 6 digits
            import re
            # Find the microseconds part and pad it to 6 digits
            pattern = r'(\.\d{1,5})(\+)'
            match = re.search(pattern, timestamp_str)
            if match:
                microseconds = match.group(1)
                # Pad to 6 digits
                padded_microseconds = microseconds.ljust(7, '0')  # .123456
                fixed_timestamp = timestamp_str.replace(microseconds, padded_microseconds)
                return datetime.fromisoformat(fixed_timestamp)
            else:
                return datetime.fromisoformat(timestamp_str)
    
    def store_campaign_data(self, campaign_data_list: List[GoogleCampaignData]) -> bool:
        """
        Store Google Ads campaign data in database with upsert logic
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
                result = self.supabase.table("google_campaign_data").upsert(data).execute()
                
            logger.info(f"Stored {len(campaign_data_list)} Google Ads campaigns")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store Google Ads campaign data: {e}")
            return False
    
    def get_campaign_data(
        self, 
        filters: Optional[GoogleDashboardFilters] = None
    ) -> List[GoogleCampaignDataResponse]:
        """
        Get Google Ads campaign data with optional filters
        """
        try:
            query = self.supabase.table("google_campaign_data").select("*")
            
            if filters:
                if filters.categories:
                    query = query.in_("category", filters.categories)
                if filters.campaign_types:
                    query = query.in_("campaign_type", filters.campaign_types)
                if filters.start_date:
                    query = query.gte("reporting_starts", filters.start_date.isoformat())
                if filters.end_date:
                    query = query.lte("reporting_ends", filters.end_date.isoformat())
            
            result = query.order("reporting_starts", desc=True).execute()
            
            campaigns = []
            for row in result.data:
                campaign = GoogleCampaignDataResponse(
                    id=row["id"],
                    campaign_id=row["campaign_id"],
                    campaign_name=row["campaign_name"],
                    category=row["category"],
                    campaign_type=row.get("campaign_type"),
                    reporting_starts=datetime.strptime(row["reporting_starts"], "%Y-%m-%d").date() if isinstance(row["reporting_starts"], str) else row["reporting_starts"],
                    reporting_ends=datetime.strptime(row["reporting_ends"], "%Y-%m-%d").date() if isinstance(row["reporting_ends"], str) else row["reporting_ends"],
                    amount_spent_usd=Decimal(str(row["amount_spent_usd"])),
                    website_purchases=row["website_purchases"],
                    purchases_conversion_value=Decimal(str(row["purchases_conversion_value"])),
                    impressions=row["impressions"],
                    link_clicks=row["link_clicks"],
                    cpa=Decimal(str(row["cpa"])),
                    roas=Decimal(str(row["roas"])),
                    cpc=Decimal(str(row["cpc"])),
                    created_at=self._parse_timestamp(row["created_at"]) if row["created_at"] else datetime.now(),
                    updated_at=self._parse_timestamp(row["updated_at"]) if row["updated_at"] else datetime.now()
                )
                campaigns.append(campaign)
            
            return campaigns
            
        except Exception as e:
            logger.error(f"Failed to get Google Ads campaign data: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def generate_pivot_table_data(
        self, 
        filters: Optional[GoogleDashboardFilters] = None
    ) -> List[GooglePivotTableData]:
        """
        Generate pivot table data grouped by month for Google Ads
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
                
                pivot_item = GooglePivotTableData(
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
            logger.error(f"Failed to generate Google Ads pivot table data: {e}")
            return []
    
    def get_all_time_summary(self) -> Dict:
        """
        Get all-time summary for Google Ads (no date filters)
        """
        try:
            # Get all data (no date filters)
            campaigns = self.get_campaign_data()
            
            total_spend = sum(campaign.amount_spent_usd for campaign in campaigns)
            total_clicks = sum(campaign.link_clicks for campaign in campaigns)
            total_purchases = sum(campaign.website_purchases for campaign in campaigns)
            total_revenue = sum(campaign.purchases_conversion_value for campaign in campaigns)
            
            avg_cpa = total_spend / total_purchases if total_purchases > 0 else Decimal('0')
            avg_roas = total_revenue / total_spend if total_spend > 0 else Decimal('0')
            avg_cpc = total_spend / total_clicks if total_clicks > 0 else Decimal('0')
            
            return {
                "period": "All Time",
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
            logger.error(f"Failed to get Google Ads all-time summary: {e}")
            return {}

    def get_month_to_date_summary(self) -> Dict:
        """
        Get month-to-date summary for Google Ads
        """
        try:
            current_date = date.today()
            month_start = current_date.replace(day=1)
            
            # Get current month data
            campaigns = self.get_campaign_data(
                GoogleDashboardFilters(start_date=month_start, end_date=current_date)
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
            logger.error(f"Failed to get Google Ads month-to-date summary: {e}")
            return {}
    
    def get_available_categories(self) -> List[str]:
        """
        Get all unique categories from Google Ads campaign data
        """
        try:
            result = self.supabase.table("google_campaign_data").select("category").execute()
            
            categories = list(set([
                row["category"] for row in result.data 
                if row["category"] and row["category"] != "Uncategorized"
            ]))
            categories.sort()
            
            return categories
            
        except Exception as e:
            logger.error(f"Failed to get Google Ads categories: {e}")
            return []
    
    def get_available_campaign_types(self) -> List[str]:
        """
        Get all unique campaign types from Google Ads campaign data
        """
        try:
            result = self.supabase.table("google_campaign_data").select("campaign_type").execute()
            
            campaign_types = list(set([
                row["campaign_type"] for row in result.data 
                if row["campaign_type"] and row["campaign_type"] != "Unclassified"
            ]))
            campaign_types.sort()
            
            return campaign_types
            
        except Exception as e:
            logger.error(f"Failed to get Google Ads campaign types: {e}")
            return []
    
    def get_data_stats(self) -> Dict:
        """
        Get statistics about Google Ads data in database
        """
        try:
            # Get total campaigns
            campaigns_result = self.supabase.table("google_campaign_data").select("id", count="exact").execute()
            total_campaigns = campaigns_result.count
            
            # Get date range
            date_result = self.supabase.table("google_campaign_data").select("reporting_starts, reporting_ends").order("reporting_starts").execute()
            
            earliest_date = None
            latest_date = None
            
            if date_result.data:
                earliest_date = date_result.data[0]["reporting_starts"]
                latest_date = date_result.data[-1]["reporting_ends"]
            
            # Get unique categories
            categories_result = self.supabase.table("google_campaign_data").select("category").execute()
            unique_categories = len(set([row["category"] for row in categories_result.data if row["category"]]))
            
            return {
                "total_campaigns": total_campaigns,
                "earliest_date": earliest_date,
                "latest_date": latest_date,
                "unique_categories": unique_categories,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get Google Ads data stats: {e}")
            return {}
    
    def delete_campaign_data(
        self,
        start_date: date,
        end_date: date,
        campaign_ids: Optional[List[str]] = None
    ) -> bool:
        """
        Delete Google Ads campaign data for specified date range
        """
        try:
            query = self.supabase.table("google_campaign_data").delete()
            query = query.gte("reporting_starts", start_date.isoformat())
            query = query.lte("reporting_ends", end_date.isoformat())
            
            if campaign_ids:
                query = query.in_("campaign_id", campaign_ids)
            
            result = query.execute()
            deleted_count = len(result.data) if result.data else 0
            
            logger.info(f"Deleted {deleted_count} Google Ads campaign records from {start_date} to {end_date}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete Google Ads campaign data: {e}")
            return False