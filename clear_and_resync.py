#!/usr/bin/env python3
"""
Clear and Resync Script
Clears all campaign data and resyncs with corrected link_clicks
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / 'app'))

from dotenv import load_dotenv
load_dotenv()

try:
    from supabase import create_client
    from app.services.reporting import ReportingService
    from loguru import logger
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def clear_and_resync():
    """
    Clear all campaign data and resync with corrected data
    """
    try:
        # Initialize Supabase client
        url = os.getenv("SUPABASE_URL") 
        key = os.getenv("SUPABASE_SERVICE_KEY")
        supabase = create_client(url, key)
        
        print("⚠️  Proceeding to delete ALL campaign data from the database...")
        
        # Clear all campaign data
        logger.info("Clearing all campaign data...")
        result = supabase.table("campaign_data").delete().neq("id", 0).execute()
        deleted_count = len(result.data) if result.data else 0
        logger.info(f"Cleared {deleted_count} records from database")
        
        # Now use the reporting service to sync new data
        logger.info("Starting fresh sync with corrected link_clicks...")
        reporting_service = ReportingService()
        
        # Sync current month data to test
        sync_result = reporting_service.sync_meta_data()
        
        if sync_result["success"]:
            logger.info(f"Successfully synced {sync_result.get('data_count', 0)} campaigns")
            return True
        else:
            logger.error(f"Sync failed: {sync_result.get('message', 'Unknown error')}")
            return False
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return False
    except Exception as e:
        logger.error(f"Error during clear and resync: {e}")
        return False

if __name__ == "__main__":
    print("HON Clear and Resync - DANGEROUS OPERATION")
    print("=" * 50)
    
    success = clear_and_resync()
    
    if success:
        print("✅ Clear and resync completed successfully!")
        print("Database now contains fresh data with corrected link_clicks.")
    else:
        print("❌ Clear and resync failed.")