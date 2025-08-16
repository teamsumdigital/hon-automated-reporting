# Google Ads API HTTP Request Node Fix

## 🚨 Current Issue
Getting 400 Bad Request from Google Ads API. This is typically caused by:
1. Incorrect request format
2. Missing required headers
3. Wrong authentication setup
4. Malformed GAQL query

## 🔧 HTTP Request Node Configuration

### **Basic Settings:**
- **Method**: `POST`
- **URL**: `https://googleads.googleapis.com/v16/customers/9860652386/googleAds:search`
- **Authentication**: `Generic Credential Type` → `OAuth2 API`

### **Headers (Required):**
```
Content-Type: application/json
developer-token: -gJOMMcQIcQBxKuaUd0FhA
```

### **Body (JSON):**
```json
{
  "query": "SELECT campaign.id, campaign.name, metrics.cost_micros, metrics.impressions, metrics.clicks, metrics.conversions, metrics.conversion_value_micros FROM campaign WHERE segments.date = 'YYYY-MM-DD' AND campaign.status = 'ENABLED'"
}
```

## ⚡ Quick Fix Steps

### **Step 1: Update HTTP Request Node**
Replace your current HTTP request node configuration with:

**URL:**
```
https://googleads.googleapis.com/v16/customers/9860652386/googleAds:search
```

**Method:** `POST`

**Authentication:** 
- Type: `Generic Credential Type`
- Auth Type: `OAuth2 API`
- Credential: Your Google OAuth2 credential

**Headers:**
```
Content-Type: application/json
developer-token: -gJOMMcQIcQBxKuaUd0FhA
```

**Body (JSON):**
```json
{
  "query": "={{ $json.query }}"
}
```

### **Step 2: Fix the Prepare Request Node**
Update your "Prepare Google Ads API Request" code node:

```javascript
// Calculate yesterday as YYYY-MM-DD
const yesterday = new Date();
yesterday.setDate(yesterday.getDate() - 1);
const dateStr = yesterday.toISOString().split('T')[0];

// Simple GAQL query (no line breaks)
const gaqlQuery = "SELECT campaign.id, campaign.name, metrics.cost_micros, metrics.impressions, metrics.clicks, metrics.conversions, metrics.conversion_value_micros FROM campaign WHERE segments.date = '" + dateStr + "' AND campaign.status = 'ENABLED'";

return {
  query: gaqlQuery,
  dateRange: dateStr
};
```

### **Step 3: OAuth2 Credential Setup**
Ensure your OAuth2 credential has:

**Client ID:** `1052692890180-r6co7k2h8un9v2bp9pi9saj670atkv7h.apps.googleusercontent.com`
**Client Secret:** `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`
**Scope:** `https://www.googleapis.com/auth/adwords`
**Grant Type:** `Authorization Code`

## 🧪 Test Configuration

### **Manual Test Query:**
Use this simple query first to test:

```json
{
  "query": "SELECT campaign.id, campaign.name FROM campaign LIMIT 10"
}
```

### **Test Headers:**
```
Content-Type: application/json
developer-token: -gJOMMcQIcQBxKuaUd0FhA
```

## 🔍 Common Issues & Solutions

### **Issue 1: Authentication Error**
**Problem:** OAuth2 not working
**Solution:** 
- Re-authorize your OAuth2 credential
- Ensure scope includes `https://www.googleapis.com/auth/adwords`
- Test with Google OAuth Playground first

### **Issue 2: Developer Token Invalid**
**Problem:** 400 Bad Request with developer token
**Solution:**
- Verify token: `-gJOMMcQIcQBxKuaUd0FhA`
- Ensure it's in header as `developer-token` (not `Developer-Token`)

### **Issue 3: Customer ID Format**
**Problem:** Wrong customer ID format
**Solution:**
- Use: `9860652386` (no dashes)
- Not: `986-065-2386`

### **Issue 4: GAQL Query Format**
**Problem:** Malformed query
**Solution:**
- No line breaks in query string
- Use single quotes for date values
- Test query in Google Ads Query Builder first

## 🎯 Working Configuration Example

**Complete working HTTP request node setup:**

```json
{
  "url": "https://googleads.googleapis.com/v16/customers/9860652386/googleAds:search",
  "method": "POST",
  "authentication": "genericCredentialType",
  "genericAuthType": "oAuth2Api",
  "sendBody": true,
  "contentType": "json",
  "body": {
    "query": "={{ $json.query }}"
  },
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Content-Type",
        "value": "application/json"
      },
      {
        "name": "developer-token",
        "value": "-gJOMMcQIcQBxKuaUd0FhA"
      }
    ]
  }
}
```

## ✅ Verification Steps

1. **Test OAuth2:** Ensure you can authorize successfully
2. **Test Simple Query:** Use basic SELECT without date filter
3. **Test with Date:** Add date filter once basic query works
4. **Check Response:** Should return campaign data, not HTML error

## 🔄 Alternative: Use Regular Search Instead of SearchStream

If issues persist, try the regular search endpoint:

**URL:** `https://googleads.googleapis.com/v16/customers/9860652386/googleAds:search`
**Method:** `POST`

This might be more stable than searchStream for n8n workflows.

Let me know what specific error you get after implementing these fixes!