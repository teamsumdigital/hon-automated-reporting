#!/usr/bin/env python3
"""
Test Google Ads API Response to Investigate Data Quality Issues
This script will make direct API calls to Google Ads and compare with stored data
"""

import os
from datetime import date, datetime, timedelta
from decimal import Decimal
from app.services.google_ads_service import GoogleAdsService
from supabase import create_client

def main():
    print("=== GOOGLE ADS API RESPONSE INVESTIGATION ===")
    print("Testing direct API calls vs stored database values")
    print()
    
    # Initialize services
    try:
        google_service = GoogleAdsService()
        print("✓ Google Ads Service initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize Google Ads Service: {e}")
        return
    
    # Test connection
    if not google_service.test_connection():
        print("✗ Google Ads API connection failed")
        return
    print("✓ Google Ads API connection successful")
    print()
    
    # Initialize Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # Test a specific date and campaign with known issues
    test_date = date(2025, 8, 13)
    print(f"Testing data for {test_date}")
    print()
    
    try:
        # Get fresh API data
        api_insights = google_service.get_campaign_insights(
            start_date=test_date,
            end_date=test_date
        )
        print(f"Retrieved {len(api_insights)} insights from Google Ads API")
        
        # Convert to campaign data format
        api_campaign_data = google_service.convert_to_campaign_data(api_insights)
        print(f"Converted to {len(api_campaign_data)} campaign data objects")
        print()
        
        # Compare with database records for the same date
        db_response = supabase.table('google_campaign_data')\
            .select('*')\
            .eq('reporting_starts', test_date.strftime('%Y-%m-%d'))\
            .execute()
        
        db_data = db_response.data if db_response.data else []
        print(f"Found {len(db_data)} database records for {test_date}")
        print()
        
        # Analyze first few campaigns
        print("=== API vs DATABASE COMPARISON ===")
        
        for i, api_data in enumerate(api_campaign_data[:5]):
            campaign_id = api_data.campaign_id
            
            # Find matching database record
            db_record = None
            for db_row in db_data:
                if str(db_row['campaign_id']) == str(campaign_id):
                    db_record = db_row
                    break
            
            print(f"\nCampaign {i+1}: {api_data.campaign_name} (ID: {campaign_id})")
            print(f"API Data:")
            print(f"  Spend: ${api_data.amount_spent_usd}")
            print(f"  Revenue: ${api_data.purchases_conversion_value}")
            print(f"  Purchases: {api_data.website_purchases}")
            print(f"  Impressions: {api_data.impressions}")
            print(f"  Clicks: {api_data.link_clicks}")
            print(f"  Calculated CPA: ${api_data.cpa}")
            print(f"  Calculated ROAS: {api_data.roas}")
            
            if db_record:
                print(f"Database Data:")
                print(f"  Spend: ${db_record['amount_spent_usd']}")
                print(f"  Revenue: ${db_record['purchases_conversion_value']}")
                print(f"  Purchases: {db_record['website_purchases']}")
                print(f"  Impressions: {db_record['impressions']}")
                print(f"  Clicks: {db_record['link_clicks']}")
                print(f"  Stored CPA: ${db_record['cpa']}")
                print(f"  Stored ROAS: {db_record['roas']}")
                
                # Check for differences
                spend_diff = abs(float(api_data.amount_spent_usd) - float(db_record['amount_spent_usd']))
                revenue_diff = abs(float(api_data.purchases_conversion_value) - float(db_record['purchases_conversion_value']))
                purchases_diff = abs(api_data.website_purchases - int(db_record['website_purchases']))
                roas_diff = abs(float(api_data.roas) - float(db_record['roas']))
                cpa_diff = abs(float(api_data.cpa) - float(db_record['cpa']))
                
                print(f"Differences:")
                print(f"  Spend: ${spend_diff:.2f}")
                print(f"  Revenue: ${revenue_diff:.2f}")
                print(f"  Purchases: {purchases_diff}")
                print(f"  ROAS: {roas_diff:.4f}")
                print(f"  CPA: ${cpa_diff:.2f}")
                
                if spend_diff > 0.01 or revenue_diff > 0.01 or purchases_diff > 0:
                    print("  ⚠️  DATA MISMATCH DETECTED!")
                elif roas_diff > 0.01 or cpa_diff > 0.01:
                    print("  ⚠️  CALCULATION DISCREPANCY DETECTED!")
                else:
                    print("  ✓ Data matches")
            else:
                print("  ⚠️  NO MATCHING DATABASE RECORD FOUND")
        
        # Test the calculation logic directly
        print("\n=== CALCULATION LOGIC VERIFICATION ===")
        if api_campaign_data:
            test_data = api_campaign_data[0]
            
            # Manual calculations
            spend = float(test_data.amount_spent_usd)
            revenue = float(test_data.purchases_conversion_value)
            purchases = test_data.website_purchases
            clicks = test_data.link_clicks
            
            manual_roas = revenue / spend if spend > 0 else 0
            manual_cpa = spend / purchases if purchases > 0 else 0
            manual_cpc = spend / clicks if clicks > 0 else 0
            
            print(f"Manual calculations for {test_data.campaign_name}:")
            print(f"  Manual ROAS: {manual_roas:.4f}")
            print(f"  Service ROAS: {float(test_data.roas):.4f}")
            print(f"  Manual CPA: ${manual_cpa:.2f}")
            print(f"  Service CPA: ${float(test_data.cpa):.2f}")
            print(f"  Manual CPC: ${manual_cpc:.4f}")
            print(f"  Service CPC: ${float(test_data.cpc):.4f}")
            
        # Check raw API response format
        print("\n=== RAW API INSIGHT ANALYSIS ===")
        if api_insights:
            sample_insight = api_insights[0]
            print(f"Sample raw API insight:")
            print(f"  Campaign ID: {sample_insight.campaign_id}")
            print(f"  Campaign Name: {sample_insight.campaign_name}")
            print(f"  Cost: {sample_insight.cost}")
            print(f"  Cost Micros: {sample_insight.cost_micros}")
            print(f"  Conversions: {sample_insight.conversions}")
            print(f"  Conversions Value: {sample_insight.conversions_value}")
            print(f"  Impressions: {sample_insight.impressions}")
            print(f"  Clicks: {sample_insight.clicks}")
            print(f"  Date Start: {sample_insight.date_start}")
            print(f"  Date Stop: {sample_insight.date_stop}")
            
    except Exception as e:
        print(f"Error during investigation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()