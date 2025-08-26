from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger
import os
from supabase import create_client
from ..services.tiktok_ad_level_service import TikTokAdLevelService

router = APIRouter()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

supabase = create_client(supabase_url, supabase_key)

# Simple in-memory lock to prevent concurrent syncs
_sync_in_progress = False

@router.get("/test-connection")
def test_tiktok_ad_connection():
    """
    Test TikTok Ads API connection for ad-level data
    """
    try:
        service = TikTokAdLevelService()
        if service.test_connection():
            return {"status": "success", "message": "TikTok Ads API connection successful for ad-level data"}
        else:
            return {"status": "error", "message": "TikTok Ads API connection failed"}
    except Exception as e:
        logger.error(f"TikTok ad-level connection test error: {e}")
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")

@router.post("/sync-14-days")
def sync_last_14_days_ad_data(background_tasks: BackgroundTasks):
    """
    Sync TikTok ad-level data for the last 14 days with weekly segmentation (runs in background)
    """
    global _sync_in_progress
    
    try:
        # Check if sync is already in progress
        if _sync_in_progress:
            return {
                "status": "already_running",
                "message": "14-day TikTok ad sync already in progress",
                "note": "Please wait for the current sync to complete before starting another."
            }
        
        # Start the sync in the background to avoid timeout issues
        background_tasks.add_task(perform_14_day_ad_sync)
        
        return {
            "status": "success",
            "message": "14-day TikTok ad sync started in background",
            "note": "This may take several minutes. Check the ad-data endpoint for results."
        }
        
    except Exception as e:
        logger.error(f"Error starting TikTok ad sync: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start sync: {str(e)}")

def perform_14_day_ad_sync():
    """
    Background task to perform 14-day TikTok ad sync with weekly segmentation
    """
    global _sync_in_progress
    
    try:
        _sync_in_progress = True
        logger.info("🚀 Starting TikTok ad-level 14-day sync...")
        
        service = TikTokAdLevelService()
        
        # Fetch ad-level data for last 14 days (split into weekly periods)
        ads_data = service.fetch_ad_level_data(days_back=14)
        
        if ads_data:
            # Sync to database
            synced_count, message = service.sync_ad_data_to_database(ads_data)
            
            if synced_count > 0:
                # Calculate summary for logging
                total_spend = sum(ad['amount_spent_usd'] for ad in ads_data)
                total_revenue = sum(ad['purchases_conversion_value'] for ad in ads_data)
                
                # Group by week for summary
                weekly_summary = {}
                for ad in ads_data:
                    week_key = ad['reporting_starts']  # Use start date as week key
                    if week_key not in weekly_summary:
                        weekly_summary[week_key] = {
                            'ads_count': 0,
                            'spend': 0,
                            'revenue': 0,
                            'purchases': 0,
                            'clicks': 0
                        }
                    
                    weekly_summary[week_key]['ads_count'] += 1
                    weekly_summary[week_key]['spend'] += ad['amount_spent_usd']
                    weekly_summary[week_key]['revenue'] += ad['purchases_conversion_value']
                    weekly_summary[week_key]['purchases'] += ad['website_purchases']
                    weekly_summary[week_key]['clicks'] += ad['link_clicks']
                
                logger.info(f"📈 TikTok ad sync summary: {synced_count} ads, ${round(total_spend, 2)} spend, ${round(total_revenue, 2)} revenue")
                logger.info(f"🗓️ Weekly breakdown: {len(weekly_summary)} weeks of data")
                
                # Log each week for debugging momentum indicators
                for week, stats in weekly_summary.items():
                    logger.info(f"   Week {week}: {stats['ads_count']} ads, ${stats['spend']:.2f} spend, ${stats['revenue']:.2f} revenue")
                
            else:
                logger.error("❌ TikTok ad background sync failed - Could not insert ad data")
        else:
            logger.info("✅ TikTok ad background sync completed - No ad data to insert")
            
    except Exception as e:
        logger.error(f"❌ TikTok ad background sync failed: {e}")
    finally:
        # Always clear the sync in progress flag
        _sync_in_progress = False
        logger.info("🔓 TikTok ad sync lock released")

@router.get("/ad-data")
def get_tiktok_ad_level_data(
    categories: Optional[str] = None,
    content_types: Optional[str] = None,
    formats: Optional[str] = None,
    campaign_optimizations: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get TikTok ad-level data with optional filtering
    Returns grouped ads with weekly periods for momentum indicators
    """
    try:
        service = TikTokAdLevelService()
        
        # Parse filter parameters
        category_filter = None
        if categories:
            category_filter = [cat.strip() for cat in categories.split(",")]
        
        # Get ad-level data
        result = service.get_ad_level_data(
            categories=category_filter,
            start_date=start_date,
            end_date=end_date
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching TikTok ad data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch TikTok ad data: {str(e)}")

@router.get("/summary")
def get_tiktok_ad_level_summary(
    categories: Optional[str] = None,
    content_types: Optional[str] = None,
    formats: Optional[str] = None,
    campaign_optimizations: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get TikTok ad-level summary metrics with optional filtering
    """
    try:
        service = TikTokAdLevelService()
        
        # Parse category filter
        category_filter = None
        if categories:
            category_filter = [cat.strip() for cat in categories.split(",")]
        
        # Get summary with filters applied
        summary = service.get_summary_metrics(
            categories=category_filter,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "status": "success",
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting TikTok ad summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get TikTok ad summary: {str(e)}")

@router.get("/filters")
def get_tiktok_ad_filter_options():
    """
    Get available filter options for TikTok ad-level dashboard
    """
    try:
        service = TikTokAdLevelService()
        
        # Get available categories
        categories = service.get_available_categories()
        
        # TikTok doesn't have the same content type/format structure as Meta
        # These filters might not be applicable, but keeping for consistency
        content_types = []  # TikTok ads don't have Meta's content type structure
        formats = []        # TikTok ads don't have Meta's format structure
        campaign_optimizations = []  # TikTok campaigns don't use Meta's optimization structure
        
        return {
            "status": "success",
            "filters": {
                "categories": categories,
                "content_types": content_types,
                "formats": formats,
                "campaign_optimizations": campaign_optimizations
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting TikTok ad filter options: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get filter options: {str(e)}")

@router.get("/categories")
def get_tiktok_ad_categories():
    """
    Get all available categories for TikTok ads
    """
    try:
        service = TikTokAdLevelService()
        categories = service.get_available_categories()
        
        return {
            "status": "success",
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"Error getting TikTok ad categories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

# Health check endpoint
@router.get("/health")
def health_check():
    """Health check for TikTok ad-level service"""
    try:
        # Test database connection
        result = supabase.table("tiktok_ad_data").select("id").limit(1).execute()
        
        return {
            "status": "healthy",
            "service": "TikTok Ad-Level Reports",
            "database": "connected" if result else "disconnected",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "TikTok Ad-Level Reports", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }