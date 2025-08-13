#!/usr/bin/env python3
"""
Clean and Proper Resync Script
Clears database and resyncs with proper monthly date ranges to avoid duplicates
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
    from supabase import create_client
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

def clean_and_proper_resync():
    """
    Clean database and resync properly month by month
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
        
        # Clear all existing data
        logger.info("Clearing all campaign data...")
        result = supabase.table("campaign_data").delete().neq("id", 0).execute()
        deleted_count = len(result.data) if result.data else 0
        logger.info(f"Cleared {deleted_count} records from database")
        
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
        
        logger.info(f"Starting proper resync for {len(months_to_sync)} months")
        
        total_campaigns = 0
        monthly_summary = []
        
        for year, month in months_to_sync:
            try:
                first_day, last_day = get_month_date_range(year, month)
                month_str = f"{year}-{month:02d}"
                
                logger.info(f"Syncing {month_str} ({first_day} to {last_day})")
                
                # Get insights for this specific month only
                insights = meta_service.get_campaign_insights(first_day, last_day)
                
                if not insights:
                    logger.warning(f"No insights for {month_str}")
                    monthly_summary.append({
                        'month': month_str,
                        'campaigns': 0,
                        'spend': 0,
                        'link_clicks': 0,
                        'cpc': 0
                    })
                    continue
                
                # Convert to campaign data with month-specific date range
                campaign_data_list = meta_service.convert_to_campaign_data(insights)
                
                # Verify date ranges are set correctly for this month
                for campaign_data in campaign_data_list:
                    campaign_data.reporting_starts = first_day
                    campaign_data.reporting_ends = last_day
                
                # Store in database
                success = reporting_service.store_campaign_data(campaign_data_list)
                
                if success:
                    # Calculate monthly totals for verification
                    month_spend = sum(float(c.amount_spent_usd) for c in campaign_data_list)
                    month_clicks = sum(c.link_clicks for c in campaign_data_list)
                    month_cpc = month_spend / month_clicks if month_clicks > 0 else 0
                    
                    monthly_summary.append({
                        'month': month_str,
                        'campaigns': len(campaign_data_list),
                        'spend': month_spend,
                        'link_clicks': month_clicks,
                        'cpc': month_cpc
                    })
                    
                    logger.info(f"✅ {month_str}: {len(campaign_data_list)} campaigns, ${month_spend:,.0f} spend, {month_clicks:,} clicks, ${month_cpc:.2f} CPC")
                    total_campaigns += len(campaign_data_list)
                else:
                    logger.error(f"Failed to store data for {month_str}")
                    
            except Exception as e:
                logger.error(f"Error syncing {year}-{month:02d}: {e}")
                continue
        
        # Print summary
        print("\n" + "="*80)
        print("RESYNC SUMMARY")
        print("="*80)
        for summary in monthly_summary:
            print(f"{summary['month']}: {summary['campaigns']:2d} campaigns, "
                  f"${summary['spend']:8,.0f} spend, {summary['link_clicks']:6,} clicks, "
                  f"${summary['cpc']:5.2f} CPC")
        
        logger.info(f"Clean resync completed! Total campaigns: {total_campaigns}")
        return True
        
    except Exception as e:
        logger.error(f"Clean resync failed: {e}")
        return False

if __name__ == "__main__":
    print("HON Clean and Proper Resync")
    print("=" * 50)
    print("This will clear ALL data and resync month by month with proper date ranges")
    
    success = clean_and_proper_resync()
    
    if success:
        print("\n✅ Clean and proper resync completed successfully!")
        print("Database now contains accurate month-by-month data with no duplicates.")
    else:
        print("\n❌ Clean and proper resync failed.")