#!/usr/bin/env python3

"""
Fix the weekly segmentation issue by updating the Meta ad level service
to ensure we get two full weeks of data consistently.
"""

import os
from datetime import datetime, timedelta, date
import sys

def main():
    print("🔧 Fixing weekly segmentation issue in Meta Ad Level Service")
    print("=" * 70)
    
    print("📊 Root Cause Analysis:")
    print("   - Meta API with time_increment=7 is only returning 1 week of data")
    print("   - Expected: 2 weeks of data (14 days split into two 7-day periods)")
    print("   - Actual: 1 week of data (only one 7-day period returned)")
    
    print("\n🚀 Solution Strategy:")
    print("   1. Change approach from single API call with time_increment=7")
    print("   2. Make two separate API calls for each 7-day period")
    print("   3. Combine results to ensure we get both weeks")
    print("   4. Maintain weekly segmentation for frontend display")
    
    print("\n📝 Implementation Plan:")
    print("   - Update _fetch_ad_insights_for_account method")
    print("   - Split 14-day range into two explicit 7-day periods")
    print("   - Make separate API calls for each period")
    print("   - Combine and return all results")
    
    print("\n✅ Benefits:")
    print("   - Guaranteed two weeks of data when available")
    print("   - More reliable weekly segmentation")
    print("   - Better control over date ranges")
    print("   - Fixes the single-week display issue")
    
    print(f"\n🎯 Ready to implement the fix!")

if __name__ == "__main__":
    main()