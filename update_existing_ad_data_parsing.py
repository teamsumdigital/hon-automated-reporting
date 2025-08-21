#!/usr/bin/env python3
"""
Database update script to apply new advanced ad name parsing to existing records
This script will re-parse all existing ad records in the meta_ad_data table
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Add the backend app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

from services.ad_name_parser import AdNameParser
from loguru import logger

# Import database connection
from supabase import create_client, Client

class AdDataUpdater:
    """
    Updates existing ad data records with new parsing logic
    """
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.supabase_url or not self.supabase_service_key:
            raise ValueError("Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables.")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_service_key)
        self.parser = AdNameParser()
        
        logger.info("Initialized Ad Data Updater with advanced parsing")
    
    def get_all_ad_records(self) -> List[Dict[str, Any]]:
        """
        Fetch all existing ad records from the database
        """
        try:
            response = self.supabase.table('meta_ad_data').select('*').execute()
            
            if hasattr(response, 'data') and response.data:
                logger.info(f"Retrieved {len(response.data)} existing ad records")
                return response.data
            else:
                logger.warning("No ad records found in database")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching ad records: {e}")
            raise
    
    def reparse_ad_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Re-parse a single ad record using the new parser
        """
        try:
            # Get the original ad name and campaign name
            # Note: We need to reconstruct the original ad name if it was cleaned
            original_ad_name = record.get('ad_name', '')
            campaign_name = record.get('campaign_name', '')
            
            # Parse using the new advanced parser
            parsed_data = self.parser.parse_ad_name(original_ad_name, campaign_name)
            
            # Create update data with only the fields that might have changed
            update_data = {
                'launch_date': parsed_data.get('launch_date'),
                'days_live': parsed_data.get('days_live', 0),
                'category': parsed_data.get('category', ''),
                'product': parsed_data.get('product', ''),
                'color': parsed_data.get('color', ''),
                'content_type': parsed_data.get('content_type', ''),
                'handle': parsed_data.get('handle', ''),
                'format': parsed_data.get('format', ''),
                'campaign_optimization': parsed_data.get('campaign_optimization', 'Standard'),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Only update the ad_name if we have a cleaned version
            if parsed_data.get('ad_name_clean') and parsed_data.get('ad_name_clean') != original_ad_name:
                update_data['ad_name'] = parsed_data.get('ad_name_clean')
            
            return update_data
            
        except Exception as e:
            logger.error(f"Error parsing ad record {record.get('ad_id', 'unknown')}: {e}")
            raise
    
    def update_record_in_database(self, record_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update a single record in the database
        """
        try:
            # Remove None values to avoid overwriting valid data with null
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            
            response = self.supabase.table('meta_ad_data').update(clean_update_data).eq('ad_id', record_id).execute()
            
            if hasattr(response, 'data') and response.data:
                logger.debug(f"Successfully updated record {record_id}")
                return True
            else:
                logger.warning(f"No data returned when updating record {record_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating record {record_id}: {e}")
            return False
    
    def update_all_records(self, dry_run: bool = True) -> Dict[str, int]:
        """
        Update all ad records with new parsing logic
        """
        stats = {
            'total_records': 0,
            'successfully_updated': 0,
            'failed_updates': 0,
            'skipped_records': 0
        }
        
        try:
            # Get all records
            all_records = self.get_all_ad_records()
            stats['total_records'] = len(all_records)
            
            if not all_records:
                logger.warning("No records to update")
                return stats
            
            logger.info(f"Starting update of {len(all_records)} records (dry_run={dry_run})")
            
            for i, record in enumerate(all_records, 1):
                try:
                    ad_id = record.get('ad_id', f'record_{i}')
                    original_ad_name = record.get('ad_name', '')
                    
                    logger.info(f"Processing {i}/{len(all_records)}: {ad_id} - {original_ad_name[:50]}...")
                    
                    # Re-parse the record
                    update_data = self.reparse_ad_record(record)
                    
                    # Show what would be updated
                    logger.info(f"  Parsed data: category={update_data.get('category')}, "
                              f"product={update_data.get('product')}, "
                              f"color={update_data.get('color')}, "
                              f"content_type={update_data.get('content_type')}, "
                              f"handle={update_data.get('handle')}, "
                              f"format={update_data.get('format')}, "
                              f"campaign_optimization={update_data.get('campaign_optimization')}")
                    
                    if dry_run:
                        logger.info(f"  DRY RUN: Would update record {ad_id}")
                        stats['successfully_updated'] += 1
                    else:
                        # Actually update the record
                        if self.update_record_in_database(ad_id, update_data):
                            stats['successfully_updated'] += 1
                        else:
                            stats['failed_updates'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing record {i}: {e}")
                    stats['failed_updates'] += 1
                    continue
            
            # Log final statistics
            logger.info(f"\n{'='*60}")
            logger.info(f"Update Summary (dry_run={dry_run}):")
            logger.info(f"  Total records: {stats['total_records']}")
            logger.info(f"  Successfully updated: {stats['successfully_updated']}")
            logger.info(f"  Failed updates: {stats['failed_updates']}")
            logger.info(f"  Skipped records: {stats['skipped_records']}")
            logger.info(f"{'='*60}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error during bulk update: {e}")
            raise
    
    def preview_parsing_changes(self, limit: int = 10) -> None:
        """
        Preview how the parsing would change existing records
        """
        logger.info(f"Previewing parsing changes for first {limit} records")
        
        all_records = self.get_all_ad_records()
        
        for i, record in enumerate(all_records[:limit], 1):
            ad_id = record.get('ad_id', f'record_{i}')
            original_ad_name = record.get('ad_name', '')
            campaign_name = record.get('campaign_name', '')
            
            print(f"\n{'-'*60}")
            print(f"Record {i}: {ad_id}")
            print(f"Original ad name: {original_ad_name}")
            print(f"Campaign name: {campaign_name}")
            
            # Show current values
            print(f"\nCurrent values:")
            print(f"  Category: {record.get('category', 'N/A')}")
            print(f"  Product: {record.get('product', 'N/A')}")
            print(f"  Color: {record.get('color', 'N/A')}")
            print(f"  Content Type: {record.get('content_type', 'N/A')}")
            print(f"  Handle: {record.get('handle', 'N/A')}")
            print(f"  Format: {record.get('format', 'N/A')}")
            print(f"  Campaign Optimization: {record.get('campaign_optimization', 'N/A')}")
            
            # Parse with new logic
            parsed_data = self.parser.parse_ad_name(original_ad_name, campaign_name)
            
            print(f"\nNew parsed values:")
            print(f"  Category: {parsed_data.get('category', 'N/A')}")
            print(f"  Product: {parsed_data.get('product', 'N/A')}")
            print(f"  Color: {parsed_data.get('color', 'N/A')}")
            print(f"  Content Type: {parsed_data.get('content_type', 'N/A')}")
            print(f"  Handle: {parsed_data.get('handle', 'N/A')}")
            print(f"  Format: {parsed_data.get('format', 'N/A')}")
            print(f"  Campaign Optimization: {parsed_data.get('campaign_optimization', 'Standard')}")
            print(f"  Launch Date: {parsed_data.get('launch_date', 'N/A')}")
            print(f"  Days Live: {parsed_data.get('days_live', 'N/A')}")

def main():
    """
    Main function to run the ad data update script
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Update existing ad data with new parsing logic')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Run in dry-run mode (default: True)')
    parser.add_argument('--execute', action='store_true', default=False,
                       help='Actually execute the updates (overrides dry-run)')
    parser.add_argument('--preview', action='store_true', default=False,
                       help='Preview parsing changes for first 10 records')
    parser.add_argument('--preview-limit', type=int, default=10,
                       help='Number of records to preview (default: 10)')
    
    args = parser.parse_args()
    
    # Determine if this is a dry run
    dry_run = not args.execute
    
    try:
        updater = AdDataUpdater()
        
        if args.preview:
            updater.preview_parsing_changes(args.preview_limit)
        else:
            stats = updater.update_all_records(dry_run=dry_run)
            
            if dry_run:
                print(f"\n🔍 DRY RUN COMPLETED")
                print(f"To actually execute the updates, run:")
                print(f"python3 {sys.argv[0]} --execute")
            else:
                print(f"\n✅ UPDATE COMPLETED")
                print(f"Updated {stats['successfully_updated']} out of {stats['total_records']} records")
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()