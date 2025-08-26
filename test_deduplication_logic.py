#!/usr/bin/env python3
"""
Test the deduplication logic to understand the spend discrepancy
"""

def test_deduplication():
    """Test the deduplication logic with sample data"""
    
    print("=== TESTING DEDUPLICATION LOGIC ===")
    
    # Simulate database records (what your SQL query counts)
    sample_db_records = [
        {'ad_name': 'Ad A', 'reporting_starts': '2025-08-11', 'reporting_ends': '2025-08-17', 'amount_spent_usd': 1000},
        {'ad_name': 'Ad A', 'reporting_starts': '2025-08-18', 'reporting_ends': '2025-08-24', 'amount_spent_usd': 500},
        {'ad_name': 'Ad B', 'reporting_starts': '2025-08-11', 'reporting_ends': '2025-08-17', 'amount_spent_usd': 750},
        {'ad_name': 'Ad B', 'reporting_starts': '2025-08-18', 'reporting_ends': '2025-08-24', 'amount_spent_usd': 250},
        # Duplicate record (should be ignored by deduplication)
        {'ad_name': 'Ad A', 'reporting_starts': '2025-08-11', 'reporting_ends': '2025-08-17', 'amount_spent_usd': 1000},
    ]
    
    print("SAMPLE DATABASE RECORDS:")
    total_db_sum = 0
    for record in sample_db_records:
        print(f"  {record['ad_name']} | {record['reporting_starts']}-{record['reporting_ends']} | ${record['amount_spent_usd']}")
        total_db_sum += record['amount_spent_usd']
    
    print(f"\nRAW DATABASE SUM: ${total_db_sum}")
    
    # Apply deduplication logic (same as the fixed summary endpoint)
    grouped_for_totals = {}
    
    for ad in sample_db_records:
        ad_name = ad['ad_name']
        date_key = f"{ad['reporting_starts']}_{ad['reporting_ends']}"
        
        if ad_name not in grouped_for_totals:
            grouped_for_totals[ad_name] = {
                'weekly_periods': {},
                'total_spend': 0
            }
        
        # Only count each ad+date combination once
        if date_key not in grouped_for_totals[ad_name]['weekly_periods']:
            grouped_for_totals[ad_name]['weekly_periods'][date_key] = True
            grouped_for_totals[ad_name]['total_spend'] += ad['amount_spent_usd']
            print(f"  ✅ COUNTED: {ad_name} | {date_key} | ${ad['amount_spent_usd']}")
        else:
            print(f"  ❌ SKIPPED (duplicate): {ad_name} | {date_key} | ${ad['amount_spent_usd']}")
    
    # Calculate deduplicated total
    deduplicated_total = sum(ad_data['total_spend'] for ad_data in grouped_for_totals.values())
    
    print(f"\nDEDUPLICATED TOTAL: ${deduplicated_total}")
    print(f"DIFFERENCE: ${total_db_sum - deduplicated_total}")
    
    return total_db_sum, deduplicated_total

if __name__ == "__main__":
    test_deduplication()