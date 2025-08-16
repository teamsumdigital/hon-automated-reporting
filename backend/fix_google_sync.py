#!/usr/bin/env python3
"""
Direct database insertion workaround for Google Ads sync
Bypasses service layer to fix schema cache issue
"""

import os
import sys
from datetime import date
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables from parent directory
load_dotenv("../.env")

# Add the app directory to the path
sys.path.append('.')

print("🔧 Google Ads Direct Database Sync Fix")
print("=" * 50)

try:
    from app.services.google_ads_service import GoogleAdsService
    
    # Initialize direct Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(url, key)
    
    # Date range: August 1-11, 2025
    start_date = date(2025, 8, 1)
    end_date = date(2025, 8, 11)
    
    print(f"📅 Date range: {start_date} to {end_date}")
    
    # Initialize Google Ads service
    print("🚀 Initializing Google Ads service...")
    google_service = GoogleAdsService()
    
    # Test connection
    print("🔗 Testing Google Ads connection...")
    if not google_service.test_connection():
        print("❌ Connection failed")
        exit(1)
    
    print("✅ Connection successful")
    
    # Get insights
    print(f"📊 Fetching campaign insights...")
    insights = google_service.get_campaign_insights(start_date, end_date)
    print(f"✅ Retrieved {len(insights)} campaign insights")
    
    if insights:
        # Convert to campaign data
        print(f"🔄 Converting to campaign data...")
        campaign_data_list = google_service.convert_to_campaign_data(insights)
        print(f"✅ Converted {len(campaign_data_list)} campaigns")
        
        # Store directly in database (bypassing service layer)
        print(f"💾 Storing directly in database...")
        
        stored_count = 0
        errors = []
        
        for campaign_data in campaign_data_list:
            try:
                data = {
                    "campaign_id": campaign_data.campaign_id,
                    "campaign_name": campaign_data.campaign_name,
                    "category": campaign_data.category,
                    "reporting_starts": campaign_data.reporting_starts.isoformat(),
                    "reporting_ends": campaign_data.reporting_ends.isoformat(),
                    "amount_spent_usd": float(campaign_data.amount_spent_usd),
                    "website_purchases": campaign_data.website_purchases,
                    "purchases_conversion_value": float(campaign_data.purchases_conversion_value),
                    "impressions": campaign_data.impressions,
                    "link_clicks": campaign_data.link_clicks,
                    "cpa": float(campaign_data.cpa),
                    "roas": float(campaign_data.roas),
                    "cpc": float(campaign_data.cpc)
                }
                
                # Use direct insert (not upsert to avoid constraint issues)
                result = supabase.table("google_campaign_data").insert(data).execute()
                stored_count += 1
                
                if stored_count % 20 == 0:
                    print(f"   📊 Stored {stored_count}/{len(campaign_data_list)} campaigns...")
                    
            except Exception as e:
                error_msg = f"Campaign {campaign_data.campaign_name}: {str(e)}"
                errors.append(error_msg)
                if "duplicate key value" in str(e):
                    # If duplicate, try upsert instead
                    try:
                        result = supabase.table("google_campaign_data").upsert(data).execute()
                        stored_count += 1
                    except Exception as upsert_error:
                        errors.append(f"Upsert failed for {campaign_data.campaign_name}: {str(upsert_error)}")
        
        print(f"✅ Successfully stored {stored_count} campaigns!")
        
        if errors:
            print(f"⚠️  {len(errors)} errors occurred:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"   - {error}")
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more errors")
        
        # Show sample data from database
        print(f"\n📊 Verifying stored data...")
        result = supabase.table("google_campaign_data").select("*").limit(3).execute()
        
        if result.data:
            print(f"   Found {len(result.data)} sample records:")
            for record in result.data:
                print(f"   - {record['campaign_name']} ({record['category']}) - ${record['amount_spent_usd']}")
        else:
            print("   ❌ No data found in database")
            
    else:
        print("⚠️ No campaign data found for this period")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🏁 Direct sync complete!")
print("🎯 Visit http://localhost:3007/dashboard to see your data")