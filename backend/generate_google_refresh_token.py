#!/usr/bin/env python3
"""
Generate Google Ads API OAuth refresh token
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow

def generate_refresh_token():
    """Generate Google Ads API refresh token via OAuth flow"""
    print("🔑 Google Ads API OAuth Setup")
    print("="*50)
    
    # OAuth scopes for Google Ads API
    SCOPES = ['https://www.googleapis.com/auth/adwords']
    
    # Client configuration
    client_config = {
        "web": {
            "client_id": "1052692890180-r6co7k2h8un9v2bp9pi9saj670atkv7h.apps.googleusercontent.com",
            "client_secret": "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",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080"]
        }
    }
    
    try:
        print("🚀 Starting OAuth flow...")
        print("   This will open your browser for Google authentication")
        print("   Please sign in with your Google Ads account")
        
        # Create flow
        flow = InstalledAppFlow.from_client_config(
            client_config, 
            SCOPES,
            redirect_uri='http://localhost:8080'
        )
        
        # Run local server OAuth flow
        print("\n📱 Opening browser for authentication...")
        credentials = flow.run_local_server(
            port=8080,
            prompt='consent',
            open_browser=True
        )
        
        if credentials and credentials.refresh_token:
            refresh_token = credentials.refresh_token
            print(f"\n✅ SUCCESS! Your refresh token:")
            print(f"   {refresh_token}")
            
            print(f"\n📝 Add this to your .env file:")
            print(f"   GOOGLE_OAUTH_REFRESH_TOKEN={refresh_token}")
            
            # Optional: Auto-update .env file
            env_file = "/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/.env"
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                
                if 'GOOGLE_OAUTH_REFRESH_TOKEN=' in content:
                    # Update existing
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith('GOOGLE_OAUTH_REFRESH_TOKEN='):
                            lines[i] = f'GOOGLE_OAUTH_REFRESH_TOKEN={refresh_token}'
                            break
                    content = '\n'.join(lines)
                else:
                    # Add new
                    content += f'\nGOOGLE_OAUTH_REFRESH_TOKEN={refresh_token}\n'
                
                with open(env_file, 'w') as f:
                    f.write(content)
                    
                print(f"🎉 Automatically updated .env file!")
                
            except Exception as e:
                print(f"⚠️  Could not auto-update .env file: {e}")
                print("   Please add the token manually")
            
            print(f"\n🎯 Google Ads API is now ready!")
            print(f"   Customer ID: 9860652386")
            print(f"   Developer Token: -gJOMMcQIcQBxKuaUd0FhA")
            
            return refresh_token
            
        else:
            print("❌ Failed to get refresh token")
            return None
            
    except Exception as e:
        print(f"❌ OAuth flow failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   • Make sure you're signed into the correct Google account")
        print("   • Check that the OAuth client is configured correctly")
        print("   • Ensure port 8080 is available")
        return None

if __name__ == "__main__":
    print("Installing required packages...")
    os.system("pip3 install google-auth-oauthlib")
    print()
    
    token = generate_refresh_token()
    
    if token:
        print("\n✅ Setup complete! Google Ads integration is ready.")
    else:
        print("\n❌ Setup failed. Please check the configuration.")