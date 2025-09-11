"""
Ad Status Sync Service - Separate workflow for fetching real ad status from Meta API

This service runs independently from the main data sync to safely update ad status 
without risking the working sync process. It uses existing database records to 
determine which ads need status updates.
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
import time
import os
from loguru import logger
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.ad import Ad
from facebook_business.exceptions import FacebookRequestError
from supabase import create_client

class AdStatusSyncService:
    def __init__(self):
        """Initialize the Ad Status Sync Service with Meta API and database connections"""
        # Initialize Meta API
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            raise ValueError("META_ACCESS_TOKEN environment variable is required")
        
        FacebookAdsApi.init(access_token=access_token)
        
        # Initialize Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables are required")
        
        self.supabase = create_client(supabase_url, supabase_key)
        
        logger.info("🔄 AdStatusSyncService initialized with Meta API and Supabase connections")

    def get_ads_needing_status_update(self) -> List[Dict[str, Any]]:
        """
        Get unique ads from database that need status updates
        Returns list of unique ads with their ad_ids and current status
        """
        try:
            # Get all ads from current database records, then deduplicate in Python
            result = self.supabase.table('meta_ad_data')\
                .select('ad_id, ad_name, status')\
                .execute()
            
            if not result.data:
                logger.warning("⚠️ No records found in meta_ad_data table")
                return []
            
            # Deduplicate by ad_id to get unique ads
            unique_ads = {}
            for record in result.data:
                ad_id = record.get('ad_id')
                if ad_id and ad_id not in unique_ads:
                    unique_ads[ad_id] = {
                        'ad_id': ad_id,
                        'ad_name': record.get('ad_name'),
                        'status': record.get('status'),
                        'record_count': 1
                    }
                elif ad_id in unique_ads:
                    unique_ads[ad_id]['record_count'] += 1
            
            ads = list(unique_ads.values())
            logger.info(f"📊 Found {len(ads)} unique ads from {len(result.data)} total records")
            
            # Log sample for inspection
            if ads:
                logger.info(f"📝 Sample ad: {ads[0]}")
                
                # Count current status distribution
                status_counts = {}
                for ad in ads:
                    status = ad.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                logger.info(f"📊 Current status distribution: {status_counts}")
            
            return ads
            
        except Exception as e:
            logger.error(f"❌ Error getting ads needing status update: {e}")
            return []

    def fetch_real_ad_status_batch(self, ad_ids: List[str], batch_size: int = 20) -> Dict[str, str]:
        """
        Fetch real ad status from Meta API in safe batches
        Returns dict mapping ad_id -> effective_status
        """
        status_results = {}
        total_batches = (len(ad_ids) + batch_size - 1) // batch_size
        
        logger.info(f"🔍 Fetching real status for {len(ad_ids)} ads in {total_batches} batches of {batch_size}")
        
        for i in range(0, len(ad_ids), batch_size):
            batch = ad_ids[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            logger.info(f"📡 Processing batch {batch_num}/{total_batches} ({len(batch)} ads)")
            
            try:
                for ad_id in batch:
                    try:
                        # Fetch individual ad status using Ad object
                        ad = Ad(ad_id)
                        ad_data = ad.api_get(fields=['effective_status'])
                        
                        real_status = ad_data.get('effective_status', 'UNKNOWN')
                        status_results[ad_id] = real_status
                        
                        logger.debug(f"✅ Ad {ad_id}: {real_status}")
                        
                    except FacebookRequestError as e:
                        logger.warning(f"⚠️ Failed to fetch status for ad {ad_id}: {e}")
                        status_results[ad_id] = 'ERROR'
                    
                    except Exception as e:
                        logger.error(f"❌ Unexpected error for ad {ad_id}: {e}")
                        status_results[ad_id] = 'ERROR'
                
                # Rate limiting between batches
                if batch_num < total_batches:
                    logger.info(f"⏱️ Rate limiting: sleeping 2 seconds before next batch...")
                    time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Batch {batch_num} failed completely: {e}")
                # Mark all ads in failed batch as ERROR
                for ad_id in batch:
                    status_results[ad_id] = 'ERROR'
        
        # Log summary
        status_summary = {}
        for status in status_results.values():
            status_summary[status] = status_summary.get(status, 0) + 1
        
        logger.info(f"📊 Status fetch complete: {status_summary}")
        return status_results

    def map_meta_status_to_db_status(self, meta_status: str) -> str:
        """
        Map Meta API status values to database constraint values
        """
        status_mapping = {
            'ACTIVE': 'active',
            'PAUSED': 'paused', 
            'DELETED': 'paused',  # Treat deleted as paused
            'ARCHIVED': 'paused', # Treat archived as paused
            'UNKNOWN': 'active',  # Default unknown to active
            'ERROR': 'active'     # Default errors to active
        }
        
        mapped_status = status_mapping.get(meta_status.upper(), 'active')
        logger.debug(f"🔄 Status mapping: {meta_status} → {mapped_status}")
        return mapped_status

    def update_ad_status_in_database(self, status_updates: Dict[str, str]) -> Dict[str, Any]:
        """
        Update ad status in database with real Meta API status
        Returns summary of updates applied
        """
        if not status_updates:
            logger.warning("⚠️ No status updates to apply")
            return {'updated': 0, 'errors': 0}
        
        updated_count = 0
        error_count = 0
        status_changes = {}
        
        logger.info(f"💾 Applying {len(status_updates)} status updates to database...")
        
        for ad_id, meta_status in status_updates.items():
            try:
                # Map Meta status to database status
                db_status = self.map_meta_status_to_db_status(meta_status)
                
                # Update all records for this ad_id
                result = self.supabase.table('meta_ad_data')\
                    .update({
                        'status': db_status,
                        'status_updated_at': datetime.now().isoformat(),
                        'status_automation_reason': f'meta_api_sync_{meta_status.lower()}'
                    })\
                    .eq('ad_id', ad_id)\
                    .execute()
                
                if result.data:
                    updated_records = len(result.data)
                    updated_count += updated_records
                    
                    # Track status changes for reporting
                    status_changes[db_status] = status_changes.get(db_status, 0) + 1
                    
                    logger.debug(f"✅ Updated {updated_records} records for ad {ad_id}: {meta_status} → {db_status}")
                else:
                    logger.warning(f"⚠️ No records updated for ad_id {ad_id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to update ad {ad_id}: {e}")
                error_count += 1
        
        summary = {
            'updated': updated_count,
            'errors': error_count,
            'status_changes': status_changes,
            'total_ads': len(status_updates)
        }
        
        logger.info(f"📊 Status update summary: {summary}")
        return summary

    def sync_ad_status(self, batch_size: int = 20, max_ads: Optional[int] = None) -> Dict[str, Any]:
        """
        Main method to sync ad status from Meta API to database
        
        Args:
            batch_size: Number of ads to process per batch (default 20)
            max_ads: Maximum number of ads to process (for testing, default None = all)
        
        Returns:
            Summary of sync operation
        """
        try:
            logger.info(f"🚀 Starting ad status sync (batch_size={batch_size}, max_ads={max_ads})")
            
            # Step 1: Get ads needing status update from database
            ads_to_update = self.get_ads_needing_status_update()
            
            if not ads_to_update:
                logger.warning("⚠️ No ads found in database for status sync")
                return {'success': False, 'message': 'No ads found'}
            
            # Extract unique ad_ids
            ad_ids = [ad['ad_id'] for ad in ads_to_update]
            
            # Limit for testing if specified
            if max_ads and len(ad_ids) > max_ads:
                ad_ids = ad_ids[:max_ads]
                logger.info(f"🔬 Testing mode: Limited to {max_ads} ads")
            
            logger.info(f"📋 Processing {len(ad_ids)} unique ads for status sync")
            
            # Step 2: Fetch real status from Meta API
            start_time = datetime.now()
            status_results = self.fetch_real_ad_status_batch(ad_ids, batch_size)
            fetch_duration = (datetime.now() - start_time).total_seconds()
            
            # Step 3: Update database with real status
            update_summary = self.update_ad_status_in_database(status_results)
            
            # Step 4: Generate final report
            total_duration = (datetime.now() - start_time).total_seconds()
            
            final_summary = {
                'success': True,
                'total_ads_processed': len(ad_ids),
                'fetch_duration_seconds': round(fetch_duration, 2),
                'total_duration_seconds': round(total_duration, 2),
                'database_updates': update_summary,
                'status_distribution': {}
            }
            
            # Count final status distribution
            for status in status_results.values():
                mapped_status = self.map_meta_status_to_db_status(status)
                final_summary['status_distribution'][mapped_status] = \
                    final_summary['status_distribution'].get(mapped_status, 0) + 1
            
            logger.info(f"🎉 Ad status sync complete: {final_summary}")
            return final_summary
            
        except Exception as e:
            logger.error(f"❌ Ad status sync failed: {e}")
            return {
                'success': False, 
                'error': str(e),
                'message': 'Ad status sync failed with exception'
            }