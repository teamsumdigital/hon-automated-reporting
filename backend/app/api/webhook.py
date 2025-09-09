from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import date
import os
from loguru import logger
from ..services.reporting import ReportingService

router = APIRouter(prefix="/api/webhook", tags=["webhook"])

# Global sync status tracking
_sync_status = {
    "in_progress": False,
    "started_at": None,
    "last_message": None
}

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
        logger.info(f"🎯 WEBHOOK RECEIVED: trigger='{payload.trigger}', target_date='{payload.target_date}', metadata={payload.metadata}")
        
        # Parse target date if provided
        target_date = None
        if payload.target_date:
            try:
                target_date = date.fromisoformat(payload.target_date)
                logger.info(f"📅 Parsed target date: {target_date}")
            except ValueError:
                logger.error(f"❌ Invalid date format: {payload.target_date}")
        
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
        
        elif payload.trigger == "sync_14_day_ad_data":
            # Immediate response - fire and forget
            import asyncio
            import threading
            
            logger.info(f"🚀 STARTING 14-DAY SYNC THREAD - trigger received, creating background thread...")
            
            # Start sync in separate thread to avoid blocking n8n
            def start_sync():
                try:
                    logger.info(f"🧵 SYNC THREAD STARTED - about to run async sync process...")
                    asyncio.run(sync_14_day_ad_data_background(payload.metadata))
                    logger.info(f"✅ SYNC THREAD COMPLETED - async sync process finished successfully")
                except Exception as e:
                    logger.error(f"❌ CRITICAL ERROR IN SYNC THREAD: {e}", exc_info=True)
                    logger.error(f"❌ THREAD CRASH DETAILS: {str(e)}")
                    global _sync_status
                    _sync_status["in_progress"] = False
                    _sync_status["last_message"] = f"Thread crashed: {str(e)}"
            
            thread = threading.Thread(target=start_sync, daemon=True)
            thread.start()
            logger.info(f"🎯 THREAD LAUNCHED - sync running in background, returning response to n8n...")
            
            return {
                "status": "accepted",
                "message": "14-day ad-level sync initiated (fire-and-forget)",
                "target": "ad_level_data_with_parsing"
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

async def sync_14_day_ad_data_background(metadata: Optional[Dict[str, Any]]):
    """
    Background task for syncing 14-day ad-level data with enhanced parsing
    """
    global _sync_status
    from datetime import datetime
    
    try:
        # Update sync status
        _sync_status["in_progress"] = True
        _sync_status["started_at"] = datetime.now().isoformat()
        _sync_status["last_message"] = "Starting 14-day ad-level data sync"
        
        logger.info("🎯 SYNC PROCESS STARTED - 14-day ad-level data sync with enhanced parsing")
        logger.info(f"⏰ SYNC START TIME: {_sync_status['started_at']}")
        logger.info(f"📊 METADATA RECEIVED: {metadata}")
        
        from ..services.meta_ad_level_service import MetaAdLevelService
        from supabase import create_client
        
        # Initialize services
        logger.info("🔧 INITIALIZING SERVICES - MetaAdLevelService and Supabase client...")
        meta_service = MetaAdLevelService()
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        logger.info(f"🔗 SUPABASE CONFIG: URL={supabase_url[:30]}..., Key={'*' * 20}")
        supabase = create_client(supabase_url, supabase_key)
        logger.info("✅ SERVICES INITIALIZED - Ready to fetch data")
        
        # Fetch 14-day ad data with weekly segmentation
        _sync_status["last_message"] = "Fetching 14-day data with weekly segments"
        logger.info("📊 FETCHING DATA - Starting 14-day data retrieval with weekly segments...")
        real_ad_data = meta_service.get_last_14_days_ad_data()
        logger.info(f"📥 DATA FETCH COMPLETE - Retrieved data: {type(real_ad_data)}, Length check pending...")
        
        if not real_ad_data:
            logger.warning("⚠️ No ad data found")
            return
        
        logger.info(f"✅ Retrieved {len(real_ad_data)} ad records")
        
        # Filter out ads with $0 spend AND 0 purchases
        filtered_ad_data = []
        zero_spend_zero_purchase_count = 0
        zero_spend_with_purchases_count = 0
        
        for ad in real_ad_data:
            spend = ad.get('amount_spent_usd', 0)
            purchases = ad.get('purchases', 0)
            
            if spend == 0 and purchases == 0:
                zero_spend_zero_purchase_count += 1
                continue
            elif spend == 0 and purchases > 0:
                zero_spend_with_purchases_count += 1
                filtered_ad_data.append(ad)
            else:
                filtered_ad_data.append(ad)
        
        logger.info(f"🔍 Filtered out {zero_spend_zero_purchase_count} ads with $0 spend + 0 purchases")
        logger.info(f"💡 Kept {zero_spend_with_purchases_count} interesting cases ($0 spend + purchases)")
        logger.info(f"✅ Final ads to insert: {len(filtered_ad_data)}")
        
        if not filtered_ad_data:
            logger.warning("⚠️ No ads remaining after filtering")
            return
        
        # Clear existing data
        logger.info("🧹 Clearing existing ad data...")
        try:
            supabase.table('meta_ad_data').delete().gt('id', 0).execute()
            logger.info("✅ Cleared existing data")
        except Exception as e:
            logger.info("ℹ️ Database already empty or clear operation not needed")
        
        # Prepare and insert data
        insert_data = []
        for ad in filtered_ad_data:
            insert_record = {
                'ad_id': ad['ad_id'],
                'in_platform_ad_name': ad.get('original_ad_name', ad['ad_name']),
                'ad_name': ad['ad_name'],
                'campaign_name': ad['campaign_name'],
                'reporting_starts': ad['reporting_starts'].isoformat(),
                'reporting_ends': ad['reporting_ends'].isoformat(),
                'launch_date': ad['launch_date'].isoformat() if ad['launch_date'] else None,
                'days_live': ad['days_live'],
                'category': ad['category'],
                'product': ad['product'],
                'color': ad['color'],
                'content_type': ad['content_type'],
                'handle': ad['handle'],
                'format': ad['format'],
                'campaign_optimization': ad['campaign_optimization'],
                'amount_spent_usd': ad['amount_spent_usd'],
                'purchases': ad['purchases'],
                'purchases_conversion_value': ad['purchases_conversion_value'],
                'impressions': ad['impressions'],
                'link_clicks': ad['link_clicks'],
                'thumbnail_url': ad.get('thumbnail_url')
            }
            insert_data.append(insert_record)
        
        # Insert in batches
        batch_size = 100
        total_inserted = 0
        
        for i in range(0, len(insert_data), batch_size):
            batch = insert_data[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            logger.info(f"📥 Inserting batch {batch_num} ({len(batch)} records)...")
            result = supabase.table('meta_ad_data').insert(batch).execute()
            
            if result.data:
                total_inserted += len(result.data)
                logger.info(f"✅ Batch {batch_num} inserted: {len(result.data)} records")
        
        # Calculate summary
        total_spend = sum(ad['amount_spent_usd'] for ad in filtered_ad_data)
        total_purchases = sum(ad['purchases'] for ad in filtered_ad_data)
        total_revenue = sum(ad['purchases_conversion_value'] for ad in filtered_ad_data)
        
        logger.info(f"🎉 14-day ad sync completed successfully!")
        logger.info(f"📊 Total inserted: {total_inserted} ad records")
        logger.info(f"💰 Total spend: ${total_spend:,.2f}")
        logger.info(f"🛒 Total purchases: {total_purchases}")
        logger.info(f"💵 Total revenue: ${total_revenue:,.2f}")
        
        # Apply automated pause detection after successful sync
        logger.info("🤖 Running automated pause detection...")
        try:
            from ..services.ad_pause_automation import AdPauseAutomationService
            automation_service = AdPauseAutomationService()
            
            # Analyze the ad data for pause status
            pause_analysis = automation_service.analyze_ad_pause_status(filtered_ad_data)
            
            # Get summary for logging
            summary_stats = {
                'total_ads_analyzed': len(pause_analysis),
                'completely_paused': sum(1 for data in pause_analysis.values() if data['status'] == 'paused'),
                'completely_active': sum(1 for data in pause_analysis.values() if data['status'] == 'active'),
                'unknown_status': sum(1 for data in pause_analysis.values() if data['status'] == 'unknown')
            }
            
            logger.info(f"📊 Pause analysis: {summary_stats['total_ads_analyzed']} ads analyzed")
            logger.info(f"   🔴 Completely paused: {summary_stats['completely_paused']} ads")
            logger.info(f"   🟢 Completely active: {summary_stats['completely_active']} ads") 
            logger.info(f"   ❓ Unknown status: {summary_stats['unknown_status']} ads")
            
            # Apply automated status updates
            import asyncio
            results = await automation_service.apply_automated_status_updates(pause_analysis)
            
            logger.info(f"✅ Automation complete: {results['updates_applied']} automated pause statuses applied")
            if results['updates_cleared'] > 0:
                logger.info(f"   🔄 {results['updates_cleared']} automated statuses cleared (ads became active)")
            if results['preserved_manual'] > 0:
                logger.info(f"   🤲 {results['preserved_manual']} manual statuses preserved")
            if results.get('errors'):
                logger.error(f"   ⚠️ {len(results['errors'])} automation errors occurred")
                
        except Exception as auto_error:
            logger.error(f"⚠️ Automated pause detection failed: {auto_error}")
            logger.error(f"⚠️ Full automation error: {str(auto_error)}", exc_info=True)
            # Don't fail the entire sync if automation fails
        
        # Update completion status
        _sync_status["in_progress"] = False
        _sync_status["last_message"] = f"Completed successfully - {total_inserted} records inserted with pause detection"
        
    except Exception as e:
        logger.error(f"❌ Error in 14-day ad sync: {e}")
        _sync_status["in_progress"] = False
        _sync_status["last_message"] = f"Failed: {str(e)}"
        # Don't raise in background thread - just log the error
        logger.error(f"❌ Full error details: {str(e)}", exc_info=True)

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
            "/api/webhook/test",
            "/api/webhook/sync-status"
        ],
        "supported_triggers": [
            "scheduled_sync",
            "manual_sync", 
            "sync_14_day_ad_data",
            "test"
        ]
    }

@router.get("/sync-status")
async def get_sync_status():
    """
    Get current sync status for monitoring
    """
    return {
        "sync_in_progress": _sync_status["in_progress"],
        "started_at": _sync_status["started_at"],
        "last_message": _sync_status["last_message"],
        "timestamp": date.today().isoformat()
    }