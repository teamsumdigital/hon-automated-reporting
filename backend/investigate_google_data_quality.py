#!/usr/bin/env python3
"""
Data Quality Investigation for Google Ads Data
Investigates ROAS and CPA calculation issues for August 1-26, 2025
"""

import os
from datetime import date
from supabase import create_client
from decimal import Decimal

def main():
    # Initialize Supabase connection
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print('ERROR: Missing Supabase credentials')
        exit(1)

    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    print('=== GOOGLE ADS DATA QUALITY INVESTIGATION ===')
    print('Checking google_campaign_data table for August 1-26, 2025')
    print()

    # Query Google Ads data for August 1-26, 2025
    try:
        response = supabase.table('google_campaign_data').select('*').gte('reporting_starts', '2025-08-01').lte('reporting_ends', '2025-08-26').execute()
        
        data = response.data if response.data else []
        print(f'Found {len(data)} records for August 1-26, 2025')
        print()
        
        if data:
            # Analyze a sample of records
            print('=== SAMPLE RECORDS (First 5) ===')
            for i, record in enumerate(data[:5]):
                print(f'Record {i+1}:')
                print(f'  Campaign ID: {record["campaign_id"]}')
                print(f'  Campaign Name: {record["campaign_name"]}')
                print(f'  Date Range: {record["reporting_starts"]} to {record["reporting_ends"]}')
                print(f'  Spend: ${record["amount_spent_usd"]}')
                print(f'  Purchases: {record["website_purchases"]}')
                print(f'  Revenue: ${record["purchases_conversion_value"]}')
                print(f'  ROAS: {record["roas"]}')
                print(f'  CPA: ${record["cpa"]}')
                print(f'  Impressions: {record["impressions"]}')
                print(f'  Clicks: {record["link_clicks"]}')
                print()
            
            # Analyze ROAS and CPA calculations
            print('=== CALCULATION ANALYSIS ===')
            issues_found = 0
            
            for record in data:
                spend = float(record['amount_spent_usd'] or 0)
                revenue = float(record['purchases_conversion_value'] or 0)
                purchases = int(record['website_purchases'] or 0)
                stored_roas = float(record['roas'] or 0)
                stored_cpa = float(record['cpa'] or 0)
                
                # Calculate expected ROAS and CPA
                expected_roas = revenue / spend if spend > 0 else 0
                expected_cpa = spend / purchases if purchases > 0 else 0
                
                # Check for discrepancies (allowing for small rounding differences)
                roas_diff = abs(stored_roas - expected_roas)
                cpa_diff = abs(stored_cpa - expected_cpa)
                
                if roas_diff > 0.01 or cpa_diff > 0.01:
                    issues_found += 1
                    if issues_found <= 10:  # Show first 10 issues
                        print(f'ISSUE FOUND - Campaign: {record["campaign_name"]}')
                        print(f'  Date: {record["reporting_starts"]}')
                        print(f'  Spend: ${spend}')
                        print(f'  Revenue: ${revenue}')
                        print(f'  Purchases: {purchases}')
                        print(f'  Stored ROAS: {stored_roas}')
                        print(f'  Expected ROAS: {expected_roas:.4f}')
                        print(f'  ROAS Difference: {roas_diff:.4f}')
                        print(f'  Stored CPA: ${stored_cpa}')
                        print(f'  Expected CPA: ${expected_cpa:.2f}')
                        print(f'  CPA Difference: ${cpa_diff:.2f}')
                        print()
            
            print(f'TOTAL ISSUES FOUND: {issues_found} out of {len(data)} records')
            
            # Summary statistics
            total_spend = sum(float(r['amount_spent_usd'] or 0) for r in data)
            total_revenue = sum(float(r['purchases_conversion_value'] or 0) for r in data)
            total_purchases = sum(int(r['website_purchases'] or 0) for r in data)
            
            print()
            print('=== SUMMARY STATISTICS ===')
            print(f'Total Spend: ${total_spend:.2f}')
            print(f'Total Revenue: ${total_revenue:.2f}')
            print(f'Total Purchases: {total_purchases}')
            print(f'Overall ROAS: {total_revenue/total_spend:.4f}' if total_spend > 0 else 'Overall ROAS: 0')
            print(f'Overall CPA: ${total_spend/total_purchases:.2f}' if total_purchases > 0 else 'Overall CPA: $0')
            
        else:
            print('No data found for the specified date range!')
            
            # Check if there is any Google Ads data at all
            all_response = supabase.table('google_campaign_data').select('reporting_starts', 'reporting_ends', 'campaign_name').order('reporting_starts', desc=True).limit(20).execute()
            all_data = all_response.data if all_response.data else []
            
            if all_data:
                print()
                print('=== AVAILABLE DATA (Most Recent 20 Records) ===')
                for record in all_data:
                    print(f'Campaign: {record["campaign_name"]} | Date: {record["reporting_starts"]} to {record["reporting_ends"]}')
            else:
                print('No Google Ads data found in database at all!')
                
    except Exception as e:
        print(f'ERROR querying database: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()