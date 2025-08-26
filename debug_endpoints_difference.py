#!/usr/bin/env python3
"""
Compare what data the different endpoints are actually querying
"""

from datetime import datetime, timedelta

def debug_endpoint_differences():
    """Compare the query logic between ad-data and summary endpoints"""
    
    print("=== COMPARING ENDPOINT QUERY LOGIC ===")
    
    # AD-DATA ENDPOINT LOGIC
    print("1. AD-DATA ENDPOINT (/api/meta-ad-reports/ad-data):")
    cutoff_date_ad_data = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    print(f"   - Filter: reporting_starts >= '{cutoff_date_ad_data}'")
    print(f"   - Pagination: Yes (500 records per batch)")
    print(f"   - Groups by: ad_name + date_key")
    print(f"   - Deduplication: Within same ad_name+date_key")
    
    # SUMMARY ENDPOINT LOGIC  
    print(f"\n2. SUMMARY ENDPOINT (/api/meta-ad-reports/summary):")
    print(f"   - Filter: Same category/format filters as ad-data")
    print(f"   - Pagination: Single query with range(0, 9999)")
    print(f"   - NO 14-day cutoff date filter!")
    print(f"   - Deduplication: None (raw sum)")
    
    print(f"\n❌ POTENTIAL ISSUE:")
    print(f"   - AD-DATA endpoint has 14-day cutoff: reporting_starts >= '{cutoff_date_ad_data}'")
    print(f"   - SUMMARY endpoint has NO cutoff - queries ALL data")
    print(f"   - If database has older data, summary will include it but ad-data won't")
    
    # Check what data would be included/excluded
    today = datetime.now().date()
    print(f"\n=== DATE RANGE COMPARISON ===")
    print(f"Today: {today}")
    print(f"14 days ago: {today - timedelta(days=14)}")
    
    test_dates = [
        '2025-08-01',  # Old data
        '2025-08-10',  # Just before cutoff
        '2025-08-11',  # Week 1 (should be included)
        '2025-08-18',  # Week 2 (should be included)  
        '2025-07-25',  # Much older data
    ]
    
    print(f"\nWhich data each endpoint would include:")
    for test_date in test_dates:
        ad_data_includes = test_date >= cutoff_date_ad_data
        summary_includes = True  # Summary has no date filter
        
        ad_status = "✅" if ad_data_includes else "❌"
        summary_status = "✅" if summary_includes else "❌"
        
        print(f"  {test_date}: AD-DATA {ad_status} | SUMMARY {summary_status}")

if __name__ == "__main__":
    debug_endpoint_differences()