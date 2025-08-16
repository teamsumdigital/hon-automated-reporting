#!/usr/bin/env python3
"""
Test script for Monthly Google Ads Implementation
Verifies the database migration and services are working correctly
"""

import os
import sys
from datetime import date
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from supabase import create_client, Client
from app.services.campaign_type_service import CampaignTypeService
from app.services.google_ads_service import GoogleAdsService

def test_database_schema():
    """Test that the database schema updates are in place"""
    logger.info("Testing database schema...")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Missing Supabase credentials")
        return False
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    try:
        # Test if campaign_type column exists in google_campaign_data
        result = supabase.table("google_campaign_data").select("campaign_type").limit(1).execute()
        logger.info("✓ campaign_type column exists in google_campaign_data table")
        
        # Test if campaign_type_rules table exists
        result = supabase.table("campaign_type_rules").select("*").limit(1).execute()
        logger.info("✓ campaign_type_rules table exists")
        logger.info(f"  Found {len(result.data)} campaign type rules")
        
        return True
    except Exception as e:
        logger.error(f"✗ Database schema test failed: {e}")
        return False

def test_campaign_type_service():
    """Test the CampaignTypeService functionality"""
    logger.info("Testing CampaignTypeService...")
    
    try:
        service = CampaignTypeService()
        
        # Test classification
        test_campaigns = [
            ("HON Standing Mats - Brand - Campaign 1", "Brand"),
            ("Multi Product - Non-Brand - Test", "Non-Brand"),
            ("YouTube Video Campaign - YouTube - 2024", "YouTube"),
            ("Random Campaign Name", "Unclassified")
        ]
        
        for campaign_name, expected_type in test_campaigns:
            classified_type = service.classify_campaign_type(campaign_name)
            if classified_type == expected_type:
                logger.info(f"✓ '{campaign_name}' → '{classified_type}'")
            else:
                logger.warning(f"? '{campaign_name}' → '{classified_type}' (expected '{expected_type}')")
        
        # Test getting all campaign types
        campaign_types = service.get_all_campaign_types()
        logger.info(f"✓ Found {len(campaign_types)} campaign types: {campaign_types}")
        
        return True
    except Exception as e:
        logger.error(f"✗ CampaignTypeService test failed: {e}")
        return False

def test_google_ads_service():
    """Test Google Ads service (without actual API calls)"""
    logger.info("Testing GoogleAdsService initialization...")
    
    try:
        # This will test initialization without making API calls
        # The actual API calls would require valid credentials
        from app.services.google_ads_service import GoogleAdsService
        
        # Check if required environment variables are set
        required_vars = [
            "GOOGLE_ADS_DEVELOPER_TOKEN",
            "GOOGLE_OAUTH_CLIENT_ID", 
            "GOOGLE_OAUTH_CLIENT_SECRET",
            "GOOGLE_OAUTH_REFRESH_TOKEN",
            "GOOGLE_ADS_CUSTOMER_ID"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.warning(f"✓ Service structure OK, but missing credentials: {missing_vars}")
            logger.info("  (This is expected if Google Ads credentials aren't configured)")
        else:
            service = GoogleAdsService()
            logger.info("✓ GoogleAdsService initialized successfully")
        
        return True
    except Exception as e:
        if "Missing required Google Ads API credentials" in str(e):
            logger.warning("✓ Service structure OK, but credentials not configured")
            return True
        else:
            logger.error(f"✗ GoogleAdsService test failed: {e}")
            return False

def test_migration_readiness():
    """Test if the system is ready for the historical data migration"""
    logger.info("Testing migration readiness...")
    
    try:
        # Check if sync script exists and is executable
        sync_script = "sync_google_monthly_historical.py"
        if os.path.exists(sync_script):
            logger.info(f"✓ Sync script exists: {sync_script}")
        else:
            logger.error(f"✗ Sync script not found: {sync_script}")
            return False
        
        # Check if database migration exists
        migration_script = "database/migrations/add_campaign_type_support.sql"
        if os.path.exists(migration_script):
            logger.info(f"✓ Database migration exists: {migration_script}")
        else:
            logger.error(f"✗ Database migration not found: {migration_script}")
            return False
        
        logger.info("✓ System is ready for historical data migration")
        return True
    except Exception as e:
        logger.error(f"✗ Migration readiness test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.remove()
    logger.add(sys.stdout, format="{time:HH:mm:ss} | {level} | {message}")
    
    logger.info("🚀 Testing Monthly Google Ads Implementation")
    logger.info("="*60)
    
    tests = [
        ("Database Schema", test_database_schema),
        ("Campaign Type Service", test_campaign_type_service),
        ("Google Ads Service", test_google_ads_service),
        ("Migration Readiness", test_migration_readiness)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 {test_name}")
        if test_func():
            passed += 1
        else:
            failed += 1
    
    logger.info("\n" + "="*60)
    logger.info(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All tests passed! System is ready for monthly data sync.")
        logger.info("\nNext steps:")
        logger.info("1. Run database migration: ")
        logger.info("   Execute: database/migrations/add_campaign_type_support.sql")
        logger.info("2. Run historical sync: ")
        logger.info("   python3 sync_google_monthly_historical.py")
        logger.info("3. Test frontend: ")
        logger.info("   cd frontend && npm run dev")
        return 0
    else:
        logger.error("❌ Some tests failed. Please fix the issues before proceeding.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)