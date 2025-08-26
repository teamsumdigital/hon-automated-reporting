#!/usr/bin/env python3
"""
Test how many records the TikTok service is getting
"""

import sys
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from app.services.tiktok_service import TikTokService

def test_record_count():
    print("TESTING TIKTOK SERVICE RECORD COUNT")
    print("=" * 50)
    
    service = TikTokService()
    
    # Get dashboard data and check how many records
    dashboard_data = service.get_dashboard_data()
    campaigns = dashboard_data.get('campaigns', [])
    
    print(f"Total campaigns returned by service: {len(campaigns)}")
    
    if len(campaigns) == 1000:
        print("🚨 Service is still limited to 1000 records!")
        print("The limit fix did not take effect.")
    elif len(campaigns) > 1000:
        print(f"✅ Service is returning {len(campaigns)} records - limit fix worked!")
    else:
        print(f"⚠️ Service returned {len(campaigns)} records")
    
    # Check July 2025 specifically
    july_2025_campaigns = [c for c in campaigns if c.get('reporting_starts', '').startswith('2025-07')]
    print(f"July 2025 campaigns in service data: {len(july_2025_campaigns)}")
    july_2025_spend = sum(c.get('amount_spent_usd', 0) for c in july_2025_campaigns)
    print(f"July 2025 spend from service: ${july_2025_spend:,.2f}")

if __name__ == "__main__":
    test_record_count()