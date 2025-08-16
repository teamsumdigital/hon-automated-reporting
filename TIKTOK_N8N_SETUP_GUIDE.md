# TikTok Ads n8n Workflow Setup Guide

## Overview
This guide covers setting up the TikTok Ads daily data fetching workflow to replace the Google Ads workflow. The workflow fetches yesterday's TikTok campaign data and inserts it into the `tiktok_campaign_data` table.

## Key Changes from Google Workflow

### 1. API Endpoint Changes
- **From**: Google Ads API (`https://googleads.googleapis.com/v14/customers/...`)
- **To**: TikTok Business API (`https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/`)

### 2. Authentication Changes
- **From**: Google OAuth2 with service account
- **To**: TikTok Access Token authentication (HTTP Header Auth)

### 3. Database Table Changes
- **From**: `google_campaign_data`
- **To**: `tiktok_campaign_data`

### 4. Metrics Changes
- **From**: Google-specific metrics
- **To**: TikTok-specific metrics including `complete_payment_roas`, `complete_payment`

## Required Configuration Steps

### Step 1: Get TikTok API Credentials
1. Access TikTok Business API dashboard
2. Obtain your **Advertiser ID** (replace `7410748089324478465` in workflow)
3. Generate an **Access Token** for API authentication

### Step 2: Configure n8n Credentials
1. In n8n, create new credential of type "HTTP Header Auth"
2. Set credential name: "TikTok Ads API"
3. Configure headers:
   ```
   Header Name: Access-Token
   Header Value: YOUR_TIKTOK_ACCESS_TOKEN
   ```

### Step 3: Update Workflow Parameters

#### In "Prepare TikTok Ads API Request" node:
```javascript
const requestData = {
  advertiser_id: "YOUR_ADVERTISER_ID", // Replace with actual ID
  report_type: "BASIC",
  data_level: "AUCTION_CAMPAIGN",
  dimensions: ["campaign_id"],
  metrics: [
    "spend",
    "impressions", 
    "clicks",
    "ctr",
    "cpc",
    "cpm",
    "cost_per_conversion",
    "conversion_rate",
    "complete_payment_roas",  // TikTok's native ROAS
    "complete_payment",       // Number of purchases
    "purchase"               // Purchase events
  ],
  start_date: dateStr,
  end_date: dateStr,
  page: 1,
  page_size: 1000
};
```

#### In "Fetch TikTok Ads Campaign Data" node:
- Update Access Token in headers
- Ensure credential is properly linked

### Step 4: Database Verification
Ensure `tiktok_campaign_data` table exists with these columns:
- campaign_id
- campaign_name
- category
- campaign_type (set to "TikTok")
- reporting_starts / reporting_ends
- amount_spent_usd
- website_purchases
- purchases_conversion_value
- impressions
- link_clicks
- cpa, roas, cpc, cpm
- created_at, updated_at

## Data Mapping Details

### TikTok API Response → Database Fields
```javascript
// From TikTok API response.data.list array
const spend = parseFloat(metrics.spend || 0);
const impressions = parseInt(metrics.impressions || 0);
const clicks = parseInt(metrics.clicks || 0);
const completePayment = parseInt(metrics.complete_payment || 0);
const completePaymentRoas = parseFloat(metrics.complete_payment_roas || 0);

// Calculated fields
const revenue = completePaymentRoas * spend;  // Revenue from ROAS
const cpa = completePayment > 0 ? spend / completePayment : 0;
const cpc = clicks > 0 ? spend / clicks : 0;
const cpm = impressions > 0 ? (spend / (impressions / 1000)) : 0;
```

### Database Insertion Mapping
- `campaign_id` ← `dimensions.campaign_id`
- `campaign_name` ← `dimensions.campaign_name`
- `amount_spent_usd` ← `metrics.spend`
- `website_purchases` ← `metrics.complete_payment`
- `purchases_conversion_value` ← `calculated revenue`
- `impressions` ← `metrics.impressions`
- `link_clicks` ← `metrics.clicks`
- `roas` ← `metrics.complete_payment_roas`

## Testing the Workflow

### 1. Manual Test
1. Import workflow into n8n
2. Configure credentials and advertiser ID
3. Execute manually to test API connection
4. Verify data appears in `tiktok_campaign_data` table

### 2. Validation Queries
```sql
-- Check recent TikTok data
SELECT campaign_name, amount_spent_usd, website_purchases, roas 
FROM tiktok_campaign_data 
WHERE reporting_starts = CURRENT_DATE - INTERVAL '1 day'
ORDER BY amount_spent_usd DESC;

-- Verify data completeness
SELECT COUNT(*) as total_campaigns,
       SUM(amount_spent_usd) as total_spend,
       AVG(roas) as avg_roas
FROM tiktok_campaign_data 
WHERE reporting_starts = CURRENT_DATE - INTERVAL '1 day';
```

## Category Auto-Assignment
The workflow includes automatic categorization based on campaign names:
- Bath Mats: keywords like 'bathmat', 'bath mat'
- Play Furniture: 'play furniture', 'playmat'
- Standing Mats: 'standing mat', 'standing'
- Tumbling Mats: 'tumbling mat', 'tumbling'
- Kitchen Mats: 'kitchen'
- Outdoor Mats: 'outdoor', 'door'
- Creative Testing: 'creative', 'test'
- Multi Category: 'multi'
- Default: 'Uncategorized'

## Scheduling
- **Current**: Daily at 6 AM
- **Fetches**: Previous day's data
- **Runtime**: ~2-3 minutes depending on campaign volume

## Troubleshooting

### Common Issues
1. **401 Unauthorized**: Check Access Token validity
2. **404 Not Found**: Verify advertiser ID is correct
3. **Empty Response**: Check date range and campaign status
4. **Database Errors**: Verify table schema matches expected fields

### Debug Steps
1. Check n8n execution logs
2. Verify TikTok API response format
3. Test database connection separately
4. Validate data transformation in "Process & Categorize" node

## Differences from Google Workflow
1. **API Structure**: TikTok uses different response format (`response.data.list`)
2. **Metrics Names**: TikTok uses `complete_payment_roas` vs calculated ROAS
3. **Authentication**: Header-based vs OAuth2
4. **Data Processing**: Different field mapping and calculations

## Next Steps
1. Import `tiktok_daily_workflow.json` into n8n
2. Update advertiser ID and access token
3. Test manually with yesterday's date
4. Enable automatic scheduling
5. Monitor first few runs for data accuracy