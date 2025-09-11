"""
Ad Status Sync API - Separate endpoints for managing ad status synchronization

This API provides endpoints to safely sync real ad status from Meta API
without interfering with the main data sync process.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
from loguru import logger
from ..services.ad_status_sync_service import AdStatusSyncService

router = APIRouter(prefix="/api/ad-status", tags=["ad-status"])

class StatusSyncRequest(BaseModel):
    batch_size: int = 20
    max_ads: Optional[int] = None
    dry_run: bool = False

class StatusSyncResponse(BaseModel):
    success: bool
    total_ads_processed: int
    fetch_duration_seconds: float
    total_duration_seconds: float
    database_updates: Dict[str, Any]
    status_distribution: Dict[str, int]
    message: Optional[str] = None
    error: Optional[str] = None

@router.post("/sync", response_model=StatusSyncResponse)
async def sync_ad_status(request: StatusSyncRequest):
    """
    Sync real ad status from Meta API to database
    
    This endpoint safely fetches real ad status from Meta API and updates
    the database without interfering with the main data sync process.
    
    Args:
        batch_size: Number of ads to process per batch (default 20)
        max_ads: Maximum number of ads to process (for testing, default None = all)
        dry_run: If true, fetch status but don't update database
    """
    try:
        logger.info(f"🚀 Ad status sync API called: {request}")
        
        # Initialize status sync service
        status_service = AdStatusSyncService()
        
        if request.dry_run:
            logger.info("🔬 DRY RUN MODE: Will fetch status but not update database")
            # TODO: Implement dry run logic
            return StatusSyncResponse(
                success=True,
                total_ads_processed=0,
                fetch_duration_seconds=0.0,
                total_duration_seconds=0.0,
                database_updates={},
                status_distribution={},
                message="Dry run not yet implemented"
            )
        
        # Run the status sync
        result = status_service.sync_ad_status(
            batch_size=request.batch_size,
            max_ads=request.max_ads
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=500, 
                detail=f"Status sync failed: {result.get('error', 'Unknown error')}"
            )
        
        return StatusSyncResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Ad status sync API error: {e}")
        raise HTTPException(status_code=500, detail=f"Status sync failed: {str(e)}")

@router.get("/preview")
async def preview_ads_for_status_sync(
    limit: int = Query(50, description="Number of ads to preview")
):
    """
    Preview which ads would be processed for status sync
    
    This endpoint shows a preview of ads in the database that need status updates
    without actually performing any Meta API calls or database updates.
    """
    try:
        logger.info(f"🔍 Previewing ads for status sync (limit={limit})")
        
        # Initialize status sync service
        status_service = AdStatusSyncService()
        
        # Get ads that need status update
        ads = status_service.get_ads_needing_status_update()
        
        # Limit results for preview
        preview_ads = ads[:limit] if ads else []
        
        # Generate summary stats
        total_ads = len(ads)
        status_distribution = {}
        
        for ad in ads:
            status = ad.get('status', 'unknown')
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        return {
            "success": True,
            "total_ads_in_database": total_ads,
            "preview_limit": limit,
            "preview_ads": preview_ads,
            "current_status_distribution": status_distribution,
            "message": f"Found {total_ads} unique ads in database ready for status sync"
        }
        
    except Exception as e:
        logger.error(f"❌ Ad status preview error: {e}")
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

@router.get("/status")
async def get_status_sync_info():
    """
    Get information about the status sync system
    
    Returns current configuration and system status without performing any operations.
    """
    try:
        return {
            "success": True,
            "system": "Ad Status Sync Service",
            "version": "1.0",
            "description": "Separate workflow for syncing real ad status from Meta API",
            "features": [
                "Batched Meta API status fetching",
                "Safe database updates", 
                "Rate limiting protection",
                "Independent from main data sync"
            ],
            "default_batch_size": 20,
            "rate_limiting": "2 seconds between batches",
            "status_mapping": {
                "ACTIVE": "active",
                "PAUSED": "paused", 
                "DELETED": "paused",
                "ARCHIVED": "paused",
                "UNKNOWN": "active",
                "ERROR": "active"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Status info error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status info: {str(e)}")

@router.post("/test")
async def test_status_sync_small_batch():
    """
    Test the status sync with a small batch of 5 ads
    
    This is a safe test endpoint that processes only 5 ads to verify
    the system is working correctly before running larger syncs.
    """
    try:
        logger.info("🧪 Running small batch test (5 ads)")
        
        # Initialize status sync service
        status_service = AdStatusSyncService()
        
        # Run with very small batch for testing
        result = status_service.sync_ad_status(
            batch_size=5,
            max_ads=5
        )
        
        return {
            "test_mode": True,
            "max_ads_processed": 5,
            **result
        }
        
    except Exception as e:
        logger.error(f"❌ Status sync test error: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")