#!/usr/bin/env python3
"""
Historic Data Resync Script
Re-pulls all campaign data from January 2024 to present using corrected link_clicks extraction
"""

import os
import sys
from datetime import date, timedelta
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / 'app'))

try:
    from app.services.meta_api import MetaAdsService
    from app.services.reporting import ReportingService
    from loguru import logger
except ImportError as e:
    print(f"Import error: {e}")
    print("Please run this script from the project root directory")
    sys.exit(1)

def resync_historic_data():
    """
    Resync all historic campaign data with corrected link_clicks extraction
    """
    try:
        # Initialize services
        meta_service = MetaAdsService()
        reporting_service = ReportingService()
        
        # Test connections
        logger.info("Testing Meta API connection...")
        if not meta_service.test_connection():
            logger.error("Meta API connection failed")
            return False
            
        logger.info("Database connection available through reporting service...")
        
        # Define sync date range (January 2024 to present)
        start_date = date(2024, 1, 1)
        end_date = date.today() - timedelta(days=1)  # Up to yesterday
        
        logger.info(f"Starting historic data resync from {start_date} to {end_date}")
        
        # Get campaign insights with corrected link_clicks extraction
        insights = meta_service.get_campaign_insights(start_date, end_date)
        logger.info(f"Retrieved {len(insights)} campaign insights")
        
        if not insights:
            logger.warning("No campaign insights retrieved")
            return True
        
        # Convert to campaign data format
        campaign_data_list = meta_service.convert_to_campaign_data(insights)
        logger.info(f"Converted {len(campaign_data_list)} campaign data records")
        
        # Save to database using reporting service
        success = reporting_service.store_campaign_data(campaign_data_list)
        
        if success:
            logger.info(f"Successfully resynced {len(campaign_data_list)} campaigns")
        else:
            logger.error("Failed to store campaign data in database")
        logger.info("Historic data resync completed!")
        
        return success
        
    except Exception as e:
        logger.error(f"Historic data resync failed: {e}")
        return False

if __name__ == "__main__":
    print("HON Automated Reporting - Historic Data Resync")
    print("=" * 50)
    print("This will re-pull all campaign data from Jan 2024 to present")
    print("using the corrected link_clicks extraction logic.")
    print()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check required environment variables
    required_vars = ["META_ACCESS_TOKEN", "META_ACCOUNT_ID", "SUPABASE_URL", "SUPABASE_SERVICE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        sys.exit(1)
    
    print("✅ Environment variables loaded")
    print()
    
    # Run the resync
    if resync_historic_data():
        print("✅ Historic data resync completed successfully!")
        print("All campaign data now uses corrected link_clicks extraction.")
    else:
        print("❌ Historic data resync failed. Check logs for details.")
        sys.exit(1)