#!/usr/bin/env python3
"""
Test to understand the REAL date calculation issue
"""

from datetime import date, timedelta

def analyze_date_issue():
    """Analyze what's really happening with the dates"""
    
    print("=== ANALYZING THE REAL DATE BUG ===")
    
    target_date = date(2025, 8, 25)  # Today
    print(f"Target date (today): {target_date}")
    
    # Current logic (what should give us 8/11 to 8/24)
    end_date = target_date - timedelta(days=1)
    start_date_current = end_date - timedelta(days=13)
    
    print(f"\nCURRENT LOGIC:")
    print(f"End date: {end_date}")
    print(f"Start date (13 days back): {start_date_current}")
    print(f"Range: {start_date_current} to {end_date}")
    print(f"Total days: {(end_date - start_date_current).days + 1}")
    
    # What we're actually seeing in production (8/10 to 8/23)
    observed_start = date(2025, 8, 10)
    observed_end = date(2025, 8, 23)
    
    print(f"\nOBSERVED IN PRODUCTION:")
    print(f"Range: {observed_start} to {observed_end}")
    print(f"Total days: {(observed_end - observed_start).days + 1}")
    
    # Test different approaches
    print(f"\n=== TESTING DIFFERENT APPROACHES ===")
    
    # Approach 1: 14 days back from end_date
    start_14_back = end_date - timedelta(days=14)
    print(f"14 days back from end: {start_14_back} to {end_date} = {(end_date - start_14_back).days + 1} days")
    
    # Approach 2: What would give us the observed result?
    # If production shows 8/10 to 8/23, and we want 8/11 to 8/24, 
    # production is 1 day too early on both start and end
    
    # Maybe the issue is the target_date itself?
    if observed_end == date(2025, 8, 23):
        # Working backwards: if end_date = target - 1, then target = end + 1
        implied_target = observed_end + timedelta(days=1)
        print(f"Implied target_date in production: {implied_target}")
        
        # And start would be end - 13
        implied_start_calc = observed_end - timedelta(days=13)
        print(f"If production end={observed_end}, start should be: {implied_start_calc}")
        print(f"But production start is: {observed_start}")
        print(f"Difference: {(implied_start_calc - observed_start).days} days")

if __name__ == "__main__":
    analyze_date_issue()