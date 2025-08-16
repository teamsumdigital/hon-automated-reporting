# Google Ads Daily Updater - n8n Workflow Setup

## 📋 Overview

This workflow automatically pulls Google Ads campaign data daily at 5 AM and inserts it into your `google_campaign_data` Supabase table. It's based on your existing Meta Ads workflow but adapted for Google Ads API.

## 🔧 Key Changes from Meta Workflow

### **1. Database Table**
- **Changed from**: `campaign_data` (Meta)
- **Changed to**: `google_campaign_data` (Google)
- **Added field**: `campaign_type` (Brand/Non-Brand/YouTube classification)

### **2. API Endpoint**
- **Changed from**: Facebook Graph API (`graph.facebook.com`)
- **Changed to**: Google Ads API (`googleads.googleapis.com/v16`)

### **3. Query Language**
- **Changed from**: REST parameters (level, fields, date_preset)
- **Changed to**: GAQL (Google Ads Query Language) - SQL-like syntax

### **4. Authentication**
- **Changed from**: Bearer token in header
- **Changed to**: OAuth2 + Developer Token in header

### **5. Data Processing**
- **Metrics conversion**: Google uses micros (1/1,000,000) - converted to dollars
- **Response structure**: Different JSON structure from Google API
- **Campaign types**: Added Brand/Non-Brand/YouTube classification

## 🚀 Setup Instructions

### **Step 1: Import Workflow**
1. Open your n8n instance
2. Go to **Workflows** → **Import from file**
3. Upload `google-ads-daily-pull.json`

### **Step 2: Configure Google OAuth2 Credentials**
1. In n8n, go to **Credentials** → **Add Credential**
2. Select **Google OAuth2 API**
3. Use these settings:
   ```
   Client ID: 1052692890180-r6co7k2h8un9v2bp9pi9saj670atkv7h.apps.googleusercontent.com
   Client Secret: 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
   Scope: https://www.googleapis.com/auth/adwords
   ```
4. **Authorize** the credential
5. **Save** as "Google OAuth2 for Ads API"

### **Step 3: Update HTTP Request Node**
1. Open the **"Fetch Google Ads Campaign Data"** node
2. In **Authentication** section:
   - Select **Generic Credential Type** → **OAuth2 API**
   - Choose your Google OAuth2 credential
3. Verify the **developer-token** header is set to: `-gJOMMcQIcQBxKuaUd0FhA`

### **Step 4: Verify Supabase Connection**
1. Open the **"Insert to Google Database"** node
2. Ensure **Supabase** credential is selected
3. Verify **Table ID** is set to: `google_campaign_data`

### **Step 5: Test the Workflow**
1. **Activate** the workflow
2. Click **"Execute Workflow"** to test manually
3. Check the execution log for any errors
4. Verify data appears in your `google_campaign_data` table

## 📊 Data Mapping

| Google Ads API Field | Database Column | Notes |
|---------------------|-----------------|-------|
| `campaign.id` | `campaign_id` | Campaign identifier |
| `campaign.name` | `campaign_name` | Campaign name |
| `metrics.cost_micros` | `amount_spent_usd` | Converted from micros to dollars |
| `metrics.clicks` | `link_clicks` | Total clicks |
| `metrics.impressions` | `impressions` | Total impressions |
| `metrics.conversions` | `website_purchases` | Total conversions (rounded) |
| `metrics.conversion_value_micros` | `purchases_conversion_value` | Revenue in dollars |
| Auto-calculated | `category` | Based on campaign name patterns |
| Auto-calculated | `campaign_type` | Brand/Non-Brand/YouTube |
| Auto-calculated | `cpa` | Cost / Conversions |
| Auto-calculated | `roas` | Revenue / Cost |
| Auto-calculated | `cpc` | Cost / Clicks |

## 🔍 Google Ads Query (GAQL)

The workflow uses this GAQL query to fetch yesterday's data:

```sql
SELECT 
  campaign.id,
  campaign.name,
  campaign.resource_name,
  metrics.cost_micros,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversion_value_micros
FROM campaign 
WHERE 
  segments.date = 'YYYY-MM-DD'  -- Yesterday's date
  AND campaign.status = 'ENABLED'
ORDER BY metrics.cost_micros DESC
```

## 🏷️ Campaign Categorization

The workflow automatically categorizes campaigns based on name patterns:

**Categories:**
- Bath Mats: `bathmat`, `bath mat`, `bath-mat`
- Play Furniture: `play furniture`, `playmat`, `play mat`
- Standing Mats: `standing mat`, `standing-mat`, `standing`
- Tumbling Mats: `tumbling mat`, `tumbling-mat`, `tumbling`
- Rugs: `rug`
- Kitchen Mats: `kitchen`
- Outdoor Mats: `outdoor`, `door`
- Creative Testing: `creative`, `test`
- Multi Category: `multi`
- **Default**: `Uncategorized`

**Campaign Types:**
- **Brand**: Contains `brand` or `competitor`
- **YouTube**: Contains `youtube`, `video`, or `yt`
- **Non-Brand**: Everything else

## ⏰ Schedule

**Trigger**: Daily at 5:00 AM  
**Data Range**: Yesterday's data only  
**Frequency**: Once per day

## 🔧 Troubleshooting

### **Common Issues:**

1. **OAuth Error**
   - Re-authorize Google OAuth2 credential
   - Check scope includes `https://www.googleapis.com/auth/adwords`

2. **Developer Token Invalid**
   - Verify token: `-gJOMMcQIcQBxKuaUd0FhA`
   - Ensure it's in the `developer-token` header

3. **No Data Returned**
   - Check if campaigns were active yesterday
   - Verify customer ID: `9860652386`
   - Check GAQL query syntax

4. **Database Insert Errors**
   - Verify `google_campaign_data` table exists
   - Check Supabase credential is valid
   - Ensure all required fields are mapped

### **Testing Individual Nodes:**

1. **Test API Request**: Execute "Fetch Google Ads Campaign Data" node
2. **Test Processing**: Check "Process & Categorize Google Data" output
3. **Test Database**: Verify "Insert to Google Database" success

## 📈 Expected Results

After successful execution, you should see:
- New rows in `google_campaign_data` table
- Campaigns automatically categorized
- Campaign types classified (Brand/Non-Brand/YouTube)
- Calculated metrics (CPA, ROAS, CPC)
- Log message: "Google Ads daily update completed: X campaigns processed"

## 🔄 Next Steps

1. **Import and configure** the workflow
2. **Test manually** to ensure it works
3. **Monitor** the 5 AM daily execution
4. **Check dashboard** to see Google Ads data
5. **Optionally create** a TikTok workflow using the same pattern

The Google Ads data will now automatically sync daily and appear in your unified dashboard alongside Meta Ads data! 🎯