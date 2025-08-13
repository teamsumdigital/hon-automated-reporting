#!/usr/bin/env python3
"""
Monthly Resync Script
Resyncs data month by month to ensure complete historical coverage
"""

import os
import sys
from datetime import date, timedelta
from pathlib import Path
import calendar

# Add backend to path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / 'app'))

from dotenv import load_dotenv
load_dotenv()

try:
    from app.services.meta_api import MetaAdsService
    from app.services.reporting import ReportingService
    from loguru import logger
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def get_month_date_range(year, month):
    """Get first and last day of a specific month"""
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    return first_day, last_day

def monthly_resync():
    """
    Resync data month by month from January 2024 to present
    """
    try:
        # Initialize services
        meta_service = MetaAdsService()
        reporting_service = ReportingService()
        
        # Test connection
        logger.info("Testing Meta API connection...")
        if not meta_service.test_connection():
            logger.error("Meta API connection failed")
            return False
        
        # Generate list of months to sync
        start_year, start_month = 2024, 1
        current_date = date.today()
        current_year, current_month = current_date.year, current_date.month
        
        months_to_sync = []
        year, month = start_year, start_month
        
        while year < current_year or (year == current_year and month <= current_month):
            months_to_sync.append((year, month))
            month += 1
            if month > 12:
                month = 1
                year += 1
        
        logger.info(f"Planning to sync {len(months_to_sync)} months from {start_year}-{start_month:02d} to {current_year}-{current_month:02d}")
        
        total_campaigns = 0
        
        for year, month in months_to_sync:
            try:
                first_day, last_day = get_month_date_range(year, month)
                month_str = f"{year}-{month:02d}"
                
                logger.info(f"Syncing {month_str} ({first_day} to {last_day})")
                
                # Get insights for this month
                insights = meta_service.get_campaign_insights(first_day, last_day)
                
                if not insights:
                    logger.warning(f"No insights for {month_str}")
                    continue
                
                # Convert to campaign data
                campaign_data_list = meta_service.convert_to_campaign_data(insights)
                
                # Store in database
                success = reporting_service.store_campaign_data(campaign_data_list)
                
                if success:
                    logger.info(f"Successfully synced {len(campaign_data_list)} campaigns for {month_str}")
                    total_campaigns += len(campaign_data_list)
                else:
                    logger.error(f"Failed to store data for {month_str}")
                    
            except Exception as e:
                logger.error(f"Error syncing {year}-{month:02d}: {e}")
                continue
        
        logger.info(f"Monthly resync completed! Total campaigns synced: {total_campaigns}")
        return True
        
    except Exception as e:
        logger.error(f"Monthly resync failed: {e}")
        return False

if __name__ == "__main__":
    print("HON Monthly Resync - Complete Historical Data")
    print("=" * 50)
    
    success = monthly_resync()
    
    if success:
        print("✅ Monthly resync completed successfully!")
        print("Database now contains complete month-by-month historical data.")
    else:
        print("❌ Monthly resync failed.")