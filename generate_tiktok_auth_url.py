#!/usr/bin/env python3
"""
Generate TikTok authorization URL with all required scopes for Marketing API
"""

import urllib.parse

def generate_tiktok_auth_url():
    """Generate TikTok authorization URL with comprehensive scopes"""
    
    # Your TikTok app credentials
    app_id = "7538237339609825297"
    
    # TikTok OAuth authorization endpoint
    auth_url = "https://business-api.tiktok.com/open_api/v1.3/oauth2/authorize/"
    
    # Required scopes for Marketing API (comprehensive list)
    # Scope IDs from TikTok Marketing API documentation:
    scopes = [
        "1",   # User Management
        "2",   # Campaign Management  
        "3",   # Ad Management
        "4",   # Creative Management
        "5",   # Asset Management
        "6",   # Page Management
        "7",   # Catalog Management
        "8",   # Comment Management
        "9",   # Spark Ad
        "10",  # Lead Generation
        "11",  # Live Stream
        "12",  # Attribution Analytics
        "13",  # Research
        "14",  # Audience Management
        "15",  # Business Account Management
        "16",  # Video Creation Kit
        "17",  # Custom Solution
        "18",  # TikTok Lead Generation
        "19",  # Reach & Frequency
        "20",  # Campaign Creation
        "21",  # Reporting
        "22",  # Audience Insights
        "23",  # Creative Authorization
        "24"   # Business Center
    ]
    
    # Essential scopes for reporting and campaign management
    essential_scopes = [
        "1",   # User Management
        "2",   # Campaign Management
        "4",   # Creative Management (you already have this)
        "15",  # Business Account Management
        "20",  # Campaign Creation (you already have this)
        "21",  # Reporting (you already have this)
        "22"   # Audience Insights (you already have this)
    ]
    
    # Redirect URI (you'll need to set this in your TikTok app settings)
    redirect_uri = "https://localhost:8080/callback"  # Update this in your app settings
    
    # Build authorization URL parameters
    params = {
        "app_id": app_id,
        "scope": ",".join(essential_scopes),
        "redirect_uri": redirect_uri,
        "state": "tiktok_auth_setup_2025"  # Optional state parameter
    }
    
    # Construct full authorization URL
    full_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    
    print("🔐 TikTok Marketing API - Authorization URL Generator")
    print("=" * 60)
    print(f"📱 App ID: {app_id}")
    print(f"🎯 Redirect URI: {redirect_uri}")
    print(f"🔑 Required Scopes: {', '.join(essential_scopes)}")
    
    print(f"\n📋 Scope Descriptions:")
    scope_descriptions = {
        "1": "User Management - Access advertiser account info",
        "2": "Campaign Management - Create/read/update campaigns", 
        "4": "Creative Management - Manage ad creatives",
        "15": "Business Account Management - Access business account data",
        "20": "Campaign Creation - Create new campaigns",
        "21": "Reporting - Access campaign reports and analytics",
        "22": "Audience Insights - Access audience analytics"
    }
    
    for scope in essential_scopes:
        print(f"  {scope}: {scope_descriptions.get(scope, 'Marketing API scope')}")
    
    print(f"\n🌐 **AUTHORIZATION URL:**")
    print(f"{full_url}")
    
    print(f"\n📝 **Instructions:**")
    print(f"1. Copy the URL above and open it in your browser")
    print(f"2. Log in to your TikTok for Business account")
    print(f"3. Authorize the app with the requested permissions")
    print(f"4. Copy the authorization code from the redirect URL")
    print(f"5. Run the exchange script with the new auth code")
    
    print(f"\n⚠️  **Important Notes:**")
    print(f"• Make sure '{redirect_uri}' is added to your app's redirect URIs")
    print(f"• The auth code will be in the URL after authorization")
    print(f"• You may need to update your app settings to enable these scopes")
    
    return full_url

if __name__ == "__main__":
    auth_url = generate_tiktok_auth_url()
    
    print(f"\n🔗 Quick copy (authorization URL):")
    print(auth_url)
    print(f"\n" + "=" * 60)