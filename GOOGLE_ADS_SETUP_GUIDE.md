# Complete Google Ads API Setup Guide

This guide walks you through setting up Google Ads API access for the HON Automated Reporting System from scratch.

## 🎯 Overview

Google Ads API setup requires:
1. Google Cloud Console project with OAuth2 credentials
2. Google Ads Manager account with developer token
3. API access approval (can take 3-7 business days)
4. OAuth2 authentication flow to get refresh token

## 📋 Prerequisites

- Google account with admin access to your Google Ads account
- Business verification completed in Google Ads
- Basic familiarity with command line operations

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Console Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create or Select Project**
   ```
   Option A: Create new project
   - Click "New Project" 
   - Name: "HON Automated Reporting"
   - Click "Create"
   
   Option B: Use existing project
   - Select your existing project from dropdown
   ```

3. **Enable Google Ads API**
   - Go to "APIs & Services" → "Library"
   - Search for "Google Ads API"
   - Click on it and press "Enable"

### Step 2: Create OAuth2 Credentials

1. **Navigate to Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "+ CREATE CREDENTIALS" 
   - Select "OAuth 2.0 Client ID"

2. **Configure OAuth Consent Screen** (if prompted)
   ```
   User Type: External (unless you have Google Workspace)
   Application name: HON Automated Reporting
   User support email: your-email@domain.com
   Developer contact: your-email@domain.com
   Scopes: Add https://www.googleapis.com/auth/adwords
   Test users: Add your email address
   ```

3. **Create OAuth Client ID**
   ```
   Application type: Web application
   Name: HON Google Ads API Client
   
   Authorized redirect URIs:
   - http://localhost:8080/oauth2callback
   - http://127.0.0.1:8080/oauth2callback
   ```

4. **Download Credentials**
   - Click "Download JSON" and save as `client_secrets.json`
   - Keep this file secure and never commit to git

### Step 3: Get Google Ads Manager Account & Developer Token

1. **Upgrade to Manager Account**
   - Go to: https://ads.google.com/
   - Click Settings → Account settings
   - If not already a manager account, upgrade to manager account
   - This is required to get a developer token

2. **Apply for Developer Token**
   - In Google Ads, go to Tools → Setup → API Center
   - Click "Apply for Basic Access" 
   - Fill out the application form:
     ```
     Company: House of Noa
     Website: your-company-website.com
     Use case: Automated reporting for advertising campaigns
     Integration type: Desktop application
     ```
   - **Important**: This approval can take 3-7 business days

3. **Get Your Developer Token**
   - Once approved, return to API Center
   - Copy your developer token (starts with letters, followed by numbers)

### Step 4: Find Your Customer ID

1. **Get Customer ID**
   - In Google Ads, click on your account name (top right)
   - Look for your Customer ID (10-digit number like 123-456-7890)
   - **Important**: Remove the dashes, use format: 1234567890

### Step 5: Get OAuth Refresh Token

#### Option A: Using Python Script (Recommended)

1. **Install Required Packages**
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2
   ```

2. **Create Authentication Script**
   ```bash
   # Create a temporary file: get_refresh_token.py
   cat > get_refresh_token.py << 'EOF'
   #!/usr/bin/env python3
   import json
   from google_auth_oauthlib.flow import InstalledAppFlow
   
   # Path to your downloaded client_secrets.json
   CLIENT_SECRETS_FILE = 'client_secrets.json'
   SCOPES = ['https://www.googleapis.com/auth/adwords']
   
   def main():
       flow = InstalledAppFlow.from_client_secrets_file(
           CLIENT_SECRETS_FILE, SCOPES)
       
       # Run local server for OAuth flow
       creds = flow.run_local_server(
           port=8080,
           prompt='select_account'
       )
       
       print("\n" + "="*50)
       print("SUCCESS! Your OAuth credentials:")
       print("="*50)
       print(f"Client ID: {creds.client_id}")
       print(f"Client Secret: {creds.client_secret}")
       print(f"Refresh Token: {creds.refresh_token}")
       print("="*50)
       
       # Save to file for reference
       with open('google_ads_tokens.json', 'w') as f:
           json.dump({
               'client_id': creds.client_id,
               'client_secret': creds.client_secret,
               'refresh_token': creds.refresh_token
           }, f, indent=2)
       
       print("Tokens saved to: google_ads_tokens.json")
       print("You can now configure your .env file!")
   
   if __name__ == '__main__':
       main()
   EOF
   ```

3. **Run Authentication**
   ```bash
   # Make sure client_secrets.json is in same directory
   python get_refresh_token.py
   ```

4. **Complete OAuth Flow**
   - Browser will open automatically
   - Sign in to Google account that has Google Ads access
   - Click "Allow" to grant permissions
   - Copy the refresh token from the output

#### Option B: Using Google's OAuth Playground

1. **Go to OAuth Playground**
   - Visit: https://developers.google.com/oauthplayground/
   
2. **Configure Settings**
   - Click gear icon (⚙️) in top right
   - Check "Use your own OAuth credentials"
   - Enter your Client ID and Client Secret from Step 2

3. **Authorize APIs**
   - In left sidebar, find "Google Ads API v14"
   - Select: `https://www.googleapis.com/auth/adwords`
   - Click "Authorize APIs"

4. **Exchange Authorization Code**
   - Click "Exchange authorization code for tokens"
   - Copy the "Refresh token" value

### Step 6: Configure Environment Variables

1. **Update Your .env File**
   ```env
   # Google Ads API Configuration
   GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token_here
   GOOGLE_ADS_CUSTOMER_ID=1234567890
   GOOGLE_OAUTH_CLIENT_ID=your_client_id.apps.googleusercontent.com
   GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret
   GOOGLE_OAUTH_REFRESH_TOKEN=your_refresh_token_here
   
   # Optional: Only needed for Manager accounts managing multiple accounts
   GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_manager_account_id
   ```

2. **Verify Your Configuration**
   ```bash
   # Double-check your customer ID format (no dashes)
   # Verify client ID ends with .apps.googleusercontent.com
   # Ensure refresh token is complete (usually starts with 1//)
   ```

### Step 7: Test Your Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install google-ads==24.1.0
   ```

2. **Run Database Migration**
   ```bash
   cd ..
   python run_google_ads_migration.py
   ```

3. **Test API Connection**
   ```bash
   # Start your backend server
   cd backend
   uvicorn main:app --reload --port 8007
   
   # In another terminal, test connection
   curl http://localhost:8007/api/google-reports/test-connection
   ```

4. **Expected Success Response**
   ```json
   {
     "status": "connected",
     "message": "Google Ads API connection successful"
   }
   ```

## 🚨 Common Issues & Solutions

### Issue: "Google Ads API not enabled"
**Solution**: Make sure you enabled Google Ads API in Step 1.3

### Issue: "Invalid customer ID"
**Solution**: 
- Remove dashes from customer ID (use 1234567890, not 123-456-7890)
- Ensure it's exactly 10 digits

### Issue: "Developer token not approved"
**Solution**: 
- Wait for Google's approval (3-7 business days)
- Use test account initially with developer token ending in 0000

### Issue: "OAuth error invalid_client"
**Solution**: 
- Verify client ID and secret are correct
- Check authorized redirect URIs include localhost:8080

### Issue: "Refresh token expired"
**Solution**: 
- Re-run the OAuth flow to get new refresh token
- Set refresh token to never expire in OAuth settings

## 🔄 Development vs Production

### Development Setup
- Use test Google Ads account
- Developer token will have 0000 suffix
- Limited to test data only

### Production Setup  
- Apply for production access after testing
- Use real Google Ads account
- Full access to live campaign data

## 📞 Getting Help

### Google Ads API Support
- Documentation: https://developers.google.com/google-ads/api/docs
- Support: https://ads-developers.googleblog.com/
- Community: https://groups.google.com/g/adwords-api

### HON Reporting System Support
- Check backend logs in `logs/hon_reporting.log`
- Verify all environment variables are set
- Test Meta Ads integration first to ensure base system works

## ✅ Verification Checklist

Before proceeding, ensure:
- [ ] Google Cloud project created with Google Ads API enabled
- [ ] OAuth2 credentials downloaded
- [ ] Google Ads Manager account with developer token (approved)
- [ ] Customer ID collected (10 digits, no dashes)
- [ ] Refresh token obtained through OAuth flow
- [ ] All environment variables configured in .env file
- [ ] Database migration completed successfully
- [ ] API connection test returns "connected" status

Once all items are checked, you're ready to sync historical data and use the Google Ads dashboard!

## 🎉 Next Steps

After setup completion:
1. Run historical data sync: `python google_historical_resync.py`
2. Access the dashboard with Google Ads tab: http://localhost:3007
3. Set up n8n automation for daily Google Ads data pulls

---

**Need help?** This setup process can be complex. If you encounter issues, Google's developer support is very helpful, and the approval process is usually straightforward for legitimate business use cases.