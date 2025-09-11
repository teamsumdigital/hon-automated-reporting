#!/usr/bin/env python3
"""
Upgrade existing thumbnail URLs from 64x64 to 400x400 without API calls
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def upgrade_existing_thumbnails():
    """Upgrade all existing thumbnail URLs from p64x64 to p400x400"""
    
    try:
        # Connect to Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials")
            return
            
        supabase = create_client(supabase_url, supabase_key)
        
        print("🔄 UPGRADING EXISTING THUMBNAILS FROM 64x64 TO 400x400")
        print("=" * 60)
        
        # Get all records with thumbnail URLs containing p64x64
        print("📋 Fetching thumbnails with p64x64...")
        response = supabase.table('meta_ad_data').select(
            'ad_id, thumbnail_url'
        ).like('thumbnail_url', '%p64x64%').execute()
        
        if not response.data:
            print("ℹ️ No thumbnails found with p64x64")
            return
            
        print(f"✅ Found {len(response.data)} thumbnails to upgrade")
        
        upgraded_count = 0
        failed_count = 0
        
        # Process in batches
        for record in response.data:
            ad_id = record['ad_id']
            original_url = record['thumbnail_url']
            
            # Upgrade URL using the same logic as our service
            upgraded_url = upgrade_thumbnail_url(original_url)
            
            if upgraded_url != original_url:
                try:
                    # Update the database
                    update_response = supabase.table('meta_ad_data').update({
                        'thumbnail_url': upgraded_url
                    }).eq('ad_id', ad_id).execute()
                    
                    if update_response.data:
                        upgraded_count += 1
                        print(f"✅ Upgraded ad {ad_id}: p64x64 → p400x400")
                    else:
                        failed_count += 1
                        print(f"❌ Failed to update ad {ad_id}")
                        
                except Exception as e:
                    failed_count += 1
                    print(f"❌ Error updating ad {ad_id}: {e}")
            else:
                print(f"⚠️ No upgrade needed for ad {ad_id}")
        
        print("\n" + "=" * 60)
        print("📊 UPGRADE SUMMARY:")
        print(f"✅ Successfully upgraded: {upgraded_count}")
        print(f"❌ Failed upgrades: {failed_count}")
        print(f"📝 Total processed: {len(response.data)}")
        
        if upgraded_count > 0:
            print("\n🎉 SUCCESS! Thumbnails upgraded to 400x400")
            print("💡 Check your dashboard - hover should now show larger images")
        else:
            print("\n⚠️ No thumbnails were upgraded")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def upgrade_thumbnail_url(original_url: str) -> str:
    """
    Upgrade a Facebook thumbnail URL from 64x64 to 400x400
    """
    upgraded_url = original_url
    
    # Method 1: Replace p64x64 with p400x400
    if 'p64x64' in original_url:
        upgraded_url = original_url.replace('p64x64', 'p400x400')
        print(f"🔧 URL upgrade: p64x64 → p400x400")
    
    # Method 2: Handle specific stp parameter pattern
    elif 'stp=c0.5000x0.5000f_dst-emg0_p64x64' in original_url:
        upgraded_url = original_url.replace(
            'stp=c0.5000x0.5000f_dst-emg0_p64x64', 
            'stp=c0.5000x0.5000f_dst-emg0_p400x400'
        )
        print(f"🔧 URL upgrade: stp parameter p64x64 → p400x400")
    
    return upgraded_url

if __name__ == "__main__":
    upgrade_existing_thumbnails()