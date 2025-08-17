// Test n8n TikTok campaign processing code
// This simulates the n8n environment

// Mock n8n input - simulated TikTok API response
const mockInput = {
  all: () => [{
    json: {
      "code": 0,
      "data": {
        "list": [
          {
            "dimensions": {"campaign_id": "1835848882707505"},
            "metrics": {
              "spend": "584.13",
              "impressions": "31291", 
              "clicks": "221",
              "complete_payment_roas": "4.69",
              "complete_payment": "9"
            }
          },
          {
            "dimensions": {"campaign_id": "1804311710999553"},
            "metrics": {
              "spend": "348.18",
              "impressions": "20930",
              "clicks": "220", 
              "complete_payment_roas": "3.67",
              "complete_payment": "5"
            }
          },
          {
            "dimensions": {"campaign_id": "1804231373274161"},
            "metrics": {
              "spend": "502.01",
              "impressions": "56056",
              "clicks": "597",
              "complete_payment_roas": "4.57", 
              "complete_payment": "10"
            }
          }
        ]
      }
    }
  }]
};

// Mock fetch function
global.fetch = async (url, options) => {
  console.log('Mock fetch called with:', url);
  
  // Return mock TikTok campaign names response
  return {
    json: async () => ({
      "code": 0,
      "data": {
        "list": [
          {
            "campaign_id": "1835848882707505",
            "campaign_name": "Prospecting - Play Furniture"
          },
          {
            "campaign_id": "1804311710999553", 
            "campaign_name": "Prospecting - Standing and Bath Mats"
          },
          {
            "campaign_id": "1804231373274161",
            "campaign_name": "Prospecting - Play and Tumbling Mats"
          }
        ]
      }
    })
  };
};

// Mock n8n $input global
global.$input = mockInput;

// The actual n8n code to test
async function testTikTokProcessing() {

// Process TikTok Ads API response and prepare for database insertion
const response = $input.all()[0].json;

// TikTok API returns data in response.data.list format
const campaigns = response?.data?.list || [];
const processedCampaigns = [];

// Category rules for auto-categorization
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

function categorizeCompany(campaignName) {
  const name = (campaignName || '').toLowerCase();
  for (const [category, keywords] of Object.entries(categoryRules)) {
    if (keywords.some(k => name.includes(k))) return category;
  }
  return 'Uncategorized';
}

// Extract all campaign IDs first
const campaignIds = campaigns.map(campaign => campaign.dimensions?.campaign_id).filter(id => id);

console.log('Campaign IDs found:', campaignIds);

// Fetch campaign names using TikTok campaign/get endpoint
let campaignNamesMap = {};

if (campaignIds.length > 0) {
  try {
    const campaignUrl = `https://business-api.tiktok.com/open_api/v1.3/campaign/get/?advertiser_id=6961828676572839938&campaign_ids=${JSON.stringify(campaignIds)}`;
    
    console.log('Fetching campaign names from:', campaignUrl);
    
    const campaignResponse = await fetch(campaignUrl, {
      headers: {
        'Access-Token': 'a3d1496268b35f9ad9a6f0d9d4492ab35d4c0bea',
        'Content-Type': 'application/json'
      }
    });
    
    const campaignData = await campaignResponse.json();
    console.log('Campaign names response:', campaignData);
    
    if (campaignData?.code === 0 && campaignData?.data?.list) {
      campaignData.data.list.forEach(camp => {
        campaignNamesMap[camp.campaign_id] = camp.campaign_name;
      });
      console.log('Campaign names map:', campaignNamesMap);
    }
  } catch (error) {
    console.log('Failed to fetch campaign names:', error);
  }
}

// Process campaigns with real names
campaigns.forEach((campaign) => {
  const dimensions = campaign.dimensions || {};
  const metrics = campaign.metrics || {};
  
  // Extract campaign info
  const campaignId = dimensions.campaign_id || '';
  const campaignName = campaignNamesMap[campaignId] || `Campaign ${campaignId}`;
  
  console.log(`Processing: ${campaignId} -> ${campaignName}`);
  
  // Extract metrics (TikTok returns as strings)
  const spend = parseFloat(metrics.spend || 0);
  const impressions = parseInt(metrics.impressions || 0);
  const clicks = parseInt(metrics.clicks || 0);
  
  // Use TikTok's native Payment Complete metrics
  const completePayment = parseInt(metrics.complete_payment || 0);
  const completePaymentRoas = parseFloat(metrics.complete_payment_roas || 0);
  
  // Calculate revenue from TikTok's ROAS
  const revenue = completePaymentRoas * spend;
  
  // Calculate derived metrics
  const cpa = completePayment > 0 ? spend / completePayment : 0;
  const cpc = clicks > 0 ? spend / clicks : 0;
  const cpm = impressions > 0 ? (spend / (impressions / 1000)) : 0;
  
  // Get yesterday's date
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const dateStr = yesterday.toISOString().split('T')[0];
  
  const processedCampaign = {
    campaign_id: campaignId,
    campaign_name: campaignName,
    amount_spent_usd: spend,
    website_purchases: completePayment,
    purchases_conversion_value: revenue,
    impressions: impressions,
    link_clicks: clicks,
    date_start: dateStr,
    date_stop: dateStr,
    category: categorizeCompany(campaignName),
    cpa: cpa,
    roas: completePaymentRoas,
    cpc: cpc,
    cpm: cpm,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };
  
  processedCampaigns.push(processedCampaign);
});

console.log(`Processed ${processedCampaigns.length} TikTok Ads campaigns with real names`);
console.log('Results:', JSON.stringify(processedCampaigns, null, 2));
return processedCampaigns;

}

// Run the test
testTikTokProcessing().then(result => {
  console.log('✅ Test completed successfully!');
}).catch(error => {
  console.error('❌ Test failed:', error);
});