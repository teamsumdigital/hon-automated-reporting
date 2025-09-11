#!/usr/bin/env python3
"""
Daily Conversion Refresh for Google Ads Data Quality
Prevents future ROAS/CPA accuracy issues by refreshing conversion data daily

This script should be run daily via cron/scheduler to:
1. Refresh conversion data for the past 30 days (attribution window)
2. Monitor data quality and alert on discrepancies  
3. Ensure ROAS/CPA calculations remain accurate
"""

import os
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from supabase import create_client
from loguru import logger

# Add the app directory to the path
sys.path.append('.')

def main():
    print("📅 DAILY CONVERSION REFRESH - Google Ads Data Quality")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Purpose: Maintain ROAS/CPA calculation accuracy")
    print()

    try:
        from app.services.google_ads_service import GoogleAdsService
        
        # Initialize services
        SUPABASE_URL = os.getenv('SUPABASE_URL')
        SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            print("❌ ERROR: Missing Supabase credentials")
            return
        
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        google_service = GoogleAdsService()
        
        # Test API connection
        if not google_service.test_connection():
            print("❌ ERROR: Google Ads API connection failed")
            return
        
        print("✅ Services initialized successfully")
        
        # Define refresh period (past 30 days for attribution window)
        end_date = date.today() - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=30)   # 30 days back
        
        print(f"📅 Refreshing conversion data: {start_date} to {end_date}")
        print("(30-day attribution window to capture delayed conversions)")
        print()
        
        # Get current database data for the period
        db_response = supabase.table('google_campaign_data')\
            .select('campaign_id', 'reporting_starts', 'purchases_conversion_value', 'website_purchases', 'roas', 'cpa')\
            .gte('reporting_starts', start_date.isoformat())\
            .lte('reporting_starts', end_date.isoformat())\
            .execute()
        
        current_data = db_response.data if db_response.data else []
        print(f"🔍 Found {len(current_data)} records to refresh")
        
        if not current_data:
            print("ℹ️  No data found for refresh period - this is normal for new setups")
            return
        
        # Track changes
        total_refreshed = 0
        significant_changes = 0  # Changes > 5%
        revenue_before = 0
        revenue_after = 0
        
        # Process in weekly chunks to manage API limits
        current = start_date
        while current <= end_date:
            chunk_end = min(current + timedelta(days=6), end_date)
            
            print(f"  Processing {current} to {chunk_end}...")
            
            try:
                # Get fresh API data for this chunk
                api_insights = google_service.get_monthly_campaign_insights(current, chunk_end)
                
                if api_insights:
                    # Convert to campaign data with fresh conversions
                    campaign_data_list = google_service.convert_to_campaign_data(api_insights)
                    
                    for campaign_data in campaign_data_list:
                        # Find matching database record
                        matching_records = [
                            r for r in current_data 
                            if (str(r['campaign_id']) == str(campaign_data.campaign_id) and
                                r['reporting_starts'] == campaign_data.reporting_starts.isoformat())
                        ]
                        
                        if matching_records:
                            db_record = matching_records[0]
                            
                            # Calculate changes
                            old_revenue = float(db_record['purchases_conversion_value'] or 0)
                            new_revenue = float(campaign_data.purchases_conversion_value)
                            old_purchases = int(db_record['website_purchases'] or 0)
                            new_purchases = campaign_data.website_purchases
                            
                            revenue_before += old_revenue
                            revenue_after += new_revenue
                            
                            # Check for significant changes (> 5% or > $50 for small amounts)
                            revenue_change_pct = abs(new_revenue - old_revenue) / old_revenue * 100 if old_revenue > 0 else 100
                            purchase_change = abs(new_purchases - old_purchases)
                            
                            is_significant = (
                                revenue_change_pct > 5 or 
                                abs(new_revenue - old_revenue) > 50 or
                                purchase_change > 0
                            )
                            
                            if is_significant:
                                significant_changes += 1
                                
                                # Log significant changes for monitoring
                                logger.info(f"Significant conversion update: Campaign {campaign_data.campaign_id} "
                                          f"on {campaign_data.reporting_starts}: "
                                          f"Revenue ${old_revenue:.2f} → ${new_revenue:.2f} "
                                          f"({revenue_change_pct:.1f}% change), "
                                          f"Purchases {old_purchases} → {new_purchases}")
                            
                            # Update database with fresh conversion data
                            if old_revenue != new_revenue or old_purchases != new_purchases:
                                update_data = {
                                    "website_purchases": campaign_data.website_purchases,
                                    "purchases_conversion_value": float(campaign_data.purchases_conversion_value),
                                    "cpa": float(campaign_data.cpa),
                                    "roas": float(campaign_data.roas),
                                    "updated_at": datetime.now().isoformat()
                                }
                                
                                supabase.table("google_campaign_data")\
                                    .update(update_data)\
                                    .eq("campaign_id", campaign_data.campaign_id)\
                                    .eq("reporting_starts", campaign_data.reporting_starts.isoformat())\
                                    .execute()
                                
                                total_refreshed += 1
                    
                    print(f"    ✅ Processed {len(campaign_data_list)} campaigns")
                else:
                    print(f"    ℹ️  No API data for {current} to {chunk_end}")
                    
            except Exception as e:
                print(f"    ❌ Error processing {current}: {e}")
                logger.error(f"Daily conversion refresh error for {current}: {e}")
                
            current = chunk_end + timedelta(days=1)
        
        # Calculate improvement metrics
        revenue_improvement = revenue_after - revenue_before
        improvement_pct = (revenue_improvement / revenue_before * 100) if revenue_before > 0 else 0
        
        print()
        print("📊 DAILY REFRESH SUMMARY:")
        print(f"  Records Refreshed: {total_refreshed}")
        print(f"  Significant Changes: {significant_changes}")
        print(f"  Revenue Before: ${revenue_before:,.2f}")
        print(f"  Revenue After: ${revenue_after:,.2f}")
        print(f"  Revenue Change: ${revenue_improvement:,.2f} ({improvement_pct:+.2f}%)")
        
        # Data quality assessment
        if significant_changes > 0:
            print(f"\n⚠️  ATTRIBUTION UPDATES DETECTED:")
            print(f"   {significant_changes} campaigns had conversion data updates")
            print(f"   This is normal - Google Ads attribution windows cause delayed conversions")
            
            # Alert if changes are unusually large
            if improvement_pct > 10 or improvement_pct < -10:
                print(f"   🚨 ALERT: Large revenue change detected ({improvement_pct:+.1f}%)")
                print(f"   Consider investigating potential data quality issues")
                
                # Log alert for monitoring systems
                logger.warning(f"Large daily conversion refresh change: {improvement_pct:+.1f}% revenue change, "
                             f"{significant_changes} campaigns affected")
        else:
            print("\n✅ No significant conversion updates - data quality stable")
        
        # Update data quality metrics
        current_time = datetime.now().isoformat()
        quality_metrics = {
            "refresh_date": current_time,
            "records_refreshed": total_refreshed,
            "significant_changes": significant_changes,
            "revenue_improvement": float(revenue_improvement),
            "improvement_percentage": float(improvement_pct)
        }
        
        # Store quality metrics for tracking (optional - would need a quality_metrics table)
        # supabase.table("data_quality_metrics").insert(quality_metrics).execute()
        
        print(f"\n✅ Daily conversion refresh completed successfully")
        print(f"Next refresh scheduled for tomorrow")
        
        # Return metrics for external monitoring
        return quality_metrics
        
    except Exception as e:
        print(f"❌ DAILY REFRESH ERROR: {e}")
        logger.error(f"Daily conversion refresh failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    main()