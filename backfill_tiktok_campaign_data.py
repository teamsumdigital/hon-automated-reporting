#!/usr/bin/env python3
"""
Comprehensive TikTok Campaign Data Backfill Script
Backfills data from January 2024 through August 14, 2025
Fixes any missing data, zeroes, and adds CPM calculation
"""

import os
import sys
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import calendar
from dotenv import load_dotenv
from supabase import create_client
from loguru import logger

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.tiktok_ads_service import TikTokAdsService

class TikTokBackfillService:
    """Service to backfill TikTok campaign data comprehensively"""
    
    def __init__(self):
        # Initialize Supabase
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        
        # Initialize TikTok service
        self.tiktok_service = TikTokAdsService()
        
        logger.info("TikTok Backfill Service initialized")
    
    def add_cpm_column(self):
        """Add CPM column to database if not exists"""
        try:
            # Read and execute the CPM migration SQL
            with open('add_cpm_column_tiktok.sql', 'r') as f:
                sql_content = f.read()
            
            # Execute the SQL (note: this might not work directly with supabase-py)
            # You may need to run this manually in Supabase SQL editor
            logger.info("Please run the add_cpm_column_tiktok.sql file in Supabase SQL editor to add CPM column")
            logger.info("CPM will be calculated as: cost / (impressions / 1000)")
            
        except Exception as e:
            logger.error(f"Error with CPM column setup: {e}")
    
    def get_month_date_range(self, year: int, month: int) -> tuple:
        """Get start and end dates for a given month"""
        start_date = date(year, month, 1)
        
        # Get last day of month
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        
        return start_date, end_date
    
    def get_existing_data_count(self, start_date: date, end_date: date) -> int:
        """Check how much data already exists for a date range"""
        try:
            result = self.supabase.table('tiktok_campaign_data').select('*').gte(
                'reporting_starts', start_date.isoformat()
            ).lte('reporting_ends', end_date.isoformat()).execute()
            
            return len(result.data) if result.data else 0
        except Exception as e:
            logger.error(f"Error checking existing data: {e}")
            return 0
    
    def backfill_month(self, year: int, month: int, force_refresh: bool = False):
        """Backfill data for a specific month"""
        start_date, end_date = self.get_month_date_range(year, month)
        month_name = start_date.strftime("%B %Y")
        
        logger.info(f"🗓️ Processing {month_name} ({start_date} to {end_date})")
        
        # Check existing data
        existing_count = self.get_existing_data_count(start_date, end_date)
        
        if existing_count > 0 and not force_refresh:
            logger.info(f"   📊 Found {existing_count} existing records - skipping (use force_refresh=True to override)")
            return True
        
        if existing_count > 0 and force_refresh:
            logger.info(f"   🔄 Found {existing_count} existing records - will refresh due to force_refresh=True")
        
        try:
            # Fetch TikTok data for the month
            logger.info(f"   📡 Fetching TikTok data from API...")
            insights = self.tiktok_service.get_campaign_insights(start_date, end_date)
            
            if not insights:
                logger.warning(f"   ⚠️ No insights returned for {month_name}")
                return True
            
            logger.info(f"   📈 Retrieved {len(insights)} campaign insights")
            
            # Convert to campaign data
            campaign_data_list = self.tiktok_service.convert_to_campaign_data(insights)
            
            if not campaign_data_list:
                logger.warning(f"   ⚠️ No campaign data converted for {month_name}")
                return True
            
            logger.info(f"   ✅ Converted {len(campaign_data_list)} campaigns")
            
            # Upsert to database
            success_count = 0
            error_count = 0
            
            for campaign_data in campaign_data_list:
                try:
                    # Calculate CPM
                    cpm = Decimal('0')
                    if campaign_data.impressions > 0:
                        cpm = (campaign_data.amount_spent_usd / (Decimal(campaign_data.impressions) / 1000)).quantize(Decimal('0.0001'))
                    
                    # Prepare data for upsert
                    upsert_data = {
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
                        'cpm': float(cpm),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    # Upsert (update if exists, insert if not)
                    result = self.supabase.table('tiktok_campaign_data').upsert(
                        upsert_data,
                        on_conflict='campaign_id,reporting_starts,reporting_ends'
                    ).execute()
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"   ❌ Failed to upsert campaign {campaign_data.campaign_id}: {e}")
                    error_count += 1
                    continue
            
            logger.info(f"   💾 Database upsert: {success_count} success, {error_count} errors")
            
            # Update monthly summary
            self.update_monthly_summary(year, month, campaign_data_list)
            
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Error processing {month_name}: {e}")
            return False
    
    def update_monthly_summary(self, year: int, month: int, campaign_data_list: list):
        """Update monthly summary table"""
        try:
            report_month = date(year, month, 1)
            
            # Calculate totals
            total_spend = sum(cd.amount_spent_usd for cd in campaign_data_list)
            total_purchases = sum(cd.website_purchases for cd in campaign_data_list)
            total_revenue = sum(cd.purchases_conversion_value for cd in campaign_data_list)
            total_impressions = sum(cd.impressions for cd in campaign_data_list)
            total_clicks = sum(cd.link_clicks for cd in campaign_data_list)
            
            # Calculate averages
            active_campaigns = [cd for cd in campaign_data_list if cd.amount_spent_usd > 0]
            
            avg_cpa = sum(cd.cpa for cd in active_campaigns) / len(active_campaigns) if active_campaigns else 0
            avg_roas = sum(cd.roas for cd in active_campaigns) / len(active_campaigns) if active_campaigns else 0
            avg_cpc = sum(cd.cpc for cd in active_campaigns) / len(active_campaigns) if active_campaigns else 0
            avg_cpm = total_spend / (total_impressions / 1000) if total_impressions > 0 else 0
            
            summary_data = {
                'report_month': report_month.isoformat(),
                'report_date': date.today().isoformat(),
                'total_spend': float(total_spend),
                'total_purchases': total_purchases,
                'total_revenue': float(total_revenue),
                'total_impressions': total_impressions,
                'total_clicks': total_clicks,
                'avg_cpa': float(avg_cpa),
                'avg_roas': float(avg_roas),
                'avg_cpc': float(avg_cpc),
                'avg_cpm': float(avg_cpm),
                'created_at': datetime.now().isoformat()
            }
            
            # Upsert monthly summary
            result = self.supabase.table('tiktok_monthly_reports').upsert(
                summary_data,
                on_conflict='report_month,report_date'
            ).execute()
            
            logger.info(f"   📊 Monthly summary updated: ${total_spend:.2f} spend, {total_purchases} purchases, {avg_roas:.2f} ROAS")
            
        except Exception as e:
            logger.error(f"   ❌ Error updating monthly summary: {e}")
    
    def fix_existing_zero_data(self):
        """Fix existing records with zero ROAS or missing data"""
        try:
            logger.info("🔧 Checking for records with zero/missing ROAS data...")
            
            # Get records with zero ROAS but non-zero spend
            result = self.supabase.table('tiktok_campaign_data').select('*').eq(
                'roas', 0
            ).gt('amount_spent_usd', 0).execute()
            
            zero_roas_records = result.data if result.data else []
            
            if zero_roas_records:
                logger.info(f"   🔍 Found {len(zero_roas_records)} records with zero ROAS but spend > 0")
                
                for record in zero_roas_records[:10]:  # Limit to first 10 for safety
                    start_date = datetime.fromisoformat(record['reporting_starts']).date()
                    end_date = datetime.fromisoformat(record['reporting_ends']).date()
                    
                    logger.info(f"   🔄 Re-fetching data for campaign {record['campaign_id']} ({start_date} to {end_date})")
                    
                    # Re-fetch from API
                    insights = self.tiktok_service.get_campaign_insights(
                        start_date, end_date, 
                        campaign_ids=[record['campaign_id']]
                    )
                    
                    if insights:
                        campaign_data_list = self.tiktok_service.convert_to_campaign_data(insights)
                        if campaign_data_list:
                            campaign_data = campaign_data_list[0]
                            
                            # Calculate CPM
                            cpm = Decimal('0')
                            if campaign_data.impressions > 0:
                                cpm = (campaign_data.amount_spent_usd / (Decimal(campaign_data.impressions) / 1000)).quantize(Decimal('0.0001'))
                            
                            # Update record
                            update_data = {
                                'roas': float(campaign_data.roas),
                                'purchases_conversion_value': float(campaign_data.purchases_conversion_value),
                                'website_purchases': campaign_data.website_purchases,
                                'cpa': float(campaign_data.cpa),
                                'cpm': float(cpm),
                                'updated_at': datetime.now().isoformat()
                            }
                            
                            self.supabase.table('tiktok_campaign_data').update(
                                update_data
                            ).eq('id', record['id']).execute()
                            
                            logger.info(f"   ✅ Updated campaign {record['campaign_id']} with ROAS: {campaign_data.roas:.2f}")
            else:
                logger.info("   ✅ No records found with zero ROAS and spend > 0")
            
        except Exception as e:
            logger.error(f"Error fixing zero ROAS data: {e}")
    
    def run_full_backfill(self, force_refresh: bool = False):
        """Run complete backfill from January 2024 to August 14, 2025"""
        logger.info("🚀 Starting TikTok Campaign Data Backfill")
        logger.info("=" * 60)
        
        # Add CPM column
        self.add_cpm_column()
        
        # Define date ranges
        start_year, start_month = 2024, 1
        end_year, end_month = 2025, 8
        
        success_count = 0
        error_count = 0
        
        # Process each month
        current_date = date(start_year, start_month, 1)
        
        while current_date <= date(end_year, end_month, 14):  # Through August 14, 2025
            year = current_date.year
            month = current_date.month
            
            try:
                success = self.backfill_month(year, month, force_refresh)
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to process {year}-{month}: {e}")
                error_count += 1
            
            # Move to next month
            current_date = current_date + relativedelta(months=1)
        
        # Fix existing zero data
        self.fix_existing_zero_data()
        
        # Final summary
        logger.info("=" * 60)
        logger.info("🎯 TikTok Backfill Complete!")
        logger.info(f"   ✅ Successful months: {success_count}")
        logger.info(f"   ❌ Failed months: {error_count}")
        logger.info(f"   📊 Date range: January 2024 - August 14, 2025")
        logger.info(f"   💡 CPM calculated as: cost / (impressions / 1000)")

def main():
    """Main function to run the backfill"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Backfill TikTok campaign data')
    parser.add_argument('--force-refresh', action='store_true', 
                       help='Force refresh of existing data')
    parser.add_argument('--fix-zeros-only', action='store_true',
                       help='Only fix records with zero ROAS')
    
    args = parser.parse_args()
    
    try:
        backfill_service = TikTokBackfillService()
        
        if args.fix_zeros_only:
            logger.info("Running zero ROAS fix only...")
            backfill_service.fix_existing_zero_data()
        else:
            logger.info(f"Running full backfill (force_refresh={args.force_refresh})")
            backfill_service.run_full_backfill(force_refresh=args.force_refresh)
            
    except Exception as e:
        logger.error(f"Backfill failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()