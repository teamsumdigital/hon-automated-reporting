# Complete Fix for Both Issues

## 🐛 Issue 1: Campaign Types Still Wrong
You still have "Non-Brand" campaigns showing as "Brand" - you need to update the processing node.

## 🐛 Issue 2: Spend Still $0  
The GAQL query has an invalid field name: `metrics.conversions_value` should be `metrics.conversions_value_micros`

## 🔧 Fix 1: Update "Prepare Google Ads API Request" Node

Replace your current code with this FIXED version:

```javascript
// Calculate yesterday as YYYY-MM-DD
const yesterday = new Date();
yesterday.setDate(yesterday.getDate() - 1);
const dateStr = yesterday.toISOString().split('T')[0];

// FIXED GAQL query - corrected field names
const gaqlQuery = `
  SELECT 
    campaign.id, 
    campaign.name, 
    segments.date,
    metrics.cost_micros, 
    metrics.impressions, 
    metrics.clicks, 
    metrics.conversions, 
    metrics.conversions_value_micros,
    metrics.all_conversions,
    metrics.all_conversions_value_micros
  FROM campaign 
  WHERE 
    segments.date = '${dateStr}' 
    AND campaign.status = 'ENABLED'
`;

return {
  customerId: '9860652386',
  query: gaqlQuery.trim(),
  dateRange: dateStr
};
```

**Key Fix:** Changed `metrics.conversions_value` to `metrics.conversions_value_micros`

## 🔧 Fix 2: Update "Process & Categorize Google Data" Node

Replace your entire processing node with this FIXED version:

```javascript
// Process Google Ads API response and prepare for database insertion
const response = $input.all()[0].json;
const campaigns = response.results || [];
const processedCampaigns = [];

// Category rules for auto-categorization (same as Meta)
const categoryRules = {
  'Bath Mats': ['bathmat', 'bath mat', 'bath-mat'],
  'Play Furniture': ['play furniture', 'playmat', 'play mat', 'play-mat'],
  'Standing Mats': ['standing mat', 'standing-mat', 'standing'],
  'Tumbling Mats': ['tumbling mat', 'tumbling-mat', 'tumbling'],
  'Rugs': ['rug'],
  'Kitchen Mats': ['kitchen'],
  'Outdoor Mats': ['outdoor', 'door'],
  'Creative Testing': ['creative', 'test'],
  'Multi Category': ['multi']
};

// FIXED Campaign type classification - checks "non-brand" FIRST
function classifyCampaignType(campaignName) {
  const name = campaignName.toLowerCase();
  
  // Check for "non-brand" first (more specific)
  if (name.includes('non-brand') || name.includes('nonbrand')) {
    return 'Non-Brand';
  }
  
  // Then check for "brand" (but not "non-brand")  
  if (name.includes('brand') || name.includes('competitor')) {
    return 'Brand';
  }
  
  // Check for YouTube/Video campaigns
  if (name.includes('youtube') || name.includes('video') || name.includes('yt')) {
    return 'YouTube';
  }
  
  // Default to Non-Brand
  return 'Non-Brand';
}

function categorizeCompany(campaignName) {
  const name = campaignName.toLowerCase();
  for (const [category, keywords] of Object.entries(categoryRules)) {
    if (keywords.some(keyword => name.includes(keyword))) {
      return category;
    }
  }
  return 'Uncategorized';
}

// Process each campaign from Google Ads API
campaigns.forEach(campaign => {
  const campaignData = campaign.campaign || {};
  const metrics = campaign.metrics || {};
  
  // Extract values from Google Ads response
  const campaignId = campaignData.resource_name ? campaignData.resource_name.split('/').pop() : campaignData.id;
  const campaignName = campaignData.name || 'Unknown Campaign';
  const costMicros = parseInt(metrics.cost_micros) || 0;
  const cost = costMicros / 1000000; // Convert from micros to dollars
  const impressions = parseInt(metrics.impressions) || 0;
  const clicks = parseInt(metrics.clicks) || 0;
  const conversions = parseFloat(metrics.conversions) || 0;
  
  // FIXED: Use correct field name for conversion value
  const conversionValueMicros = parseFloat(metrics.conversions_value_micros) || 0;
  const conversionValueDollars = conversionValueMicros / 1000000; // Convert from micros
  
  // Calculate yesterday's date
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const dateStr = yesterday.toISOString().split('T')[0];
  
  const processedCampaign = {
    campaign_id: campaignId,
    campaign_name: campaignName,
    campaign_type: classifyCampaignType(campaignName), // FIXED function
    amount_spent_usd: cost,
    link_clicks: clicks,
    impressions: impressions,
    website_purchases: Math.round(conversions),
    purchases_conversion_value: conversionValueDollars,
    date_start: dateStr,
    date_stop: dateStr,
    category: categorizeCompany(campaignName),
    cpa: conversions > 0 ? cost / conversions : 0,
    roas: cost > 0 ? conversionValueDollars / cost : 0,
    cpc: clicks > 0 ? cost / clicks : 0,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  processedCampaigns.push(processedCampaign);
});

console.log(`Processed ${processedCampaigns.length} Google Ads campaigns`);
return processedCampaigns;
```

## 🎯 Expected Results After Fixes:

**Campaign Types Should Be:**
- `"Playmats - Shopping - Non-Brand"` → `"Non-Brand"` ✅
- `"Multiple - Search - Brand"` → `"Brand"` ✅  
- `"YouTube - Standing Mats - Video Views"` → `"YouTube"` ✅

**Spend Data Should Show:**
- `amount_spent_usd: 15.42` (actual amounts instead of 0)
- `purchases_conversion_value: 234.56` (actual revenue)

## 🚀 Steps to Apply:

1. **Update "Prepare Google Ads API Request" node** with fixed GAQL query
2. **Update "Process & Categorize Google Data" node** with fixed classification logic  
3. **Test the workflow** - you should see actual spend amounts and correct campaign types
4. **Run again** to verify data flows to Supabase correctly

Both issues should be resolved with these fixes! 🎯