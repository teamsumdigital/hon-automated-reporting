#!/usr/bin/env python3
"""
Test script to verify the Standing Mats filter fix is working correctly
"""

import os
import sys
from datetime import datetime, date
from decimal import Decimal

# Add the backend path to import services
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.tiktok_ad_level_service import TikTokAdLevelService

def test_summary_filtering():
    """Test TikTok summary filtering with Standing Mats"""
    
    print("🧪 Testing TikTok Summary Filtering Fix...")
    print("=" * 60)
    
    try:
        service = TikTokAdLevelService()
        
        # Test cases based on the original issue
        test_cases = [
            {
                "name": "Working combination (without Standing Mats)",
                "categories": ['Play Furniture', 'Tumbling Mats', 'Play Mats', 'Bath Mats'],
                "expected_spend": 22158.75
            },
            {
                "name": "Problematic combination (with Standing Mats)", 
                "categories": ['Play Furniture', 'Tumbling Mats', 'Play Mats', 'Bath Mats', 'Standing Mats'],
                "expected_spend": 30452.43
            },
            {
                "name": "Standing Mats only",
                "categories": ['Standing Mats'],
                "expected_spend": 8293.68
            },
            {
                "name": "All categories (no filter)",
                "categories": None,
                "expected_spend": 30452.43
            }
        ]
        
        # Set date range to July 2025 for consistency with debug
        july_start = "2025-07-01"
        july_end = "2025-07-31"
        
        print(f"📅 Testing for July 2025: {july_start} to {july_end}\n")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"Test {i}: {test_case['name']}")
            
            # Call the updated get_summary_metrics method
            summary = service.get_summary_metrics(
                categories=test_case['categories'],
                start_date=july_start,
                end_date=july_end
            )
            
            actual_spend = summary['total_spend']
            expected_spend = test_case['expected_spend']
            
            print(f"   Expected spend: ${expected_spend:,.2f}")
            print(f"   Actual spend:   ${actual_spend:,.2f}")
            
            # Check if the values match (within a small tolerance for floating point)
            if abs(actual_spend - expected_spend) < 0.01:
                print(f"   ✅ PASSED")
            else:
                print(f"   ❌ FAILED - Difference: ${actual_spend - expected_spend:+,.2f}")
            
            print(f"   Categories: {test_case['categories'] or 'All'}")
            print(f"   Other metrics: Revenue=${summary['total_revenue']:,.2f}, "
                  f"Purchases={summary['total_purchases']}, ROAS={summary['avg_roas']:.2f}")
            print()
        
        print("=" * 60)
        print("🎯 Testing complete! If all tests pass, the Standing Mats filter fix is working.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_summary_filtering()