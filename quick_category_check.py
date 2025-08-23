#!/usr/bin/env python3
"""
Quick category check for Meta Ad Level standardization
"""

import requests
import time

def quick_category_check():
    backend_url = "http://localhost:8007"
    
    print("🔍 Quick Category Standardization Check")
    print("=" * 45)
    
    max_attempts = 6
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{backend_url}/api/meta-ad-reports/filters", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                categories = sorted(data.get('categories', []))
                
                print(f"Attempt {attempt + 1}/{max_attempts} - Categories: {categories}")
                
                # Check for standardized names
                has_play_mats = 'Play Mats' in categories
                has_bath_mats = 'Bath Mats' in categories
                has_standing_mats = 'Standing Mats' in categories
                has_old_format = any(cat in ['Bath', 'Playmat', 'Multi'] for cat in categories)
                
                if has_play_mats and has_bath_mats and has_standing_mats and not has_old_format:
                    print("\n✅ SUCCESS: Categories fully standardized!")
                    print(f"📊 Standardized categories: {categories}")
                    return True
                elif has_play_mats or has_bath_mats:
                    print(f"⏳ Partial standardization in progress...")
                else:
                    print(f"❌ Still using old format: {categories}")
                
                if attempt < max_attempts - 1:
                    print("   Waiting 20 seconds...")
                    time.sleep(20)
                
            else:
                print(f"❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    success = quick_category_check()
    
    if success:
        print("\n🎉 Category standardization completed!")
        print("📱 Visit http://localhost:3007 → Meta Ad Level dashboard")
    else:
        print("\n⚠️ Category standardization may need more time or manual intervention")