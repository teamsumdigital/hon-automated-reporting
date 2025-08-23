#!/usr/bin/env python3
"""
Debug the Play Mat vs Playmat categorization issue
"""

import requests

def debug_categorization():
    backend_url = "http://localhost:8007"
    
    print("🔍 Debugging Play Mat vs Playmat Categorization")
    print("=" * 50)
    
    try:
        # Get ads with both categories
        response = requests.get(f"{backend_url}/api/meta-ad-reports/ad-data?categories=Play Mat,Playmat", timeout=10)
        data = response.json()
        ads = data.get('grouped_ads', [])
        
        if not ads:
            print("❌ No Play Mat or Playmat ads found")
            return False
        
        print(f"Found {len(ads)} Play Mat/Playmat ads")
        print("\nSample categorization (first 10 ads):")
        
        for i, ad in enumerate(ads[:10]):
            name_short = ad['ad_name'][:50] + ('...' if len(ad['ad_name']) > 50 else '')
            print(f"  {i+1:2d}. {ad['category']:10s} | ${ad['total_spend']:6.0f} | {name_short}")
        
        # Separate by category
        play_mat_ads = [ad for ad in ads if ad['category'] == 'Play Mat']
        playmat_ads = [ad for ad in ads if ad['category'] == 'Playmat']
        
        play_mat_spend = sum(ad['total_spend'] for ad in play_mat_ads)
        playmat_spend = sum(ad['total_spend'] for ad in playmat_ads)
        
        print(f"\n📊 Category Breakdown:")
        print(f"  Play Mat:  {len(play_mat_ads):3d} ads, ${play_mat_spend:7.0f} spend")
        print(f"  Playmat:   {len(playmat_ads):3d} ads, ${playmat_spend:7.0f} spend")
        print(f"  Total:     {len(ads):3d} ads, ${play_mat_spend + playmat_spend:7.0f} spend")
        
        # Find the highest spender in each category
        if play_mat_ads:
            top_play_mat = max(play_mat_ads, key=lambda x: x['total_spend'])
            print(f"\n🏆 Top 'Play Mat' spender: ${top_play_mat['total_spend']:,.0f}")
            print(f"    {top_play_mat['ad_name'][:70]}...")
        
        if playmat_ads:
            top_playmat = max(playmat_ads, key=lambda x: x['total_spend'])
            print(f"\n🏆 Top 'Playmat' spender: ${top_playmat['total_spend']:,.0f}")
            print(f"    {top_playmat['ad_name'][:70]}...")
        
        # This explains why high spenders disappear from "All Categories" - 
        # they're split between "Play Mat" and "Playmat"
        print(f"\n❓ Issue Analysis:")
        print(f"   - High-spending ads are split between 'Play Mat' and 'Playmat'")
        print(f"   - When viewing 'All Categories', user sees only some Play Mat ads")
        print(f"   - The missing ads are categorized as 'Playmat' instead")
        print(f"   - Need to consolidate all 'Playmat' -> 'Play Mats' for consistency")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    debug_categorization()