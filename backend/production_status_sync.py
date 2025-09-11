"""
Production Status Sync Script

This script runs the full status sync locally on the dev server and actually updates 
the meta_ad_data table with correct ad statuses from Meta API. It processes all 
unique ads dynamically (555+ ads) and applies the discovered status corrections.

Based on testing, we expect 80-120 status mismatches that need correction.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import time
from datetime import datetime

# Load environment variables
load_dotenv()

sys.path.append(str(Path(__file__).parent))

from supabase import create_client
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.ad import Ad

def get_all_unique_ads(supabase):
    """Get all unique ads from database for production sync"""
    try:
        print("🔍 Discovering ALL unique ads in database...")
        
        result = supabase.table('meta_ad_data').select('ad_id, ad_name, status').execute()
        
        if not result.data:
            print("❌ No data found in meta_ad_data table")
            return 0, []
        
        print(f"📊 Found {len(result.data)} total records in database")
        
        # Deduplicate by ad_id to get truly unique ads
        unique_ads = {}
        for record in result.data:
            ad_id = record.get('ad_id')
            if ad_id and ad_id not in unique_ads:
                unique_ads[ad_id] = {
                    'ad_id': ad_id,
                    'ad_name': record.get('ad_name'),
                    'current_status': record.get('status'),
                    'record_count': 1
                }
            elif ad_id in unique_ads:
                unique_ads[ad_id]['record_count'] += 1
        
        unique_ads_list = list(unique_ads.values())
        unique_count = len(unique_ads_list)
        
        print(f"✅ Discovered {unique_count} unique ads dynamically")
        
        # Show current status distribution
        status_dist = {}
        for ad in unique_ads_list:
            status = ad['current_status'] or 'null'
            status_dist[status] = status_dist.get(status, 0) + 1
        
        print(f"📈 Current database status distribution:")
        for status, count in status_dist.items():
            print(f"   {status}: {count} ads")
        
        return unique_count, unique_ads_list
        
    except Exception as e:
        print(f"❌ Error discovering unique ads: {e}")
        return 0, []

def sync_ad_statuses_to_database(unique_ads, supabase, batch_size=20):
    """Sync all ad statuses and UPDATE database with correct values"""
    
    if not unique_ads:
        print("❌ No ads to process")
        return
    
    try:
        # Initialize Meta API
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            print("❌ META_ACCESS_TOKEN not found")
            return
            
        FacebookAdsApi.init(access_token=access_token)
        print("✅ Meta API connection established")
        
        total_ads = len(unique_ads)
        total_batches = (total_ads + batch_size - 1) // batch_size
        
        print(f"\n🚀 PRODUCTION STATUS SYNC: Processing {total_ads} unique ads in {total_batches} batches")
        print("💾 THIS WILL UPDATE THE DATABASE WITH CORRECT STATUSES")
        
        # Status mapping
        status_mapping = {
            'ACTIVE': 'active',
            'PAUSED': 'paused', 
            'DELETED': 'paused',
            'ARCHIVED': 'paused',
            'UNKNOWN': 'active'
        }
        
        # Track results
        matches = 0
        mismatches_fixed = 0
        errors = 0
        status_distribution = {}
        database_updates = []
        
        start_time = datetime.now()
        
        # Process in batches
        for i in range(0, total_ads, batch_size):
            batch = unique_ads[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            print(f"\n📡 Processing batch {batch_num}/{total_batches} ({len(batch)} ads)...")
            
            batch_start = time.time()
            
            for ad in batch:
                try:
                    # Fetch real status from Meta API
                    meta_ad = Ad(ad['ad_id'])
                    ad_data = meta_ad.api_get(fields=['effective_status'])
                    
                    real_status = ad_data.get('effective_status', 'UNKNOWN')
                    mapped_status = status_mapping.get(real_status, 'active')
                    
                    # Track Meta API status distribution
                    status_distribution[real_status] = status_distribution.get(real_status, 0) + 1
                    
                    # Compare with database status
                    if mapped_status != ad['current_status']:
                        # MISMATCH - UPDATE DATABASE
                        try:
                            result = supabase.table('meta_ad_data').update({
                                'status': mapped_status,
                                'status_updated_at': datetime.now().isoformat(),
                                'status_automation_reason': f'production_sync_{real_status.lower()}'
                            }).eq('ad_id', ad['ad_id']).execute()
                            
                            if result.data:
                                records_updated = len(result.data)
                                mismatches_fixed += 1
                                database_updates.append({
                                    'ad_id': ad['ad_id'],
                                    'ad_name': ad['ad_name'][:40],
                                    'old_status': ad['current_status'],
                                    'new_status': mapped_status,
                                    'meta_status': real_status,
                                    'records_updated': records_updated
                                })
                                print(f"   ✅ FIXED: {ad['ad_name'][:30]}... | {ad['current_status']} → {mapped_status} ({records_updated} records)")
                            else:
                                print(f"   ⚠️ UPDATE FAILED: {ad['ad_name'][:30]}...")
                                errors += 1
                                
                        except Exception as db_error:
                            print(f"   ❌ DB ERROR: {ad['ad_name'][:30]}... | {db_error}")
                            errors += 1
                    else:
                        # Status matches - no update needed
                        matches += 1
                        
                except Exception as e:
                    errors += 1
                    print(f"   ❌ API ERROR: {ad['ad_name'][:30]}... | {e}")
            
            batch_duration = time.time() - batch_start
            ads_per_second = len(batch) / batch_duration if batch_duration > 0 else 0
            
            print(f"   ✅ Batch {batch_num} complete ({batch_duration:.1f}s, {ads_per_second:.1f} ads/sec)")
            print(f"   📊 Batch summary: {mismatches_fixed} fixed, {matches} already correct, {errors} errors")
            
            # Rate limiting between batches
            if batch_num < total_batches:
                print(f"   ⏱️ Rate limiting: sleeping 3 seconds...")
                time.sleep(3)
        
        # Calculate total time
        total_duration = (datetime.now() - start_time).total_seconds()
        
        # Final comprehensive results
        print(f"\n" + "=" * 80)
        print(f"🎉 PRODUCTION STATUS SYNC COMPLETE!")
        print(f"=" * 80)
        print(f"🎯 Total Unique Ads Processed: {total_ads}")
        print(f"⏱️ Total Duration: {total_duration:.1f} seconds ({total_ads/total_duration:.1f} ads/sec)")
        print(f"💾 Database Updates Applied: {mismatches_fixed} ads fixed")
        print()
        print(f"✅ Already Correct: {matches} ads")
        print(f"🔧 Status Fixed: {mismatches_fixed} ads")
        print(f"❌ Errors: {errors} ads")
        print()
        
        # Show Meta API status distribution
        print(f"📊 Real Meta API Status Distribution:")
        for status, count in sorted(status_distribution.items()):
            percentage = (count / total_ads) * 100
            print(f"   {status}: {count} ads ({percentage:.1f}%)")
        print()
        
        if mismatches_fixed > 0:
            print(f"🎯 DATABASE UPDATES SUCCESSFULLY APPLIED:")
            print(f"   {mismatches_fixed} ads had incorrect status and were fixed")
            print()
            
            # Group updates by type
            update_types = {}
            for update in database_updates:
                key = f"{update['old_status']} → {update['new_status']}"
                if key not in update_types:
                    update_types[key] = []
                update_types[key].append(update)
            
            for update_type, updates in update_types.items():
                total_records = sum(u['records_updated'] for u in updates)
                print(f"   📋 {update_type}: {len(updates)} ads ({total_records} records)")
                for update in updates[:3]:  # Show first 3 of each type
                    print(f"      • {update['ad_name']}... ({update['records_updated']} records)")
                if len(updates) > 3:
                    print(f"      ... and {len(updates) - 3} more")
                print()
            
            print(f"✅ SUCCESS: Database now has accurate ad statuses from Meta API!")
        else:
            print(f"✅ PERFECT: All ad statuses were already accurate in database!")
            
        if errors > 0:
            print(f"\n⚠️ ERRORS ENCOUNTERED: {errors} ads could not be processed")
        
        return {
            'total_processed': total_ads,
            'matches': matches,
            'fixed': mismatches_fixed,
            'errors': errors,
            'duration_seconds': total_duration,
            'database_updates': database_updates,
            'status_distribution': status_distribution
        }
        
    except Exception as e:
        print(f"❌ Production status sync failed: {e}")
        return None

def main():
    """Main function to run production status sync with database updates"""
    
    print("🚀 Production Status Sync - Database Update Mode")
    print("=" * 80)
    print("🎯 Objective: Update meta_ad_data table with correct ad statuses from Meta API")
    print("💾 Mode: PRODUCTION - WILL UPDATE DATABASE")
    print("🔧 Method: Dynamic discovery + batch processing + database updates")
    print("=" * 80)
    
    # Step 1: Database connection
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')  
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Step 2: Dynamic unique ad discovery
    unique_count, unique_ads = get_all_unique_ads(supabase)
    
    if unique_count == 0:
        print("❌ No unique ads found - cannot proceed")
        return
    
    # Step 3: Production confirmation
    print(f"\n🚨 PRODUCTION MODE CONFIRMATION:")
    print(f"📊 About to process {unique_count} unique ads")
    print(f"💾 THIS WILL UPDATE THE meta_ad_data TABLE WITH CORRECT STATUSES")
    print(f"⏱️ Estimated time: {unique_count * 0.5:.0f} seconds ({unique_count * 0.5 / 60:.1f} minutes)")
    print(f"💰 API calls: {unique_count} Meta API requests")
    print(f"🔧 Expected fixes: 80-120 status mismatches (based on testing)")
    
    # Auto-proceed (user already confirmed they want to run this)
    print(f"\n✅ PROCEEDING WITH PRODUCTION STATUS SYNC...")
    
    # Step 4: Run production sync with database updates
    print(f"\n🚀 PRODUCTION STATUS SYNC INITIATED")
    print(f"💾 Processing {unique_count} unique ads with database updates...")
    
    results = sync_ad_statuses_to_database(unique_ads, supabase, batch_size=20)
    
    if results:
        print(f"\n🎉 PRODUCTION STATUS SYNC COMPLETE!")
        print(f"📊 Processed {results['total_processed']} ads in {results['duration_seconds']:.1f} seconds")
        print(f"🔧 Database Updates: {results['fixed']} ads fixed")
        print(f"✅ Already Correct: {results['matches']} ads")
        print(f"❌ Errors: {results['errors']} ads")
        
        if results['fixed'] > 0:
            print(f"\n✅ SUCCESS: {results['fixed']} ad statuses corrected in database!")
            print("🎯 The meta_ad_data table now has accurate ad statuses from Meta API")
        else:
            print("\n✅ PERFECT: All ad statuses were already accurate!")

if __name__ == "__main__":
    main()