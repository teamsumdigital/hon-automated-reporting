#!/usr/bin/env python3
"""
Google Ads Historical Resync Script
Syncs historical Google Ads data month by month with proper date ranges to avoid duplicates
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
    from app.services.google_ads_service import GoogleAdsService
    from app.services.google_reporting import GoogleReportingService
    from loguru import logger
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you have installed the required dependencies:")
    print("pip install google-ads supabase loguru python-dotenv")
    sys.exit(1)

def get_month_date_range(year, month):
    """Get first and last day of a specific month"""
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    return first_day, last_day

def google_historical_resync():
    """
    Resync Google Ads data month by month from January 2024 to present
    """
    try:
        # Initialize services
        url = os.getenv("SUPABASE_URL") 
        key = os.getenv("SUPABASE_SERVICE_KEY")
        supabase = create_client(url, key)
        
        google_ads_service = GoogleAdsService()
        reporting_service = GoogleReportingService()
        
        # Test connection
        logger.info("Testing Google Ads API connection...")
        if not google_ads_service.test_connection():
            logger.error("Google Ads API connection failed")
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
        monthly_summary = []
        
        for year, month in months_to_sync:
            try:
                first_day, last_day = get_month_date_range(year, month)
                month_str = f"{year}-{month:02d}"
                
                logger.info(f"Syncing Google Ads data for {month_str} ({first_day} to {last_day})")
                
                # Get insights for this month
                insights = google_ads_service.get_campaign_insights(first_day, last_day)
                
                if not insights:
                    logger.warning(f"No Google Ads insights for {month_str}")
                    monthly_summary.append({
                        'month': month_str,
                        'campaigns': 0,
                        'spend': 0,
                        'clicks': 0,
                        'cpc': 0
                    })
                    continue
                
                # Convert to campaign data with month-specific date range
                campaign_data_list = google_ads_service.convert_to_campaign_data(insights)
                
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
                        'clicks': month_clicks,
                        'cpc': month_cpc
                    })
                    
                    logger.info(f"✅ {month_str}: {len(campaign_data_list)} campaigns, ${month_spend:,.0f} spend, {month_clicks:,} clicks, ${month_cpc:.2f} CPC")
                    total_campaigns += len(campaign_data_list)
                else:
                    logger.error(f"Failed to store Google Ads data for {month_str}")
                    
            except Exception as e:
                logger.error(f"Error syncing Google Ads data for {year}-{month:02d}: {e}")
                continue
        
        # Print summary
        print("\n" + "="*80)
        print("GOOGLE ADS RESYNC SUMMARY")
        print("="*80)
        for summary in monthly_summary:
            print(f"{summary['month']}: {summary['campaigns']:2d} campaigns, "
                  f"${summary['spend']:8,.0f} spend, {summary['clicks']:6,} clicks, "
                  f"${summary['cpc']:5.2f} CPC")
        
        logger.info(f"Google Ads historical resync completed! Total campaigns: {total_campaigns}")
        return True
        
    except Exception as e:
        logger.error(f"Google Ads historical resync failed: {e}")
        return False

if __name__ == "__main__":
    print("HON Google Ads Historical Resync")
    print("=" * 50)
    print("This will sync Google Ads data month by month from January 2024 to present")
    
    success = google_historical_resync()
    
    if success:
        print("\n✅ Google Ads historical resync completed successfully!")
        print("Database now contains historical Google Ads data with proper month-by-month breakdown.")
    else:
        print("\n❌ Google Ads historical resync failed.")
        print("Check the logs for more details. Ensure your Google Ads API credentials are correct.")