# Google Ads API OAuth Setup Instructions

## 🔑 Get Your Google Ads Refresh Token

Since we can't run the OAuth flow directly in Claude Code, here's how to get your refresh token:

### Method 1: Using Google's OAuth Playground (Easiest)

1. **Go to OAuth Playground**: https://developers.google.com/oauthplayground/

2. **Configure OAuth Settings**:
   - Click the gear icon ⚙️ in top right
   - Check "Use your own OAuth credentials"
   - Enter your credentials:
     - **OAuth Client ID**: `1052692890180-r6co7k2h8un9v2bp9pi9saj670atkv7h.apps.googleusercontent.com`
     - **OAuth Client Secret**: `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`

3. **Select Scope**:
   - In the left panel, find "Google Ads API v17"
   - Select: `https://www.googleapis.com/auth/adwords`

4. **Authorize**:
   - Click "Authorize APIs" button
   - Sign in with your Google Ads account
   - Click "Allow" to grant permissions

5. **Exchange Code for Token**:
   - You'll see an authorization code
   - Click "Exchange authorization code for tokens"

6. **Copy Refresh Token**:
   - Copy the `refresh_token` value (starts with `1//`)

### Method 2: Manual OAuth URL

If OAuth Playground doesn't work:

1. **Open this URL** in your browser (replace CLIENT_ID):
```
https://accounts.google.com/o/oauth2/auth?client_id=1052692890180-r6co7k2h8un9v2bp9pi9saj670atkv7h.apps.googleusercontent.com&redirect_uri=http://localhost&scope=https://www.googleapis.com/auth/adwords&response_type=code&access_type=offline&prompt=consent
```

2. **Sign in** with your Google Ads account

3. **Copy the code** from the redirect URL (after `?code=`)

4. **Exchange for token** using curl:
```bash
curl -X POST https://oauth2.googleapis.com/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "code=YOUR_AUTHORIZATION_CODE&client_id=1052692890180-r6co7k2h8un9v2bp9pi9saj670atkv7h.apps.googleusercontent.com&client_secret=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&redirect_uri=http://localhost&grant_type=authorization_code"
```

5. **Copy refresh_token** from the response

## 🎯 Once You Have the Refresh Token

Add it to your `.env` file:
```
GOOGLE_OAUTH_REFRESH_TOKEN=your_refresh_token_here
```

Then your Google Ads integration will be complete!

## 📞 Alternative: n8n OAuth Flow

If you prefer using n8n:

1. **Create Google OAuth2 node** in n8n
2. **Configure credentials** with your Client ID/Secret
3. **Add Google Ads API scope**: `https://www.googleapis.com/auth/adwords`
4. **Complete OAuth flow** through n8n interface
5. **Extract refresh token** from n8n credentials

Let me know which method you'd prefer to use!