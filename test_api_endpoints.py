#!/usr/bin/env python3
"""
Simple test script to verify the ad-level API endpoints are working
"""

import requests
import json
from datetime import date, timedelta

# Test the new ad-level endpoints
BASE_URL = "http://localhost:8007"

def test_health_check():
    """Test basic health check"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test root endpoint shows new ad-level endpoints"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            if "meta_ad_level" in data.get("endpoints", {}):
                print("✅ Root endpoint shows meta ad-level endpoints")
                print(f"   Available endpoints: {list(data['endpoints']['meta_ad_level'].keys())}")
                return True
            else:
                print("❌ Meta ad-level endpoints not found in root")
                return False
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint test failed: {e}")
        return False

def test_ad_data_endpoint():
    """Test the ad data endpoint (should work even without data)"""
    try:
        response = requests.get(f"{BASE_URL}/api/meta-ad-reports/ad-data")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ad data endpoint accessible: {data.get('count', 0)} records found")
            return True
        else:
            print(f"❌ Ad data endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                pass
            return False
    except Exception as e:
        print(f"❌ Ad data endpoint test failed: {e}")
        return False

def test_weekly_summary_endpoint():
    """Test the weekly summary endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/meta-ad-reports/weekly-summary")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Weekly summary endpoint accessible")
            print(f"   Status: {data.get('status')}")
            if 'weekly_summary' in data:
                print(f"   Weekly data: {len(data['weekly_summary'])} weeks found")
            return True
        else:
            print(f"❌ Weekly summary endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                pass
            return False
    except Exception as e:
        print(f"❌ Weekly summary endpoint test failed: {e}")
        return False

def test_meta_connection_endpoint():
    """Test the Meta connection endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/meta-ad-reports/test-connection")
        print(f"📡 Meta connection test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Meta connection test failed: {e}")
        return False

def main():
    """Run all API endpoint tests"""
    print("🚀 Testing Meta Ad-Level API Endpoints")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("Ad Data Endpoint", test_ad_data_endpoint),
        ("Weekly Summary Endpoint", test_weekly_summary_endpoint),
        ("Meta Connection Test", test_meta_connection_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"   ⚠️  Note: Some failures expected if server not running or credentials not configured")
    
    print(f"\n📊 Summary: {passed}/{total} tests passed")
    
    if passed >= 3:  # Health, root, and at least one endpoint
        print("🎉 API endpoints are properly configured!")
        print("\n📋 Next steps:")
        print("1. Start the backend server: uvicorn main:app --reload --port 8007")
        print("2. Configure Meta API credentials in .env file")
        print("3. Test sync endpoint: POST /api/meta-ad-reports/sync-14-days")
    else:
        print("❌ Some endpoints may need configuration")

if __name__ == "__main__":
    main()