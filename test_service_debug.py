#!/usr/bin/env python3

import os
import sys
sys.path.append('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend')

from dotenv import load_dotenv
from app.services.google_reporting import GoogleReportingService

load_dotenv()

def test_service():
    print('🔍 Testing GoogleReportingService...')
    
    try:
        service = GoogleReportingService()
        print('✅ Service initialized')
        
        # Test get_campaign_data
        print('Testing get_campaign_data...')
        campaigns = service.get_campaign_data()
        print(f'✅ get_campaign_data returned {len(campaigns)} campaigns')
        
        if campaigns:
            print('First campaign:', campaigns[0])
        
        # Test all_time_summary
        print('\nTesting get_all_time_summary...')
        summary = service.get_all_time_summary()
        print('✅ Summary:', summary)
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_service()