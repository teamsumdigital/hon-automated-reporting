#!/usr/bin/env python3
"""
Google Ads Monthly Historical Data Sync
Fetches monthly campaign data from January 2024 through August 12, 2025
"""

import os
import sys
import time
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from loguru import logger
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from supabase import create_client, Client
from app.services.google_ads_service import GoogleAdsService
from app.services.campaign_type_service import CampaignTypeService

class GoogleMonthlySync:
    """Handles monthly Google Ads data synchronization"""
    
    def __init__(self):
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Initialize Google Ads service
        try:
            self.google_ads_service = GoogleAdsService()
        except Exception as e:
            logger.error(f"Failed to initialize Google Ads service: {e}")
            raise
        
        # Initialize Campaign Type service
        self.campaign_type_service = CampaignTypeService()
        
        logger.info("Google Monthly Sync initialized")
    
    def get_month_date_ranges(self, start_year: int = 2024, start_month: int = 1, 
                             end_year: int = 2025, end_month: int = 8, end_day: int = 12) -> List[tuple]:
        """Generate list of month date ranges from start to end"""
        month_ranges = []
        
        current = date(start_year, start_month, 1)
        end_date = date(end_year, end_month, end_day)
        
        while current <= end_date:
            # Calculate month start and end dates
            month_start = current
            
            # For the last month (August 2025), use the specific end date
            if current.year == end_year and current.month == end_month:
                month_end = end_date
            else:
                # Calculate last day of the month
                if current.month == 12:
                    next_month = date(current.year + 1, 1, 1)
                else:
                    next_month = date(current.year, current.month + 1, 1)
                month_end = next_month - timedelta(days=1)
            
            month_ranges.append((month_start, month_end))
            logger.info(f"Added month range: {month_start} to {month_end}")
            
            # Move to next month
            current = current + relativedelta(months=1)
        
        return month_ranges
    
    def sync_month_data(self, month_start: date, month_end: date) -> int:
        """Sync data for a specific month"""
        try:
            logger.info(f"Syncing Google Ads data for {month_start.strftime('%B %Y')} ({month_start} to {month_end})")
            
            # Fetch monthly insights from Google Ads
            insights = self.google_ads_service.get_monthly_campaign_insights(
                start_date=month_start,
                end_date=month_end
            )
            
            if not insights:
                logger.warning(f"No insights returned for {month_start} to {month_end}")
                return 0
            
            # Convert insights to campaign data
            campaign_data_list = self.google_ads_service.convert_to_campaign_data(insights)
            
            if not campaign_data_list:
                logger.warning(f"No campaign data generated for {month_start} to {month_end}")
                return 0
            
            # Insert/update data in Supabase
            inserted_count = 0
            for campaign_data in campaign_data_list:
                try:
                    # Prepare data for database
                    db_data = {
                        'campaign_id': campaign_data.campaign_id,
                        'campaign_name': campaign_data.campaign_name,
                        'category': campaign_data.category,
                        'campaign_type': campaign_data.campaign_type,
                        'reporting_starts': campaign_data.reporting_starts.isoformat(),
                        'reporting_ends': campaign_data.reporting_ends.isoformat(),
                        'amount_spent_usd': float(campaign_data.amount_spent_usd),
                        'website_purchases': campaign_data.website_purchases,
                        'purchases_conversion_value': float(campaign_data.purchases_conversion_value),
                        'impressions': campaign_data.impressions,
                        'link_clicks': campaign_data.link_clicks,
                        'cpa': float(campaign_data.cpa),
                        'roas': float(campaign_data.roas),
                        'cpc': float(campaign_data.cpc),
                    }
                    
                    # Use insert (will skip if duplicate exists due to constraints)
                    result = self.supabase.table('google_campaign_data').insert(db_data).execute()
                    
                    if result.data:
                        inserted_count += 1
                        logger.debug(f"Inserted campaign: {campaign_data.campaign_name} for {campaign_data.reporting_starts}")
                    
                except Exception as e:
                    logger.error(f"Error inserting campaign {campaign_data.campaign_id}: {e}")
                    continue
            
            logger.info(f"Successfully synced {inserted_count} campaigns for {month_start.strftime('%B %Y')}")
            return inserted_count
            
        except Exception as e:
            logger.error(f"Error syncing month {month_start}: {e}")
            return 0
    
    def run_full_sync(self) -> dict:
        """Run complete historical sync from Jan 2024 to Aug 12, 2025"""
        logger.info("Starting Google Ads monthly historical sync")
        
        # Get all month ranges
        month_ranges = self.get_month_date_ranges()
        
        total_synced = 0
        successful_months = 0
        failed_months = 0
        sync_results = {}
        
        for i, (month_start, month_end) in enumerate(month_ranges, 1):
            try:
                logger.info(f"[{i}/{len(month_ranges)}] Processing {month_start.strftime('%B %Y')}...")
                
                synced_count = self.sync_month_data(month_start, month_end)
                
                if synced_count > 0:
                    successful_months += 1
                    total_synced += synced_count
                    sync_results[month_start.strftime('%Y-%m')] = {
                        'status': 'success',
                        'campaigns_synced': synced_count
                    }
                    logger.info(f"✓ {month_start.strftime('%B %Y')}: {synced_count} campaigns")
                else:
                    failed_months += 1
                    sync_results[month_start.strftime('%Y-%m')] = {
                        'status': 'no_data',
                        'campaigns_synced': 0
                    }
                    logger.warning(f"⚠ {month_start.strftime('%B %Y')}: No data")
                
                # Small delay to avoid hitting API rate limits
                if i < len(month_ranges):
                    time.sleep(1)
                
            except Exception as e:
                failed_months += 1
                sync_results[month_start.strftime('%Y-%m')] = {
                    'status': 'error',
                    'error': str(e),
                    'campaigns_synced': 0
                }
                logger.error(f"✗ {month_start.strftime('%B %Y')}: {e}")
                
                # Longer delay on error to avoid further issues
                if i < len(month_ranges):
                    time.sleep(2)
        
        # Summary
        summary = {
            'total_months': len(month_ranges),
            'successful_months': successful_months,
            'failed_months': failed_months,
            'total_campaigns_synced': total_synced,
            'sync_results': sync_results
        }
        
        logger.info(f"Historical sync completed:")
        logger.info(f"  Total months: {summary['total_months']}")
        logger.info(f"  Successful: {summary['successful_months']}")
        logger.info(f"  Failed: {summary['failed_months']}")
        logger.info(f"  Total campaigns synced: {summary['total_campaigns_synced']}")
        
        return summary
    
    def classify_existing_campaigns(self) -> int:
        """Classify campaign types for any existing campaigns that don't have types"""
        logger.info("Classifying existing campaigns without campaign types")
        return self.campaign_type_service.classify_existing_campaigns()

def main():
    """Main execution function"""
    # Set up logging
    logger.remove()
    logger.add(
        "backend/logs/google_monthly_sync.log",
        rotation="10 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    logger.add(sys.stdout, format="{time:HH:mm:ss} | {level} | {message}")
    
    try:
        # Initialize sync service
        sync_service = GoogleMonthlySync()
        
        # Run the full historical sync
        results = sync_service.run_full_sync()
        
        # Classify any existing campaigns without types
        classified_count = sync_service.classify_existing_campaigns()
        if classified_count > 0:
            logger.info(f"Classified {classified_count} existing campaigns")
        
        # Print final summary
        print("\n" + "="*60)
        print("GOOGLE ADS MONTHLY SYNC SUMMARY")
        print("="*60)
        print(f"Date Range: January 2024 - August 12, 2025")
        print(f"Total Months: {results['total_months']}")
        print(f"Successful Months: {results['successful_months']}")
        print(f"Failed Months: {results['failed_months']}")
        print(f"Total Campaigns Synced: {results['total_campaigns_synced']}")
        if classified_count > 0:
            print(f"Campaigns Classified: {classified_count}")
        print("="*60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)