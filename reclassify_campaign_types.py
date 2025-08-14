#!/usr/bin/env python3
"""Reclassify all campaign types with the corrected logic"""

import os
from dotenv import load_dotenv
from backend.app.services.campaign_type_service import CampaignTypeService
from supabase import create_client

load_dotenv()

def reclassify_all_campaigns():
    """Reclassify all campaigns to fix the Brand/Non-Brand classification issue"""
    
    print("🔄 Reclassifying Campaign Types...")
    print("=" * 50)
    
    # Create service instances
    campaign_type_service = CampaignTypeService()
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
    
    # Get all campaigns
    result = supabase.table("google_campaign_data").select("id, campaign_name, campaign_type").execute()
    
    print(f"📊 Found {len(result.data)} campaigns to reclassify")
    
    # Track classification changes
    changes = {
        'Brand': 0,
        'Non-Brand': 0, 
        'YouTube': 0,
        'Unclassified': 0
    }
    
    # Reclassify each campaign
    for i, campaign in enumerate(result.data, 1):
        old_type = campaign['campaign_type']
        new_type = campaign_type_service.classify_campaign_type(campaign['campaign_name'])
        
        # Update the campaign type
        update_result = supabase.table("google_campaign_data").update({
            "campaign_type": new_type
        }).eq("id", campaign['id']).execute()
        
        if new_type != old_type:
            print(f"{i:3d}. {campaign['campaign_name'][:50]:50s} | {old_type:15s} -> {new_type:15s}")
        
        changes[new_type] = changes.get(new_type, 0) + 1
        
        if i % 50 == 0:
            print(f"    ... processed {i}/{len(result.data)} campaigns")
    
    print("\n✅ Reclassification Complete!")
    print("📈 New Distribution:")
    for ctype, count in sorted(changes.items(), key=lambda x: x[1], reverse=True):
        print(f"   {ctype:15s}: {count:3d} campaigns")
    
    print(f"\n🎯 Total: {sum(changes.values())} campaigns")

if __name__ == "__main__":
    reclassify_all_campaigns()