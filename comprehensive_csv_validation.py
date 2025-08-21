#!/usr/bin/env python3
"""
Comprehensive validation using a larger sample from your CSV data
Tests edge cases and less structured ad names
"""

import os
import sys
from datetime import date, datetime
from typing import List, Dict, Any

# Add the backend app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

from services.ad_name_parser import AdNameParser

def create_comprehensive_test_data():
    """
    Create test data based on a broader sample from your CSV
    Including some edge cases and non-structured ad names
    """
    return [
        # Standard structured format
        {
            'original_ad_name': '7/9/2025 - Tumbling Mat - Folklore - Fog - Whitelist - BrookeKnuth - Video - Brooke.knuth Folklore Tumbling Mat Whitelist',
            'campaign_name': 'Campaign with Incrementality Testing',
            'expected': {
                'category': 'Tumbling Mat',
                'product': 'Folklore',
                'color': 'Fog',
                'content_type': 'Whitelist',
                'handle': 'BrookeKnuth',
                'format': 'Video',
                'campaign_optimization': 'Incremental'
            }
        },
        # Bath category
        {
            'original_ad_name': '4/4/2025 - Bath - Darby - Pasadena - Whitelist - modern.desert.living - Video - Modern.desert.living Darby Pasadena Bath Mat Whitelist',
            'campaign_name': 'Bath Standard Campaign',
            'expected': {
                'category': 'Bath',
                'product': 'Darby',
                'color': 'Pasadena',
                'content_type': 'Whitelist',
                'handle': 'modern.desert.living',
                'format': 'Video',
                'campaign_optimization': 'Standard'
            }
        },
        # Play Furniture category
        {
            'original_ad_name': '5/19/2025 - Play Furniture - Seat - Harlan - Whitelist - thesabrinatan - Video - Sabrina Tan Harlan Seat Play Furniture Whitelist',
            'campaign_name': 'Play Furniture Incrementality Test',
            'expected': {
                'category': 'Play Furniture',
                'product': 'Seat',
                'color': 'Harlan',
                'content_type': 'Whitelist',
                'handle': 'thesabrinatan',
                'format': 'Video',
                'campaign_optimization': 'Incremental'
            }
        },
        # Multi category
        {
            'original_ad_name': '7/11/2025 - Multi - Multi - Multi - Whitelist - alina.kom - Video - Alina Kom Playmat + Furniture Whitelist',
            'campaign_name': 'Multi Category Incrementality',
            'expected': {
                'category': 'Multi',
                'product': 'Multi',
                'color': 'Multi',
                'content_type': 'Whitelist',
                'handle': 'alina.kom',
                'format': 'Video',
                'campaign_optimization': 'Incremental'
            }
        },
        # Brand UGC content type
        {
            'original_ad_name': '3/28/2025 - Standing Mat - Georgia - Clay - Brand UGC - HoN - Video - SosimplyJessica Georgia Clay Standing Mat UGC Ad Long',
            'campaign_name': 'Standard Brand UGC Campaign',
            'expected': {
                'category': 'Standing Mat',
                'product': 'Georgia',
                'color': 'Clay',
                'content_type': 'Brand UGC',
                'handle': 'HoN',
                'format': 'Video',
                'campaign_optimization': 'Standard'
            }
        },
        # Static format
        {
            'original_ad_name': '1/22/2025 - Bath - Darby - Darby - Brand - HoN - Static - Darby Bath Mats Launch Static V2',
            'campaign_name': 'Bath Static Campaign Incrementality',
            'expected': {
                'category': 'Bath',
                'product': 'Darby',
                'color': 'Darby',
                'content_type': 'Brand',
                'handle': 'HoN',
                'format': 'Static',
                'campaign_optimization': 'Incremental'
            }
        },
        # Collection format
        {
            'original_ad_name': '4/25/2025 - Bath - Zelda - Tawny - Brand - HoN - Collection - New Bath Mats Collection V3',
            'campaign_name': 'Bath Collection Campaign',
            'expected': {
                'category': 'Bath',
                'product': 'Zelda',
                'color': 'Tawny',
                'content_type': 'Brand',
                'handle': 'HoN',
                'format': 'Collection',
                'campaign_optimization': 'Standard'
            }
        },
        # GIF format
        {
            'original_ad_name': '1/22/2025 - Bath - Darby - Darby - Brand - HoN - GIF - Darby Bath Mats Launch GIF',
            'campaign_name': 'Bath GIF Incrementality Campaign',
            'expected': {
                'category': 'Bath',
                'product': 'Darby',
                'color': 'Darby',
                'content_type': 'Brand',
                'handle': 'HoN',
                'format': 'GIF',
                'campaign_optimization': 'Incremental'
            }
        },
        # Carousel format
        {
            'original_ad_name': '6/18/2025 - Standing Mat - Devon - Multi - Brand - HoN - Carousel - Standing Mat Launch Swatch Lifestyle Devon',
            'campaign_name': 'Standing Mat Carousel Standard',
            'expected': {
                'category': 'Standing Mat',
                'product': 'Devon',
                'color': 'Multi',
                'content_type': 'Brand',
                'handle': 'HoN',
                'format': 'Carousel',
                'campaign_optimization': 'Standard'
            }
        },
        # Playmat category (vs Play Mat)
        {
            'original_ad_name': '6/25/2025 - Playmat - Emile - Laurel - Whitelist - Sabrina Molu - Video - Sabrina Molu Emile Laurel Play Mat Whitelist',
            'campaign_name': 'Playmat Standard Campaign',
            'expected': {
                'category': 'Playmat',  # Note: different from "Play Mat"
                'product': 'Emile',
                'color': 'Laurel',
                'content_type': 'Whitelist',
                'handle': 'Sabrina Molu',
                'format': 'Video',
                'campaign_optimization': 'Standard'
            }
        },
        # Complex color name
        {
            'original_ad_name': '7/18/2025 - Play Furniture - Seat - Kit Ivory & Sky - Whitelist - Jessi Malay - Video - Jessi Malay Play Furniture Whitelist',
            'campaign_name': 'Complex Color Standard',
            'expected': {
                'category': 'Play Furniture',
                'product': 'Seat',
                'color': 'Kit Ivory & Sky',
                'content_type': 'Whitelist',
                'handle': 'Jessi Malay',
                'format': 'Video',
                'campaign_optimization': 'Standard'
            }
        },
        # Less structured ad name (more realistic)
        {
            'original_ad_name': 'Standing Mats Dedicated Video',
            'campaign_name': 'Standing Mat Brand Campaign',
            'expected': {
                'category': 'Standing Mat',  # Should detect from name
                'product': '',  # Might not detect
                'color': '',   # Might not detect
                'content_type': '',  # Might not detect
                'handle': '',  # Might not detect
                'format': 'Video',  # Should detect
                'campaign_optimization': 'Standard'
            }
        },
        # Brand ad name without structure
        {
            'original_ad_name': 'BIS Bath Mats Video',
            'campaign_name': 'Bath BIS Campaign',
            'expected': {
                'category': 'Bath',  # Should detect
                'product': '',
                'color': '',
                'content_type': '',
                'handle': '',
                'format': 'Video',
                'campaign_optimization': 'Standard'
            }
        }
    ]

def run_comprehensive_validation():
    """
    Run comprehensive validation with edge cases
    """
    parser = AdNameParser()
    test_data = create_comprehensive_test_data()
    
    print("🎯 COMPREHENSIVE PARSER VALIDATION - Real CSV Data + Edge Cases")
    print("=" * 80)
    
    total_tests = len(test_data)
    fields_to_test = ['category', 'product', 'color', 'content_type', 'handle', 'format', 'campaign_optimization']
    
    # Track results
    perfect_matches = 0
    field_accuracy = {field: 0 for field in fields_to_test}
    partial_matches = 0
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
            expected_value = expected.get(field, '')
            parsed_value = parsed.get(field, '')
            
            # For empty expected values, count as match if parsed is also empty
            if expected_value == '' and parsed_value == '':
                match = True
            elif expected_value == parsed_value:
                match = True
            else:
                match = False
            
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
            
            # Show result
            if expected_value == '' and parsed_value == '':
                print(f"  ✅ MATCH {field}: (both empty)")
            else:
                print(f"  {status} {field}: expected='{expected_value}', parsed='{parsed_value}'")
        
        # Categorize result
        if test_result['matches'] == len(fields_to_test):
            perfect_matches += 1
            print(f"  🎉 PERFECT MATCH! ({test_result['matches']}/{len(fields_to_test)})")
        elif test_result['matches'] >= len(fields_to_test) * 0.7:  # 70% or better
            partial_matches += 1
            print(f"  👍 GOOD MATCH: ({test_result['matches']}/{len(fields_to_test)})")
        else:
            print(f"  ⚠️ PARTIAL MATCH: ({test_result['matches']}/{len(fields_to_test)})")
        
        detailed_results.append(test_result)
    
    # Calculate and display summary
    print(f"\n{'='*80}")
    print("📊 COMPREHENSIVE VALIDATION SUMMARY")
    print(f"{'='*80}")
    
    total_possible_matches = total_tests * len(fields_to_test)
    total_actual_matches = sum(field_accuracy.values())
    overall_accuracy = (total_actual_matches / total_possible_matches) * 100
    
    print(f"📈 Overall Results:")
    print(f"  • Total Tests: {total_tests}")
    print(f"  • Perfect Matches: {perfect_matches}/{total_tests} ({(perfect_matches/total_tests)*100:.1f}%)")
    print(f"  • Good Matches (≥70%): {partial_matches}/{total_tests} ({(partial_matches/total_tests)*100:.1f}%)")
    print(f"  • Overall Accuracy: {total_actual_matches}/{total_possible_matches} ({overall_accuracy:.1f}%)")
    
    print(f"\n📋 Field-by-Field Performance:")
    for field in fields_to_test:
        accuracy = (field_accuracy[field] / total_tests) * 100
        if accuracy >= 90:
            emoji = "🟢"
            status = "EXCELLENT"
        elif accuracy >= 80:
            emoji = "🟡"  
            status = "GOOD"
        elif accuracy >= 70:
            emoji = "🟠"
            status = "ACCEPTABLE"
        else:
            emoji = "🔴"
            status = "NEEDS WORK"
        
        print(f"  {emoji} {field.replace('_', ' ').title()}: {field_accuracy[field]}/{total_tests} ({accuracy:.1f}%) - {status}")
    
    # Performance analysis
    strengths = []
    improvements = []
    critical = []
    
    for field in fields_to_test:
        accuracy = (field_accuracy[field] / total_tests) * 100
        if accuracy >= 90:
            strengths.append(f"{field.replace('_', ' ').title()}: {accuracy:.1f}%")
        elif accuracy >= 70:
            improvements.append(f"{field.replace('_', ' ').title()}: {accuracy:.1f}%")
        else:
            critical.append(f"{field.replace('_', ' ').title()}: {accuracy:.1f}%")
    
    if strengths:
        print(f"\n💪 Parser Strengths (≥90%):")
        for strength in strengths:
            print(f"  🟢 {strength}")
    
    if improvements:
        print(f"\n⚠️ Areas for Improvement (70-89%):")
        for improvement in improvements:
            print(f"  🟡 {improvement}")
    
    if critical:
        print(f"\n🚨 Critical Issues (<70%):")
        for issue in critical:
            print(f"  🔴 {issue}")
    
    # Overall assessment
    print(f"\n🏆 OVERALL ASSESSMENT:")
    if overall_accuracy >= 95:
        print("  🌟 OUTSTANDING! Parser is production-ready.")
    elif overall_accuracy >= 90:
        print("  🎉 EXCELLENT! Parser performs very well.")
    elif overall_accuracy >= 80:
        print("  👍 GOOD! Parser is solid with minor improvements needed.")
    elif overall_accuracy >= 70:
        print("  ⚠️ ACCEPTABLE! Some improvements recommended.")
    else:
        print("  🚨 NEEDS MAJOR WORK! Significant improvements required.")
    
    # Specific recommendations
    print(f"\n🔧 SPECIFIC RECOMMENDATIONS:")
    
    # Category-specific advice
    category_accuracy = (field_accuracy['category'] / total_tests) * 100
    if category_accuracy < 90:
        print("  • Add 'Playmat' as distinct from 'Play Mat' in category detection")
        print("  • Improve fallback category detection for unstructured names")
    
    # Product-specific advice  
    product_accuracy = (field_accuracy['product'] / total_tests) * 100
    if product_accuracy < 80:
        print("  • Expand product name database with more House of Noa products")
        print("  • Add better product extraction for unstructured ad names")
    
    # Color-specific advice
    color_accuracy = (field_accuracy['color'] / total_tests) * 100
    if color_accuracy < 80:
        print("  • Add support for complex color names like 'Kit Ivory & Sky'")
        print("  • Improve color extraction from unstructured ad names")
    
    # Handle-specific advice
    handle_accuracy = (field_accuracy['handle'] / total_tests) * 100
    if handle_accuracy < 85:
        print("  • Add more influencer/creator handle patterns")
        print("  • Improve handle detection for names with spaces")
    
    # Format-specific advice
    format_accuracy = (field_accuracy['format'] / total_tests) * 100
    if format_accuracy < 90:
        print("  • Add 'GIF' and 'Carousel' to format detection")
        print("  • Improve format extraction from ad names")
    
    print(f"\n{'='*80}")
    
    return {
        'overall_accuracy': overall_accuracy,
        'perfect_matches': perfect_matches,
        'partial_matches': partial_matches,
        'total_tests': total_tests,
        'field_accuracy': field_accuracy,
        'detailed_results': detailed_results
    }

if __name__ == "__main__":
    run_comprehensive_validation()