from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import date, datetime
from ..models.tiktok_campaign_data import (
    TikTokCampaignDataResponse,
    TikTokPivotTableData,
    TikTokDashboardFilters,
    TikTokApiResponse
)
from ..models.campaign_data import (
    CategoryRule,
    CategoryOverride
)
from ..services.tiktok_reporting import TikTokReportingService
from ..services.categorization import CategorizationService
from ..services.tiktok_ads_service import TikTokAdsService

router = APIRouter(prefix="/api/tiktok-reports", tags=["tiktok-reports"])

def get_tiktok_reporting_service():
    return TikTokReportingService()

def get_categorization_service():
    return CategorizationService()

def get_tiktok_ads_service():
    try:
        return TikTokAdsService()
    except ValueError as e:
        # Return None if credentials are not configured
        return None

@router.get("/dashboard")
async def get_tiktok_dashboard_data(
    categories: Optional[str] = Query(None, description="Comma-separated list of categories"),
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    reporting_service: TikTokReportingService = Depends(get_tiktok_reporting_service)
):
    """
    Get TikTok Ads dashboard data with optional filters
    """
    try:
        filters = TikTokDashboardFilters()
        if categories:
            filters.categories = [cat.strip() for cat in categories.split(",")]
        if start_date:
            filters.start_date = start_date
        if end_date:
            filters.end_date = end_date
        
        # Get month-to-date summary
        summary = reporting_service.get_month_to_date_summary()
        
        # Get pivot table data
        pivot_data = reporting_service.generate_pivot_table_data(filters)
        
        # Get categories for filter dropdown
        categories_list = reporting_service.get_available_categories()
        
        return {
            "summary": summary,
            "pivot_data": pivot_data,
            "categories": categories_list,
            "filters": filters
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get TikTok dashboard data: {str(e)}")

@router.get("/monthly")
async def get_tiktok_monthly_data(
    categories: Optional[str] = Query(None, description="Comma-separated list of categories"),
    reporting_service: TikTokReportingService = Depends(get_tiktok_reporting_service)
) -> List[TikTokPivotTableData]:
    """
    Get TikTok Ads monthly breakdown data
    """
    try:
        filters = TikTokDashboardFilters()
        if categories:
            filters.categories = [cat.strip() for cat in categories.split(",")]
        
        return reporting_service.generate_pivot_table_data(filters)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get TikTok monthly data: {str(e)}")

@router.get("/campaigns")
async def get_tiktok_campaigns_data(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    category: Optional[str] = Query(None, description="Filter by category"),
    reporting_service: TikTokReportingService = Depends(get_tiktok_reporting_service)
) -> List[TikTokCampaignDataResponse]:
    """
    Get TikTok Ads campaign-level data
    """
    try:
        filters = TikTokDashboardFilters()
        if start_date:
            filters.start_date = start_date
        if end_date:
            filters.end_date = end_date
        if category:
            filters.categories = [category]
        
        return reporting_service.get_campaign_data(filters)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get TikTok campaigns data: {str(e)}")

@router.post("/sync")
async def sync_tiktok_ads_data(
    start_date: date = Query(..., description="Start date for sync"),
    end_date: date = Query(..., description="End date for sync"),
    tiktok_ads_service = Depends(get_tiktok_ads_service),
    reporting_service: TikTokReportingService = Depends(get_tiktok_reporting_service)
):
    """
    Manually sync TikTok Ads data for the specified date range
    """
    try:
        if tiktok_ads_service is None:
            raise HTTPException(status_code=503, detail="TikTok Ads API not configured. Please set up credentials.")
        
        # Get insights from TikTok Ads API
        insights = tiktok_ads_service.get_campaign_insights(start_date, end_date)
        
        if not insights:
            return {"message": "No TikTok Ads data found for the specified date range", "synced": 0}
        
        # Convert to campaign data
        campaign_data_list = tiktok_ads_service.convert_to_campaign_data(insights)
        
        # Store in database
        success = reporting_service.store_campaign_data(campaign_data_list)
        
        if success:
            return {
                "message": f"Successfully synced TikTok Ads data from {start_date} to {end_date}",
                "synced": len(campaign_data_list)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to store TikTok Ads data in database")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync TikTok Ads data: {str(e)}")

@router.get("/test-connection")
async def test_tiktok_ads_connection(
    tiktok_ads_service = Depends(get_tiktok_ads_service)
):
    """
    Test TikTok Ads API connection
    """
    try:
        if tiktok_ads_service is None:
            return {
                "status": "not_configured",
                "message": "TikTok Ads API credentials not configured"
            }
        
        is_connected = tiktok_ads_service.test_connection()
        
        if is_connected:
            return {"status": "connected", "message": "TikTok Ads API connection successful"}
        else:
            return {"status": "failed", "message": "TikTok Ads API connection failed"}
            
    except Exception as e:
        return {"status": "error", "message": f"TikTok Ads API connection error: {str(e)}"}

@router.get("/categories")
async def get_tiktok_categories(
    categorization_service: CategorizationService = Depends(get_categorization_service)
):
    """
    Get all available categories for TikTok Ads campaigns
    """
    try:
        # Use the same categorization system as Meta/Google
        categories = categorization_service.get_all_categories()
        return {"categories": categories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

@router.get("/campaigns-list")
async def get_tiktok_campaigns_list(
    tiktok_ads_service = Depends(get_tiktok_ads_service)
):
    """
    Get list of TikTok Ads campaigns from the account
    """
    try:
        if tiktok_ads_service is None:
            raise HTTPException(status_code=503, detail="TikTok Ads API not configured")
        
        campaigns = tiktok_ads_service.get_campaigns()
        return {"campaigns": campaigns}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get TikTok campaigns list: {str(e)}")

@router.post("/categories/rules")
async def add_category_rule(
    rule: CategoryRule,
    categorization_service: CategorizationService = Depends(get_categorization_service)
):
    """
    Add a new categorization rule (shared across all platforms)
    """
    try:
        success = categorization_service.add_category_rule(rule)
        
        if success:
            return {"message": "Category rule added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add category rule")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add category rule: {str(e)}")

@router.post("/categories/overrides")
async def add_tiktok_category_override(
    override: CategoryOverride,
    categorization_service: CategorizationService = Depends(get_categorization_service)
):
    """
    Add a manual category override for a specific TikTok campaign
    """
    try:
        # Add platform-specific override for TikTok
        success = categorization_service.add_category_override(override)
        
        if success:
            return {"message": "TikTok category override added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add TikTok category override")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add TikTok category override: {str(e)}")

@router.get("/health")
async def tiktok_ads_health_check():
    """
    Health check endpoint for TikTok Ads API
    """
    return {"status": "healthy", "service": "TikTok Ads API"}

@router.get("/stats")
async def get_tiktok_ads_stats(
    reporting_service: TikTokReportingService = Depends(get_tiktok_reporting_service)
):
    """
    Get TikTok Ads data statistics
    """
    try:
        stats = reporting_service.get_data_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get TikTok Ads stats: {str(e)}")

@router.get("/performance-comparison")
async def get_tiktok_performance_comparison(
    months: int = Query(6, description="Number of months to compare"),
    reporting_service: TikTokReportingService = Depends(get_tiktok_reporting_service)
):
    """
    Get performance comparison for TikTok Ads
    """
    try:
        comparison = reporting_service.get_performance_comparison(months)
        return comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get TikTok performance comparison: {str(e)}")

@router.delete("/campaigns/data")
async def delete_tiktok_campaign_data(
    start_date: date = Query(..., description="Start date for deletion"),
    end_date: date = Query(..., description="End date for deletion"),
    campaign_ids: Optional[str] = Query(None, description="Comma-separated campaign IDs"),
    reporting_service: TikTokReportingService = Depends(get_tiktok_reporting_service)
):
    """
    Delete TikTok campaign data for specified date range
    """
    try:
        campaign_ids_list = None
        if campaign_ids:
            campaign_ids_list = [cid.strip() for cid in campaign_ids.split(",")]
        
        success = reporting_service.delete_campaign_data(start_date, end_date, campaign_ids_list)
        
        if success:
            return {"message": f"Successfully deleted TikTok campaign data from {start_date} to {end_date}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete TikTok campaign data")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete TikTok campaign data: {str(e)}")

@router.get("/sandbox-status")
async def get_tiktok_sandbox_status(
    tiktok_ads_service = Depends(get_tiktok_ads_service)
):
    """
    Check if TikTok API is in sandbox mode
    """
    try:
        if tiktok_ads_service is None:
            return {"sandbox_mode": False, "configured": False}
        
        return {
            "sandbox_mode": tiktok_ads_service.sandbox_mode,
            "configured": True,
            "base_url": tiktok_ads_service.base_url
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get TikTok sandbox status: {str(e)}")