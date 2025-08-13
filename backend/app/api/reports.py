from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import date, datetime
from ..models.campaign_data import (
    CampaignDataResponse, 
    PivotTableData, 
    DashboardFilters,
    CategoryRule,
    CategoryOverride
)
from ..services.reporting import ReportingService
from ..services.categorization import CategorizationService
from ..services.meta_api import MetaAdsService

router = APIRouter(prefix="/api/reports", tags=["reports"])

def get_reporting_service():
    return ReportingService()

def get_categorization_service():
    return CategorizationService()

def get_meta_service():
    return MetaAdsService()

@router.get("/dashboard")
async def get_dashboard_data(
    categories: Optional[str] = Query(None, description="Comma-separated list of categories"),
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    reporting_service: ReportingService = Depends(get_reporting_service)
):
    """
    Get dashboard data with optional filters
    """
    try:
        filters = DashboardFilters()
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
        
        # Get category breakdown
        category_breakdown = reporting_service.get_category_breakdown(filters)
        
        return {
            "summary": summary,
            "pivot_data": pivot_data,
            "category_breakdown": category_breakdown,
            "filters_applied": filters.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pivot-table")
async def get_pivot_table(
    categories: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    reporting_service: ReportingService = Depends(get_reporting_service)
) -> List[PivotTableData]:
    """
    Get pivot table data similar to Excel pivot
    """
    try:
        filters = DashboardFilters()
        if categories:
            filters.categories = [cat.strip() for cat in categories.split(",")]
        if start_date:
            filters.start_date = start_date
        if end_date:
            filters.end_date = end_date
        
        return reporting_service.generate_pivot_table_data(filters)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/month-to-date")
async def get_month_to_date(
    target_date: Optional[date] = Query(None, description="Target date for MTD calculation"),
    reporting_service: ReportingService = Depends(get_reporting_service)
):
    """
    Get month-to-date summary
    """
    try:
        return reporting_service.get_month_to_date_summary(target_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns")
async def get_campaigns(
    categories: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    reporting_service: ReportingService = Depends(get_reporting_service)
):
    """
    Get campaign data with filters
    """
    try:
        filters = DashboardFilters()
        if categories:
            filters.categories = [cat.strip() for cat in categories.split(",")]
        if start_date:
            filters.start_date = start_date
        if end_date:
            filters.end_date = end_date
        
        return reporting_service.get_campaign_data(filters, start_date, end_date)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def sync_meta_data(
    target_date: Optional[date] = None,
    reporting_service: ReportingService = Depends(get_reporting_service)
):
    """
    Sync data from Meta Ads API
    """
    try:
        result = reporting_service.sync_meta_data(target_date)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_categories(
    categorization_service: CategorizationService = Depends(get_categorization_service)
):
    """
    Get all available categories
    """
    try:
        return categorization_service.get_all_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/category-breakdown")
async def get_category_breakdown(
    categories: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    reporting_service: ReportingService = Depends(get_reporting_service)
):
    """
    Get performance breakdown by category
    """
    try:
        filters = DashboardFilters()
        if categories:
            filters.categories = [cat.strip() for cat in categories.split(",")]
        if start_date:
            filters.start_date = start_date
        if end_date:
            filters.end_date = end_date
        
        return reporting_service.get_category_breakdown(filters)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/category-rules")
async def get_category_rules(
    categorization_service: CategorizationService = Depends(get_categorization_service)
):
    """
    Get all category rules
    """
    try:
        return categorization_service.get_category_rules()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/category-rules")
async def add_category_rule(
    rule: CategoryRule,
    categorization_service: CategorizationService = Depends(get_categorization_service)
):
    """
    Add a new category rule
    """
    try:
        success = categorization_service.add_category_rule(rule)
        if success:
            return {"message": "Category rule added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add category rule")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/category-overrides")
async def add_category_override(
    override: CategoryOverride,
    categorization_service: CategorizationService = Depends(get_categorization_service)
):
    """
    Add a manual category override
    """
    try:
        success = categorization_service.add_category_override(override)
        if success:
            return {"message": "Category override added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add category override")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monthly")
async def get_monthly_data(
    categories: Optional[str] = Query(None, description="Comma-separated list of categories"),
    reporting_service: ReportingService = Depends(get_reporting_service)
):
    """
    Get monthly reporting data with category filtering
    """
    try:
        filters = DashboardFilters()
        if categories:
            filters.categories = [cat.strip() for cat in categories.split(",")]
        
        # Get monthly breakdown
        monthly_breakdown = reporting_service.get_monthly_breakdown(filters)
        
        # Get overall summary for filtered categories
        summary = reporting_service.get_filtered_summary(filters)
        
        # Get available categories for the slicer
        all_categories = reporting_service.get_available_categories()
        
        return {
            "summary": summary,
            "monthly_breakdown": monthly_breakdown,
            "available_categories": all_categories,
            "filters_applied": filters.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-connection")
async def test_meta_connection(
    meta_service: MetaAdsService = Depends(get_meta_service)
):
    """
    Test Meta Ads API connection
    """
    try:
        success = meta_service.test_connection()
        if success:
            return {"status": "connected", "message": "Meta Ads API connection successful"}
        else:
            return {"status": "failed", "message": "Meta Ads API connection failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))