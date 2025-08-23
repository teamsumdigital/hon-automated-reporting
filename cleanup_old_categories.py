#!/usr/bin/env python3
"""
Clean up old category names in the Meta Ad Level database
Convert all legacy categories to standardized names
"""

import os
from supabase import create_client
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/.env')

def cleanup_old_categories():
    """Update all old category names to standardized format"""
    
    # Initialize Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not url or key:
        print("❌ Missing Supabase credentials")
        return False
    
    supabase = create_client(url, key)
    
    print("🧹 Cleaning up old category names in Meta Ad Level database")
    print("=" * 60)
    
    # Define the category mapping from old -> new
    category_mapping = {
        'Bath': 'Bath Mats',
        'Multi': 'Multi Category', 
        'Playmat': 'Play Mats',
        'Standing Mat': 'Standing Mats',
        'Tumbling Mat': 'Tumbling Mats'
    }
    
    try:
        # Get current category counts
        result = supabase.table('meta_ad_data').select('category').execute()
        
        if not result.data:
            print("❌ No data found in meta_ad_data table")
            return False
        
        # Count current categories
        category_counts = {}
        for record in result.data:
            cat = record.get('category', 'None')
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        print("📊 Current category distribution:")
        for cat, count in sorted(category_counts.items()):
            marker = "🔄" if cat in category_mapping else "✅" if cat in category_mapping.values() else "➡️"
            print(f"  {marker} {cat:15s}: {count:3d} records")
        
        # Update each old category to new format
        total_updated = 0
        
        for old_cat, new_cat in category_mapping.items():
            if old_cat in category_counts:
                print(f"\n🔄 Updating '{old_cat}' -> '{new_cat}'...")
                
                # Update all records with old category
                update_result = supabase.table('meta_ad_data')\
                    .update({'category': new_cat})\
                    .eq('category', old_cat)\
                    .execute()
                
                if update_result.data:
                    updated_count = len(update_result.data)
                    total_updated += updated_count
                    print(f"   ✅ Updated {updated_count} records")
                else:
                    print(f"   ⚠️ No records updated (may already be updated)")
        
        print(f"\n📈 Cleanup Summary:")
        print(f"   Total records updated: {total_updated}")
        
        if total_updated > 0:
            print(f"\n🎉 SUCCESS: Category cleanup completed!")
            print(f"📱 Meta Ad Level dashboard should now show only standardized categories")
            return True
        else:
            print(f"\n✅ No updates needed - categories already standardized")
            return True
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

def verify_cleanup():
    """Verify that cleanup was successful"""
    
    url = os.getenv("SUPABASE_URL") 
    key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(url, key)
    
    print(f"\n🔍 Verifying category cleanup...")
    
    try:
        # Get updated category counts
        result = supabase.table('meta_ad_data').select('category').execute()
        
        category_counts = {}
        for record in result.data:
            cat = record.get('category', 'None')
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        print("📊 Categories after cleanup:")
        
        # Expected standardized categories
        standard_categories = ['Bath Mats', 'Multi Category', 'Play Mats', 'Standing Mats', 'Tumbling Mats', 'Play Furniture']
        old_categories = ['Bath', 'Multi', 'Playmat', 'Standing Mat', 'Tumbling Mat']
        
        has_standard = False
        has_old = False
        
        for cat, count in sorted(category_counts.items()):
            if cat in standard_categories:
                print(f"  ✅ {cat:15s}: {count:3d} records (standardized)")
                has_standard = True
            elif cat in old_categories:
                print(f"  ❌ {cat:15s}: {count:3d} records (old format)")
                has_old = True
            else:
                print(f"  ➡️ {cat:15s}: {count:3d} records (other)")
        
        if has_standard and not has_old:
            print(f"\n🎉 VERIFICATION PASSED: Only standardized categories remain!")
            return True
        elif has_old:
            print(f"\n⚠️ Old categories still exist - may need additional cleanup")
            return False
        else:
            print(f"\n❓ No standard categories found - unexpected state")
            return False
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

if __name__ == "__main__":
    print("Category Cleanup for Meta Ad Level Dashboard")
    print("This will standardize all category names to match other dashboards\n")
    
    # Perform cleanup
    cleanup_success = cleanup_old_categories()
    
    if cleanup_success:
        # Verify results
        verify_success = verify_cleanup()
        
        if verify_success:
            print(f"\n" + "=" * 60)
            print("🎉 CLEANUP COMPLETED SUCCESSFULLY!")
            print("✅ Meta Ad Level dashboard now has clean, standardized categories")
            print("📱 Visit http://localhost:3007 → Meta Ad Level dashboard")
            print("🔧 Filter dropdown should now show only the standardized category names")
        else:
            print(f"\n" + "=" * 60)
            print("⚠️ Cleanup completed but verification found issues")
            print("🔧 May need manual database review")
    else:
        print(f"\n" + "=" * 60)
        print("❌ Cleanup failed - manual intervention may be required")