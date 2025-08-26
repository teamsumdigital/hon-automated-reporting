#!/usr/bin/env python3
"""
Simple test of just the date calculation logic without API dependencies
"""

from datetime import date, timedelta

def test_date_calculation():
    """Test the date calculation logic"""
    
    print("=== SIMPLE DATE CALCULATION TEST ===")
    
    # Simulate today's date
    target_date = date.today()
    print(f"Target date (today): {target_date}")
    
    # Apply the fixed calculation
    end_date = target_date - timedelta(days=1)
    start_date = end_date - timedelta(days=13)
    
    print(f"End date (yesterday): {end_date}")
    print(f"Start date (14 days back): {start_date}")
    print(f"Total days: {(end_date - start_date).days + 1}")
    print(f"Date range: {start_date} to {end_date}")
    
    # Check if this matches what should happen on Aug 25th
    if target_date == date(2025, 8, 25):
        expected_end = date(2025, 8, 24)
        expected_start = date(2025, 8, 11)
        
        print(f"\nFor August 25th, 2025:")
        print(f"Expected: {expected_start} to {expected_end}")
        print(f"Actual:   {start_date} to {end_date}")
        
        if start_date == expected_start and end_date == expected_end:
            print("✅ CORRECT: Should pull 8/11 to 8/24")
        else:
            print("❌ INCORRECT: Date calculation is wrong")
    
    return start_date, end_date

if __name__ == "__main__":
    test_date_calculation()