#!/usr/bin/env python3
"""
Test script to verify the HON Automated Reporting setup
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment variables"""
    print("🔍 Testing environment variables...")
    
    load_dotenv()
    
    required_vars = [
        'META_APP_ID',
        'META_APP_SECRET', 
        'META_ACCOUNT_ID',
        'SUPABASE_URL',
        'SUPABASE_SERVICE_KEY'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            # Don't print sensitive values
            if 'SECRET' in var or 'KEY' in var:
                print(f"   ✅ {var}: ***")
            else:
                print(f"   ✅ {var}: {value}")
    
    if missing:
        print(f"   ❌ Missing: {', '.join(missing)}")
        return False
    
    print("   ✅ All environment variables found")
    return True

def test_supabase():
    """Test Supabase connection"""
    print("\n🔍 Testing Supabase connection...")
    
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        
        supabase = create_client(url, key)
        
        # Test simple query
        result = supabase.table("category_rules").select("*").limit(1).execute()
        print(f"   ✅ Supabase connection successful")
        print(f"   ✅ Database accessible (found {len(result.data)} category rules)")
        return True
        
    except Exception as e:
        print(f"   ❌ Supabase connection failed: {e}")
        print("   💡 Make sure you've run the database schema in Supabase SQL editor")
        return False

def test_meta_ads():
    """Test Meta Ads API configuration (not connection)"""
    print("\n🔍 Testing Meta Ads API configuration...")
    
    try:
        from facebook_business.api import FacebookAdsApi
        
        app_id = os.getenv("META_APP_ID")
        app_secret = os.getenv("META_APP_SECRET") 
        access_token = os.getenv("META_ACCESS_TOKEN")
        
        if not access_token or access_token == "your_long_lived_token_here":
            print("   ⚠️  META_ACCESS_TOKEN not set - you'll need this for data sync")
            print("   💡 Get your access token from Facebook Developers Console")
            return False
        
        # Initialize API (doesn't make actual request)
        FacebookAdsApi.init(access_token=access_token)
        print("   ✅ Meta Ads API configuration loaded")
        return True
        
    except Exception as e:
        print(f"   ❌ Meta Ads API configuration failed: {e}")
        return False

def test_imports():
    """Test all required imports"""
    print("\n🔍 Testing Python imports...")
    
    imports = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pandas', 'Pandas'),
        ('loguru', 'Loguru'),
        ('supabase', 'Supabase'),
        ('facebook_business', 'Facebook Business API'),
    ]
    
    failed = []
    for module, name in imports:
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError as e:
            print(f"   ❌ {name}: {e}")
            failed.append(module)
    
    if failed:
        print(f"   💡 Install missing modules: pip install {' '.join(failed)}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 HON Automated Reporting - Setup Test\n")
    
    tests = [
        test_imports,
        test_environment,
        test_supabase,
        test_meta_ads,
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 Setup complete! Ready to start the server.")
        print("\nNext steps:")
        print("1. Start backend: python main.py")
        print("2. Start frontend: cd ../frontend && npm install && npm run dev")
        print("3. Visit: http://localhost:3000")
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()