#!/usr/bin/env python3
"""
Validation script to test our ad name parser against real Meta Ads data
and the analyst's curated dataset for July 28 - August 10, 2025
"""

import os
import sys
import csv
from datetime import date, datetime
from typing import List, Dict, Any, Optional
import json

# Add the backend app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

from services.ad_name_parser import AdNameParser
from services.meta_ad_level_service import MetaAdLevelService
from loguru import logger

class ParserValidator:
    """
    Validates the ad name parser against real Meta Ads data and analyst's curated data
    """
    
    def __init__(self):
        self.parser = AdNameParser()
        self.analyst_data = []
        self.meta_service = None
        
        # Initialize Meta service if credentials are available
        try:
            self.meta_service = MetaAdLevelService()
            logger.info("Meta Ads service initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize Meta Ads service: {e}")
        
        # Analyst's curated data from your example
        self.load_analyst_sample_data()
    
    def load_analyst_sample_data(self):
        """
        Load the analyst's sample data for comparison
        """
        sample_data = [
            {
                'reporting_starts': '2025-08-04',
                'reporting_ends': '2025-08-10',
                'launch_date': '7/9/2025',
                'days_live': 41,
                'category': 'Tumbling Mat',
                'product': 'Folklore',
                'color': 'Fog',
                'content_type': 'Whitelist',
                'handle': 'BrookeKnuth',
                'format': 'Video',
                'ad_name': 'Brooke.knuth Folklore Tumbling Mat Whitelist',
                'campaign_optimization': 'Incremental',
                'amount_spent_usd': 287.05,
                'original_ad_name': '7/9/2025 - Tumbling Mat - Folklore - Fog - Whitelist - BrookeKnuth - Video - Brooke.knuth Folklore Tumbling Mat Whitelist',
                'campaign_name': 'Some Campaign With Incrementality'
            },
            {
                'reporting_starts': '2025-07-28',
                'reporting_ends': '2025-08-03',
                'launch_date': '7/9/2025',
                'days_live': 41,
                'category': 'Tumbling Mat',
                'product': 'Folklore',
                'color': 'Fog',
                'content_type': 'Whitelist',
                'handle': 'BrookeKnuth',
                'format': 'Video',
                'ad_name': 'Brooke.knuth Folklore Tumbling Mat Whitelist',
                'campaign_optimization': 'Incremental',
                'amount_spent_usd': 245.67,
                'original_ad_name': '7/9/2025 - Tumbling Mat - Folklore - Fog - Whitelist - BrookeKnuth - Video - Brooke.knuth Folklore Tumbling Mat Whitelist',
                'campaign_name': 'Some Campaign With Incrementality'
            },
            {
                'reporting_starts': '2025-08-04',
                'reporting_ends': '2025-08-10',
                'launch_date': '4/25/2025',
                'days_live': 116,
                'category': 'Bath',
                'product': 'Checks',
                'color': 'Biscuit',
                'content_type': 'Brand',
                'handle': 'HoN',
                'format': 'Collection',
                'ad_name': 'New Bath Mats Collection V1',
                'campaign_optimization': 'Standard',
                'amount_spent_usd': 254.15,
                'original_ad_name': '4/25/2025 - Bath - Checks - Biscuit - Brand - HoN - Collection - New Bath Mats Collection V1',
                'campaign_name': 'Bath Campaign Standard'
            },
            {
                'reporting_starts': '2025-08-04',
                'reporting_ends': '2025-08-10',
                'launch_date': '7/1/2025',
                'days_live': 49,
                'category': 'Standing Mat',
                'product': 'Multi',
                'color': 'Multi',
                'content_type': 'Brand UGC',
                'handle': 'HoN',
                'format': 'Video',
                'ad_name': 'Sydnee UGC Video Standing Mats V1',
                'campaign_optimization': 'Standard',
                'amount_spent_usd': 6.01,
                'original_ad_name': '7/1/2025 - Standing Mat - Multi - Multi - Brand UGC - HoN - Video - Sydnee UGC Video Standing Mats V1',
                'campaign_name': 'Standing Mat Campaign'
            }
        ]
        
        self.analyst_data = sample_data
        logger.info(f"Loaded {len(self.analyst_data)} sample records from analyst data")
    
    def fetch_real_meta_data(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """
        Fetch real Meta Ads data for the specified date range
        """
        if not self.meta_service:
            logger.error("Meta Ads service not available")
            return []
        
        try:
            logger.info(f"Fetching Meta Ads data from {start_date} to {end_date}")
            
            # Use the existing service to get ad-level insights
            ad_data = self.meta_service.get_ad_level_insights(start_date, end_date)
            
            logger.info(f"Retrieved {len(ad_data)} ad records from Meta API")
            return ad_data
            
        except Exception as e:
            logger.error(f"Error fetching Meta Ads data: {e}")
            return []
    
    def validate_parser_against_analyst_data(self) -> Dict[str, Any]:
        """
        Validate parser against the analyst's curated data
        """
        results = {
            'total_tested': len(self.analyst_data),
            'overall_accuracy': 0,
            'field_accuracy': {},
            'discrepancies': [],
            'perfect_matches': 0
        }
        
        fields_to_check = ['launch_date', 'category', 'product', 'color', 'content_type', 'handle', 'format', 'campaign_optimization']
        field_matches = {field: 0 for field in fields_to_check}
        
        for i, analyst_record in enumerate(self.analyst_data):
            original_ad_name = analyst_record['original_ad_name']
            campaign_name = analyst_record.get('campaign_name', '')
            
            # Parse with our parser
            parsed_result = self.parser.parse_ad_name(original_ad_name, campaign_name)
            
            # Track matches for each field
            record_matches = 0
            discrepancy = {
                'record_index': i,
                'original_ad_name': original_ad_name,
                'expected': {},
                'parsed': {},
                'mismatches': []
            }
            
            for field in fields_to_check:
                expected = analyst_record.get(field)
                
                if field == 'launch_date':
                    # Convert expected date string to date object for comparison
                    try:
                        expected_date = self.parser._parse_date(expected)
                        parsed_value = parsed_result.get('launch_date')
                        
                        if expected_date == parsed_value:
                            field_matches[field] += 1
                            record_matches += 1
                        else:
                            discrepancy['expected'][field] = str(expected_date)
                            discrepancy['parsed'][field] = str(parsed_value)
                            discrepancy['mismatches'].append(field)
                    except:
                        discrepancy['expected'][field] = expected
                        discrepancy['parsed'][field] = str(parsed_result.get('launch_date'))
                        discrepancy['mismatches'].append(field)
                
                else:
                    parsed_value = parsed_result.get(field, '')
                    
                    if expected == parsed_value:
                        field_matches[field] += 1
                        record_matches += 1
                    else:
                        discrepancy['expected'][field] = expected
                        discrepancy['parsed'][field] = parsed_value
                        discrepancy['mismatches'].append(field)
            
            # Check if this is a perfect match
            if record_matches == len(fields_to_check):
                results['perfect_matches'] += 1
            
            # Add discrepancy if there were any mismatches
            if discrepancy['mismatches']:
                results['discrepancies'].append(discrepancy)
            
            # Log detailed comparison for this record
            logger.info(f"Record {i+1}: {record_matches}/{len(fields_to_check)} fields matched")
            logger.debug(f"  Ad: {original_ad_name[:60]}...")
            logger.debug(f"  Matches: {record_matches}/{len(fields_to_check)}")
        
        # Calculate accuracy metrics
        total_fields = len(self.analyst_data) * len(fields_to_check)
        total_matches = sum(field_matches.values())
        results['overall_accuracy'] = (total_matches / total_fields) * 100 if total_fields > 0 else 0
        
        for field in fields_to_check:
            results['field_accuracy'][field] = (field_matches[field] / len(self.analyst_data)) * 100
        
        return results
    
    def validate_parser_against_meta_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Validate parser against real Meta Ads data
        """
        meta_data = self.fetch_real_meta_data(start_date, end_date)
        
        if not meta_data:
            return {'error': 'No Meta Ads data retrieved'}
        
        results = {
            'total_tested': len(meta_data),
            'parsing_success_rate': 0,
            'parsing_errors': [],
            'sample_results': [],
            'field_coverage': {}
        }
        
        successful_parses = 0
        parsing_errors = []
        
        # Track which fields are successfully extracted
        field_extraction_count = {
            'launch_date': 0,
            'category': 0,
            'product': 0,
            'color': 0,
            'content_type': 0,
            'handle': 0,
            'format': 0,
            'campaign_optimization': 0
        }
        
        for i, meta_record in enumerate(meta_data[:20]):  # Test first 20 records
            ad_name = meta_record.get('ad_name', '')
            campaign_name = meta_record.get('campaign_name', '')
            
            try:
                parsed_result = self.parser.parse_ad_name(ad_name, campaign_name)
                successful_parses += 1
                
                # Track field extraction success
                for field in field_extraction_count:
                    if parsed_result.get(field):
                        field_extraction_count[field] += 1
                
                # Add to sample results
                if len(results['sample_results']) < 5:
                    results['sample_results'].append({
                        'original_ad_name': ad_name,
                        'campaign_name': campaign_name,
                        'parsed_result': {k: str(v) for k, v in parsed_result.items()}
                    })
                
            except Exception as e:
                parsing_errors.append({
                    'ad_name': ad_name,
                    'error': str(e)
                })
                logger.warning(f"Error parsing ad name '{ad_name}': {e}")
        
        # Calculate metrics
        tested_count = min(len(meta_data), 20)
        results['parsing_success_rate'] = (successful_parses / tested_count) * 100 if tested_count > 0 else 0
        results['parsing_errors'] = parsing_errors
        
        # Calculate field coverage
        for field, count in field_extraction_count.items():
            results['field_coverage'][field] = (count / successful_parses) * 100 if successful_parses > 0 else 0
        
        return results
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive validation report
        """
        logger.info("Starting comprehensive parser validation...")
        
        # Define the exact date range from your analyst data
        start_date = date(2025, 7, 28)
        end_date = date(2025, 8, 10)
        
        report = {
            'validation_date': datetime.now().isoformat(),
            'date_range_tested': f"{start_date} to {end_date}",
            'analyst_data_validation': {},
            'meta_data_validation': {},
            'summary': {},
            'recommendations': []
        }
        
        # Test against analyst's curated data
        logger.info("Validating against analyst's curated data...")
        analyst_results = self.validate_parser_against_analyst_data()
        report['analyst_data_validation'] = analyst_results
        
        # Test against real Meta data
        logger.info("Validating against real Meta Ads data...")
        meta_results = self.validate_parser_against_meta_data(start_date, end_date)
        report['meta_data_validation'] = meta_results
        
        # Generate summary and recommendations
        report['summary'] = self.generate_summary(analyst_results, meta_results)
        report['recommendations'] = self.generate_recommendations(analyst_results, meta_results)
        
        return report
    
    def generate_summary(self, analyst_results: Dict, meta_results: Dict) -> Dict[str, Any]:
        """
        Generate a summary of validation results
        """
        summary = {
            'overall_status': 'Unknown',
            'key_metrics': {},
            'strengths': [],
            'weaknesses': []
        }
        
        # Analyst data summary
        if analyst_results:
            analyst_accuracy = analyst_results.get('overall_accuracy', 0)
            perfect_matches = analyst_results.get('perfect_matches', 0)
            total_tested = analyst_results.get('total_tested', 0)
            
            summary['key_metrics']['analyst_accuracy'] = f"{analyst_accuracy:.1f}%"
            summary['key_metrics']['perfect_matches'] = f"{perfect_matches}/{total_tested}"
            
            # Determine strengths and weaknesses
            field_accuracy = analyst_results.get('field_accuracy', {})
            for field, accuracy in field_accuracy.items():
                if accuracy >= 90:
                    summary['strengths'].append(f"{field.replace('_', ' ').title()}: {accuracy:.1f}%")
                elif accuracy < 70:
                    summary['weaknesses'].append(f"{field.replace('_', ' ').title()}: {accuracy:.1f}%")
        
        # Meta data summary
        if meta_results and 'error' not in meta_results:
            parsing_success = meta_results.get('parsing_success_rate', 0)
            summary['key_metrics']['parsing_success_rate'] = f"{parsing_success:.1f}%"
        
        # Overall status
        if analyst_results:
            if analyst_results.get('overall_accuracy', 0) >= 85:
                summary['overall_status'] = 'Excellent'
            elif analyst_results.get('overall_accuracy', 0) >= 70:
                summary['overall_status'] = 'Good'
            elif analyst_results.get('overall_accuracy', 0) >= 50:
                summary['overall_status'] = 'Needs Improvement'
            else:
                summary['overall_status'] = 'Poor'
        
        return summary
    
    def generate_recommendations(self, analyst_results: Dict, meta_results: Dict) -> List[str]:
        """
        Generate recommendations based on validation results
        """
        recommendations = []
        
        # Analyze analyst results
        if analyst_results:
            field_accuracy = analyst_results.get('field_accuracy', {})
            
            for field, accuracy in field_accuracy.items():
                if accuracy < 80:
                    if field == 'launch_date':
                        recommendations.append(f"Improve date parsing - only {accuracy:.1f}% accuracy. Consider adding more date format patterns.")
                    elif field == 'category':
                        recommendations.append(f"Enhance category detection - {accuracy:.1f}% accuracy. Add more category keywords and patterns.")
                    elif field == 'product':
                        recommendations.append(f"Improve product extraction - {accuracy:.1f}% accuracy. Expand product name database.")
                    elif field == 'color':
                        recommendations.append(f"Enhance color recognition - {accuracy:.1f}% accuracy. Add more color variations.")
                    elif field == 'content_type':
                        recommendations.append(f"Improve content type parsing - {accuracy:.1f}% accuracy. Add more content type patterns.")
                    elif field == 'handle':
                        recommendations.append(f"Enhance handle detection - {accuracy:.1f}% accuracy. Add more known handle patterns.")
                    elif field == 'format':
                        recommendations.append(f"Improve format detection - {accuracy:.1f}% accuracy. Add more format keywords.")
                    elif field == 'campaign_optimization':
                        recommendations.append(f"Enhance campaign optimization detection - {accuracy:.1f}% accuracy. Check incrementality keyword matching.")
        
        # Analyze meta results
        if meta_results and 'error' not in meta_results:
            parsing_success = meta_results.get('parsing_success_rate', 0)
            if parsing_success < 95:
                recommendations.append(f"Parser success rate is {parsing_success:.1f}%. Add error handling for edge cases.")
            
            # Check field coverage
            field_coverage = meta_results.get('field_coverage', {})
            for field, coverage in field_coverage.items():
                if coverage < 50:
                    recommendations.append(f"Low {field} extraction rate ({coverage:.1f}%) on real data. Review ad name patterns.")
        
        if not recommendations:
            recommendations.append("Parser performance is excellent! No major improvements needed.")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], output_file: str = "parser_validation_report.json"):
        """
        Save the validation report to a file
        """
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Validation report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
    
    def print_summary_report(self, report: Dict[str, Any]):
        """
        Print a human-readable summary of the validation results
        """
        print("\n" + "="*80)
        print("🎯 META ADS AD NAME PARSER VALIDATION REPORT")
        print("="*80)
        
        summary = report.get('summary', {})
        analyst_results = report.get('analyst_data_validation', {})
        meta_results = report.get('meta_data_validation', {})
        
        # Overall Status
        status = summary.get('overall_status', 'Unknown')
        status_emoji = {'Excellent': '🟢', 'Good': '🟡', 'Needs Improvement': '🟠', 'Poor': '🔴'}.get(status, '⚪')
        print(f"\n{status_emoji} Overall Status: {status}")
        
        # Key Metrics
        print(f"\n📊 Key Metrics:")
        metrics = summary.get('key_metrics', {})
        for metric, value in metrics.items():
            print(f"  • {metric.replace('_', ' ').title()}: {value}")
        
        # Detailed Results
        if analyst_results:
            print(f"\n📋 Analyst Data Validation:")
            print(f"  • Total Records Tested: {analyst_results.get('total_tested', 0)}")
            print(f"  • Perfect Matches: {analyst_results.get('perfect_matches', 0)}")
            print(f"  • Overall Accuracy: {analyst_results.get('overall_accuracy', 0):.1f}%")
            
            # Field-by-field accuracy
            print(f"\n📝 Field-by-Field Accuracy:")
            field_accuracy = analyst_results.get('field_accuracy', {})
            for field, accuracy in sorted(field_accuracy.items()):
                emoji = '✅' if accuracy >= 90 else '⚠️' if accuracy >= 70 else '❌'
                print(f"  {emoji} {field.replace('_', ' ').title()}: {accuracy:.1f}%")
        
        if meta_results and 'error' not in meta_results:
            print(f"\n🔗 Meta API Data Validation:")
            print(f"  • Records Tested: {meta_results.get('total_tested', 0)}")
            print(f"  • Parsing Success Rate: {meta_results.get('parsing_success_rate', 0):.1f}%")
            
            field_coverage = meta_results.get('field_coverage', {})
            if field_coverage:
                print(f"\n📈 Field Extraction Coverage:")
                for field, coverage in sorted(field_coverage.items()):
                    emoji = '✅' if coverage >= 80 else '⚠️' if coverage >= 50 else '❌'
                    print(f"  {emoji} {field.replace('_', ' ').title()}: {coverage:.1f}%")
        
        # Strengths and Weaknesses
        strengths = summary.get('strengths', [])
        weaknesses = summary.get('weaknesses', [])
        
        if strengths:
            print(f"\n💪 Strengths:")
            for strength in strengths:
                print(f"  ✅ {strength}")
        
        if weaknesses:
            print(f"\n⚠️  Areas for Improvement:")
            for weakness in weaknesses:
                print(f"  ❌ {weakness}")
        
        # Recommendations
        recommendations = report.get('recommendations', [])
        if recommendations:
            print(f"\n🔧 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*80)

def main():
    """
    Main function to run the parser validation
    """
    validator = ParserValidator()
    
    try:
        # Generate comprehensive report
        report = validator.generate_comprehensive_report()
        
        # Print summary
        validator.print_summary_report(report)
        
        # Save detailed report
        validator.save_report(report)
        
        print(f"\n✅ Validation complete! Detailed report saved to parser_validation_report.json")
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()