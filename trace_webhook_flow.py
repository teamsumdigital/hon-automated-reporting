#!/usr/bin/env python3
"""
Complete webhook flow analysis for date calculation debugging
"""

from datetime import date, datetime, timedelta
import pytz

def trace_complete_flow():
    """Trace the complete webhook flow to identify date calculation issues"""
    
    print("=== COMPLETE WEBHOOK FLOW ANALYSIS ===")
    
    # 1. Webhook Entry Point
    print("\n1. WEBHOOK ENTRY POINT:")
    print("   - Payload: {trigger: 'sync_14_day_ad_data', metadata: {...}}")
    print("   - Calls: sync_14_day_ad_data_background(payload.metadata)")
    print("   - ❌ NOTE: No target_date passed to background task")
    
    # 2. Background Task  
    print("\n2. BACKGROUND TASK:")
    print("   - Calls: meta_service.get_last_14_days_ad_data()")
    print("   - ❌ NOTE: Called with NO target_date parameter (defaults to None)")
    
    # 3. Service Method Date Calculation
    print("\n3. SERVICE METHOD DATE CALCULATION:")
    
    # Simulate the Pacific timezone calculation
    pacific_tz = pytz.timezone('US/Pacific')
    pacific_now = datetime.now(pacific_tz)
    target_date = pacific_now.date()
    
    end_date = target_date - timedelta(days=1)
    start_date = end_date - timedelta(days=13)
    
    print(f"   - Pacific target_date: {target_date}")
    print(f"   - Calculated end_date: {end_date}")
    print(f"   - Calculated start_date: {start_date}")
    print(f"   - Range: {start_date} to {end_date} ({(end_date - start_date).days + 1} days)")
    
    # 4. Meta API Parameters
    print("\n4. META API PARAMETERS:")
    print(f"   - time_range.since: '{start_date.strftime('%Y-%m-%d')}'")
    print(f"   - time_range.until: '{end_date.strftime('%Y-%m-%d')}'")
    print("   - time_increment: 7 (weekly segments)")
    print("   - level: 'ad'")
    
    # 5. Critical Issue: Meta API Response Dates
    print("\n5. ❌ CRITICAL ISSUE IDENTIFIED:")
    print("   - We send correct dates to Meta API")
    print("   - BUT stored dates come from Meta's response fields:")
    print("     * insight_start = insight.get('date_start')")  
    print("     * insight_end = insight.get('date_stop')")
    print("   - Meta API might return different dates due to:")
    print("     * Weekly segmentation (time_increment: 7)")
    print("     * Meta's internal date processing")
    print("     * API timezone handling")
    
    # 6. Weekly Segmentation Impact
    print("\n6. WEEKLY SEGMENTATION ANALYSIS:")
    print("   With time_increment=7, Meta splits the range into weekly periods:")
    
    current_date = start_date
    week_num = 1
    while current_date <= end_date:
        week_end = min(current_date + timedelta(days=6), end_date)
        print(f"   Week {week_num}: {current_date} to {week_end}")
        current_date = week_end + timedelta(days=1)
        week_num += 1
    
    # 7. Potential Solutions
    print("\n7. POTENTIAL SOLUTIONS:")
    print("   A. Use our calculated dates instead of Meta's response dates")
    print("   B. Remove weekly segmentation (time_increment=1)")
    print("   C. Add logging to see Meta's actual response dates")
    print("   D. Force date range in data processing, not storage")
    
    return start_date, end_date

if __name__ == "__main__":
    trace_complete_flow()