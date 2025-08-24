#!/usr/bin/env python3
"""
Sync TikTok Ad-Level Historical Data
Fetches TikTok ad-level data from January 2024 to August 22, 2024
and populates the tiktok_ad_data table
"""

import os
import sys
from datetime import date, timedelta
from loguru import logger
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.tiktok_ad_level_service import TikTokAdLevelService

# Load environment variables
load_dotenv()

def generate_date_ranges(start_date: date, end_date: date, days_per_period: int = 7) -> list:
    """Generate weekly date ranges for the sync period"""
    date_ranges = []
    current_start = start_date
    
    while current_start <= end_date:
        period_end = min(current_start + timedelta(days=days_per_period - 1), end_date)
        date_ranges.append((current_start, period_end))
        current_start = period_end + timedelta(days=1)
    
    return date_ranges

def fetch_historical_ad_data():
    """Fetch and sync TikTok ad-level historical data"""
    # Initialize service
    service = TikTokAdLevelService()
    
    # Test connection first
    if not service.test_connection():
        logger.error("Failed to connect to TikTok Ads API")
        return
    
    logger.info("TikTok Ads API connection successful")
    
    # Define date range: January 2024 to August 22, 2024
    start_date = date(2024, 1, 1)
    end_date = date(2024, 8, 22)
    
    # Generate weekly periods for the entire range
    date_ranges = generate_date_ranges(start_date, end_date, days_per_period=7)
    
    logger.info(f"Processing {len(date_ranges)} weekly periods from {start_date} to {end_date}")
    
    total_synced = 0
    total_ads_with_spend = 0
    
    # Process each weekly period
    for period_num, (period_start, period_end) in enumerate(date_ranges, 1):
        logger.info(f"\nProcessing period {period_num}/{len(date_ranges)}: {period_start} to {period_end}")
        
        try:
            # Fetch ad-level data for this period
            ads_data = service._fetch_ads_for_period(period_start, period_end)
            
            if not ads_data:
                logger.warning(f"No ad data found for period {period_start} to {period_end}")
                continue
            
            # Filter ads with spend > 0
            ads_with_spend = [ad for ad in ads_data if ad.get('amount_spent_usd', 0) > 0]
            
            logger.info(f"Found {len(ads_data)} total ads, {len(ads_with_spend)} with spend > 0")
            
            if ads_with_spend:
                # Sync to database
                synced_count, message = service.sync_ad_data_to_database(ads_with_spend)
                total_synced += synced_count
                total_ads_with_spend += len(ads_with_spend)
                logger.info(f"Synced {synced_count} ads: {message}")
            else:
                logger.info("No ads with spend > 0 to sync for this period")
        
        except Exception as e:
            logger.error(f"Error processing period {period_start} to {period_end}: {e}")
            continue
    
    logger.info("\n" + "="*60)
    logger.info(f"Historical sync completed!")
    logger.info(f"Total periods processed: {len(date_ranges)}")
    logger.info(f"Total ads with spend > 0: {total_ads_with_spend}")
    logger.info(f"Total records synced to database: {total_synced}")
    logger.info("="*60)
    
    # Fetch summary statistics
    try:
        summary = service.get_summary_metrics()
        logger.info("\nDatabase Summary Metrics:")
        logger.info(f"Total ads in database: {summary['ads_count']}")
        logger.info(f"Total spend: ${summary['total_spend']:,.2f}")
        logger.info(f"Total revenue: ${summary['total_revenue']:,.2f}")
        logger.info(f"Total purchases: {summary['total_purchases']:,}")
        logger.info(f"Average ROAS: {summary['avg_roas']:.2f}")
        logger.info(f"Average CPA: ${summary['avg_cpa']:.2f}")
    except Exception as e:
        logger.error(f"Failed to fetch summary metrics: {e}")

if __name__ == "__main__":
    logger.info("Starting TikTok Ad-Level Historical Data Sync")
    logger.info("Date range: January 1, 2024 to August 22, 2024")
    
    try:
        fetch_historical_ad_data()
    except KeyboardInterrupt:
        logger.info("\nSync interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
    logger.info("\nSync script completed")