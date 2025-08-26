#!/usr/bin/env python3
"""
Debug the API vs Service discrepancy for July 2025
"""

import os
import sys
from datetime import date
import requests
import json

# Add the backend path to import services
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.tiktok_reporting import TikTokReportingService
from backend.app.models.tiktok_campaign_data import TikTokDashboardFilters

def debug_api_vs_service():
    """Debug the discrepancy between API and service responses"""
    
    print("🔍 Debugging API vs Service Discrepancy")
    print("=" * 50)
    
    try:
        service = TikTokReportingService()
        
        # Test 1: Direct service call for July 2025 (no filters)
        print("📊 Test 1: Direct Service Call")
        pivot_data = service.generate_pivot_table_data(None)
        july_pivot = [month for month in pivot_data if month.month == '2025-07']
        
        if july_pivot:
            service_spend = july_pivot[0].spend
            print(f"   Service pivot data: ${service_spend:,.2f}")
        else:
            print("   No July 2025 data in service pivot")
        
        # Test 2: API call to dashboard endpoint
        print("\n📊 Test 2: API Dashboard Endpoint")
        try:
            api_response = requests.get('http://localhost:8007/api/tiktok-reports/dashboard')
            
            if api_response.status_code == 200:
                data = api_response.json()
                
                # Check pivot data in API response
                pivot_data_api = data.get('pivot_data', [])
                api_july = [month for month in pivot_data_api if month['month'] == '2025-07']
                
                if api_july:
                    api_july_spend = api_july[0]['spend']
                    print(f"   API pivot data: ${api_july_spend:,.2f}")
                    
                    # Check if this matches what we expect
                    if abs(float(service_spend) - api_july_spend) < 0.01:
                        print("   ✅ API pivot matches service")
                    else:
                        diff = float(service_spend) - api_july_spend
                        print(f"   ❌ API pivot differs by: ${diff:+,.2f}")
                else:
                    print("   No July 2025 data in API pivot response")
                
                # Check summary data
                summary = data.get('summary', {})
                summary_spend = summary.get('total_spend', 0)
                print(f"   API summary spend: ${summary_spend:,.2f}")
                
                # Analyze the full API response structure
                print("\n📋 API Response Structure:")
                print(f"   Summary keys: {list(summary.keys())}")
                print(f"   Pivot data months: {[p.get('month') for p in pivot_data_api]}")
                
            else:
                print(f"   API call failed: {api_response.status_code}")
        
        except Exception as api_error:
            print(f"   API call error: {api_error}")
        
        # Test 3: Check month-to-date summary directly
        print("\n📊 Test 3: Month-to-date Summary Service")
        
        # Current month (August 2025)
        current_summary = service.get_month_to_date_summary()
        print(f"   Current month summary: ${current_summary.get('total_spend', 0):,.2f}")
        
        # July 2025 specifically
        july_filters = TikTokDashboardFilters(
            start_date=date(2025, 7, 1),
            end_date=date(2025, 7, 31)
        )
        july_summary = service.get_month_to_date_summary(july_filters)
        print(f"   July 2025 summary: ${july_summary.get('total_spend', 0):,.2f}")
        
        # Test 4: API call with no filters but for July specifically
        print("\n📊 Test 4: API Call for All Data")
        try:
            # Get all data from API
            full_api_response = requests.get('http://localhost:8007/api/tiktok-reports/monthly')
            
            if full_api_response.status_code == 200:
                all_months = full_api_response.json()
                july_month = [m for m in all_months if m['month'] == '2025-07']
                
                if july_month:
                    monthly_july_spend = july_month[0]['spend']
                    print(f"   Monthly API July: ${monthly_july_spend:,.2f}")
                    
                    if abs(float(service_spend) - monthly_july_spend) < 0.01:
                        print("   ✅ Monthly API matches service")
                    else:
                        diff = float(service_spend) - monthly_july_spend
                        print(f"   ❌ Monthly API differs by: ${diff:+,.2f}")
                else:
                    print("   No July 2025 in monthly API response")
            
        except Exception as monthly_error:
            print(f"   Monthly API error: {monthly_error}")
        
        print("\n📋 ANALYSIS:")
        print("=" * 40)
        print("The issue is that the user is seeing $10,385 on the frontend")
        print("But our service is returning $30,452.43 consistently")
        print("This suggests the frontend is either:")
        print("1. Using a different API endpoint")
        print("2. Processing the data incorrectly")
        print("3. Getting cached/stale data")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api_vs_service()