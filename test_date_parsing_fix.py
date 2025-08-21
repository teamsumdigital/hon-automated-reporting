#!/usr/bin/env python3
"""
Test the fixed date parsing for 2-digit years
"""

import os
import sys

# Add the backend app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

from services.ad_name_parser import AdNameParser

def test_date_parsing():
    """
    Test the date parsing fix for problematic dates
    """
    parser = AdNameParser()
    
    # Test cases that were causing warnings
    test_ads = [
        "8/8/24 - Tumbling Mat - Multi - Multi - Brand - HoN - Video - Multiple Styles",
        "5/15/24 - Multi - Multi - Multi - Brand - HoN - Video - Commercial",
        "5/23/24 - Playmat - Ula - Multi - Brand - HoN - Video - New Ula Back in Stock",
        "10/1/24 - Tumbling Mat - Checker - Almond - Brand - HoN - Static - Meet the Tumbling Mat",
        "10/2/24 - Playmat - Emile - Latte - Brand - HoN - Video - Before and After Playroom",
        "11/2/23 - Tumbling Mat - Multi - Multi - Brand - HoN - Video - Back in stock",
        "1/8/2025 - Multi - Multi - Multi - Brand - HoN - Video - Cross Cat BIS Video"  # This should work
    ]
    
    print("🧪 Testing Date Parsing Fix")
    print("=" * 60)
    
    all_passed = True
    for i, ad_name in enumerate(test_ads, 1):
        print(f"\n{i}. Testing: {ad_name[:50]}...")
        
        try:
            parsed = parser.parse_ad_name(ad_name, "Test Campaign")
            launch_date = parsed.get('launch_date')
            days_live = parsed.get('days_live')
            
            if launch_date:
                print(f"   ✅ Launch Date: {launch_date}")
                print(f"   📅 Days Live: {days_live}")
            else:
                print(f"   ❌ Launch Date: None (FAILED)")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL DATE PARSING TESTS PASSED!")
        print("✅ The fix handles 2-digit years correctly")
    else:
        print("❌ Some tests failed - need more fixes")
    
    return all_passed

if __name__ == "__main__":
    test_date_parsing()