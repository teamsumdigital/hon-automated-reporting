// FIXED Campaign type classification function
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

// COMPLETE FIXED CODE FOR YOUR NODE:

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

// FIXED Campaign type classification
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
  const conversionValue = parseFloat(metrics.conversion_value_micros) || 0;
  const conversionValueDollars = conversionValue / 1000000; // Convert from micros
  
  // Calculate yesterday's date
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const dateStr = yesterday.toISOString().split('T')[0];
  
  const processedCampaign = {
    campaign_id: campaignId,
    campaign_name: campaignName,
    campaign_type: classifyCampaignType(campaignName),
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