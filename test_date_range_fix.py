#!/usr/bin/env python3
"""
Test the date range fix in the summary endpoint
"""

from datetime import datetime

def test_date_formatting():
    """Test the date formatting logic added to the summary endpoint"""
    
    print("=== TESTING DATE RANGE FORMATTING ===")
    
    # Test data that should match what's now in the database
    test_dates_start = ['2025-08-11', '2025-08-18']
    test_dates_end = ['2025-08-17', '2025-08-24']
    
    # Apply the same logic as the fixed endpoint
    if test_dates_start and test_dates_end:
        min_date = min(test_dates_start)
        max_date = max(test_dates_end)
        
        print(f"Min date: {min_date}")
        print(f"Max date: {max_date}")
        
        try:
            min_date_obj = datetime.strptime(min_date, '%Y-%m-%d')
            max_date_obj = datetime.strptime(max_date, '%Y-%m-%d')
            date_range = f"{min_date_obj.strftime('%-m/%-d/%Y')} - {max_date_obj.strftime('%-m/%-d/%Y')}"
            print(f"Formatted date range: {date_range}")
        except Exception as e:
            print(f"Formatting failed, using fallback: {min_date} - {max_date}")
            print(f"Error: {e}")
    
    print("\n✅ Expected result: '8/11/2025 - 8/24/2025'")
    print("This should replace the old '8/10/2025 - 8/16/2025' in the frontend")

if __name__ == "__main__":
    test_date_formatting()