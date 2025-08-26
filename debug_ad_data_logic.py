#!/usr/bin/env python3
"""
Debug the ad-data endpoint logic to understand why totals are wrong
"""

def debug_ad_data_logic():
    """Test the ad-data endpoint logic with sample data"""
    
    print("=== DEBUGGING AD-DATA ENDPOINT LOGIC ===")
    
    # Simulate what should be in the database after webhook
    sample_db_data = [
        # Ad A in both weeks
        {'ad_name': 'New Bath Mats Collection V3', 'reporting_starts': '2025-08-11', 'reporting_ends': '2025-08-17', 'amount_spent_usd': 3000, 'purchases_conversion_value': 18000},
        {'ad_name': 'New Bath Mats Collection V3', 'reporting_starts': '2025-08-18', 'reporting_ends': '2025-08-24', 'amount_spent_usd': 2431, 'purchases_conversion_value': 12000},
        
        # Ad B in both weeks 
        {'ad_name': 'Standing Mats Video Ad', 'reporting_starts': '2025-08-11', 'reporting_ends': '2025-08-17', 'amount_spent_usd': 2500, 'purchases_conversion_value': 9000},
        {'ad_name': 'Standing Mats Video Ad', 'reporting_starts': '2025-08-18', 'reporting_ends': '2025-08-24', 'amount_spent_usd': 2728, 'purchases_conversion_value': 10000},
    ]
    
    print("INPUT DATA:")
    total_raw_spend = 0
    for ad in sample_db_data:
        print(f"  {ad['ad_name'][:25]}... | {ad['reporting_starts']}-{ad['reporting_ends']} | ${ad['amount_spent_usd']}")
        total_raw_spend += ad['amount_spent_usd']
    
    print(f"\nRAW TOTAL SPEND: ${total_raw_spend}")
    
    # Apply the current ad-data endpoint logic
    print(f"\n=== APPLYING AD-DATA ENDPOINT LOGIC ===")
    
    grouped_data = {}
    
    for ad in sample_db_data:
        ad_name = ad['ad_name']
        date_key = f"{ad['reporting_starts']}_{ad['reporting_ends']}"
        
        print(f"\nProcessing: {ad_name[:25]}... | {date_key} | ${ad['amount_spent_usd']}")
        
        if ad_name not in grouped_data:
            print(f"  Creating new group for: {ad_name[:25]}...")
            grouped_data[ad_name] = {
                'ad_name': ad_name,
                'weekly_periods': {},
                'total_spend': 0,
                'total_revenue': 0
            }
        
        # Check if this date period already exists for this ad
        if date_key not in grouped_data[ad_name]['weekly_periods']:
            print(f"  ✅ NEW weekly period - adding to totals")
            # Add weekly period data (first occurrence)
            grouped_data[ad_name]['weekly_periods'][date_key] = {
                'reporting_starts': ad['reporting_starts'],
                'reporting_ends': ad['reporting_ends'],
                'spend': ad['amount_spent_usd'],
                'revenue': ad['purchases_conversion_value']
            }
            
            # Add to totals (only for unique periods)
            grouped_data[ad_name]['total_spend'] += ad['amount_spent_usd']
            grouped_data[ad_name]['total_revenue'] += ad['purchases_conversion_value']
        else:
            print(f"  🔄 DUPLICATE weekly period - aggregating")
            # Duplicate found - aggregate the metrics
            existing = grouped_data[ad_name]['weekly_periods'][date_key]
            existing['spend'] += ad['amount_spent_usd']
            existing['revenue'] += ad['purchases_conversion_value']
            
            # Add to totals
            grouped_data[ad_name]['total_spend'] += ad['amount_spent_usd']
            grouped_data[ad_name]['total_revenue'] += ad['purchases_conversion_value']
    
    # Calculate final totals
    print(f"\n=== FINAL RESULTS ===")
    total_dashboard_spend = 0
    
    for ad_name, data in grouped_data.items():
        print(f"\n{ad_name[:30]}:")
        print(f"  Weekly periods: {len(data['weekly_periods'])}")
        for date_key, period in data['weekly_periods'].items():
            print(f"    {date_key}: ${period['spend']}")
        print(f"  Total spend: ${data['total_spend']}")
        total_dashboard_spend += data['total_spend']
    
    print(f"\nDASHBOARD TOTAL: ${total_dashboard_spend}")
    print(f"RAW DATABASE TOTAL: ${total_raw_spend}")
    print(f"DIFFERENCE: ${total_raw_spend - total_dashboard_spend}")
    
    if total_dashboard_spend != total_raw_spend:
        print("❌ LOGIC ERROR: Dashboard total doesn't match raw total!")
    else:
        print("✅ Logic is correct")

if __name__ == "__main__":
    debug_ad_data_logic()