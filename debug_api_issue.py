#!/usr/bin/env python3
"""
Debug API issue by testing the exact API logic
"""

import os
import sys
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from dotenv import load_dotenv
from app.services.google_reporting import GoogleReportingService
from app.models.google_campaign_data import GoogleDashboardFilters

load_dotenv()

def debug_api():
    print('🔧 Debugging API logic...')
    
    try:
        # Simulate the exact API logic
        service = GoogleReportingService()
        
        # Test 1: No filters (like API call without parameters)
        print('\n1. Testing get_campaign_data() with no filters:')
        filters = GoogleDashboardFilters()
        campaigns = service.get_campaign_data(filters)
        print(f'   Campaigns returned: {len(campaigns)}')
        
        if campaigns:
            print('   ✅ Campaigns found - API should work')
            total_spend = sum(float(c.amount_spent_usd) for c in campaigns)
            print(f'   Total spend: ${total_spend:,.2f}')
        else:
            print('   ❌ No campaigns returned - this is the issue!')
            
            # Try direct database query
            print('\n   Testing direct database query:')
            result = service.supabase.table("google_campaign_data").select("*").execute()
            print(f'   Direct query returned: {len(result.data)} rows')
            
            if result.data:
                print('   Sample row:', result.data[0])
                
                # Try parsing the first row manually
                print('\n   Testing manual row parsing:')
                row = result.data[0]
                try:
                    from datetime import datetime
                    from decimal import Decimal
                    from app.models.google_campaign_data import GoogleCampaignDataResponse
                    
                    campaign = GoogleCampaignDataResponse(
                        id=row["id"],
                        campaign_id=row["campaign_id"],
                        campaign_name=row["campaign_name"],
                        category=row["category"],
                        reporting_starts=datetime.strptime(row["reporting_starts"], "%Y-%m-%d").date(),
                        reporting_ends=datetime.strptime(row["reporting_ends"], "%Y-%m-%d").date(),
                        amount_spent_usd=Decimal(str(row["amount_spent_usd"])),
                        website_purchases=row["website_purchases"],
                        purchases_conversion_value=Decimal(str(row["purchases_conversion_value"])),
                        impressions=row["impressions"],
                        link_clicks=row["link_clicks"],
                        cpa=Decimal(str(row["cpa"])),
                        roas=Decimal(str(row["roas"])),
                        cpc=Decimal(str(row["cpc"])),
                        created_at=datetime.fromisoformat(row["created_at"]),
                        updated_at=datetime.fromisoformat(row["updated_at"])
                    )
                    print('   ✅ Manual parsing successful')
                    print(f'   Campaign: {campaign.campaign_name}, Spend: ${campaign.amount_spent_usd}')
                    
                except Exception as e:
                    print(f'   ❌ Manual parsing failed: {e}')
                    import traceback
                    traceback.print_exc()
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api()