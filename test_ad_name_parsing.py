#!/usr/bin/env python3
"""
Test script to validate the advanced ad name parser
Tests against the example ad names provided
"""

import sys
import os
from datetime import date

# Add the backend app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

from services.ad_name_parser import AdNameParser

def test_ad_name_parser():
    """Test the ad name parser with the provided examples"""
    
    parser = AdNameParser()
    
    # Test cases with expected results
    test_cases = [
        {
            'ad_name': '7/9/2025 - Tumbling Mat - Folklore - Fog - Whitelist - BrookeKnuth - Video - Brooke.knuth Folklore Tumbling Mat Whitelist',
            'campaign_name': 'Standard Tumbling Mat Campaign',
            'expected': {
                'launch_date': '7/9/2025',
                'days_live': 41,  # Will be calculated based on today's date
                'category': 'Tumbling Mat',
                'product': 'Folklore',
                'color': 'Fog',
                'content_type': 'Whitelist',
                'handle': 'BrookeKnuth',
                'format': 'Video',
                'ad_name_clean': 'Brooke.knuth Folklore Tumbling Mat Whitelist',
                'campaign_optimization': 'Standard'
            }
        },
        {
            'ad_name': '4/25/2025 - Bath - Checks - Biscuit - Brand - HoN - Collection - New Bath Mats Collection V1',
            'campaign_name': 'Bath Campaign Standard',
            'expected': {
                'launch_date': '4/25/2025',
                'days_live': 116,  # Will be calculated based on today's date
                'category': 'Bath',
                'product': 'Checks',
                'color': 'Biscuit',
                'content_type': 'Brand',
                'handle': 'HoN',
                'format': 'Collection',
                'ad_name_clean': 'New Bath Mats Collection V1',
                'campaign_optimization': 'Standard'
            }
        },
        {
            'ad_name': '7/1/2025 - Standing Mat - Multi - Multi - Brand UGC - HoN - Video - Sydnee UGC Video Standing Mats V1',
            'campaign_name': 'Standing Mat Campaign',
            'expected': {
                'launch_date': '7/1/2025',
                'days_live': 49,  # Will be calculated based on today's date
                'category': 'Standing Mat',
                'product': 'Multi',
                'color': 'Multi',
                'content_type': 'Brand UGC',
                'handle': 'HoN',
                'format': 'Video',
                'ad_name_clean': 'Sydnee UGC Video Standing Mats V1',
                'campaign_optimization': 'Standard'
            }
        },
        {
            'ad_name': '6/15/2025 - Bath - Arden - Wisp - Brand - HoN - Vi',
            'campaign_name': 'Bath Campaign with Incrementality Testing',
            'expected': {
                'launch_date': '6/15/2025',
                'category': 'Bath',
                'product': 'Arden',
                'color': 'Wisp',
                'content_type': 'Brand',
                'handle': 'HoN',
                'format': 'Vi',  # This might be parsed as format
                'campaign_optimization': 'Incremental'
            }
        }
    ]
    
    print("🧪 Testing Ad Name Parser")
    print("=" * 50)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}:")
        print(f"Ad Name: {test_case['ad_name']}")
        print(f"Campaign: {test_case['campaign_name']}")
        
        # Parse the ad name
        result = parser.validate_parsing(
            test_case['ad_name'], 
            test_case['campaign_name'], 
            test_case['expected']
        )
        
        # Print results
        print(f"\n📊 Parsed Results:")
        for key, value in result.items():
            if key != 'validation':
                print(f"  {key}: {value}")
        
        # Check validation
        if 'validation' in result:
            validation = result['validation']
            if validation['passed']:
                print(f"✅ Test {i}: PASSED")
            else:
                print(f"❌ Test {i}: FAILED")
                for error in validation['errors']:
                    print(f"   - {error}")
                all_passed = False
        else:
            print(f"⚠️  Test {i}: No validation performed")
        
        print("-" * 30)
    
    # Test fallback parsing (unstructured ad names)
    print(f"\n🔄 Testing Fallback Parsing (Unstructured Names):")
    fallback_tests = [
        'Folklore Tumbling Mat Video by Brooke Knuth',
        'Bath Mats Collection - New Design Video',
        'Standing Mat UGC Content by Sydnee'
    ]
    
    for fallback_ad in fallback_tests:
        print(f"\nAd Name: {fallback_ad}")
        result = parser.parse_ad_name(fallback_ad)
        print(f"Parsed: Category={result['category']}, Product={result['product']}, Format={result['format']}")
    
    # Summary
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 All tests PASSED!")
    else:
        print("❌ Some tests FAILED. Check output above.")
    
    return all_passed

def test_individual_parsing_methods():
    """Test individual parsing methods"""
    parser = AdNameParser()
    
    print(f"\n🔧 Testing Individual Parsing Methods:")
    print("-" * 40)
    
    # Test date parsing
    dates = ['7/9/2025', '4/25/2025', '12/31/2024']
    print("📅 Date Parsing:")
    for date_str in dates:
        parsed_date = parser._parse_date(date_str)
        print(f"  {date_str} -> {parsed_date}")
    
    # Test category normalization
    categories = ['Tumbling Mat', 'bath', 'STANDING MAT', 'Play Mat']
    print("\n📂 Category Normalization:")
    for cat in categories:
        normalized = parser._normalize_category(cat)
        print(f"  {cat} -> {normalized}")
    
    # Test content type normalization
    content_types = ['whitelist', 'BRAND UGC', 'brand', 'UGC']
    print("\n🎭 Content Type Normalization:")
    for ct in content_types:
        normalized = parser._normalize_content_type(ct)
        print(f"  {ct} -> {normalized}")
    
    # Test campaign optimization detection
    campaigns = [
        'Bath Campaign Standard',
        'Tumbling Mat Incrementality Test',
        'Standing Mat Campaign with Incremental Testing',
        'Regular Campaign'
    ]
    print("\n🎯 Campaign Optimization Detection:")
    for campaign in campaigns:
        optimization = parser._parse_campaign_optimization(campaign)
        print(f"  {campaign} -> {optimization}")

if __name__ == "__main__":
    print("🚀 Starting Ad Name Parser Tests")
    print("=" * 60)
    
    try:
        # Run main tests
        passed = test_ad_name_parser()
        
        # Run individual method tests
        test_individual_parsing_methods()
        
        print(f"\n{'='*60}")
        if passed:
            print("✨ All tests completed successfully!")
            sys.exit(0)
        else:
            print("⚠️  Some tests failed. Please review the output.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)