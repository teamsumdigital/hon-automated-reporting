from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
import pandas as pd
from supabase import create_client, Client
import os
from loguru import logger
from ..models.campaign_data import CampaignData, PivotTableData, MonthlyReport, DashboardFilters
from .meta_api import MetaAdsService
from .categorization import CategorizationService

class ReportingService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase: Client = create_client(url, key)
        self.meta_service = MetaAdsService()
        self.categorization_service = CategorizationService()
    
    def store_campaign_data(self, campaign_data_list: List[CampaignData]) -> bool:
        """
        Store campaign data in the database with automatic categorization
        """
        try:
            for campaign_data in campaign_data_list:
                # Auto-categorize if no category is set
                if not campaign_data.category:
                    campaign_data.category = self.categorization_service.categorize_campaign(
                        campaign_data.campaign_name, 
                        campaign_data.campaign_id
                    )
                
                # Convert to dict for database insertion
                data_dict = {
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
                    "cpc": float(campaign_data.cpc),
                    "cpm": float(campaign_data.cpm)
                }
                
                # Upsert (insert or update) the data
                result = self.supabase.table("campaign_data").upsert(data_dict).execute()
            
            logger.info(f"Stored {len(campaign_data_list)} campaign records")
            return True
            
        except Exception as e:
            logger.error(f"Error storing campaign data: {e}")
            return False
    
    def get_campaign_data(
        self, 
        filters: Optional[DashboardFilters] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[dict]:
        """
        Retrieve campaign data with optional filters
        """
        try:
            query = self.supabase.table("campaign_data").select("*")
            
            # Apply date range filter
            if start_date:
                query = query.gte("reporting_starts", start_date.isoformat())
            if end_date:
                query = query.lte("reporting_ends", end_date.isoformat())
            
            # Apply category filter
            if filters and filters.categories:
                query = query.in_("category", filters.categories)
            
            result = query.order("reporting_starts", desc=True).execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Error getting campaign data: {e}")
            return []
    
    def generate_pivot_table_data(
        self, 
        filters: Optional[DashboardFilters] = None
    ) -> List[PivotTableData]:
        """
        Generate pivot table data grouped by month, similar to Excel pivot
        """
        try:
            # Get campaign data
            campaign_data = self.get_campaign_data(filters)
            
            if not campaign_data:
                return []
            
            # Convert to DataFrame for easier aggregation
            df = pd.DataFrame(campaign_data)
            df['reporting_starts'] = pd.to_datetime(df['reporting_starts'])
            df['month'] = df['reporting_starts'].dt.to_period('M').astype(str)
            
            # Group by month and aggregate
            monthly_agg = df.groupby('month').agg({
                'amount_spent_usd': 'sum',
                'link_clicks': 'sum',
                'website_purchases': 'sum',
                'purchases_conversion_value': 'sum',
                'impressions': 'sum'
            }).reset_index()
            
            # Calculate derived metrics
            monthly_agg['roas'] = monthly_agg['purchases_conversion_value'] / monthly_agg['amount_spent_usd']
            monthly_agg['roas'] = monthly_agg['roas'].fillna(0)
            
            monthly_agg['cpa'] = monthly_agg['amount_spent_usd'] / monthly_agg['website_purchases']
            monthly_agg['cpa'] = monthly_agg['cpa'].fillna(0)
            
            monthly_agg['cpc'] = monthly_agg['amount_spent_usd'] / monthly_agg['link_clicks']
            monthly_agg['cpc'] = monthly_agg['cpc'].fillna(0)
            
            monthly_agg['cpm'] = (monthly_agg['amount_spent_usd'] / (monthly_agg['impressions'] / 1000))
            monthly_agg['cpm'] = monthly_agg['cpm'].fillna(0)
            
            # Sort by month (oldest first, Excel style)
            monthly_agg = monthly_agg.sort_values('month')
            
            # Convert to PivotTableData models
            pivot_data = []
            for _, row in monthly_agg.iterrows():
                pivot_data.append(PivotTableData(
                    month=row['month'],
                    spend=Decimal(str(row['amount_spent_usd'])),
                    revenue=Decimal(str(row['purchases_conversion_value'])),
                    roas=Decimal(str(row['roas'])),
                    cpa=Decimal(str(row['cpa'])),
                    cpc=Decimal(str(row['cpc'])),
                    cpm=Decimal(str(row['cpm']))
                ))
            
            return pivot_data
            
        except Exception as e:
            logger.error(f"Error generating pivot table data: {e}")
            return []
    
    def get_month_to_date_summary(self, target_date: Optional[date] = None) -> dict:
        """
        Get month-to-date summary for the dashboard
        """
        try:
            if target_date is None:
                target_date = date.today()
            
            start_of_month = target_date.replace(day=1)
            
            # Get campaign data for current month
            campaign_data = self.get_campaign_data(
                start_date=start_of_month,
                end_date=target_date
            )
            
            if not campaign_data:
                return {
                    "total_spend": 0,
                    "total_purchases": 0,
                    "total_revenue": 0,
                    "total_impressions": 0,
                    "total_clicks": 0,
                    "avg_cpa": 0,
                    "avg_roas": 0,
                    "avg_cpc": 0,
                    "avg_cpm": 0,
                    "campaign_count": 0,
                    "date_range": f"{start_of_month} to {target_date}"
                }
            
            # Calculate aggregates
            df = pd.DataFrame(campaign_data)
            
            total_spend = df['amount_spent_usd'].sum()
            total_purchases = df['website_purchases'].sum()
            total_revenue = df['purchases_conversion_value'].sum()
            total_impressions = df['impressions'].sum()
            total_clicks = df['link_clicks'].sum()
            
            avg_cpa = total_spend / total_purchases if total_purchases > 0 else 0
            avg_roas = total_revenue / total_spend if total_spend > 0 else 0
            avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0
            avg_cpm = (total_spend / (total_impressions / 1000)) if total_impressions > 0 else 0
            
            return {
                "total_spend": float(total_spend),
                "total_purchases": int(total_purchases),
                "total_revenue": float(total_revenue),
                "total_impressions": int(total_impressions),
                "total_clicks": int(total_clicks),
                "avg_cpa": float(avg_cpa),
                "avg_roas": float(avg_roas),
                "avg_cpc": float(avg_cpc),
                "avg_cpm": float(avg_cpm),
                "campaign_count": len(df),
                "date_range": f"{start_of_month} to {target_date}"
            }
            
        except Exception as e:
            logger.error(f"Error getting month-to-date summary: {e}")
            return {}
    
    def sync_meta_data(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Sync latest data from Meta Ads API and store in database
        """
        try:
            logger.info("Starting Meta Ads data sync...")
            
            # Get month-to-date data from Meta
            campaign_data = self.meta_service.get_month_to_date_data(target_date)
            
            if not campaign_data:
                return {"success": False, "message": "No data retrieved from Meta Ads API"}
            
            # Store in database
            success = self.store_campaign_data(campaign_data)
            
            if success:
                summary = self.get_month_to_date_summary(target_date)
                return {
                    "success": True,
                    "message": f"Synced {len(campaign_data)} campaigns",
                    "data_count": len(campaign_data),
                    "summary": summary
                }
            else:
                return {"success": False, "message": "Failed to store data in database"}
                
        except Exception as e:
            logger.error(f"Error syncing Meta data: {e}")
            return {"success": False, "message": str(e)}
    
    def get_category_breakdown(self, filters: Optional[DashboardFilters] = None) -> List[dict]:
        """
        Get spending and performance breakdown by category
        """
        try:
            campaign_data = self.get_campaign_data(filters)
            
            if not campaign_data:
                return []
            
            df = pd.DataFrame(campaign_data)
            
            category_agg = df.groupby('category').agg({
                'amount_spent_usd': 'sum',
                'website_purchases': 'sum',
                'purchases_conversion_value': 'sum',
                'impressions': 'sum'
            }).reset_index()
            
            # Calculate metrics
            category_agg['cpa'] = category_agg['amount_spent_usd'] / category_agg['website_purchases']
            category_agg['cpa'] = category_agg['cpa'].fillna(0)
            
            category_agg['roas'] = category_agg['purchases_conversion_value'] / category_agg['amount_spent_usd']
            category_agg['roas'] = category_agg['roas'].fillna(0)
            
            category_agg['cpm'] = (category_agg['amount_spent_usd'] / (category_agg['impressions'] / 1000))
            category_agg['cpm'] = category_agg['cpm'].fillna(0)
            
            # Convert to list of dicts
            return category_agg.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting category breakdown: {e}")
            return []
    
    def get_monthly_breakdown(self, filters: Optional[DashboardFilters] = None) -> List[dict]:
        """
        Get performance breakdown by month with optional category filtering
        """
        try:
            campaign_data = self.get_campaign_data(filters)
            
            if not campaign_data:
                return []
            
            df = pd.DataFrame(campaign_data)
            
            # Convert dates and extract month-year
            df['reporting_starts'] = pd.to_datetime(df['reporting_starts'])
            df['month_year'] = df['reporting_starts'].dt.to_period('M')
            
            # Group by month
            monthly_agg = df.groupby('month_year').agg({
                'amount_spent_usd': 'sum',
                'website_purchases': 'sum',
                'purchases_conversion_value': 'sum',
                'link_clicks': 'sum',
                'impressions': 'sum'
            }).reset_index()
            
            # Convert period to string for JSON serialization
            monthly_agg['month'] = monthly_agg['month_year'].astype(str)
            monthly_agg = monthly_agg.drop('month_year', axis=1)
            
            # Calculate metrics
            monthly_agg['cpa'] = monthly_agg['amount_spent_usd'] / monthly_agg['website_purchases']
            monthly_agg['cpa'] = monthly_agg['cpa'].fillna(0)
            
            monthly_agg['roas'] = monthly_agg['purchases_conversion_value'] / monthly_agg['amount_spent_usd']
            monthly_agg['roas'] = monthly_agg['roas'].fillna(0)
            
            monthly_agg['cpc'] = monthly_agg['amount_spent_usd'] / monthly_agg['link_clicks']
            monthly_agg['cpc'] = monthly_agg['cpc'].fillna(0)
            
            # Sort by month (most recent first)
            monthly_agg = monthly_agg.sort_values('month', ascending=False)
            
            # Convert to list of dicts
            return monthly_agg.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting monthly breakdown: {e}")
            return []
    
    def get_filtered_summary(self, filters: Optional[DashboardFilters] = None) -> dict:
        """
        Get summary statistics for filtered data
        """
        try:
            campaign_data = self.get_campaign_data(filters)
            
            if not campaign_data:
                return {}
            
            df = pd.DataFrame(campaign_data)
            
            total_spend = df['amount_spent_usd'].sum()
            total_purchases = df['website_purchases'].sum()
            total_revenue = df['purchases_conversion_value'].sum()
            total_impressions = df['impressions'].sum()
            total_clicks = df['link_clicks'].sum()
            
            avg_cpa = total_spend / total_purchases if total_purchases > 0 else 0
            avg_roas = total_revenue / total_spend if total_spend > 0 else 0
            avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0
            avg_cpm = (total_spend / (total_impressions / 1000)) if total_impressions > 0 else 0
            
            return {
                "total_spend": float(total_spend),
                "total_purchases": int(total_purchases),
                "total_revenue": float(total_revenue),
                "total_impressions": int(total_impressions),
                "total_clicks": int(total_clicks),
                "avg_cpa": float(avg_cpa),
                "avg_roas": float(avg_roas),
                "avg_cpc": float(avg_cpc),
                "avg_cpm": float(avg_cpm),
                "campaign_count": len(df)
            }
            
        except Exception as e:
            logger.error(f"Error getting filtered summary: {e}")
            return {}
    
    def get_available_categories(self) -> List[str]:
        """
        Get list of all available categories from the data
        """
        try:
            response = self.supabase.table("campaign_data").select("category").execute()
            
            if response.data:
                categories = list(set([row['category'] for row in response.data if row['category']]))
                return sorted(categories)
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting available categories: {e}")
            return []