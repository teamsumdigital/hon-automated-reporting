#!/usr/bin/env python3
"""
Debug script to test date calculation logic for 14-day range
Run this to see exactly what dates are being calculated
"""

from datetime import date, timedelta

def test_date_calculation():
    """Test the current date calculation logic"""
    
    # Simulate running today (August 25th, 2025)
    target_date = date(2025, 8, 25)
    
    print("=== CURRENT DATE CALCULATION LOGIC ===")
    print(f"Target date (today): {target_date}")
    
    # Current logic from meta_ad_level_service.py
    end_date = target_date - timedelta(days=1)
    start_date = end_date - timedelta(days=13)
    
    print(f"End date (yesterday): {end_date}")
    print(f"Start date (13 days before end_date): {start_date}")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Total days: {(end_date - start_date).days + 1} days")
    
    # Show what the range should be for true "last 14 days through yesterday"
    print("\n=== WHAT IT SHOULD BE ===")
    correct_end_date = target_date - timedelta(days=1)  # Yesterday
    correct_start_date = correct_end_date - timedelta(days=13)  # 14 days before yesterday (inclusive)
    
    print(f"Correct end date: {correct_end_date}")
    print(f"Correct start date: {correct_start_date}")
    print(f"Correct range: {correct_start_date} to {correct_end_date}")
    print(f"Total days: {(correct_end_date - correct_start_date).days + 1} days")
    
    # Let's also test what would give us 8/10 to 8/23
    print("\n=== ANALYZING THE 8/10 to 8/23 RESULT ===")
    observed_start = date(2025, 8, 10)
    observed_end = date(2025, 8, 23)
    
    print(f"Observed range: {observed_start} to {observed_end}")
    print(f"Observed total days: {(observed_end - observed_start).days + 1} days")
    
    # What target_date would produce this?
    # If end_date = target_date - 1, then target_date = end_date + 1
    implied_target = observed_end + timedelta(days=1)
    print(f"Implied target_date that would produce this: {implied_target}")
    
    # Check if there's an off-by-one error
    print(f"Days between 8/25 and implied target {implied_target}: {(target_date - implied_target).days} days")

if __name__ == "__main__":
    test_date_calculation()