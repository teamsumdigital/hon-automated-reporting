#!/usr/bin/env python3
"""
Simple parser validation test using the provided analyst data
Tests our ad name parser against the real examples from your CSV
"""

import os
import sys
from datetime import date, datetime
from typing import List, Dict, Any

# Add the backend app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

from services.ad_name_parser import AdNameParser

def create_test_data_from_csv():
    """
    Create test data based on the CSV examples you provided
    """
    return [
        {
            'original_ad_name': '7/9/2025 - Tumbling Mat - Folklore - Fog - Whitelist - BrookeKnuth - Video - Brooke.knuth Folklore Tumbling Mat Whitelist',
            'campaign_name': 'Campaign with Incrementality Testing',
            'expected': {
                'launch_date': date(2025, 7, 9),
                'days_live': 41,
                'category': 'Tumbling Mat',
                'product': 'Folklore',
                'color': 'Fog',
                'content_type': 'Whitelist',
                'handle': 'BrookeKnuth',
                'format': 'Video',
                'ad_name_clean': 'Brooke.knuth Folklore Tumbling Mat Whitelist',
                'campaign_optimization': 'Incremental'
            }
        },
        {
            'original_ad_name': '4/25/2025 - Bath - Checks - Biscuit - Brand - HoN - Collection - New Bath Mats Collection V1',
            'campaign_name': 'Bath Campaign Standard',
            'expected': {
                'launch_date': date(2025, 4, 25),
                'days_live': 116,
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
            'original_ad_name': '7/1/2025 - Standing Mat - Multi - Multi - Brand UGC - HoN - Video - Sydnee UGC Video Standing Mats V1',
            'campaign_name': 'Standing Mat Campaign',
            'expected': {
                'launch_date': date(2025, 7, 1),
                'days_live': 49,
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
            'original_ad_name': '5/6/2025 - Tumbling Mat - Fawn - Shea - Whitelist - moore.of.lo - Video - Moore.of.lo Fawn Shea Tumbling Mat Whitelist',
            'campaign_name': 'Tumbling Mat Incrementality Campaign',
            'expected': {
                'launch_date': date(2025, 5, 6),
                'days_live': 105,
                'category': 'Tumbling Mat',
                'product': 'Fawn',
                'color': 'Shea',
                'content_type': 'Whitelist',
                'handle': 'moore.of.lo',
                'format': 'Video',
                'ad_name_clean': 'Moore.of.lo Fawn Shea Tumbling Mat Whitelist',
                'campaign_optimization': 'Incremental'
            }
        },
        {
            'original_ad_name': '4/11/2025 - Standing Mat - Fawn - Brown - Whitelist - kayleebrookesburks - Video - KayleeBrookeBurks Fawn Brown Standing Mat Whitelist',
            'campaign_name': 'Standing Mat Standard Campaign',
            'expected': {
                'launch_date': date(2025, 4, 11),
                'days_live': 130,
                'category': 'Standing Mat',
                'product': 'Fawn',
                'color': 'Brown',
                'content_type': 'Whitelist',
                'handle': 'kayleebrookesburks',
                'format': 'Video',
                'ad_name_clean': 'KayleeBrookeBurks Fawn Brown Standing Mat Whitelist',
                'campaign_optimization': 'Standard'
            }
        },
        {
            'original_ad_name': '5/19/2025 - Play Furniture - Seat - Harlan - Whitelist - thesabrinatan - Video - Sabrina Tan Harlan Seat Play Furniture Whitelist',
            'campaign_name': 'Play Furniture Incrementality Test',
            'expected': {
                'launch_date': date(2025, 5, 19),
                'days_live': 92,
                'category': 'Play Furniture',
                'product': 'Seat',
                'color': 'Harlan',
                'content_type': 'Whitelist',
                'handle': 'thesabrinatan',
                'format': 'Video',
                'ad_name_clean': 'Sabrina Tan Harlan Seat Play Furniture Whitelist',
                'campaign_optimization': 'Incremental'
            }
        },
        {
            'original_ad_name': '3/28/2025 - Standing Mat - Georgia - Clay - Brand UGC - HoN - Video - SosimplyJessica Georgia Clay Standing Mat UGC Ad Long',
            'campaign_name': 'Standard Brand UGC Campaign',
            'expected': {
                'launch_date': date(2025, 3, 28),
                'days_live': 144,
                'category': 'Standing Mat',
                'product': 'Georgia',
                'color': 'Clay',
                'content_type': 'Brand UGC',
                'handle': 'HoN',
                'format': 'Video',
                'ad_name_clean': 'SosimplyJessica Georgia Clay Standing Mat UGC Ad Long',
                'campaign_optimization': 'Standard'
            }
        },
        {
            'original_ad_name': '1/15/2025 - Standing Mat - Multi - Multi - Brand - HoN - Video - Standing Mats Dedicated Video',
            'campaign_name': 'Standing Mat Incrementality Dedicated',
            'expected': {
                'launch_date': date(2025, 1, 15),
                'days_live': 216,
                'category': 'Standing Mat',
                'product': 'Multi',
                'color': 'Multi',
                'content_type': 'Brand',
                'handle': 'HoN',
                'format': 'Video',
                'ad_name_clean': 'Standing Mats Dedicated Video',
                'campaign_optimization': 'Incremental'
            }
        }
    ]

def run_comprehensive_test():
    """
    Run comprehensive validation test
    """
    parser = AdNameParser()
    test_data = create_test_data_from_csv()
    
    print("🎯 PARSER VALIDATION TEST - Real House of Noa Ad Data")
    print("=" * 70)
    
    total_tests = len(test_data)
    fields_to_test = ['launch_date', 'category', 'product', 'color', 'content_type', 'handle', 'format', 'campaign_optimization']
    
    # Track results
    perfect_matches = 0
    field_accuracy = {field: 0 for field in fields_to_test}
    detailed_results = []
    
    for i, test_case in enumerate(test_data, 1):
        original_ad_name = test_case['original_ad_name']
        campaign_name = test_case['campaign_name']
        expected = test_case['expected']
        
        print(f"\n📝 Test {i}/{total_tests}")
        print(f"Ad: {original_ad_name}")
        print(f"Campaign: {campaign_name}")
        
        # Parse the ad name
        parsed = parser.parse_ad_name(original_ad_name, campaign_name)
        
        # Check each field
        test_result = {
            'test_number': i,
            'ad_name': original_ad_name,
            'matches': 0,
            'total_fields': len(fields_to_test),
            'field_results': {}
        }
        
        for field in fields_to_test:
            expected_value = expected.get(field)
            parsed_value = parsed.get(field)
            
            # Handle date comparison specially
            if field == 'launch_date':
                if isinstance(parsed_value, date) and isinstance(expected_value, date):
                    match = parsed_value == expected_value
                else:
                    match = False
            else:
                match = expected_value == parsed_value
            
            if match:
                field_accuracy[field] += 1
                test_result['matches'] += 1
                status = "✅ MATCH"
            else:
                status = "❌ MISS"
            
            test_result['field_results'][field] = {
                'expected': str(expected_value),
                'parsed': str(parsed_value),
                'match': match
            }
            
            print(f"  {status} {field}: expected='{expected_value}', parsed='{parsed_value}'")
        
        # Check if perfect match
        if test_result['matches'] == len(fields_to_test):
            perfect_matches += 1
            print(f"  🎉 PERFECT MATCH! ({test_result['matches']}/{len(fields_to_test)})")
        else:
            print(f"  📊 Partial match: ({test_result['matches']}/{len(fields_to_test)})")
        
        detailed_results.append(test_result)
    
    # Calculate and display summary
    print(f"\n{'='*70}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'='*70}")
    
    total_possible_matches = total_tests * len(fields_to_test)
    total_actual_matches = sum(field_accuracy.values())
    overall_accuracy = (total_actual_matches / total_possible_matches) * 100
    
    print(f"📈 Overall Results:")
    print(f"  • Total Tests: {total_tests}")
    print(f"  • Perfect Matches: {perfect_matches}/{total_tests} ({(perfect_matches/total_tests)*100:.1f}%)")
    print(f"  • Overall Accuracy: {total_actual_matches}/{total_possible_matches} ({overall_accuracy:.1f}%)")
    
    print(f"\n📋 Field-by-Field Accuracy:")
    for field in fields_to_test:
        accuracy = (field_accuracy[field] / total_tests) * 100
        emoji = "✅" if accuracy >= 90 else "⚠️" if accuracy >= 70 else "❌"
        print(f"  {emoji} {field.replace('_', ' ').title()}: {field_accuracy[field]}/{total_tests} ({accuracy:.1f}%)")
    
    # Identify strengths and weaknesses
    strengths = [field for field in fields_to_test if (field_accuracy[field] / total_tests) >= 0.9]
    weaknesses = [field for field in fields_to_test if (field_accuracy[field] / total_tests) < 0.7]
    
    if strengths:
        print(f"\n💪 Parser Strengths:")
        for field in strengths:
            accuracy = (field_accuracy[field] / total_tests) * 100
            print(f"  ✅ {field.replace('_', ' ').title()}: {accuracy:.1f}%")
    
    if weaknesses:
        print(f"\n⚠️ Areas for Improvement:")
        for field in weaknesses:
            accuracy = (field_accuracy[field] / total_tests) * 100
            print(f"  ❌ {field.replace('_', ' ').title()}: {accuracy:.1f}%")
    
    # Generate recommendations
    print(f"\n🔧 Recommendations:")
    if overall_accuracy >= 90:
        print("  🎉 Excellent performance! Parser is working very well.")
    elif overall_accuracy >= 80:
        print("  👍 Good performance! Consider minor tweaks to improve weak areas.")
    elif overall_accuracy >= 70:
        print("  ⚠️ Moderate performance. Focus on improving the weakest fields.")
    else:
        print("  🚨 Poor performance. Major improvements needed.")
    
    for field in weaknesses:
        if field == 'launch_date':
            print("  • Add more date format patterns to improve date parsing")
        elif field == 'category':
            print("  • Expand category detection keywords and patterns")
        elif field == 'product':
            print("  • Add more product names to the known products list")
        elif field == 'color':
            print("  • Expand color recognition database")
        elif field == 'content_type':
            print("  • Improve content type pattern matching")
        elif field == 'handle':
            print("  • Add more known handles and improve handle detection")
        elif field == 'format':
            print("  • Enhance format detection patterns")
        elif field == 'campaign_optimization':
            print("  • Review incrementality keyword detection logic")
    
    print(f"\n{'='*70}")
    
    return {
        'overall_accuracy': overall_accuracy,
        'perfect_matches': perfect_matches,
        'total_tests': total_tests,
        'field_accuracy': field_accuracy,
        'detailed_results': detailed_results
    }

if __name__ == "__main__":
    run_comprehensive_test()