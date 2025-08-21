#!/usr/bin/env python3
"""
Insert properly segmented 14-day batch with correct weekly periods
Ensures 2 weeks (14 days) segmented by week (7 days each)
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

def create_proper_14_day_segmented_batch():
    """
    Create a batch with proper 14-day period segmented by week (7 days each)
    Week 1: Aug 5-11, 2024 (7 days)
    Week 2: Aug 12-18, 2024 (7 days)
    Total: 14 days
    """
    parser = AdNameParser()
    
    # Define the proper 14-day period with weekly segmentation
    week1_start = date(2024, 8, 5)   # Monday
    week1_end = date(2024, 8, 11)    # Sunday (7 days)
    week2_start = date(2024, 8, 12)  # Monday  
    week2_end = date(2024, 8, 18)    # Sunday (7 days)
    
    logger.info(f"📅 Creating 14-day segmented batch:")
    logger.info(f"   Week 1: {week1_start} to {week1_end} (7 days)")
    logger.info(f"   Week 2: {week2_start} to {week2_end} (7 days)")
    logger.info(f"   Total: 14 days")
    
    # Week 1 ads (Aug 5-11, 2024)
    week1_ads = [
        {
            'ad_id': 'week1_001',
            'original_ad_name': '7/9/2024 - Tumbling Mat - Folklore - Fog - Whitelist - BrookeKnuth - Video - Brooke.knuth Folklore Tumbling Mat Whitelist',
            'campaign_name': 'Tumbling Mat Incrementality Campaign',
            'reporting_starts': week1_start,
            'reporting_ends': week1_end,
            'amount_spent_usd': 1250.75,
            'purchases': 12,
            'purchases_conversion_value': 2987.50,
            'impressions': 45230,
            'link_clicks': 892
        },
        {
            'ad_id': 'week1_002', 
            'original_ad_name': '1/22/2024 - Bath - Darby - Darby - Brand - HoN - Static - Darby Bath Mats Launch Static V2',
            'campaign_name': 'Bath Static Campaign Incrementality',
            'reporting_starts': week1_start,
            'reporting_ends': week1_end,
            'amount_spent_usd': 892.30,
            'purchases': 8,
            'purchases_conversion_value': 1876.40,
            'impressions': 32140,
            'link_clicks': 654
        },
        {
            'ad_id': 'week1_003',
            'original_ad_name': '6/18/2024 - Standing Mat - Devon - Multi - Brand - HoN - Carousel - Standing Mat Launch Swatch Lifestyle Devon',
            'campaign_name': 'Standing Mat Carousel Standard',
            'reporting_starts': week1_start,
            'reporting_ends': week1_end,
            'amount_spent_usd': 743.60,
            'purchases': 6,
            'purchases_conversion_value': 1425.30,
            'impressions': 28750,
            'link_clicks': 521
        },
        {
            'ad_id': 'week1_004',
            'original_ad_name': '1/22/2024 - Bath - Darby - Darby - Brand - HoN - GIF - Darby Bath Mats Launch GIF',
            'campaign_name': 'Bath GIF Incrementality Campaign',
            'reporting_starts': week1_start,
            'reporting_ends': week1_end,
            'amount_spent_usd': 634.90,
            'purchases': 5,
            'purchases_conversion_value': 1287.75,
            'impressions': 23680,
            'link_clicks': 478
        },
        {
            'ad_id': 'week1_005',
            'original_ad_name': '6/25/2024 - Playmat - Emile - Laurel - Whitelist - Sabrina Molu - Video - Sabrina Molu Emile Laurel Play Mat Whitelist',
            'campaign_name': 'Playmat Standard Campaign',
            'reporting_starts': week1_start,
            'reporting_ends': week1_end,
            'amount_spent_usd': 567.20,
            'purchases': 7,
            'purchases_conversion_value': 1654.80,
            'impressions': 21340,
            'link_clicks': 423
        }
    ]
    
    # Week 2 ads (Aug 12-18, 2024)
    week2_ads = [
        {
            'ad_id': 'week2_001',
            'original_ad_name': '7/18/2024 - Play Furniture - Seat - Kit Ivory & Sky - Whitelist - Jessi Malay - Video - Jessi Malay Play Furniture Whitelist',
            'campaign_name': 'Complex Color Standard',
            'reporting_starts': week2_start,
            'reporting_ends': week2_end,
            'amount_spent_usd': 823.45,
            'purchases': 9,
            'purchases_conversion_value': 2145.60,
            'impressions': 35420,
            'link_clicks': 687
        },
        {
            'ad_id': 'week2_002',
            'original_ad_name': 'Standing Mats Dedicated Video Campaign Launch',
            'campaign_name': 'Standing Mat Brand Campaign',
            'reporting_starts': week2_start,
            'reporting_ends': week2_end,
            'amount_spent_usd': 456.80,
            'purchases': 4,
            'purchases_conversion_value': 987.20,
            'impressions': 18920,
            'link_clicks': 365
        },
        {
            'ad_id': 'week2_003',
            'original_ad_name': 'BIS Bath Mats Video Creative Test', 
            'campaign_name': 'Bath BIS Campaign',
            'reporting_starts': week2_start,
            'reporting_ends': week2_end,
            'amount_spent_usd': 678.95,
            'purchases': 6,
            'purchases_conversion_value': 1456.30,
            'impressions': 26540,
            'link_clicks': 512
        },
        {
            'ad_id': 'week2_004',
            'original_ad_name': '3/15/2024 - Play Mat - Aurora - Multi - Brand - HoN - Collection - Aurora Play Mat Collection Launch',
            'campaign_name': 'Play Mat Collection Incrementality',
            'reporting_starts': week2_start,
            'reporting_ends': week2_end,
            'amount_spent_usd': 945.30,
            'purchases': 11,
            'purchases_conversion_value': 2234.85,
            'impressions': 38650,
            'link_clicks': 756
        },
        {
            'ad_id': 'week2_005',
            'original_ad_name': '5/8/2024 - Tumbling Mat - Heritage - Stone - Whitelist - Sarah Chen - Image - Heritage Stone Tumbling Mat Static',
            'campaign_name': 'Tumbling Mat Standard Campaign',
            'reporting_starts': week2_start,
            'reporting_ends': week2_end,
            'amount_spent_usd': 712.40,
            'purchases': 8,
            'purchases_conversion_value': 1789.60,
            'impressions': 29340,
            'link_clicks': 589
        }
    ]
    
    # Combine all ads
    all_ads = week1_ads + week2_ads
    
    # Parse each ad and add the enhanced data with new field structure
    parsed_ads = []
    for ad in all_ads:
        # Parse the ad name with our enhanced parser
        parsed_data = parser.parse_ad_name(ad['original_ad_name'], ad['campaign_name'])
        
        # Determine week number for proper segmentation
        if ad['reporting_starts'] == week1_start:
            week_number = f"Week {week1_start.strftime('%m/%d')}-{week1_end.strftime('%m/%d')}"
        else:
            week_number = f"Week {week2_start.strftime('%m/%d')}-{week2_end.strftime('%m/%d')}"
        
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
            # 'week_number': week_number  # Column doesn't exist yet
        }
        parsed_ads.append(enhanced_ad)
        
        # Log the parsing results showing BOTH original and cleaned names
        logger.info(f"✅ {ad['ad_id']}: {ad['reporting_starts']} to {ad['reporting_ends']} ({(ad['reporting_ends'] - ad['reporting_starts']).days + 1} days)")
        logger.info(f"   Original: {enhanced_ad['in_platform_ad_name'][:50]}...")
        logger.info(f"   Cleaned:  {enhanced_ad['ad_name'][:50]}...")
        logger.info(f"   Category: {enhanced_ad['category']} | Product: {enhanced_ad['product']} | Format: {enhanced_ad['format']}")
        logger.info("   " + "-" * 60)
    
    return parsed_ads

def insert_proper_14_day_batch():
    """
    Insert properly segmented 14-day batch data
    """
    # Initialize Supabase client
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    
    supabase = create_client(supabase_url, supabase_key)
    
    logger.info("🎯 Creating properly segmented 14-day batch data...")
    
    # Create batch data with parsing
    batch_data = create_proper_14_day_segmented_batch()
    
    logger.info(f"📤 Inserting {len(batch_data)} properly segmented records into Supabase...")
    
    try:
        # Clear existing week-based batch data first
        logger.info("🧹 Clearing existing week-based batch data...")
        supabase.table('meta_ad_data').delete().like('ad_id', 'week%_%').execute()
        
        # Insert new batch data
        result = supabase.table('meta_ad_data').insert(batch_data).execute()
        
        if result.data:
            logger.info(f"✅ Successfully inserted {len(result.data)} properly segmented ad records")
            
            # Calculate statistics by week
            week1_data = [ad for ad in batch_data if ad['ad_id'].startswith('week1_')]
            week2_data = [ad for ad in batch_data if ad['ad_id'].startswith('week2_')]
            
            week1_spend = sum(ad['amount_spent_usd'] for ad in week1_data)
            week2_spend = sum(ad['amount_spent_usd'] for ad in week2_data)
            
            logger.info(f"📊 Properly Segmented 14-Day Data Summary:")
            logger.info(f"   📅 Week 1 (Aug 5-11): {len(week1_data)} ads, ${week1_spend:,.2f} spend")
            logger.info(f"   📅 Week 2 (Aug 12-18): {len(week2_data)} ads, ${week2_spend:,.2f} spend")
            logger.info(f"   📈 Total 14 days: {len(batch_data)} ads, ${week1_spend + week2_spend:,.2f} spend")
            
            # Show parsing accuracy and new field usage
            categories = set(ad['category'] for ad in batch_data if ad['category'])
            formats = set(ad['format'] for ad in batch_data if ad['format'])
            optimizations = set(ad['campaign_optimization'] for ad in batch_data)
            
            logger.info(f"🎨 Enhanced Parsing Results:")
            logger.info(f"   📂 Categories: {', '.join(sorted(categories))}")
            logger.info(f"   🎭 Formats: {', '.join(sorted(formats))}")
            logger.info(f"   ⚙️ Optimizations: {', '.join(sorted(optimizations))}")
            
            logger.info(f"✅ Date Range Validation:")
            logger.info(f"   📊 All Week 1 records: Aug 5-11 (7 days each)")
            logger.info(f"   📊 All Week 2 records: Aug 12-18 (7 days each)")
            logger.info(f"   📊 Total period: 14 days, properly segmented by week")
            
            return True
        else:
            logger.error("❌ Failed to insert batch data")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error inserting batch data: {e}")
        return False

def main():
    """
    Main function to insert properly segmented 14-day batch
    """
    logger.info("🚀 Inserting properly segmented 14-day batch with weekly segments")
    
    try:
        success = insert_proper_14_day_batch()
        
        if success:
            print("\n" + "=" * 80)
            print("🎉 PROPERLY SEGMENTED 14-DAY BATCH INSERTION COMPLETE")
            print("=" * 80)
            print("✅ Successfully inserted 10 ad records with proper weekly segmentation")
            print("📅 Date Structure:")
            print("   • Week 1: Aug 5-11, 2024 (7 days) - 5 ad records")
            print("   • Week 2: Aug 12-18, 2024 (7 days) - 5 ad records") 
            print("   • Total: 14 days, properly segmented by week")
            print("\n🎯 Field Structure:")
            print("   • Original platform ad names (in_platform_ad_name)")
            print("   • Cleaned/parsed ad names (ad_name)")
            print("   • Consistent 7-day weekly reporting periods")
            print("   • Proper 14-day total timeframe")
            print("\n📈 Now your data shows consistent weekly segments!")
            print("=" * 80)
        else:
            print("❌ Batch data insertion failed")
            
    except Exception as e:
        logger.error(f"Script failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()