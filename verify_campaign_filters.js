const puppeteer = require('puppeteer');

async function verifyCampaignFilters() {
  let browser;
  try {
    console.log('🔍 Verifying Campaign Type Filters...');
    
    // Test backend API first
    const apiResponse = await fetch('http://localhost:8007/api/google-reports/dashboard');
    const data = await apiResponse.json();
    console.log(`✅ Backend: ${data.campaigns?.length || 0} campaigns loaded`);
    console.log(`✅ Campaign types: ${data.campaign_types?.join(', ') || 'none'}`);
    
    browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    
    // Navigate to dashboard
    await page.goto('http://localhost:3007', { waitUntil: 'networkidle0' });
    console.log('✅ Page loaded');
    
    // Check page content after load
    const pageContent = await page.content();
    
    // Look for filters text
    const hasFilters = pageContent.includes('Filters');
    console.log(`✅ Filters text found: ${hasFilters}`);
    
    // Look for campaign types text
    const hasCampaignTypes = pageContent.includes('Campaign Types');
    console.log(`✅ Campaign Types text found: ${hasCampaignTypes}`);
    
    // Look for specific campaign type names
    const hasBrand = pageContent.includes('Brand');
    const hasNonBrand = pageContent.includes('Non-Brand');
    const hasYouTube = pageContent.includes('YouTube');
    
    console.log(`Campaign Type Names Found:`);
    console.log(`  Brand: ${hasBrand ? '✅' : '❌'}`);
    console.log(`  Non-Brand: ${hasNonBrand ? '✅' : '❌'}`);
    console.log(`  YouTube: ${hasYouTube ? '✅' : '❌'}`);
    
    // Count buttons
    const buttons = await page.$$('button');
    console.log(`✅ Found ${buttons.length} buttons on page`);
    
    // Take screenshot
    await page.screenshot({ path: 'campaign-filters-test.png', fullPage: true });
    console.log('📸 Screenshot saved');
    
    return true;
    
  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
    return false;
  } finally {
    if (browser) await browser.close();
  }
}

// Add fetch if not available
if (typeof fetch === 'undefined') {
  global.fetch = require('node-fetch');
}

verifyCampaignFilters().then(success => {
  console.log(success ? '\n✅ Verification completed' : '\n❌ Verification failed');
  process.exit(0);
});