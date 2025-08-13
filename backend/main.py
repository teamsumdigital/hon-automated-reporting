from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from loguru import logger

# Load environment variables
load_dotenv()

# Import routers
from app.api.reports import router as reports_router
from app.api.webhook import router as webhook_router

# Configure logging
logger.add("logs/hon_reporting.log", rotation="1 day", retention="30 days", level="INFO")

app = FastAPI(
    title="HON Automated Reporting API",
    description="Meta Ads reporting automation with categorization and pivot tables",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reports_router)
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {
        "message": "HON Automated Reporting API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "dashboard": "/api/reports/dashboard",
            "pivot_table": "/api/reports/pivot-table",
            "sync": "/api/reports/sync",
            "webhook": "/api/webhook/n8n-trigger"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": os.getenv("APP_ENV", "development"),
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