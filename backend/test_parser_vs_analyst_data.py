#!/usr/bin/env python3
"""
Comprehensive comparison script to validate our ad name parser against analyst's CSV data
Fetches Meta Ads data for July 28 - August 10, 2025 and compares parsing results

Usage:
    python test_parser_vs_analyst_data.py [analyst_data.csv]
    
If no CSV file is provided, the script will create sample data based on the examples provided.
"""

import sys
import os
import csv
import json
from datetime import date, datetime
from typing import Dict, List, Any, Optional
from decimal import Decimal
import pandas as pd
from pathlib import Path

# Add the backend app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.ad_name_parser import AdNameParser
from services.meta_ad_level_service import MetaAdLevelService

class ParserValidationReport:
    """Generate comprehensive comparison report between parser and analyst data"""
    
    def __init__(self):
        self.parser = AdNameParser()
        self.meta_service = None
        self.report = {
            'summary': {},
            'field_accuracy': {},
            'discrepancies': [],
            'parser_performance': {},
            'recommendations': []
        }
        
        # Initialize Meta service if credentials are available
        try:
            self.meta_service = MetaAdLevelService()
            print("✅ Meta Ads API connection initialized")
        except Exception as e:
            print(f"⚠️  Meta Ads API not available: {e}")
            print("   Will work with sample/CSV data only")
    
    def load_analyst_data(self, csv_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load analyst data from CSV or create sample data"""
        
        if csv_path and Path(csv_path).exists():
            print(f"📂 Loading analyst data from: {csv_path}")
            
            # Load CSV data
            df = pd.read_csv(csv_path)
            analyst_data = df.to_dict('records')
            
            # Normalize column names
            for row in analyst_data:
                normalized_row = {}
                for key, value in row.items():
                    # Convert column names to match our expected format
                    normalized_key = self._normalize_column_name(key)
                    normalized_row[normalized_key] = value
                analyst_data = [normalized_row if normalized_row else row for row in analyst_data]
            
            print(f"   Loaded {len(analyst_data)} records")
            return analyst_data
        
        else:
            print("📝 Creating sample analyst data based on provided examples")
            return self._create_sample_analyst_data()
    
    def _normalize_column_name(self, column_name: str) -> str:
        """Normalize CSV column names to match our expected format"""
        column_mapping = {
            'Reporting starts': 'reporting_starts',
            'Reporting ends': 'reporting_ends', 
            'Launch Date': 'launch_date',
            'Days Live': 'days_live',
            'Category': 'category',
            'Product': 'product',
            'Color': 'color',
            'Content Type': 'content_type',
            'Handle': 'handle',
            'Format': 'format',
            'Ad Name': 'ad_name',
            'Campaign Optimization': 'campaign_optimization',
            'Amount spent (USD)': 'amount_spent_usd'
        }
        
        return column_mapping.get(column_name, column_name.lower().replace(' ', '_'))
    
    def _create_sample_analyst_data(self) -> List[Dict[str, Any]]:
        """Create sample data based on the examples provided"""
        
        sample_data = [
            {
                'reporting_starts': '2025-07-28',
                'reporting_ends': '2025-08-10',
                'launch_date': '2025-07-09',
                'days_live': 32,
                'category': 'Tumbling Mat',
                'product': 'Folklore',
                'color': 'Fog',
                'content_type': 'Whitelist',
                'handle': 'BrookeKnuth',
                'format': 'Video',
                'ad_name': '7/9/2025 - Tumbling Mat - Folklore - Fog - Whitelist - BrookeKnuth - Video - Brooke.knuth Folklore Tumbling Mat Whitelist',
                'campaign_optimization': 'Standard',
                'amount_spent_usd': 1250.75
            },
            {
                'reporting_starts': '2025-07-28',
                'reporting_ends': '2025-08-10',
                'launch_date': '2025-04-25',
                'days_live': 107,
                'category': 'Bath',
                'product': 'Checks',
                'color': 'Biscuit',
                'content_type': 'Brand',
                'handle': 'HoN',
                'format': 'Collection',
                'ad_name': '4/25/2025 - Bath - Checks - Biscuit - Brand - HoN - Collection - New Bath Mats Collection V1',
                'campaign_optimization': 'Standard',
                'amount_spent_usd': 890.50
            },
            {
                'reporting_starts': '2025-07-28',
                'reporting_ends': '2025-08-10',
                'launch_date': '2025-07-01',
                'days_live': 40,
                'category': 'Standing Mat',
                'product': 'Multi',
                'color': 'Multi',
                'content_type': 'Brand UGC',
                'handle': 'HoN',
                'format': 'Video',
                'ad_name': '7/1/2025 - Standing Mat - Multi - Multi - Brand UGC - HoN - Video - Sydnee UGC Video Standing Mats V1',
                'campaign_optimization': 'Standard',
                'amount_spent_usd': 675.25
            },
            {
                'reporting_starts': '2025-07-28',
                'reporting_ends': '2025-08-10',
                'launch_date': '2025-06-15',
                'days_live': 56,
                'category': 'Bath',
                'product': 'Arden',
                'color': 'Wisp',
                'content_type': 'Brand',
                'handle': 'HoN',
                'format': 'Video',
                'ad_name': '6/15/2025 - Bath - Arden - Wisp - Brand - HoN - Video - New Arden Wisp Bath Collection',
                'campaign_optimization': 'Incremental',
                'amount_spent_usd': 1575.80
            },
            {
                'reporting_starts': '2025-07-28',
                'reporting_ends': '2025-08-10',
                'launch_date': '2025-05-20',
                'days_live': 82,
                'category': 'Play Mat',
                'product': 'Botanical',
                'color': 'Sage',
                'content_type': 'UGC',
                'handle': 'Madison',
                'format': 'Carousel',
                'ad_name': '5/20/2025 - Play Mat - Botanical - Sage - UGC - Madison - Carousel - Madison UGC Botanical Play Mat Collection',
                'campaign_optimization': 'Standard',
                'amount_spent_usd': 980.40
            }
        ]
        
        print(f"   Created {len(sample_data)} sample records")
        return sample_data
    
    def fetch_meta_api_data(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Fetch ad data from Meta API for the specified date range"""
        
        if not self.meta_service:
            print("⚠️  Meta API service not available, using sample data for API comparison")
            return []
        
        try:
            print(f"🔄 Fetching Meta API data for {start_date} to {end_date}")
            api_data = self.meta_service.get_ad_level_insights(start_date, end_date)
            print(f"   Retrieved {len(api_data)} ad records from Meta API")
            return api_data
            
        except Exception as e:
            print(f"❌ Error fetching Meta API data: {e}")
            return []
    
    def compare_parsing_results(self, analyst_data: List[Dict[str, Any]], api_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Compare parser results against analyst data and optionally API data"""
        
        print("\n🔍 Analyzing parser performance...")
        
        # Track metrics
        total_ads = len(analyst_data)
        field_matches = {
            'launch_date': 0,
            'category': 0,
            'product': 0,
            'color': 0,
            'content_type': 0,
            'handle': 0,
            'format': 0,
            'campaign_optimization': 0
        }
        
        discrepancies = []
        detailed_results = []
        
        for i, analyst_row in enumerate(analyst_data, 1):
            ad_name = analyst_row.get('ad_name', '')
            campaign_name = f"Sample Campaign {i}"  # Since we don't have campaign names in sample data
            
            # Parse with our parser
            parsed_result = self.parser.parse_ad_name(ad_name, campaign_name)
            
            # Compare each field
            comparison = {
                'ad_name': ad_name,
                'analyst_data': analyst_row,
                'parsed_data': parsed_result,
                'matches': {},
                'discrepancies': {}
            }
            
            for field in field_matches.keys():
                analyst_value = analyst_row.get(field)
                parsed_value = parsed_result.get(field)
                
                # Special handling for date fields
                if field == 'launch_date':
                    analyst_value = self._normalize_date(analyst_value)
                    # parsed_value is already a date object
                
                # Check if values match
                if self._values_match(analyst_value, parsed_value, field):
                    field_matches[field] += 1
                    comparison['matches'][field] = True
                else:
                    comparison['matches'][field] = False
                    comparison['discrepancies'][field] = {
                        'analyst': analyst_value,
                        'parsed': parsed_value
                    }
                    
                    discrepancies.append({
                        'ad_name': ad_name[:50] + '...' if len(ad_name) > 50 else ad_name,
                        'field': field,
                        'analyst_value': analyst_value,
                        'parsed_value': parsed_value
                    })
            
            detailed_results.append(comparison)
        
        # Calculate accuracy percentages
        field_accuracy = {}
        for field, matches in field_matches.items():
            accuracy = (matches / total_ads) * 100 if total_ads > 0 else 0
            field_accuracy[field] = {
                'matches': matches,
                'total': total_ads,
                'accuracy_percent': round(accuracy, 2)
            }
        
        # Overall accuracy
        total_field_checks = sum(field_matches.values())
        max_possible_matches = len(field_matches) * total_ads
        overall_accuracy = (total_field_checks / max_possible_matches) * 100 if max_possible_matches > 0 else 0
        
        # Store results
        self.report['summary'] = {
            'total_ads_analyzed': total_ads,
            'overall_accuracy_percent': round(overall_accuracy, 2),
            'total_discrepancies': len(discrepancies)
        }
        
        self.report['field_accuracy'] = field_accuracy
        self.report['discrepancies'] = discrepancies
        self.report['detailed_results'] = detailed_results
        
        return self.report
    
    def _normalize_date(self, date_value: Any) -> Optional[date]:
        """Normalize date values for comparison"""
        if isinstance(date_value, date):
            return date_value
        elif isinstance(date_value, str):
            try:
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                    try:
                        return datetime.strptime(date_value, fmt).date()
                    except ValueError:
                        continue
            except:
                pass
        return None
    
    def _values_match(self, analyst_value: Any, parsed_value: Any, field: str) -> bool:
        """Check if two values match with appropriate normalization"""
        
        # Handle None values
        if analyst_value is None and parsed_value is None:
            return True
        if analyst_value is None or parsed_value is None:
            return False
        
        # Convert to strings for comparison (except dates)
        if field == 'launch_date':
            return analyst_value == parsed_value
        
        # Normalize strings for comparison
        analyst_str = str(analyst_value).lower().strip()
        parsed_str = str(parsed_value).lower().strip()
        
        return analyst_str == parsed_str
    
    def generate_detailed_report(self) -> str:
        """Generate a comprehensive text report"""
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("🧪 META ADS PARSER VALIDATION REPORT")
        report_lines.append("=" * 80)
        
        # Summary
        summary = self.report['summary']
        report_lines.append(f"\n📊 SUMMARY:")
        report_lines.append(f"   Total Ads Analyzed: {summary['total_ads_analyzed']}")
        report_lines.append(f"   Overall Accuracy: {summary['overall_accuracy_percent']}%")
        report_lines.append(f"   Total Discrepancies: {summary['total_discrepancies']}")
        
        # Field-by-field accuracy
        report_lines.append(f"\n📈 FIELD ACCURACY:")
        for field, accuracy in self.report['field_accuracy'].items():
            report_lines.append(f"   {field.title().replace('_', ' ')}: {accuracy['matches']}/{accuracy['total']} ({accuracy['accuracy_percent']}%)")
        
        # Top discrepancies
        if self.report['discrepancies']:
            report_lines.append(f"\n❌ DISCREPANCIES FOUND:")
            
            # Group discrepancies by field
            field_discrepancies = {}
            for disc in self.report['discrepancies']:
                field = disc['field']
                if field not in field_discrepancies:
                    field_discrepancies[field] = []
                field_discrepancies[field].append(disc)
            
            for field, discs in field_discrepancies.items():
                report_lines.append(f"\n   {field.title().replace('_', ' ')} Issues ({len(discs)} total):")
                for disc in discs[:5]:  # Show first 5 examples
                    report_lines.append(f"     • {disc['ad_name']}")
                    report_lines.append(f"       Analyst: '{disc['analyst_value']}' | Parser: '{disc['parsed_value']}'")
                
                if len(discs) > 5:
                    report_lines.append(f"     ... and {len(discs) - 5} more")
        
        # Recommendations
        report_lines.append(f"\n💡 RECOMMENDATIONS:")
        recommendations = self._generate_recommendations()
        for rec in recommendations:
            report_lines.append(f"   • {rec}")
        
        # Detailed breakdown (first 3 examples)
        if 'detailed_results' in self.report and self.report['detailed_results']:
            report_lines.append(f"\n🔍 DETAILED EXAMPLES (First 3):")
            for i, result in enumerate(self.report['detailed_results'][:3], 1):
                report_lines.append(f"\n   Example {i}: {result['ad_name'][:60]}...")
                
                for field in ['category', 'product', 'color', 'content_type', 'handle', 'format']:
                    match_status = "✅" if result['matches'].get(field, False) else "❌"
                    analyst_val = result['analyst_data'].get(field, 'N/A')
                    parsed_val = result['parsed_data'].get(field, 'N/A')
                    
                    report_lines.append(f"     {match_status} {field}: '{analyst_val}' vs '{parsed_val}'")
        
        return "\n".join(report_lines)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on the analysis"""
        recommendations = []
        
        field_accuracy = self.report.get('field_accuracy', {})
        
        for field, accuracy in field_accuracy.items():
            if accuracy['accuracy_percent'] < 90:
                if field == 'launch_date':
                    recommendations.append(f"Improve date parsing - only {accuracy['accuracy_percent']}% accuracy")
                elif field == 'category':
                    recommendations.append(f"Review category detection patterns - {accuracy['accuracy_percent']}% accuracy")
                elif field == 'product':
                    recommendations.append(f"Expand product name recognition - {accuracy['accuracy_percent']}% accuracy")
                elif field == 'color':
                    recommendations.append(f"Add more color variations to color list - {accuracy['accuracy_percent']}% accuracy")
                elif field == 'content_type':
                    recommendations.append(f"Refine content type parsing logic - {accuracy['accuracy_percent']}% accuracy")
                elif field == 'handle':
                    recommendations.append(f"Update handle/creator recognition - {accuracy['accuracy_percent']}% accuracy")
                elif field == 'format':
                    recommendations.append(f"Improve format detection - {accuracy['accuracy_percent']}% accuracy")
        
        overall_accuracy = self.report['summary']['overall_accuracy_percent']
        if overall_accuracy < 85:
            recommendations.append("Consider implementing machine learning-based parsing for better accuracy")
        elif overall_accuracy > 95:
            recommendations.append("Parser performance is excellent! Consider this ready for production use")
        
        if not recommendations:
            recommendations.append("Parser performance looks good overall!")
        
        return recommendations
    
    def save_report(self, filename: str = None):
        """Save detailed report to files"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"parser_validation_report_{timestamp}"
        
        # Save text report
        text_report = self.generate_detailed_report()
        text_file = f"{filename}.txt"
        with open(text_file, 'w') as f:
            f.write(text_report)
        print(f"📄 Text report saved to: {text_file}")
        
        # Save JSON report
        json_file = f"{filename}.json"
        with open(json_file, 'w') as f:
            # Convert date objects to strings for JSON serialization
            json_report = self._serialize_report_for_json(self.report)
            json.dump(json_report, f, indent=2, default=str)
        print(f"📊 JSON report saved to: {json_file}")
        
        # Save CSV of discrepancies
        if self.report['discrepancies']:
            csv_file = f"{filename}_discrepancies.csv"
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['ad_name', 'field', 'analyst_value', 'parsed_value'])
                writer.writeheader()
                writer.writerows(self.report['discrepancies'])
            print(f"📋 Discrepancies CSV saved to: {csv_file}")
    
    def _serialize_report_for_json(self, obj):
        """Convert report object to JSON-serializable format"""
        if isinstance(obj, dict):
            return {key: self._serialize_report_for_json(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_report_for_json(item) for item in obj]
        elif isinstance(obj, date):
            return obj.isoformat()
        else:
            return obj

def main():
    """Main execution function"""
    
    print("🚀 Starting Meta Ads Parser Validation")
    print("=" * 60)
    
    # Check for CSV file argument
    csv_file = None
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        if not Path(csv_file).exists():
            print(f"❌ CSV file not found: {csv_file}")
            sys.exit(1)
    
    try:
        # Initialize validation report
        validator = ParserValidationReport()
        
        # Load analyst data
        analyst_data = validator.load_analyst_data(csv_file)
        
        # Fetch API data for the same period (if available)
        api_data = []
        if validator.meta_service:
            start_date = date(2025, 7, 28)
            end_date = date(2025, 8, 10)
            api_data = validator.fetch_meta_api_data(start_date, end_date)
        
        # Run comparison
        results = validator.compare_parsing_results(analyst_data, api_data)
        
        # Display results
        print(validator.generate_detailed_report())
        
        # Save detailed report
        validator.save_report()
        
        # Exit with appropriate code
        overall_accuracy = results['summary']['overall_accuracy_percent']
        if overall_accuracy >= 90:
            print(f"\n✅ VALIDATION PASSED: {overall_accuracy}% accuracy")
            sys.exit(0)
        elif overall_accuracy >= 80:
            print(f"\n⚠️  VALIDATION WARNING: {overall_accuracy}% accuracy (below 90%)")
            sys.exit(1)
        else:
            print(f"\n❌ VALIDATION FAILED: {overall_accuracy}% accuracy (below 80%)")
            sys.exit(2)
            
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()