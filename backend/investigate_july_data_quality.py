#!/usr/bin/env python3
"""
July 2025 Google Ads Data Quality Investigation
==============================================
Comprehensive analysis to determine if July data suffers from the same
stale conversion data issue discovered in August 2025.
"""

import os
import sys
from datetime import datetime, timedelta
from supabase import create_client
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import pandas as pd

# Add the parent directory to the Python path
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from dotenv import load_dotenv
load_dotenv()

# Initialize clients
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

# Google Ads Client
client = GoogleAdsClient.load_from_dict({
    "developer_token": os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
    "client_id": os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
    "client_secret": os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
    "refresh_token": os.getenv('GOOGLE_OAUTH_REFRESH_TOKEN'),
    "login_customer_id": os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID'),
    "use_proto_plus": True
})

CUSTOMER_ID = os.getenv('GOOGLE_ADS_CUSTOMER_ID')

def investigate_july_database_data():
    """Examine July 2025 data stored in the database"""
    print("=" * 60)
    print("JULY 2025 DATABASE ANALYSIS")
    print("=" * 60)
    
    try:
        # Query July 2025 data from database
        response = supabase.table('google_campaign_data').select('*').gte('reporting_starts', '2025-07-01').lte('reporting_starts', '2025-07-31').execute()
        
        if not response.data:
            print("❌ NO JULY 2025 DATA FOUND IN DATABASE")
            return None
        
        df = pd.DataFrame(response.data)
        
        print(f"📊 Total July 2025 records: {len(df)}")
        print(f"📅 Date range: {df['reporting_starts'].min()} to {df['reporting_starts'].max()}")
        
        # Analyze key metrics (using actual column names)
        total_spend = df['amount_spent_usd'].sum()
        total_revenue = df['purchases_conversion_value'].sum()
        avg_roas = total_revenue / total_spend if total_spend > 0 else 0
        
        print(f"💰 Total Spend: ${total_spend:,.2f}")
        print(f"💵 Total Revenue: ${total_revenue:,.2f}")
        print(f"📈 Database ROAS: {avg_roas:.2f}")
        
        # Check for campaigns with zero conversions
        zero_conversion_campaigns = df[df['website_purchases'] == 0]
        print(f"⚠️  Campaigns with 0 conversions: {len(zero_conversion_campaigns)} ({len(zero_conversion_campaigns)/len(df)*100:.1f}%)")
        
        # Check for campaigns with zero revenue
        zero_revenue_campaigns = df[df['purchases_conversion_value'] == 0]
        print(f"⚠️  Campaigns with $0 revenue: {len(zero_revenue_campaigns)} ({len(zero_revenue_campaigns)/len(df)*100:.1f}%)")
        
        # Show top campaigns by spend
        print("\n🏆 Top 5 July Campaigns by Spend:")
        top_campaigns = df.nlargest(5, 'amount_spent_usd')[['campaign_name', 'amount_spent_usd', 'purchases_conversion_value', 'website_purchases', 'reporting_starts']]
        for _, row in top_campaigns.iterrows():
            roas = row['purchases_conversion_value'] / row['amount_spent_usd'] if row['amount_spent_usd'] > 0 else 0
            print(f"   • {row['campaign_name'][:50]}...")
            print(f"     Date: {row['reporting_starts']} | Spend: ${row['amount_spent_usd']:.2f} | Revenue: ${row['purchases_conversion_value']:.2f} | ROAS: {roas:.2f}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error analyzing July database data: {e}")
        return None

def fetch_july_api_data():
    """Fetch current July 2025 data from Google Ads API"""
    print("\n" + "=" * 60)
    print("JULY 2025 GOOGLE ADS API ANALYSIS")
    print("=" * 60)
    
    try:
        ga_service = client.get_service("GoogleAdsService")
        
        query = """
        SELECT
            campaign.id,
            campaign.name,
            segments.date,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign
        WHERE segments.date BETWEEN '2025-07-01' AND '2025-07-31'
        AND campaign.status = 'ENABLED'
        ORDER BY segments.date DESC
        """
        
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = CUSTOMER_ID
        search_request.query = query
        
        results = ga_service.search(request=search_request)
        
        api_data = []
        for row in results:
            api_data.append({
                'campaign_id': str(row.campaign.id),
                'campaign_name': row.campaign.name,
                'date': str(row.segments.date),
                'spend': row.metrics.cost_micros / 1_000_000,  # Convert micros to dollars
                'conversions': row.metrics.conversions,
                'revenue': row.metrics.conversions_value
            })
        
        if not api_data:
            print("❌ NO JULY 2025 DATA FROM API")
            return None
            
        api_df = pd.DataFrame(api_data)
        
        print(f"📊 Total July API records: {len(api_df)}")
        print(f"📅 API Date range: {api_df['date'].min()} to {api_df['date'].max()}")
        
        # Analyze API metrics
        total_spend_api = api_df['spend'].sum()
        total_revenue_api = api_df['revenue'].sum()
        avg_roas_api = total_revenue_api / total_spend_api if total_spend_api > 0 else 0
        
        print(f"💰 API Total Spend: ${total_spend_api:,.2f}")
        print(f"💵 API Total Revenue: ${total_revenue_api:,.2f}")
        print(f"📈 API ROAS: {avg_roas_api:.2f}")
        
        # Check API conversion data
        zero_conversion_api = api_df[api_df['conversions'] == 0]
        print(f"⚠️  API Campaigns with 0 conversions: {len(zero_conversion_api)} ({len(zero_conversion_api)/len(api_df)*100:.1f}%)")
        
        return api_df
        
    except GoogleAdsException as ex:
        print(f"❌ Google Ads API Error: {ex}")
        return None
    except Exception as e:
        print(f"❌ Error fetching July API data: {e}")
        return None

def compare_july_data(db_df, api_df):
    """Compare July database data with current API data"""
    print("\n" + "=" * 60)
    print("JULY 2025 DATA COMPARISON & DISCREPANCY ANALYSIS")
    print("=" * 60)
    
    if db_df is None or api_df is None:
        print("❌ Cannot compare - missing database or API data")
        return
    
    # Aggregate data for comparison
    db_totals = {
        'spend': db_df['amount_spent_usd'].sum(),
        'revenue': db_df['purchases_conversion_value'].sum(),
        'conversions': db_df['website_purchases'].sum(),
    }
    
    api_totals = {
        'spend': api_df['spend'].sum(),
        'revenue': api_df['revenue'].sum(), 
        'conversions': api_df['conversions'].sum(),
    }
    
    db_roas = db_totals['revenue'] / db_totals['spend'] if db_totals['spend'] > 0 else 0
    api_roas = api_totals['revenue'] / api_totals['spend'] if api_totals['spend'] > 0 else 0
    
    print("📊 TOTAL JULY METRICS COMPARISON:")
    print(f"   Spend      - Database: ${db_totals['spend']:,.2f} | API: ${api_totals['spend']:,.2f}")
    print(f"   Revenue    - Database: ${db_totals['revenue']:,.2f} | API: ${api_totals['revenue']:,.2f}")
    print(f"   Conversions- Database: {db_totals['conversions']:,.1f} | API: {api_totals['conversions']:,.1f}")
    print(f"   ROAS       - Database: {db_roas:.2f} | API: {api_roas:.2f}")
    
    # Calculate discrepancies
    spend_diff = api_totals['spend'] - db_totals['spend']
    revenue_diff = api_totals['revenue'] - db_totals['revenue']
    conversions_diff = api_totals['conversions'] - db_totals['conversions']
    roas_diff = api_roas - db_roas
    
    print("\n🚨 JULY DATA DISCREPANCIES:")
    print(f"   Spend Gap:      ${spend_diff:,.2f} ({spend_diff/db_totals['spend']*100:.1f}%)")
    print(f"   Revenue Gap:    ${revenue_diff:,.2f} ({revenue_diff/db_totals['revenue']*100 if db_totals['revenue'] > 0 else 0:.1f}%)")
    print(f"   Conversion Gap: {conversions_diff:,.1f} ({conversions_diff/db_totals['conversions']*100 if db_totals['conversions'] > 0 else 0:.1f}%)")
    print(f"   ROAS Gap:       {roas_diff:.2f} ({roas_diff/db_roas*100 if db_roas > 0 else 0:.1f}%)")
    
    # Identify if this is the same issue as August
    if abs(revenue_diff) > 1000:  # Significant revenue discrepancy
        print("\n🔍 JULY ATTRIBUTION WINDOW ANALYSIS:")
        print("   ✅ CONFIRMED: July 2025 data also affected by stale conversion data")
        print(f"   📉 Revenue underreported by ${revenue_diff:,.2f}")
        print(f"   📉 ROAS underreported by {roas_diff:.2f}")
        print("   🎯 Same issue as August - attribution windows not captured in original sync")
    else:
        print("\n✅ July data appears current - no significant attribution lag detected")
    
    # Sample campaign-level analysis
    print("\n🔍 CAMPAIGN-LEVEL DISCREPANCY EXAMPLES:")
    
    # Merge data for comparison
    db_summary = db_df.groupby('campaign_name').agg({
        'amount_spent_usd': 'sum',
        'purchases_conversion_value': 'sum',
        'website_purchases': 'sum'
    }).reset_index()
    db_summary = db_summary.rename(columns={
        'amount_spent_usd': 'spend',
        'purchases_conversion_value': 'revenue',
        'website_purchases': 'conversions'
    })
    
    api_summary = api_df.groupby('campaign_name').agg({
        'spend': 'sum',
        'revenue': 'sum', 
        'conversions': 'sum'
    }).reset_index()
    
    # Find common campaigns
    merged = db_summary.merge(api_summary, on='campaign_name', suffixes=('_db', '_api'))
    
    # Calculate discrepancies per campaign
    merged['revenue_diff'] = merged['revenue_api'] - merged['revenue_db']
    merged['roas_db'] = merged['revenue_db'] / merged['spend_db']
    merged['roas_api'] = merged['revenue_api'] / merged['spend_api']
    merged['roas_diff'] = merged['roas_api'] - merged['roas_db']
    
    # Show top revenue discrepancies
    top_discrepancies = merged.nlargest(5, 'revenue_diff')
    
    for _, row in top_discrepancies.iterrows():
        print(f"   • {row['campaign_name'][:50]}...")
        print(f"     DB Revenue: ${row['revenue_db']:.2f} | API Revenue: ${row['revenue_api']:.2f}")
        print(f"     Revenue Gap: ${row['revenue_diff']:.2f} | ROAS Gap: {row['roas_diff']:.2f}")

def assess_historical_scope():
    """Assess the full scope of the data quality issue"""
    print("\n" + "=" * 60) 
    print("HISTORICAL DATA QUALITY SCOPE ASSESSMENT")
    print("=" * 60)
    
    try:
        # Check what months we have data for
        response = supabase.table('google_campaign_data').select('reporting_starts').execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            df['reporting_starts'] = pd.to_datetime(df['reporting_starts'])
            df['month'] = df['reporting_starts'].dt.to_period('M')
            
            months_with_data = df['month'].unique()
            months_with_data = sorted([str(m) for m in months_with_data])
            
            print(f"📅 Months with Google Ads data: {months_with_data}")
            
            # Focus on 2025 data
            recent_months = [m for m in months_with_data if '2025' in m]
            print(f"🎯 2025 months requiring investigation: {recent_months}")
            
            if len(recent_months) >= 2:
                print("\n🚨 RECOMMENDED REMEDIATION SCOPE:")
                print("   • Re-sync all 2025 Google Ads data to capture attribution updates")
                print("   • Focus on Jul-Aug 2025 as highest priority (recent data)")
                print("   • Implement attribution window buffer in future syncs")
                print("   • Add data freshness monitoring alerts")
            
        else:
            print("❌ No historical data found")
            
    except Exception as e:
        print(f"❌ Error assessing historical scope: {e}")

def generate_july_remediation_plan():
    """Generate specific remediation recommendations for July data"""
    print("\n" + "=" * 60)
    print("JULY 2025 DATA REMEDIATION PLAN")
    print("=" * 60)
    
    print("🎯 IMMEDIATE ACTIONS:")
    print("   1. Re-sync July 1-31, 2025 Google Ads data with current API values")
    print("   2. Update all campaign metrics (revenue, conversions, ROAS, CPA)")
    print("   3. Verify attribution window capture in sync process")
    print("   4. Update dashboard to reflect corrected July metrics")
    
    print("\n📋 VALIDATION CHECKLIST:")
    print("   ✓ Confirm July revenue totals match current API")
    print("   ✓ Verify ROAS calculations are accurate")
    print("   ✓ Check that high-spending campaigns show proper conversions")
    print("   ✓ Test dashboard filtering with corrected data")
    
    print("\n🔧 TECHNICAL IMPLEMENTATION:")
    print("   • Use google_ads_service.py sync_google_ads_data() with July date range")
    print("   • Ensure sync includes attribution window buffer")
    print("   • Monitor for API rate limits during historical re-sync")
    print("   • Backup existing July data before overwriting")

def main():
    """Run complete July 2025 data quality investigation"""
    print("🔍 JULY 2025 GOOGLE ADS DATA QUALITY INVESTIGATION")
    print("=" * 80)
    print("Investigating if July suffers from same stale conversion data issue as August...")
    
    # Update todo status
    try:
        from todo_update import mark_todo_in_progress
        mark_todo_in_progress("july-db-analysis")
    except:
        pass
    
    # Step 1: Analyze July database data
    db_df = investigate_july_database_data()
    
    # Step 2: Fetch current July API data
    api_df = fetch_july_api_data()
    
    # Step 3: Compare database vs API
    compare_july_data(db_df, api_df)
    
    # Step 4: Assess historical scope
    assess_historical_scope()
    
    # Step 5: Generate remediation plan
    generate_july_remediation_plan()
    
    print("\n" + "=" * 80)
    print("🏁 JULY 2025 INVESTIGATION COMPLETE")
    print("Review findings above to determine remediation priority and scope")
    print("=" * 80)

if __name__ == "__main__":
    main()