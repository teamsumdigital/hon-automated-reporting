from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import date
from loguru import logger
from ..services.reporting import ReportingService

router = APIRouter(prefix="/api/webhook", tags=["webhook"])

class N8NWebhookPayload(BaseModel):
    trigger: str  # "scheduled_sync", "manual_sync", etc.
    target_date: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@router.post("/n8n-trigger")
async def handle_n8n_webhook(
    payload: N8NWebhookPayload,
    background_tasks: BackgroundTasks
):
    """
    Handle webhook triggers from n8n workflows
    """
    try:
        logger.info(f"Received n8n webhook: {payload.trigger}")
        
        # Parse target date if provided
        target_date = None
        if payload.target_date:
            try:
                target_date = date.fromisoformat(payload.target_date)
            except ValueError:
                logger.error(f"Invalid date format: {payload.target_date}")
        
        if payload.trigger == "scheduled_sync":
            # Schedule background task for data sync
            background_tasks.add_task(sync_meta_data_background, target_date, payload.metadata)
            return {
                "status": "accepted", 
                "message": "Scheduled sync initiated",
                "target_date": payload.target_date
            }
        
        elif payload.trigger == "manual_sync":
            # Immediate sync for manual triggers
            reporting_service = ReportingService()
            result = reporting_service.sync_meta_data(target_date)
            return {
                "status": "completed",
                "result": result
            }
        
        elif payload.trigger == "test":
            return {
                "status": "success",
                "message": "Webhook endpoint is working",
                "timestamp": date.today().isoformat()
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown trigger: {payload.trigger}")
    
    except Exception as e:
        logger.error(f"Error handling n8n webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def sync_meta_data_background(target_date: Optional[date], metadata: Optional[Dict[str, Any]]):
    """
    Background task for syncing Meta Ads data
    """
    try:
        logger.info(f"Starting background sync for {target_date}")
        
        reporting_service = ReportingService()
        result = reporting_service.sync_meta_data(target_date)
        
        if result["success"]:
            logger.info(f"Background sync completed: {result['message']}")
        else:
            logger.error(f"Background sync failed: {result['message']}")
        
        # TODO: Could send notification back to n8n or other systems here
        
    except Exception as e:
        logger.error(f"Error in background sync: {e}")

@router.post("/test")
async def test_webhook():
    """
    Simple webhook test endpoint
    """
    return {
        "status": "success",
        "message": "Webhook endpoint is working",
        "timestamp": date.today().isoformat()
    }

@router.get("/status")
async def get_webhook_status():
    """
    Get webhook endpoint status
    """
    return {
        "status": "active",
        "endpoints": [
            "/api/webhook/n8n-trigger",
            "/api/webhook/test"
        ],
        "supported_triggers": [
            "scheduled_sync",
            "manual_sync", 
            "test"
        ]
    }