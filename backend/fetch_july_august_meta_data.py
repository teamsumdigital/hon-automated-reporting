#!/usr/bin/env python3
"""
Script to fetch Meta Ads data for the exact date range July 28 - August 10, 2025
This matches the date range from the analyst's CSV data for direct comparison

Usage:
    python fetch_july_august_meta_data.py [--save-csv] [--test-parser]
    
Options:
    --save-csv      Save results to CSV file
    --test-parser   Test parser on each ad name and show results
"""

import sys
import os
import csv
import json
import argparse
from datetime import date, datetime
from typing import Dict, List, Any
from pathlib import Path

# Add the backend app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.meta_ad_level_service import MetaAdLevelService
from services.ad_name_parser import AdNameParser

def fetch_meta_data_for_comparison():
    """Fetch Meta Ads data for July 28 - August 10, 2025"""
    
    print("🔄 Fetching Meta Ads data for July 28 - August 10, 2025")
    print("=" * 60)
    
    # Define the exact date range from analyst data
    start_date = date(2025, 7, 28)
    end_date = date(2025, 8, 10)
    
    try:
        # Initialize Meta service
        meta_service = MetaAdLevelService()
        print("✅ Meta Ads API connection established")
        
        # Test connection first
        if not meta_service.test_connection():
            print("❌ Meta API connection test failed")
            return None
        
        # Fetch ad-level data
        print(f"\n📊 Fetching ad insights for {start_date} to {end_date}")
        ad_data = meta_service.get_ad_level_insights(start_date, end_date)
        
        print(f"✅ Retrieved {len(ad_data)} ad records")
        
        # Display summary
        if ad_data:
            total_spend = sum(float(ad.get('amount_spent_usd', 0)) for ad in ad_data)
            unique_campaigns = len(set(ad.get('campaign_name', '') for ad in ad_data))
            
            print(f"\n📈 Data Summary:")
            print(f"   Total Ads: {len(ad_data)}")
            print(f"   Unique Campaigns: {unique_campaigns}")
            print(f"   Total Spend: ${total_spend:,.2f}")
            print(f"   Date Range: {start_date} to {end_date}")
            
            # Show sample ad names
            print(f"\n📝 Sample Ad Names:")
            for i, ad in enumerate(ad_data[:5], 1):
                ad_name = ad.get('ad_name', 'N/A')
                spend = ad.get('amount_spent_usd', 0)
                print(f"   {i}. {ad_name[:80]}{'...' if len(ad_name) > 80 else ''}")
                print(f"      Spend: ${spend:.2f} | Campaign: {ad.get('campaign_name', 'N/A')}")
        
        return ad_data
        
    except Exception as e:
        print(f"❌ Error fetching Meta data: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_parser_on_meta_data(ad_data: List[Dict[str, Any]]):
    """Test our parser on each ad from Meta API"""
    
    print(f"\n🧪 Testing Ad Name Parser on {len(ad_data)} Meta API ads")
    print("=" * 60)
    
    parser = AdNameParser()
    
    # Track parsing success
    parsing_stats = {
        'total_ads': len(ad_data),
        'structured_format': 0,
        'fallback_parsing': 0,
        'dates_extracted': 0,
        'categories_found': 0,
        'products_found': 0,
        'colors_found': 0,
        'formats_found': 0
    }
    
    parsed_results = []
    
    for i, ad in enumerate(ad_data, 1):
        ad_name = ad.get('ad_name', '')
        campaign_name = ad.get('campaign_name', '')
        
        # Parse the ad name
        parsed = parser.parse_ad_name(ad_name, campaign_name)
        
        # Track what was successfully parsed
        if ' - ' in ad_name and len(ad_name.split(' - ')) >= 7:
            parsing_stats['structured_format'] += 1
        else:
            parsing_stats['fallback_parsing'] += 1
        
        if parsed.get('launch_date'):
            parsing_stats['dates_extracted'] += 1
        if parsed.get('category'):
            parsing_stats['categories_found'] += 1
        if parsed.get('product'):
            parsing_stats['products_found'] += 1
        if parsed.get('color'):
            parsing_stats['colors_found'] += 1
        if parsed.get('format'):
            parsing_stats['formats_found'] += 1
        
        # Store combined result
        combined_result = {
            'meta_data': ad,
            'parsed_data': parsed,
            'ad_name': ad_name,
            'campaign_name': campaign_name
        }
        parsed_results.append(combined_result)
        
        # Show detailed results for first few ads
        if i <= 3:
            print(f"\n📝 Ad {i}: {ad_name[:50]}{'...' if len(ad_name) > 50 else ''}")
            print(f"   Campaign: {campaign_name}")
            print(f"   Parsed Results:")
            print(f"     Launch Date: {parsed.get('launch_date', 'N/A')}")
            print(f"     Category: {parsed.get('category', 'N/A')}")
            print(f"     Product: {parsed.get('product', 'N/A')}")
            print(f"     Color: {parsed.get('color', 'N/A')}")
            print(f"     Content Type: {parsed.get('content_type', 'N/A')}")
            print(f"     Handle: {parsed.get('handle', 'N/A')}")
            print(f"     Format: {parsed.get('format', 'N/A')}")
            print(f"     Campaign Opt: {parsed.get('campaign_optimization', 'N/A')}")
    
    # Display parsing statistics
    print(f"\n📊 Parsing Statistics:")
    print(f"   Total Ads Processed: {parsing_stats['total_ads']}")
    print(f"   Structured Format: {parsing_stats['structured_format']} ({parsing_stats['structured_format']/parsing_stats['total_ads']*100:.1f}%)")
    print(f"   Fallback Parsing: {parsing_stats['fallback_parsing']} ({parsing_stats['fallback_parsing']/parsing_stats['total_ads']*100:.1f}%)")
    print(f"   Dates Extracted: {parsing_stats['dates_extracted']} ({parsing_stats['dates_extracted']/parsing_stats['total_ads']*100:.1f}%)")
    print(f"   Categories Found: {parsing_stats['categories_found']} ({parsing_stats['categories_found']/parsing_stats['total_ads']*100:.1f}%)")
    print(f"   Products Found: {parsing_stats['products_found']} ({parsing_stats['products_found']/parsing_stats['total_ads']*100:.1f}%)")
    print(f"   Colors Found: {parsing_stats['colors_found']} ({parsing_stats['colors_found']/parsing_stats['total_ads']*100:.1f}%)")
    print(f"   Formats Found: {parsing_stats['formats_found']} ({parsing_stats['formats_found']/parsing_stats['total_ads']*100:.1f}%)")
    
    return parsed_results, parsing_stats

def save_to_csv(ad_data: List[Dict[str, Any]], filename: str = None):
    """Save ad data to CSV file"""
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meta_ads_july_august_2025_{timestamp}.csv"
    
    if not ad_data:
        print("⚠️  No data to save")
        return
    
    # Define CSV columns based on the data structure
    columns = [
        'ad_id', 'ad_name', 'campaign_name', 'campaign_id',
        'reporting_starts', 'reporting_ends', 'launch_date', 'days_live',
        'category', 'product', 'color', 'content_type', 'handle', 'format',
        'campaign_optimization', 'amount_spent_usd', 'purchases', 
        'purchases_conversion_value', 'impressions', 'link_clicks', 'week_number'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        
        for ad in ad_data:
            # Ensure all columns exist with default values
            row = {}
            for col in columns:
                value = ad.get(col, '')
                # Convert date objects to strings
                if isinstance(value, date):
                    value = value.isoformat()
                row[col] = value
            writer.writerow(row)
    
    print(f"💾 Data saved to: {filename}")
    print(f"   Records: {len(ad_data)}")
    print(f"   Columns: {len(columns)}")

def save_parsed_results_to_csv(parsed_results: List[Dict[str, Any]], filename: str = None):
    """Save parsed results comparison to CSV"""
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meta_ads_parsed_comparison_{timestamp}.csv"
    
    if not parsed_results:
        print("⚠️  No parsed results to save")
        return
    
    # Define columns for comparison CSV
    columns = [
        # Meta API data
        'meta_ad_id', 'meta_ad_name', 'meta_campaign_name', 'meta_spend',
        'meta_reporting_start', 'meta_reporting_end',
        
        # Parser results
        'parsed_launch_date', 'parsed_days_live', 'parsed_category',
        'parsed_product', 'parsed_color', 'parsed_content_type',
        'parsed_handle', 'parsed_format', 'parsed_campaign_optimization',
        'parsed_ad_name_clean'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        
        for result in parsed_results:
            meta_data = result['meta_data']
            parsed_data = result['parsed_data']
            
            row = {
                # Meta API data
                'meta_ad_id': meta_data.get('ad_id', ''),
                'meta_ad_name': meta_data.get('ad_name', ''),
                'meta_campaign_name': meta_data.get('campaign_name', ''),
                'meta_spend': meta_data.get('amount_spent_usd', ''),
                'meta_reporting_start': meta_data.get('reporting_starts', ''),
                'meta_reporting_end': meta_data.get('reporting_ends', ''),
                
                # Parser results
                'parsed_launch_date': parsed_data.get('launch_date', ''),
                'parsed_days_live': parsed_data.get('days_live', ''),
                'parsed_category': parsed_data.get('category', ''),
                'parsed_product': parsed_data.get('product', ''),
                'parsed_color': parsed_data.get('color', ''),
                'parsed_content_type': parsed_data.get('content_type', ''),
                'parsed_handle': parsed_data.get('handle', ''),
                'parsed_format': parsed_data.get('format', ''),
                'parsed_campaign_optimization': parsed_data.get('campaign_optimization', ''),
                'parsed_ad_name_clean': parsed_data.get('ad_name_clean', '')
            }
            
            # Convert date objects to strings
            for key, value in row.items():
                if isinstance(value, date):
                    row[key] = value.isoformat()
            
            writer.writerow(row)
    
    print(f"💾 Parsed comparison saved to: {filename}")
    print(f"   Records: {len(parsed_results)}")

def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description='Fetch and analyze Meta Ads data for July 28 - August 10, 2025')
    parser.add_argument('--save-csv', action='store_true', help='Save results to CSV file')
    parser.add_argument('--test-parser', action='store_true', help='Test parser on each ad name')
    parser.add_argument('--output', type=str, help='Output filename prefix')
    
    args = parser.parse_args()
    
    print("🚀 Meta Ads Data Fetcher for July 28 - August 10, 2025")
    print("=" * 70)
    
    # Fetch Meta API data
    ad_data = fetch_meta_data_for_comparison()
    
    if ad_data is None:
        print("❌ Failed to fetch Meta API data")
        sys.exit(1)
    
    if not ad_data:
        print("⚠️  No ad data found for the specified date range")
        sys.exit(0)
    
    # Save raw data to CSV if requested
    if args.save_csv:
        output_prefix = args.output or "meta_ads_july_august_2025"
        save_to_csv(ad_data, f"{output_prefix}_raw.csv")
    
    # Test parser if requested
    parsed_results = None
    parsing_stats = None
    
    if args.test_parser:
        parsed_results, parsing_stats = test_parser_on_meta_data(ad_data)
        
        # Save parsed results comparison
        if args.save_csv and parsed_results:
            output_prefix = args.output or "meta_ads_july_august_2025"
            save_parsed_results_to_csv(parsed_results, f"{output_prefix}_parsed.csv")
    
    # Final summary
    print(f"\n{'='*70}")
    print("✅ Data fetch complete!")
    
    if parsing_stats:
        success_rate = (parsing_stats['categories_found'] + parsing_stats['products_found'] + 
                       parsing_stats['colors_found']) / (3 * parsing_stats['total_ads']) * 100
        print(f"🧪 Parser Success Rate: {success_rate:.1f}%")
    
    print(f"📊 Total Ads Retrieved: {len(ad_data)}")
    
    if args.save_csv:
        print("💾 CSV files have been saved for further analysis")
    
    print("\n💡 Next Steps:")
    print("   1. Compare with analyst CSV data using test_parser_vs_analyst_data.py")
    print("   2. Review any discrepancies in parsing logic")
    print("   3. Update parser rules based on real ad name patterns")

if __name__ == "__main__":
    main()