from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from loguru import logger

# Load environment variables
load_dotenv()

# Import routers
from app.api.reports import router as reports_router
from app.api.google_reports import router as google_reports_router
from app.api.v1.endpoints.tiktok_reports import router as tiktok_reports_router
from app.api.webhook import router as webhook_router

# Configure logging
logger.add("logs/hon_reporting.log", rotation="1 day", retention="30 days", level="INFO")

app = FastAPI(
    title="HON Automated Reporting API",
    description="Meta Ads, Google Ads, and TikTok Ads reporting automation with categorization and pivot tables",
    version="1.2.0"
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
app.include_router(tiktok_reports_router, prefix="/api/tiktok-reports", tags=["TikTok Reports"])
app.include_router(webhook_router)

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
    
    logger.info(f"Starting HON Automated Reporting API on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG_MODE", "false").lower() == "true"
    )