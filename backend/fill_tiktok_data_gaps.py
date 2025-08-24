#!/usr/bin/env python3
"""
Fill gaps in TikTok data and complete through August 22, 2024
"""

import os
from datetime import date, timedelta
from loguru import logger
from dotenv import load_dotenv
from fetch_remaining_tiktok_data import TikTokRemainingDataFetcher

# Load environment variables
load_dotenv()

def main():
    """Fill in missing date ranges"""
    fetcher = TikTokRemainingDataFetcher()
    
    # Define the missing periods based on the output
    missing_periods = [
        # April gap
        (date(2024, 4, 8), date(2024, 4, 14)),
        # Complete July 2024
        (date(2024, 7, 22), date(2024, 7, 28)),
        (date(2024, 7, 29), date(2024, 7, 31)),
        # August 2024 (up to August 22)
        (date(2024, 8, 1), date(2024, 8, 4)),
        (date(2024, 8, 5), date(2024, 8, 11)),
        (date(2024, 8, 12), date(2024, 8, 18)),
        (date(2024, 8, 19), date(2024, 8, 22))
    ]
    
    logger.info(f"Filling {len(missing_periods)} missing periods")
    
    total_synced = 0
    
    for i, (start_date, end_date) in enumerate(missing_periods, 1):
        logger.info(f"\nProcessing period {i}/{len(missing_periods)}: {start_date} to {end_date}")
        
        try:
            # Fetch ads for this period
            ads_data = fetcher.fetch_ads_for_period(start_date, end_date)
            
            if ads_data:
                # Sync to database
                synced = fetcher.sync_to_database(ads_data)
                total_synced += synced
                logger.info(f"Synced {synced} ads for this period")
            else:
                logger.info("No ads found for this period")
        
        except Exception as e:
            logger.error(f"Error processing period: {e}")
            continue
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Gap filling complete!")
    logger.info(f"Total ads synced: {total_synced}")
    logger.info('='*60)
    
    # Show final statistics
    fetcher.show_final_stats()
    
    # Verify continuous coverage
    logger.info("\nVerifying date coverage...")
    from supabase import create_client
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    # Get date range summary
    result = supabase.table("tiktok_ad_data")\
        .select("reporting_starts")\
        .order("reporting_starts")\
        .execute()
    
    if result.data:
        # Count records by month
        month_counts = {}
        for record in result.data:
            month = record['reporting_starts'][:7]
            month_counts[month] = month_counts.get(month, 0) + 1
        
        print("\nFinal coverage by month:")
        for month in sorted(month_counts.keys()):
            print(f"  {month}: {month_counts[month]:,} records")

if __name__ == "__main__":
    logger.info("Starting TikTok data gap filling")
    logger.info("Target: Complete coverage through August 22, 2024")
    
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nProcess interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("\nGap filling script completed")