#!/usr/bin/env python3
"""
Debug script to check what date the webhook is actually using
"""

from datetime import date, datetime, timedelta
import os

def debug_webhook_date():
    """Debug the actual date being used by the system"""
    
    print("=== WEBHOOK DATE DEBUG ===")
    print(f"Current date.today(): {date.today()}")
    print(f"Current datetime.now(): {datetime.now()}")
    print(f"Current datetime.utcnow(): {datetime.utcnow()}")
    
    # Simulate the webhook date calculation
    target_date = date.today()
    end_date = target_date - timedelta(days=1)
    start_date = end_date - timedelta(days=13)
    
    print(f"\nWebhook calculation:")
    print(f"Target date: {target_date}")
    print(f"End date: {end_date}")
    print(f"Start date: {start_date}")
    print(f"Range: {start_date} to {end_date}")
    
    # Test what happens if we force the target_date
    print(f"\n=== FORCED TARGET DATE TEST ===")
    forced_target = date(2025, 8, 25)  # Today
    forced_end = forced_target - timedelta(days=1)
    forced_start = forced_end - timedelta(days=13)
    
    print(f"Forced target: {forced_target}")
    print(f"Forced end: {forced_end}")
    print(f"Forced start: {forced_start}")
    print(f"Forced range: {forced_start} to {forced_end}")

if __name__ == "__main__":
    debug_webhook_date()