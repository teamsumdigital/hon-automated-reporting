#!/usr/bin/env python3
"""
Fix August 2025 Script
Wipes August 2025 data and re-fetches from Aug 1-11, 2025 with correct reporting_ends date
"""

import os
import sys
from datetime import date
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / 'app'))

from dotenv import load_dotenv
load_dotenv()

try:
    from supabase import create_client
    from app.services.meta_api import MetaAdsService
    from app.services.reporting import ReportingService
    from loguru import logger
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def fix_august_2025():
    """
    Fix August 2025 data: wipe and re-fetch Aug 1-11, 2025
    """
    try:
        # Initialize services
        url = os.getenv("SUPABASE_URL") 
        key = os.getenv("SUPABASE_SERVICE_KEY")
        supabase = create_client(url, key)
        
        meta_service = MetaAdsService()
        reporting_service = ReportingService()
        
        # Test connection
        logger.info("Testing Meta API connection...")
        if not meta_service.test_connection():
            logger.error("Meta API connection failed")
            return False
        
        # Delete existing August 2025 data
        logger.info("Deleting existing August 2025 data...")
        delete_result = supabase.table("campaign_data").delete().gte("reporting_starts", "2025-08-01").lt("reporting_starts", "2025-09-01").execute()
        deleted_count = len(delete_result.data) if delete_result.data else 0
        logger.info(f"Deleted {deleted_count} August 2025 records")
        
        # Set correct date range: August 1-11, 2025
        start_date = date(2025, 8, 1)
        end_date = date(2025, 8, 11)
        
        logger.info(f"Fetching August 2025 data from {start_date} to {end_date}")
        
        # Get insights for Aug 1-11, 2025
        insights = meta_service.get_campaign_insights(start_date, end_date)
        
        if not insights:
            logger.warning("No insights retrieved for August 1-11, 2025")
            return True
        
        # Convert to campaign data with correct date range
        campaign_data_list = meta_service.convert_to_campaign_data(insights)
        
        # Set correct reporting dates
        for campaign_data in campaign_data_list:
            campaign_data.reporting_starts = start_date
            campaign_data.reporting_ends = end_date  # August 11, not 31
        
        # Store in database
        success = reporting_service.store_campaign_data(campaign_data_list)
        
        if success:
            # Calculate totals for verification
            total_spend = sum(float(c.amount_spent_usd) for c in campaign_data_list)
            total_clicks = sum(c.link_clicks for c in campaign_data_list)
            total_cpc = total_spend / total_clicks if total_clicks > 0 else 0
            
            print(f"\n✅ August 2025 Fixed:")
            print(f"   Date Range: {start_date} to {end_date}")
            print(f"   Campaigns: {len(campaign_data_list)}")
            print(f"   Spend: ${total_spend:,.2f}")
            print(f"   Link Clicks: {total_clicks:,}")
            print(f"   CPC: ${total_cpc:.2f}")
            print(f"\n   Ready for n8n to add August 12+ data!")
            
            logger.info(f"Successfully fixed August 2025: {len(campaign_data_list)} campaigns")
            return True
        else:
            logger.error("Failed to store August 2025 data")
            return False
            
    except Exception as e:
        logger.error(f"Fix August 2025 failed: {e}")
        return False

if __name__ == "__main__":
    print("HON Fix August 2025")
    print("=" * 50)
    print("Wiping August 2025 and re-fetching Aug 1-11, 2025 data")
    print("This prepares for n8n to add Aug 12+ data daily")
    
    success = fix_august_2025()
    
    if success:
        print("\n✅ August 2025 fix completed successfully!")
        print("Database ready for n8n daily automation starting Aug 12.")
    else:
        print("\n❌ August 2025 fix failed.")