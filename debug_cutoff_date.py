#!/usr/bin/env python3
"""
Debug the 14-day cutoff date that might be filtering data
"""

from datetime import datetime, timedelta

def debug_cutoff_date():
    """Check what the 14-day cutoff date resolves to"""
    
    print("=== DEBUGGING 14-DAY CUTOFF DATE ===")
    
    # Same logic as the ad-data endpoint
    cutoff_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    
    print(f"Current datetime: {datetime.now()}")
    print(f"14 days ago: {datetime.now() - timedelta(days=14)}")
    print(f"Cutoff date filter: {cutoff_date}")
    
    # Check what data this would include/exclude
    test_dates = [
        '2025-08-11',  # Week 1 start
        '2025-08-17',  # Week 1 end
        '2025-08-18',  # Week 2 start  
        '2025-08-24',  # Week 2 end
        '2025-08-10',  # Before our range
        '2025-08-25',  # Today
    ]
    
    print(f"\nTesting which dates pass the filter (reporting_starts >= '{cutoff_date}'):")
    for test_date in test_dates:
        passes = test_date >= cutoff_date
        status = "✅ INCLUDED" if passes else "❌ EXCLUDED"
        print(f"  {test_date}: {status}")
    
    return cutoff_date

if __name__ == "__main__":
    debug_cutoff_date()