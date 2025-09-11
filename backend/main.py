from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from loguru import logger

# Load environment variables
load_dotenv()

# Import routers
from app.api.reports import router as reports_router
from app.api.google_reports import router as google_reports_router
from app.api.tiktok_reports import router as tiktok_reports_router
from app.api.meta_ad_reports import router as meta_ad_reports_router
from app.api.tiktok_ad_reports import router as tiktok_ad_reports_router
from app.api.webhook import router as webhook_router
from app.api.ad_status_sync import router as ad_status_sync_router

# Configure logging with crash detection
logger.add("logs/hon_reporting.log", rotation="1 day", retention="30 days", level="INFO")
logger.add("logs/hon_errors.log", rotation="1 day", retention="30 days", level="ERROR")

# Add startup/shutdown logging
import atexit
import signal
import sys

def log_shutdown(signal_num=None, frame=None):
    if signal_num:
        logger.error(f"💥 SERVER CRASH/FORCED SHUTDOWN - Signal {signal_num} received")
    else:
        logger.info("🛑 SERVER SHUTDOWN - Clean shutdown initiated")
    logger.info(f"⏰ SHUTDOWN TIME: {__import__('datetime').datetime.now().isoformat()}")

# Register shutdown handlers
atexit.register(log_shutdown)
signal.signal(signal.SIGTERM, log_shutdown)  # Termination signal
signal.signal(signal.SIGINT, log_shutdown)   # Ctrl+C

app = FastAPI(
    title="HON Automated Reporting API",
    description="Meta Ads, Google Ads, and TikTok Ads reporting automation with categorization and pivot tables",
    version="1.2.0"
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"💥 UNHANDLED EXCEPTION: {type(exc).__name__}: {str(exc)}")
    logger.error(f"🌐 REQUEST: {request.method} {request.url}")
    logger.error(f"📍 EXCEPTION DETAILS:", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__}
    )

# CORS middleware - Configure allowed origins
allowed_origins = [
    "http://localhost:3007",  # Development frontend
    "http://localhost:3000",  # Legacy development port
    "https://hon-automated-reporting.netlify.app",  # Production frontend
]

# Allow all origins in development, restrict in production
if os.getenv("ENVIRONMENT") == "production":
    origins = [origin for origin in allowed_origins if origin.startswith("https://")]
else:
    origins = allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reports_router)
app.include_router(google_reports_router)
app.include_router(tiktok_reports_router)
app.include_router(meta_ad_reports_router, prefix="/api/meta-ad-reports", tags=["Meta Ad Level Reports"])
app.include_router(tiktok_ad_reports_router, prefix="/api/tiktok-ad-reports", tags=["TikTok Ad Level Reports"])
app.include_router(webhook_router)
app.include_router(ad_status_sync_router)

@app.get("/list-tables")
async def list_tables():
    """List all available tables to find the correct Meta ad table name"""
    
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        supabase = create_client(supabase_url, supabase_key)
        
        # Query information_schema to get table names
        response = supabase.rpc('get_table_names').execute()
        
        if response.data:
            return {"tables": response.data}
        
        # Alternative approach - try common table names
        common_tables = [
            'meta_ad_data',
            'meta_ad_level_data', 
            'meta_ads',
            'campaign_data',
            'ad_data'
        ]
        
        existing_tables = []
        for table_name in common_tables:
            try:
                test_response = supabase.table(table_name).select('*').limit(1).execute()
                existing_tables.append({
                    "table": table_name,
                    "status": "exists",
                    "record_count": len(test_response.data)
                })
            except Exception as e:
                existing_tables.append({
                    "table": table_name,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "message": "Testing common table names",
            "table_tests": existing_tables
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/test-existing-thumbnails")
async def test_existing_thumbnails():
    """Test thumbnail quality from existing database data"""
    
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        supabase = create_client(supabase_url, supabase_key)
        
        # Get recent ads with thumbnails from database
        response = supabase.table('meta_ad_data').select(
            'ad_id, ad_name, thumbnail_url'
        ).not_.is_('thumbnail_url', 'null').limit(5).execute()
        
        if not response.data:
            return {"error": "No ads with thumbnails found in database"}
        
        # Analyze existing thumbnail URLs
        results = []
        for ad in response.data:
            thumbnail_url = ad['thumbnail_url']
            
            # Analyze URL quality
            if any(size in thumbnail_url for size in ['1080x1080', '600x600', '400x400']):
                quality = "HIGH-RES (400x400+)"
                status = "success"
            elif any(size in thumbnail_url for size in ['320x320', '192x192']):
                quality = "MEDIUM-RES (192x192+)"
                status = "good"  
            elif 'p64x64' in thumbnail_url:
                quality = "LOW-RES (64x64)"
                status = "fallback"
            else:
                quality = "UNKNOWN"
                status = "unknown"
                
            results.append({
                "ad_id": ad['ad_id'],
                "ad_name": ad['ad_name'][:50] + "..." if len(ad['ad_name']) > 50 else ad['ad_name'],
                "thumbnail_url": thumbnail_url,
                "estimated_quality": quality,
                "status": status
            })
        
        # Summary
        high_res_count = sum(1 for r in results if r['status'] == 'success')
        total_count = len(results)
        
        return {
            "test_summary": {
                "source": "existing_database_data",
                "total_ads_tested": total_count,
                "high_res_thumbnails": high_res_count,
                "success_rate": f"{(high_res_count/total_count)*100:.1f}%" if total_count > 0 else "0%",
                "system_working": high_res_count > 0,
                "note": "Testing existing thumbnails (no new API calls)"
            },
            "thumbnail_results": results,
            "next_steps": [
                "Copy a thumbnail URL and test in browser",
                "If still 64x64, wait for rate limit reset and run full sync",
                "Check logs during next sync for high-res indicators"
            ]
        }
        
    except Exception as e:
        logger.error(f"Database thumbnail test error: {e}")
        return {"error": str(e)}

@app.get("/test-thumbnails")
async def test_thumbnails():
    """Test the new high-resolution thumbnail system"""
    
    try:
        from app.services.meta_ad_level_service import MetaAdLevelService
        
        service = MetaAdLevelService()
        
        # Get 3 recent ads for testing  
        recent_ads = service.ad_account.get_ads(fields=['id', 'name'], params={'limit': 3})
        test_ad_ids = [ad['id'] for ad in list(recent_ads)]
        
        if not test_ad_ids:
            return {"error": "No ads found for testing"}
        
        # Test the new thumbnail system
        thumbnails = service.get_ad_thumbnails(test_ad_ids)
        
        # Analyze results
        results = []
        for ad_id, thumbnail_url in thumbnails.items():
            # Determine likely quality based on URL patterns
            if any(size in thumbnail_url for size in ['1080x1080', '600x600', '400x400']):
                quality = "HIGH-RES (400x400+)"
                status = "success"
            elif any(size in thumbnail_url for size in ['320x320', '192x192']):
                quality = "MEDIUM-RES (192x192+)"
                status = "good"
            elif 'p64x64' in thumbnail_url:
                quality = "LOW-RES (64x64)"
                status = "fallback"
            else:
                quality = "UNKNOWN"
                status = "unknown"
                
            results.append({
                "ad_id": ad_id,
                "thumbnail_url": thumbnail_url,
                "estimated_quality": quality,
                "status": status
            })
        
        # Summary
        high_res_count = sum(1 for r in results if r['status'] == 'success')
        total_count = len(results)
        
        return {
            "test_summary": {
                "total_ads_tested": total_count,
                "high_res_thumbnails": high_res_count,
                "success_rate": f"{(high_res_count/total_count)*100:.1f}%" if total_count > 0 else "0%",
                "system_working": high_res_count > 0
            },
            "thumbnail_results": results,
            "next_steps": [
                "Copy a thumbnail URL and test in browser",
                "If image is large/clear, run full N8N sync",
                "Check dashboard for improved hover zoom quality"
            ]
        }
        
    except Exception as e:
        logger.error(f"Thumbnail test error: {e}")
        return {"error": str(e)}

@app.post("/upgrade-thumbnails")
async def upgrade_thumbnails():
    """Upgrade existing thumbnail URLs from 64x64 to 400x400 without API calls"""
    
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        supabase = create_client(supabase_url, supabase_key)
        
        # Get all records with p64x64 thumbnails
        response = supabase.table('meta_ad_data').select(
            'ad_id, thumbnail_url'
        ).like('thumbnail_url', '%p64x64%').execute()
        
        if not response.data:
            return {"message": "No thumbnails found with p64x64", "upgraded": 0}
        
        upgraded_count = 0
        failed_count = 0
        
        # Upgrade each thumbnail URL
        for record in response.data:
            ad_id = record['ad_id']
            original_url = record['thumbnail_url']
            
            # Apply URL upgrade
            upgraded_url = original_url
            if 'p64x64' in original_url:
                upgraded_url = original_url.replace('p64x64', 'p400x400')
            
            if upgraded_url != original_url:
                try:
                    update_response = supabase.table('meta_ad_data').update({
                        'thumbnail_url': upgraded_url
                    }).eq('ad_id', ad_id).execute()
                    
                    if update_response.data:
                        upgraded_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    failed_count += 1
        
        return {
            "status": "success",
            "message": f"Upgraded {upgraded_count} thumbnails from 64x64 to 400x400",
            "total_found": len(response.data),
            "successfully_upgraded": upgraded_count,
            "failed_upgrades": failed_count,
            "upgrade_working": upgraded_count > 0
        }
        
    except Exception as e:
        logger.error(f"Thumbnail upgrade error: {e}")
        return {"error": str(e)}

@app.get("/tables")
async def list_tables():
    """List all available tables to find the correct Meta ad table name"""
    
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        supabase = create_client(supabase_url, supabase_key)
        
        # Try common table names
        common_tables = [
            'meta_ad_data',
            'meta_ad_level_data', 
            'meta_ads',
            'campaign_data',
            'ad_data',
            'ads'
        ]
        
        existing_tables = []
        for table_name in common_tables:
            try:
                test_response = supabase.table(table_name).select('*').limit(1).execute()
                existing_tables.append({
                    "table": table_name,
                    "status": "exists",
                    "columns": list(test_response.data[0].keys()) if test_response.data else [],
                    "has_thumbnail_url": "thumbnail_url" in (test_response.data[0].keys() if test_response.data else [])
                })
            except Exception as e:
                existing_tables.append({
                    "table": table_name,
                    "status": "not_found"
                })
        
        return {
            "message": "Testing common table names",
            "table_tests": existing_tables,
            "working_tables": [t for t in existing_tables if t["status"] == "exists"]
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def root():
    return {
        "message": "HON Automated Reporting API",
        "version": "1.2.0",
        "status": "active",
        "platforms": ["Meta Ads", "Google Ads", "TikTok Ads"],
        "endpoints": {
            "meta_ads": {
                "dashboard": "/api/reports/dashboard",
                "monthly": "/api/reports/monthly", 
                "sync": "/api/reports/sync",
                "test": "/api/reports/test-connection"
            },
            "google_ads": {
                "dashboard": "/api/google-reports/dashboard",
                "monthly": "/api/google-reports/monthly",
                "sync": "/api/google-reports/sync", 
                "test": "/api/google-reports/test-connection"
            },
            "tiktok_ads": {
                "dashboard": "/api/tiktok-reports/dashboard",
                "monthly": "/api/tiktok-reports/monthly",
                "sync": "/api/tiktok-reports/sync",
                "test": "/api/tiktok-reports/test-connection"
            },
            "meta_ad_level": {
                "ad_data": "/api/meta-ad-reports/ad-data",
                "summary": "/api/meta-ad-reports/summary",
                "filters": "/api/meta-ad-reports/filters",
                "sync_14_days": "/api/meta-ad-reports/sync-14-days",
                "update_status": "/api/meta-ad-reports/update-status",
                "status_counts": "/api/meta-ad-reports/status-counts",
                "test": "/api/meta-ad-reports/test-connection"
            },
            "tiktok_ad_level": {
                "ad_data": "/api/tiktok-ad-reports/ad-data",
                "summary": "/api/tiktok-ad-reports/summary", 
                "filters": "/api/tiktok-ad-reports/filters",
                "sync_14_days": "/api/tiktok-ad-reports/sync-14-days",
                "categories": "/api/tiktok-ad-reports/categories",
                "test": "/api/tiktok-ad-reports/test-connection"
            },
            "webhook": "/api/webhook/n8n-trigger"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug_mode": os.getenv("DEBUG_MODE", "false").lower() == "true"
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8007))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 STARTING HON AUTOMATED REPORTING API on {host}:{port}")
    logger.info(f"⏰ SERVER START TIME: {__import__('datetime').datetime.now().isoformat()}")
    logger.info(f"🔧 ENVIRONMENT: {os.getenv('APP_ENV', 'production')}")
    logger.info(f"📝 LOGGING SETUP: Main log=logs/hon_reporting.log, Errors=logs/hon_errors.log")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG_MODE", "false").lower() == "true"
    )