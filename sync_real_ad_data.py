#!/usr/bin/env python3
"""
Script to sync real ad-level data from Meta Ads API
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8007"

def check_current_data():
    """Check current state of ad data in database"""
    print("📊 Checking current ad data in database...")
    try:
        response = requests.get(f"{BASE_URL}/api/meta-ad-reports/ad-data")
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"   Current ad records: {count}")
            return count
        else:
            print(f"   Error checking data: {response.status_code}")
            return 0
    except Exception as e:
        print(f"   Error: {e}")
        return 0

def sync_ad_data():
    """Sync last 14 days of ad-level data"""
    print(f"\n🚀 Starting ad-level data sync at {datetime.now().strftime('%H:%M:%S')}")
    print("   This may take 1-3 minutes as it fetches real data from Meta API...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/meta-ad-reports/sync-14-days",
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minute timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Sync completed successfully!")
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            
            if 'summary' in data:
                summary = data['summary']
                print(f"\n📈 Summary:")
                print(f"   Total ads synced: {summary.get('total_ads', 0)}")
                print(f"   Total spend: ${summary.get('total_spend', 0):,.2f}")
                print(f"   Total purchases: {summary.get('total_purchases', 0):,}")
                print(f"   Total revenue: ${summary.get('total_revenue', 0):,.2f}")
                print(f"   Average ROAS: {summary.get('average_roas', 0):.2f}x")
            
            if 'weekly_breakdown' in data:
                print(f"\n📅 Weekly Breakdown:")
                for week, stats in data['weekly_breakdown'].items():
                    print(f"   {week}:")
                    print(f"      Ads: {stats['ads_count']}")
                    print(f"      Spend: ${stats['spend']:,.2f}")
                    print(f"      Purchases: {stats['purchases']}")
                    print(f"      Revenue: ${stats['revenue']:,.2f}")
            
            return True
        else:
            print(f"\n❌ Sync failed with status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n⏰ Sync request timed out (took longer than 5 minutes)")
        print("   This might indicate a large amount of data or API rate limits")
        print("   Check the backend logs and try again in a few minutes")
        return False
    except Exception as e:
        print(f"\n❌ Sync failed with error: {e}")
        return False

def check_weekly_summary():
    """Check the weekly summary after sync"""
    print(f"\n📊 Fetching weekly summary...")
    try:
        response = requests.get(f"{BASE_URL}/api/meta-ad-reports/weekly-summary")
        if response.status_code == 200:
            data = response.json()
            weekly_summary = data.get('weekly_summary', {})
            category_totals = data.get('category_totals', {})
            total_ads = data.get('total_ads', 0)
            
            print(f"   Total ads in summary: {total_ads}")
            print(f"   Weeks found: {len(weekly_summary)}")
            print(f"   Categories found: {len(category_totals)}")
            
            if category_totals:
                print(f"\n🏷️  Performance by Category:")
                for category, stats in category_totals.items():
                    roas = stats['revenue'] / stats['spend'] if stats['spend'] > 0 else 0
                    print(f"   {category}:")
                    print(f"      Ads: {stats['ads_count']}")
                    print(f"      Spend: ${stats['spend']:,.2f}")
                    print(f"      Revenue: ${stats['revenue']:,.2f}")
                    print(f"      ROAS: {roas:.2f}x")
            
            return True
        else:
            print(f"   Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    """Main execution flow"""
    print("🎯 Meta Ads Ad-Level Data Sync")
    print("=" * 50)
    
    # Check initial state
    initial_count = check_current_data()
    
    # Run sync
    if sync_ad_data():
        # Check final state
        print(f"\n🔍 Checking updated data...")
        final_count = check_current_data()
        
        if final_count > initial_count:
            print(f"✅ Success! Added {final_count - initial_count} new ad records")
            
            # Show weekly summary
            check_weekly_summary()
            
            print(f"\n🎉 Ad-level data sync completed successfully!")
            print(f"\n📋 You can now:")
            print(f"   • View data: GET /api/meta-ad-reports/ad-data")
            print(f"   • Filter by category: GET /api/meta-ad-reports/ad-data?category=Play%20Mats")
            print(f"   • View weekly summary: GET /api/meta-ad-reports/weekly-summary")
        else:
            print(f"⚠️  No new ad records added. This might indicate:")
            print(f"   • No ad activity in the last 14 days")
            print(f"   • API rate limits")
            print(f"   • Data already up to date")
    else:
        print(f"\n❌ Sync failed. Please check backend logs for details.")

if __name__ == "__main__":
    main()