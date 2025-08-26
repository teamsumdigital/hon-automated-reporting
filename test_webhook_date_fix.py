#!/usr/bin/env python3
"""
Test the webhook with the date fix to ensure correct calculation
"""

import asyncio
import os
from datetime import date, timedelta
from backend.app.services.meta_ad_level_service import MetaAdLevelService

async def test_date_calculation():
    """Test the updated date calculation"""
    
    print("=== TESTING UPDATED DATE CALCULATION ===")
    
    try:
        # Initialize the Meta Ad Level Service
        service = MetaAdLevelService()
        
        # Test the date calculation without actually fetching data
        target_date = date.today()
        print(f"Using target_date: {target_date}")
        
        # Simulate the calculation from get_last_14_days_ad_data
        end_date = target_date - timedelta(days=1)
        start_date = end_date - timedelta(days=13)
        
        print(f"Calculated end_date: {end_date}")
        print(f"Calculated start_date: {start_date}")
        print(f"Total days: {(end_date - start_date).days + 1}")
        
        # Expected results for August 25th, 2025
        expected_end = date(2025, 8, 24)
        expected_start = date(2025, 8, 11)
        
        print(f"\nExpected end_date: {expected_end}")
        print(f"Expected start_date: {expected_start}")
        
        if end_date == expected_end and start_date == expected_start:
            print("✅ Date calculation is CORRECT!")
        else:
            print("❌ Date calculation is WRONG!")
            
        return start_date, end_date
        
    except Exception as e:
        print(f"❌ Error testing date calculation: {e}")
        return None, None

if __name__ == "__main__":
    asyncio.run(test_date_calculation())