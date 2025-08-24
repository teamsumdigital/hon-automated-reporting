"""TikTok Marketing API Service for campaign data and reporting"""

import os
import json
import requests
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from supabase import create_client
from ..models.tiktok_campaign_data import TikTokCampaignData


class TikTokService:
    def __init__(self):
        # TikTok API credentials
        self.app_id = os.getenv("TIKTOK_APP_ID")
        self.app_secret = os.getenv("TIKTOK_APP_SECRET")
        self.access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        self.advertiser_id = os.getenv("TIKTOK_ADVERTISER_ID")
        self.sandbox_mode = os.getenv("TIKTOK_SANDBOX_MODE", "false").lower() == "true"
        
        # Database connection
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.supabase = create_client(supabase_url, supabase_key)
        
        # TikTok API base URL
        self.base_url = "https://business-api.tiktok.com/open_api/v1.3"
        
        # Standard headers for TikTok API
        self.headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
    
    def fetch_campaigns(self) -> List[Dict[str, Any]]:
        """Fetch all campaigns from TikTok API"""
        url = f"{self.base_url}/campaign/get/"
        
        params = {
            "advertiser_id": self.advertiser_id,
            "filtering": json.dumps({
                "campaign_statuses": ["ENABLE", "DISABLE", "PAUSED"]
            }),
            "fields": json.dumps([
                "campaign_id", "campaign_name", "operation_status", 
                "objective_type", "budget", "create_time", "modify_time"
            ])
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0:
                return data.get("data", {}).get("list", [])
            else:
                raise Exception(f"TikTok API Error: {data.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"Error fetching TikTok campaigns: {e}")
            return []
    
    def fetch_campaign_reports(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch campaign performance reports from TikTok API"""
        url = f"{self.base_url}/report/integrated/get/"
        
        params = {
            "advertiser_id": self.advertiser_id,
            "report_type": "BASIC",
            "dimensions": json.dumps(["campaign_id"]),
            "metrics": json.dumps([
                "spend", "impressions", "clicks", "conversion", "cost_per_conversion", "cpc", "cpm", "ctr"
            ]),
            "data_level": "AUCTION_CAMPAIGN",
            "start_date": start_date,
            "end_date": end_date,
            "service_type": "AUCTION"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0:
                return data.get("data", {}).get("list", [])
            else:
                raise Exception(f"TikTok API Error: {data.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"Error fetching TikTok reports: {e}")
            return []
    
    def sync_campaign_data(self, start_date: str, end_date: str) -> Tuple[int, str]:
        """Sync TikTok campaign data to database"""
        try:
            # Fetch campaigns and reports
            campaigns = self.fetch_campaigns()
            reports = self.fetch_campaign_reports(start_date, end_date)
            
            # Create lookup for reports by campaign_id
            reports_lookup = {report["dimensions"]["campaign_id"]: report for report in reports}
            
            synced_count = 0
            
            for campaign in campaigns:
                campaign_id = campaign["campaign_id"]
                campaign_name = campaign["campaign_name"]
                
                # Get report data for this campaign
                report = reports_lookup.get(campaign_id, {})
                metrics = report.get("metrics", {})
                
                # Prepare campaign data - using correct TikTok field names
                campaign_data = {
                    "campaign_id": campaign_id,
                    "campaign_name": campaign_name,
                    "category": None,  # Will be auto-categorized by trigger
                    "campaign_type": self._classify_campaign_type(campaign_name),
                    "reporting_starts": start_date,
                    "reporting_ends": end_date,
                    "amount_spent_usd": float(metrics.get("spend", 0)),
                    "website_purchases": int(metrics.get("conversion", 0)),  # Fixed: 'conversion' not 'conversions'
                    "purchases_conversion_value": 0.0,  # TikTok doesn't provide conversion_value directly
                    "impressions": int(metrics.get("impressions", 0)),
                    "link_clicks": int(metrics.get("clicks", 0)),
                    "cpa": float(metrics.get("cost_per_conversion", 0)),  # Use TikTok's calculated CPA
                    "roas": 0.0,  # Cannot calculate without conversion value
                    "cpc": float(metrics.get("cpc", 0))  # Use TikTok's calculated CPC
                }
                
                # Insert or update in database
                result = self.supabase.table("tiktok_campaign_data").upsert(
                    campaign_data,
                    on_conflict="campaign_id,reporting_starts,reporting_ends"
                ).execute()
                
                if result.data:
                    synced_count += 1
            
            return synced_count, f"Successfully synced {synced_count} TikTok campaigns"
            
        except Exception as e:
            return 0, f"Error syncing TikTok data: {str(e)}"
    
    def get_dashboard_data(self, categories: Optional[str] = None, 
                          start_date: Optional[str] = None, 
                          end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get TikTok dashboard data with optional filtering"""
        
        # Build query filters - Now using ad-level data
        query = self.supabase.table("tiktok_ad_data").select("*")
        
        if categories:
            category_list = [cat.strip() for cat in categories.split(",")]
            query = query.in_("category", category_list)
        
        if start_date:
            query = query.gte("reporting_starts", start_date)
        
        if end_date:
            query = query.lte("reporting_ends", end_date)
        
        # Execute query
        result = query.execute()
        campaigns = result.data
        
        # Calculate summary metrics
        summary = self._calculate_summary_metrics(campaigns)
        
        # Generate pivot table data (monthly aggregation)
        pivot_data = self._generate_pivot_data(campaigns)
        
        # Get available categories - Now from ad-level data
        categories_result = self.supabase.table("tiktok_ad_data")\
            .select("category")\
            .not_.is_("category", "null")\
            .execute()
        
        unique_categories = list(set([row["category"] for row in categories_result.data if row["category"]]))
        
        # Category breakdown
        category_breakdown = self._generate_category_breakdown(campaigns)
        
        return {
            "summary": summary,
            "pivot_data": pivot_data,
            "categories": sorted(unique_categories),
            "category_breakdown": category_breakdown,
            "campaigns": campaigns
        }
    
    def get_categories(self) -> List[str]:
        """Get all available TikTok categories from ad-level data"""
        result = self.supabase.table("tiktok_ad_data")\
            .select("category")\
            .not_.is_("category", "null")\
            .execute()
        
        categories = list(set([row["category"] for row in result.data if row["category"]]))
        return sorted(categories)
    
    def test_connection(self) -> Dict[str, str]:
        """Test TikTok API connection"""
        try:
            url = f"{self.base_url}/advertiser/info/"
            params = {
                "advertiser_ids": json.dumps([self.advertiser_id])
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0:
                advertiser_list = data.get("data", {}).get("list", [])
                if advertiser_list:
                    info = advertiser_list[0]
                    return {
                        "status": "success",
                        "message": f"Connected to {info.get('name', 'Unknown')} ({info.get('currency', 'Unknown')})"
                    }
            
            return {
                "status": "error",
                "message": f"TikTok API Error: {data.get('message', 'Unknown error')}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }
    
    def _classify_campaign_type(self, campaign_name: str) -> str:
        """Classify campaign type based on naming patterns"""
        name_lower = campaign_name.lower()
        
        if any(keyword in name_lower for keyword in ["brand", "branded", "competitor"]):
            return "Brand"
        elif any(keyword in name_lower for keyword in ["youtube", "video", "yt"]):
            return "YouTube"
        else:
            return "Non-Brand"
    
    def _calculate_cpa(self, spend: float, conversions: int) -> float:
        """Calculate Cost Per Acquisition"""
        if conversions > 0:
            return spend / conversions
        return 0.0
    
    def _calculate_roas(self, revenue: float, spend: float) -> float:
        """Calculate Return on Ad Spend"""
        if spend > 0:
            return revenue / spend
        return 0.0
    
    def _calculate_cpc(self, spend: float, clicks: int) -> float:
        """Calculate Cost Per Click"""
        if clicks > 0:
            return spend / clicks
        return 0.0
    
    def _calculate_summary_metrics(self, campaigns: List[Dict]) -> Dict[str, Any]:
        """Calculate summary metrics from campaign data"""
        if not campaigns:
            return {
                "period": "No Data",
                "total_spend": 0,
                "total_clicks": 0,
                "total_purchases": 0,
                "total_revenue": 0,
                "total_impressions": 0,
                "avg_cpa": 0,
                "avg_roas": 0,
                "avg_cpc": 0,
                "campaigns_count": 0,
                "date_range": ""
            }
        
        total_spend = sum(c.get("amount_spent_usd", 0) for c in campaigns)
        total_purchases = sum(c.get("website_purchases", 0) for c in campaigns)
        total_revenue = sum(c.get("purchases_conversion_value", 0) for c in campaigns)
        total_impressions = sum(c.get("impressions", 0) for c in campaigns)
        total_clicks = sum(c.get("link_clicks", 0) for c in campaigns)
        
        avg_cpa = total_spend / total_purchases if total_purchases > 0 else 0
        avg_roas = total_revenue / total_spend if total_spend > 0 else 0
        avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0
        
        # Determine date range
        dates = [c.get("reporting_starts") for c in campaigns if c.get("reporting_starts")]
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            date_range = f"{min_date} to {max_date}"
        else:
            date_range = "Unknown"
        
        return {
            "period": "Custom Range",
            "total_spend": total_spend,
            "total_clicks": total_clicks,
            "total_purchases": total_purchases,
            "total_revenue": total_revenue,
            "total_impressions": total_impressions,
            "avg_cpa": avg_cpa,
            "avg_roas": avg_roas,
            "avg_cpc": avg_cpc,
            "campaigns_count": len(campaigns),
            "date_range": date_range
        }
    
    def _generate_pivot_data(self, campaigns: List[Dict]) -> List[Dict[str, Any]]:
        """Generate monthly pivot table data"""
        monthly_data = {}
        
        for campaign in campaigns:
            # Extract month from reporting_starts
            reporting_date = campaign.get("reporting_starts")
            if not reporting_date:
                continue
                
            try:
                month_key = datetime.strptime(reporting_date, "%Y-%m-%d").strftime("%Y-%m")
            except:
                continue
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "month": month_key,
                    "spend": 0,
                    "link_clicks": 0,
                    "purchases": 0,
                    "revenue": 0,
                    "impressions": 0,
                    "cpa": 0,
                    "roas": 0,
                    "cpc": 0,
                    "cpm": 0
                }
            
            month_data = monthly_data[month_key]
            month_data["spend"] += campaign.get("amount_spent_usd", 0)
            month_data["link_clicks"] += campaign.get("link_clicks", 0)
            month_data["purchases"] += campaign.get("website_purchases", 0)
            month_data["revenue"] += campaign.get("purchases_conversion_value", 0)
            month_data["impressions"] += campaign.get("impressions", 0)
        
        # Calculate derived metrics for each month
        for month_data in monthly_data.values():
            if month_data["purchases"] > 0:
                month_data["cpa"] = month_data["spend"] / month_data["purchases"]
            if month_data["spend"] > 0:
                month_data["roas"] = month_data["revenue"] / month_data["spend"]
            if month_data["link_clicks"] > 0:
                month_data["cpc"] = month_data["spend"] / month_data["link_clicks"]
            if month_data["impressions"] > 0:
                month_data["cpm"] = (month_data["spend"] / month_data["impressions"]) * 1000
        
        return sorted(monthly_data.values(), key=lambda x: x["month"])
    
    def _generate_category_breakdown(self, campaigns: List[Dict]) -> List[Dict[str, Any]]:
        """Generate category breakdown data"""
        category_data = {}
        
        for campaign in campaigns:
            category = campaign.get("category", "Uncategorized")
            
            if category not in category_data:
                category_data[category] = {
                    "category": category,
                    "amount_spent_usd": 0,
                    "website_purchases": 0,
                    "purchases_conversion_value": 0,
                    "roas": 0,
                    "cpa": 0
                }
            
            cat_data = category_data[category]
            cat_data["amount_spent_usd"] += campaign.get("amount_spent_usd", 0)
            cat_data["website_purchases"] += campaign.get("website_purchases", 0)
            cat_data["purchases_conversion_value"] += campaign.get("purchases_conversion_value", 0)
        
        # Calculate derived metrics for each category
        for cat_data in category_data.values():
            if cat_data["website_purchases"] > 0:
                cat_data["cpa"] = cat_data["amount_spent_usd"] / cat_data["website_purchases"]
            if cat_data["amount_spent_usd"] > 0:
                cat_data["roas"] = cat_data["purchases_conversion_value"] / cat_data["amount_spent_usd"]
        
        return sorted(category_data.values(), key=lambda x: x["amount_spent_usd"], reverse=True)