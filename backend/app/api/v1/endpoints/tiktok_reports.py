"""TikTok Ads reporting API endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, date
from loguru import logger
from ....services.tiktok_reporting import TikTokReportingService
from ....models.tiktok_campaign_data import TikTokDashboardFilters

router = APIRouter()
tiktok_service = TikTokReportingService()


@router.get("/dashboard")
async def get_tiktok_dashboard(
    categories: Optional[str] = Query(None, description="Comma-separated list of categories to filter by"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
) -> Dict[str, Any]:
    """
    Get TikTok dashboard data with optional filtering using the standardized TikTokReportingService
    
    Returns summary metrics, pivot table data, and category breakdown
    """
    try:
        # Build filters for table data (all historical data)
        table_filters = None
        if categories:
            table_filters = TikTokDashboardFilters()
            table_filters.categories = [cat.strip() for cat in categories.split(",")]
        
        # Build filters for KPI summary (current month only for summary)
        summary_filters = TikTokDashboardFilters()
        if categories:
            summary_filters.categories = [cat.strip() for cat in categories.split(",")]
        
        # Always filter summary to current month (August 2025) for KPI cards  
        from datetime import date
        current_date = date.today()
        current_month_start = current_date.replace(day=1)
        summary_filters.start_date = current_month_start
        
        logger.info(f"TikTok dashboard: filtering summary to {current_month_start}")
        
        # Get summary for current month only (KPI cards)
        summary = tiktok_service.get_month_to_date_summary(summary_filters)
        logger.info(f"TikTok summary result: ${summary.get('total_spend', 0):,.2f} spend")
        
        # Get all historical data for table (Jan 2024 - Aug 2025)  
        pivot_data = tiktok_service.generate_pivot_table_data(table_filters)
        categories_list = tiktok_service.get_available_categories()
        
        # Convert pivot data to the format expected by frontend
        pivot_data_formatted = []
        for pivot in pivot_data:
            pivot_data_formatted.append({
                "month": pivot.month,
                "spend": float(pivot.spend),
                "link_clicks": pivot.link_clicks,
                "purchases": pivot.purchases,
                "revenue": float(pivot.revenue),
                "cpa": float(pivot.cpa),
                "roas": float(pivot.roas),
                "cpc": float(pivot.cpc),
                "impressions": 0  # TikTok reporting service doesn't track impressions in pivot data
            })
        
        return {
            "summary": summary,
            "pivot_data": pivot_data_formatted,
            "categories": categories_list,
            "category_breakdown": []  # Not implemented in new service yet
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving TikTok dashboard data: {str(e)}")


@router.get("/monthly")
async def get_tiktok_monthly_data(
    categories: Optional[str] = Query(None, description="Comma-separated list of categories to filter by")
) -> List[Dict[str, Any]]:
    """
    Get TikTok monthly aggregated data for pivot table using the standardized service
    """
    try:
        filters = None
        if categories:
            filters = TikTokDashboardFilters()
            filters.categories = [cat.strip() for cat in categories.split(",")]
        
        pivot_data = tiktok_service.generate_pivot_table_data(filters)
        
        # Convert to the format expected by frontend
        formatted_data = []
        for pivot in pivot_data:
            formatted_data.append({
                "month": pivot.month,
                "spend": float(pivot.spend),
                "link_clicks": pivot.link_clicks,
                "purchases": pivot.purchases,
                "revenue": float(pivot.revenue),
                "cpa": float(pivot.cpa),
                "roas": float(pivot.roas),
                "cpc": float(pivot.cpc)
            })
        
        return formatted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving TikTok monthly data: {str(e)}")


@router.get("/categories")
async def get_tiktok_categories() -> Dict[str, List[str]]:
    """
    Get all available TikTok campaign categories from the standardized service
    """
    try:
        categories = tiktok_service.get_available_categories()
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving TikTok categories: {str(e)}")


@router.get("/campaigns")
async def get_tiktok_campaigns(
    start_date: Optional[str] = Query(None, description="Start date filter"),
    end_date: Optional[str] = Query(None, description="End date filter"),
    category: Optional[str] = Query(None, description="Category filter")
) -> List[Dict[str, Any]]:
    """
    Get TikTok campaigns with optional filtering
    """
    try:
        # Build query filters
        query = tiktok_service.supabase.table("tiktok_campaign_data").select("*")
        
        if category:
            query = query.eq("category", category)
        
        if start_date:
            query = query.gte("reporting_starts", start_date)
        
        if end_date:
            query = query.lte("reporting_ends", end_date)
        
        result = query.execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving TikTok campaigns: {str(e)}")


@router.post("/sync")
async def sync_tiktok_data(
    start_date: Optional[str] = Query(None, description="Start date for sync (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for sync (YYYY-MM-DD)")
) -> Dict[str, Any]:
    """
    Sync TikTok campaign data from API to database
    
    If no dates provided, syncs last 30 days
    """
    try:
        # Default to last 30 days if no dates provided
        if not start_date or not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        synced_count, message = tiktok_service.sync_campaign_data(start_date, end_date)
        
        return {
            "message": message,
            "synced": synced_count,
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing TikTok data: {str(e)}")


@router.get("/test-connection")
async def test_tiktok_connection() -> Dict[str, str]:
    """
    Test TikTok Marketing API connection
    """
    try:
        result = tiktok_service.test_connection()
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing TikTok connection: {str(e)}")


@router.get("/campaigns-list")
async def get_tiktok_campaigns_list() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get campaigns directly from TikTok API (not from database)
    """
    try:
        campaigns = tiktok_service.fetch_campaigns()
        return {"campaigns": campaigns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching TikTok campaigns from API: {str(e)}")


@router.get("/stats")
async def get_tiktok_stats() -> Dict[str, Any]:
    """
    Get TikTok campaign statistics and metrics
    """
    try:
        # Get all campaigns from database
        result = tiktok_service.supabase.table("tiktok_campaign_data").select("*").execute()
        campaigns = result.data
        
        if not campaigns:
            return {
                "total_campaigns": 0,
                "total_spend": 0,
                "total_conversions": 0,
                "total_revenue": 0,
                "date_range": "No data"
            }
        
        # Calculate stats
        total_campaigns = len(campaigns)
        total_spend = sum(c.get("amount_spent_usd", 0) for c in campaigns)
        total_conversions = sum(c.get("website_purchases", 0) for c in campaigns)
        total_revenue = sum(c.get("purchases_conversion_value", 0) for c in campaigns)
        
        # Get date range
        dates = [c.get("reporting_starts") for c in campaigns if c.get("reporting_starts")]
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            date_range = f"{min_date} to {max_date}"
        else:
            date_range = "Unknown"
        
        return {
            "total_campaigns": total_campaigns,
            "total_spend": total_spend,
            "total_conversions": total_conversions,
            "total_revenue": total_revenue,
            "date_range": date_range,
            "avg_cpa": total_spend / total_conversions if total_conversions > 0 else 0,
            "avg_roas": total_revenue / total_spend if total_spend > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving TikTok stats: {str(e)}")


@router.get("/performance-comparison")
async def get_tiktok_performance_comparison(
    months: int = Query(6, description="Number of months to compare", ge=1, le=24)
) -> Dict[str, Any]:
    """
    Get TikTok performance comparison over specified number of months
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)  # Approximate months
        
        # Get campaigns in date range
        result = tiktok_service.supabase.table("tiktok_campaign_data")\
            .select("*")\
            .gte("reporting_starts", start_date.strftime("%Y-%m-%d"))\
            .lte("reporting_ends", end_date.strftime("%Y-%m-%d"))\
            .execute()
        
        campaigns = result.data
        
        # Generate monthly comparison
        monthly_comparison = {}
        
        for campaign in campaigns:
            reporting_date = campaign.get("reporting_starts")
            if not reporting_date:
                continue
                
            try:
                month_key = datetime.strptime(reporting_date, "%Y-%m-%d").strftime("%Y-%m")
            except:
                continue
            
            if month_key not in monthly_comparison:
                monthly_comparison[month_key] = {
                    "month": month_key,
                    "spend": 0,
                    "conversions": 0,
                    "revenue": 0,
                    "campaigns": 0
                }
            
            month_data = monthly_comparison[month_key]
            month_data["spend"] += campaign.get("amount_spent_usd", 0)
            month_data["conversions"] += campaign.get("website_purchases", 0)
            month_data["revenue"] += campaign.get("purchases_conversion_value", 0)
            month_data["campaigns"] += 1
        
        # Calculate derived metrics
        for month_data in monthly_comparison.values():
            month_data["cpa"] = month_data["spend"] / month_data["conversions"] if month_data["conversions"] > 0 else 0
            month_data["roas"] = month_data["revenue"] / month_data["spend"] if month_data["spend"] > 0 else 0
        
        return {
            "months_requested": months,
            "data": sorted(monthly_comparison.values(), key=lambda x: x["month"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving TikTok performance comparison: {str(e)}")