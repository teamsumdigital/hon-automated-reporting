from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import date, datetime
from ..models.google_campaign_data import (
    GoogleCampaignDataResponse,
    GooglePivotTableData,
    GoogleDashboardFilters,
    GoogleAdsApiResponse
)
from ..models.campaign_data import (
    CategoryRule,
    CategoryOverride
)
from ..services.google_reporting import GoogleReportingService
from ..services.categorization import CategorizationService
from ..services.campaign_type_service import CampaignTypeService
from ..services.google_ads_service import GoogleAdsService

router = APIRouter(prefix="/api/google-reports", tags=["google-reports"])

def get_google_reporting_service():
    return GoogleReportingService()

def get_categorization_service():
    return CategorizationService()

def get_campaign_type_service():
    return CampaignTypeService()

def get_google_ads_service():
    return GoogleAdsService()

@router.get("/dashboard")
async def get_google_dashboard_data(
    categories: Optional[str] = Query(None, description="Comma-separated list of categories"),
    campaign_types: Optional[str] = Query(None, description="Comma-separated list of campaign types"),
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    reporting_service: GoogleReportingService = Depends(get_google_reporting_service)
):
    """
    Get Google Ads dashboard data with optional filters
    """
    try:
        filters = GoogleDashboardFilters()
        if categories:
            filters.categories = [cat.strip() for cat in categories.split(",")]
        if campaign_types:
            filters.campaign_types = [ct.strip() for ct in campaign_types.split(",")]
        if start_date:
            filters.start_date = start_date
        if end_date:
            filters.end_date = end_date
        
        # Get filtered campaign data for summary calculation
        campaigns = reporting_service.get_campaign_data(filters)
        
        # Calculate summary from actual filtered data
        if campaigns:
            total_spend = sum(float(c.amount_spent_usd) for c in campaigns)
            total_clicks = sum(c.link_clicks for c in campaigns)
            total_purchases = sum(c.website_purchases for c in campaigns)
            total_revenue = sum(float(c.purchases_conversion_value) for c in campaigns)
            
            avg_cpa = total_spend / total_purchases if total_purchases > 0 else 0
            avg_roas = total_revenue / total_spend if total_spend > 0 else 0
            avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0
            
            summary = {
                "period": "Filtered" if filters and (filters.categories or filters.start_date or filters.end_date) else "All Time",
                "total_spend": total_spend,
                "total_clicks": total_clicks,
                "total_purchases": total_purchases,
                "total_revenue": total_revenue,
                "avg_cpa": avg_cpa,
                "avg_roas": avg_roas,
                "avg_cpc": avg_cpc,
                "campaigns_count": len(campaigns)
            }
        else:
            # Fallback if no data found
            summary = {
                "period": "No Data",
                "total_spend": 0,
                "total_clicks": 0,
                "total_purchases": 0,
                "total_revenue": 0,
                "avg_cpa": 0,
                "avg_roas": 0,
                "avg_cpc": 0,
                "campaigns_count": 0
            }
        
        # Get pivot table data
        pivot_data = reporting_service.generate_pivot_table_data(filters)
        
        # Get categories and campaign types for filter dropdowns
        categories_list = reporting_service.get_available_categories()
        campaign_types_list = reporting_service.get_available_campaign_types()
        
        # Get campaign data for client-side filtering
        campaigns_data = [
            {
                "id": c.id,
                "campaign_id": c.campaign_id,
                "campaign_name": c.campaign_name,
                "category": c.category,
                "campaign_type": getattr(c, 'campaign_type', 'Unclassified'),
                "reporting_starts": c.reporting_starts.isoformat(),
                "reporting_ends": c.reporting_ends.isoformat(), 
                "amount_spent_usd": float(c.amount_spent_usd),
                "website_purchases": c.website_purchases,
                "purchases_conversion_value": float(c.purchases_conversion_value),
                "link_clicks": c.link_clicks,
                "cpa": float(c.cpa),
                "roas": float(c.roas),
                "cpc": float(c.cpc)
            }
            for c in campaigns
        ]
        
        return {
            "summary": summary,
            "pivot_data": pivot_data,
            "campaigns": campaigns_data,  # Add campaign data for client-side filtering
            "categories": categories_list,
            "campaign_types": campaign_types_list,
            "filters": filters
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Google Ads dashboard data: {str(e)}")

@router.get("/monthly")
async def get_google_monthly_data(
    categories: Optional[str] = Query(None, description="Comma-separated list of categories"),
    reporting_service: GoogleReportingService = Depends(get_google_reporting_service)
) -> List[GooglePivotTableData]:
    """
    Get Google Ads monthly breakdown data
    """
    try:
        filters = GoogleDashboardFilters()
        if categories:
            filters.categories = [cat.strip() for cat in categories.split(",")]
        
        return reporting_service.generate_pivot_table_data(filters)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Google Ads monthly data: {str(e)}")

@router.get("/campaigns")
async def get_google_campaigns_data(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    category: Optional[str] = Query(None, description="Filter by category"),
    reporting_service: GoogleReportingService = Depends(get_google_reporting_service)
) -> List[GoogleCampaignDataResponse]:
    """
    Get Google Ads campaign-level data
    """
    try:
        filters = GoogleDashboardFilters()
        if start_date:
            filters.start_date = start_date
        if end_date:
            filters.end_date = end_date
        if category:
            filters.categories = [category]
        
        return reporting_service.get_campaign_data(filters)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Google Ads campaigns data: {str(e)}")

@router.post("/sync")
async def sync_google_ads_data(
    start_date: date = Query(..., description="Start date for sync"),
    end_date: date = Query(..., description="End date for sync"),
    google_ads_service: GoogleAdsService = Depends(get_google_ads_service),
    reporting_service: GoogleReportingService = Depends(get_google_reporting_service)
):
    """
    Manually sync Google Ads data for the specified date range
    """
    try:
        # Get insights from Google Ads API
        insights = google_ads_service.get_campaign_insights(start_date, end_date)
        
        if not insights:
            return {"message": "No Google Ads data found for the specified date range", "synced": 0}
        
        # Convert to campaign data
        campaign_data_list = google_ads_service.convert_to_campaign_data(insights)
        
        # Store in database
        success = reporting_service.store_campaign_data(campaign_data_list)
        
        if success:
            return {
                "message": f"Successfully synced Google Ads data from {start_date} to {end_date}",
                "synced": len(campaign_data_list)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to store Google Ads data in database")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync Google Ads data: {str(e)}")

@router.get("/test-connection")
async def test_google_ads_connection(
    google_ads_service: GoogleAdsService = Depends(get_google_ads_service)
):
    """
    Test Google Ads API connection
    """
    try:
        is_connected = google_ads_service.test_connection()
        
        if is_connected:
            return {"status": "connected", "message": "Google Ads API connection successful"}
        else:
            return {"status": "failed", "message": "Google Ads API connection failed"}
            
    except Exception as e:
        return {"status": "error", "message": f"Google Ads API connection error: {str(e)}"}

@router.get("/categories")
async def get_google_categories(
    categorization_service: CategorizationService = Depends(get_categorization_service)
):
    """
    Get all available categories for Google Ads campaigns
    """
    try:
        categories = categorization_service.get_all_categories()
        return {"categories": categories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

@router.get("/campaign-types")
async def get_google_campaign_types(
    campaign_type_service: CampaignTypeService = Depends(get_campaign_type_service)
):
    """
    Get all available campaign types for Google Ads campaigns
    """
    try:
        campaign_types = campaign_type_service.get_all_campaign_types()
        return {"campaign_types": campaign_types}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaign types: {str(e)}")

@router.get("/campaigns-list")
async def get_google_campaigns_list(
    google_ads_service: GoogleAdsService = Depends(get_google_ads_service)
):
    """
    Get list of Google Ads campaigns from the account
    """
    try:
        campaigns = google_ads_service.get_campaigns()
        return {"campaigns": campaigns}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Google Ads campaigns list: {str(e)}")

@router.post("/categories/rules")
async def add_category_rule(
    rule: CategoryRule,
    categorization_service: CategorizationService = Depends(get_categorization_service)
):
    """
    Add a new categorization rule
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
async def add_category_override(
    override: CategoryOverride,
    categorization_service: CategorizationService = Depends(get_categorization_service)
):
    """
    Add a manual category override for a specific campaign
    """
    try:
        success = categorization_service.add_category_override(override)
        
        if success:
            return {"message": "Category override added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add category override")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add category override: {str(e)}")

@router.get("/health")
async def google_ads_health_check():
    """
    Health check endpoint for Google Ads API
    """
    return {"status": "healthy", "service": "Google Ads API"}

@router.get("/stats")
async def get_google_ads_stats(
    reporting_service: GoogleReportingService = Depends(get_google_reporting_service)
):
    """
    Get Google Ads data statistics
    """
    try:
        stats = reporting_service.get_data_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Google Ads stats: {str(e)}")