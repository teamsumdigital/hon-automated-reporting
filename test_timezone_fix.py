#!/usr/bin/env python3
"""
Test the timezone fix to ensure it calculates the correct date
"""

from datetime import date, datetime, timedelta
import pytz

def test_timezone_fix():
    """Test the fixed timezone calculation"""
    
    print("=== TESTING TIMEZONE FIX ===")
    
    # Test what we get with UTC (what production was using)
    utc_now = datetime.utcnow()
    utc_date = utc_now.date()
    print(f"UTC date: {utc_date}")
    
    # Test what we get with Pacific timezone (the fix)
    pacific_tz = pytz.timezone('US/Pacific')
    pacific_now = datetime.now(pacific_tz)
    pacific_date = pacific_now.date()
    print(f"Pacific date: {pacific_date}")
    
    print(f"Timezone difference: {(pacific_date - utc_date).days} days")
    
    # Test the fixed calculation
    target_date = pacific_date
    end_date = target_date - timedelta(days=1)
    start_date = end_date - timedelta(days=13)
    
    print(f"\nFIXED CALCULATION:")
    print(f"Target date (Pacific): {target_date}")
    print(f"End date: {end_date}")
    print(f"Start date: {start_date}")
    print(f"Range: {start_date} to {end_date}")
    print(f"Total days: {(end_date - start_date).days + 1}")
    
    # Show what this should give us
    if pacific_date == date(2025, 8, 25):
        print(f"\n✅ EXPECTED: 2025-08-11 to 2025-08-24")
        if start_date == date(2025, 8, 11) and end_date == date(2025, 8, 24):
            print("✅ CORRECT - This will fix the production issue!")
        else:
            print("❌ Still wrong")

if __name__ == "__main__":
    test_timezone_fix()