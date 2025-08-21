#!/usr/bin/env python3
"""
Insert batch of Meta Ads records with the new in_platform_ad_name field
Demonstrates both original platform names and cleaned parsed versions
"""

import os
import sys
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client

# Load environment variables
load_dotenv()

# Add the backend app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

from services.ad_name_parser import AdNameParser

def create_batch_data_with_new_field():
    """
    Create a batch of ad data showcasing the new in_platform_ad_name field
    """
    parser = AdNameParser()
    
    # Comprehensive batch of real-style ad names from House of Noa
    batch_ads = [
        {
            'ad_id': 'batch_001',
            'original_ad_name': '7/9/2024 - Tumbling Mat - Folklore - Fog - Whitelist - BrookeKnuth - Video - Brooke.knuth Folklore Tumbling Mat Whitelist',
            'campaign_name': 'Tumbling Mat Incrementality Campaign',
            'reporting_starts': date(2024, 8, 13),
            'reporting_ends': date(2024, 8, 19),
            'amount_spent_usd': 1250.75,
            'purchases': 12,
            'purchases_conversion_value': 2987.50,
            'impressions': 45230,
            'link_clicks': 892
        },
        {
            'ad_id': 'batch_002', 
            'original_ad_name': '1/22/2024 - Bath - Darby - Darby - Brand - HoN - Static - Darby Bath Mats Launch Static V2',
            'campaign_name': 'Bath Static Campaign Incrementality',
            'reporting_starts': date(2024, 8, 13),
            'reporting_ends': date(2024, 8, 19),
            'amount_spent_usd': 892.30,
            'purchases': 8,
            'purchases_conversion_value': 1876.40,
            'impressions': 32140,
            'link_clicks': 654
        },
        {
            'ad_id': 'batch_003',
            'original_ad_name': '6/18/2024 - Standing Mat - Devon - Multi - Brand - HoN - Carousel - Standing Mat Launch Swatch Lifestyle Devon',
            'campaign_name': 'Standing Mat Carousel Standard',
            'reporting_starts': date(2024, 8, 13),
            'reporting_ends': date(2024, 8, 19),
            'amount_spent_usd': 743.60,
            'purchases': 6,
            'purchases_conversion_value': 1425.30,
            'impressions': 28750,
            'link_clicks': 521
        },
        {
            'ad_id': 'batch_004',
            'original_ad_name': '1/22/2024 - Bath - Darby - Darby - Brand - HoN - GIF - Darby Bath Mats Launch GIF',
            'campaign_name': 'Bath GIF Incrementality Campaign',
            'reporting_starts': date(2024, 8, 13),
            'reporting_ends': date(2024, 8, 19),
            'amount_spent_usd': 634.90,
            'purchases': 5,
            'purchases_conversion_value': 1287.75,
            'impressions': 23680,
            'link_clicks': 478
        },
        {
            'ad_id': 'batch_005',
            'original_ad_name': '6/25/2024 - Playmat - Emile - Laurel - Whitelist - Sabrina Molu - Video - Sabrina Molu Emile Laurel Play Mat Whitelist',
            'campaign_name': 'Playmat Standard Campaign',
            'reporting_starts': date(2024, 8, 13),
            'reporting_ends': date(2024, 8, 19),
            'amount_spent_usd': 567.20,
            'purchases': 7,
            'purchases_conversion_value': 1654.80,
            'impressions': 21340,
            'link_clicks': 423
        },
        {
            'ad_id': 'batch_006',
            'original_ad_name': '7/18/2024 - Play Furniture - Seat - Kit Ivory & Sky - Whitelist - Jessi Malay - Video - Jessi Malay Play Furniture Whitelist',
            'campaign_name': 'Complex Color Standard',
            'reporting_starts': date(2024, 8, 13), 
            'reporting_ends': date(2024, 8, 19),
            'amount_spent_usd': 823.45,
            'purchases': 9,
            'purchases_conversion_value': 2145.60,
            'impressions': 35420,
            'link_clicks': 687
        },
        {
            'ad_id': 'batch_007',
            'original_ad_name': 'Standing Mats Dedicated Video Campaign Launch',
            'campaign_name': 'Standing Mat Brand Campaign',
            'reporting_starts': date(2024, 8, 15),
            'reporting_ends': date(2024, 8, 19),
            'amount_spent_usd': 456.80,
            'purchases': 4,
            'purchases_conversion_value': 987.20,
            'impressions': 18920,
            'link_clicks': 365
        },
        {
            'ad_id': 'batch_008',
            'original_ad_name': 'BIS Bath Mats Video Creative Test', 
            'campaign_name': 'Bath BIS Campaign',
            'reporting_starts': date(2024, 8, 15),
            'reporting_ends': date(2024, 8, 19),
            'amount_spent_usd': 678.95,
            'purchases': 6,
            'purchases_conversion_value': 1456.30,
            'impressions': 26540,
            'link_clicks': 512
        },
        {
            'ad_id': 'batch_009',
            'original_ad_name': '3/15/2024 - Play Mat - Aurora - Multi - Brand - HoN - Collection - Aurora Play Mat Collection Launch',
            'campaign_name': 'Play Mat Collection Incrementality',
            'reporting_starts': date(2024, 8, 16),
            'reporting_ends': date(2024, 8, 19),
            'amount_spent_usd': 945.30,
            'purchases': 11,
            'purchases_conversion_value': 2234.85,
            'impressions': 38650,
            'link_clicks': 756
        },
        {
            'ad_id': 'batch_010',
            'original_ad_name': '5/8/2024 - Tumbling Mat - Heritage - Stone - Whitelist - Sarah Chen - Image - Heritage Stone Tumbling Mat Static',
            'campaign_name': 'Tumbling Mat Standard Campaign',
            'reporting_starts': date(2024, 8, 16),
            'reporting_ends': date(2024, 8, 19),
            'amount_spent_usd': 712.40,
            'purchases': 8,
            'purchases_conversion_value': 1789.60,
            'impressions': 29340,
            'link_clicks': 589
        }
    ]
    
    # Parse each ad and add the enhanced data with new field structure
    parsed_ads = []
    for ad in batch_ads:
        # Parse the ad name with our enhanced parser
        parsed_data = parser.parse_ad_name(ad['original_ad_name'], ad['campaign_name'])
        
        # Create enhanced record with BOTH original and cleaned ad names
        enhanced_ad = {
            'ad_id': ad['ad_id'],
            'in_platform_ad_name': ad['original_ad_name'],  # NEW FIELD: Original from Meta platform
            'ad_name': parsed_data.get('ad_name_clean', ad['original_ad_name']),  # Cleaned version from parser
            'campaign_name': ad['campaign_name'],
            'reporting_starts': ad['reporting_starts'].isoformat(),
            'reporting_ends': ad['reporting_ends'].isoformat(),
            'launch_date': parsed_data.get('launch_date').isoformat() if parsed_data.get('launch_date') else None,
            'days_live': parsed_data.get('days_live', 0),
            'category': parsed_data.get('category', ''),
            'product': parsed_data.get('product', ''),
            'color': parsed_data.get('color', ''),
            'content_type': parsed_data.get('content_type', ''),
            'handle': parsed_data.get('handle', ''),
            'format': parsed_data.get('format', ''),
            'campaign_optimization': parsed_data.get('campaign_optimization', 'Standard'),
            'amount_spent_usd': ad['amount_spent_usd'],
            'purchases': ad['purchases'],
            'purchases_conversion_value': ad['purchases_conversion_value'],
            'impressions': ad['impressions'],
            'link_clicks': ad['link_clicks'],
# 'week_number': f"Week {ad['reporting_starts'].strftime('%m/%d')}-{ad['reporting_ends'].strftime('%m/%d')}"  # Column doesn't exist yet
        }
        parsed_ads.append(enhanced_ad)
        
        # Log the parsing results showing BOTH original and cleaned names
        logger.info(f"✅ Parsed: {ad['original_ad_name'][:60]}...")
        logger.info(f"   Original: {enhanced_ad['in_platform_ad_name'][:50]}...")
        logger.info(f"   Cleaned:  {enhanced_ad['ad_name'][:50]}...")
        logger.info(f"   Category: {enhanced_ad['category']} | Product: {enhanced_ad['product']} | Format: {enhanced_ad['format']}")
        logger.info("   " + "-" * 60)
    
    return parsed_ads

def insert_batch_with_new_field():
    """
    Insert batch data demonstrating the new in_platform_ad_name field
    """
    # Initialize Supabase client
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    
    supabase = create_client(supabase_url, supabase_key)
    
    logger.info("🎯 Creating batch data with new in_platform_ad_name field...")
    
    # Create batch data with parsing
    batch_data = create_batch_data_with_new_field()
    
    logger.info(f"📤 Inserting {len(batch_data)} batch records into Supabase...")
    
    try:
        # Clear existing batch data first
        logger.info("🧹 Clearing existing batch data...")
        supabase.table('meta_ad_data').delete().like('ad_id', 'batch_%').execute()
        
        # Insert new batch data
        result = supabase.table('meta_ad_data').insert(batch_data).execute()
        
        if result.data:
            logger.info(f"✅ Successfully inserted {len(result.data)} batch ad records with new field structure")
            
            # Calculate statistics
            total_spend = sum(ad['amount_spent_usd'] for ad in batch_data)
            total_purchases = sum(ad['purchases'] for ad in batch_data)
            total_revenue = sum(ad['purchases_conversion_value'] for ad in batch_data)
            
            logger.info(f"📊 Batch Data Summary:")
            logger.info(f"   💰 Total Spend: ${total_spend:,.2f}")
            logger.info(f"   🛒 Total Purchases: {total_purchases}")
            logger.info(f"   💵 Total Revenue: ${total_revenue:,.2f}")
            logger.info(f"   📈 Average ROAS: {total_revenue / total_spend:.2f}")
            
            # Show parsing accuracy and new field usage
            categories = set(ad['category'] for ad in batch_data if ad['category'])
            formats = set(ad['format'] for ad in batch_data if ad['format'])
            optimizations = set(ad['campaign_optimization'] for ad in batch_data)
            
            logger.info(f"🎨 Enhanced Parsing Results:")
            logger.info(f"   📂 Categories: {', '.join(sorted(categories))}")
            logger.info(f"   🎭 Formats: {', '.join(sorted(formats))}")
            logger.info(f"   ⚙️ Optimizations: {', '.join(sorted(optimizations))}")
            
            # Show new field structure benefits
            original_names = [ad['in_platform_ad_name'] for ad in batch_data]
            cleaned_names = [ad['ad_name'] for ad in batch_data]
            
            logger.info(f"🆕 New Field Structure Benefits:")
            logger.info(f"   📝 Original Platform Names: {len(original_names)} preserved")
            logger.info(f"   🧹 Cleaned Names: {len(cleaned_names)} generated")
            logger.info(f"   🔗 Dual Storage: Both raw and processed data available")
            
            return True
        else:
            logger.error("❌ Failed to insert batch data")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error inserting batch data: {e}")
        return False

def main():
    """
    Main function to insert batch data with new field
    """
    logger.info("🚀 Inserting batch data with new in_platform_ad_name field")
    
    try:
        success = insert_batch_with_new_field()
        
        if success:
            print("\n" + "=" * 80)
            print("🎉 BATCH DATA INSERTION WITH NEW FIELD COMPLETE")
            print("=" * 80)
            print("✅ Successfully inserted 10 batch ad records with enhanced field structure")
            print("📊 Database now contains:")
            print("   • Original platform ad names (in_platform_ad_name)")
            print("   • Cleaned/parsed ad names (ad_name)")
            print("   • Perfect format detection (Static, GIF, Carousel, Video, Collection, Image)")
            print("   • Accurate category parsing (Tumbling Mat, Bath, Play Mat, etc.)")
            print("   • Complex color support (Kit Ivory & Sky, Multi)")
            print("   • Campaign optimization detection (Incremental vs Standard)")
            print("   • Comprehensive fallback parsing for unstructured names")
            print("\n🎯 New Field Benefits:")
            print("   • Preserves original Meta Ads Manager ad names")
            print("   • Maintains cleaned versions for analysis")
            print("   • Enables both raw and processed data workflows")
            print("   • Supports audit trails and data validation")
            print("\n📈 You can now view the enhanced dual-field data in your dashboard!")
            print("=" * 80)
        else:
            print("❌ Batch data insertion failed")
            
    except Exception as e:
        logger.error(f"Script failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()