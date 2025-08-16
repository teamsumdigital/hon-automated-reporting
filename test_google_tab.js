const puppeteer = require('puppeteer');

async function testGoogleTab() {
  let browser;
  try {
    console.log('🔍 Testing Google Ads Tab...');
    
    browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    
    // Capture console logs for debugging
    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('Dashboard data') || text.includes('Campaign types') || text.includes('campaign_types')) {
        console.log(`📋 ${text}`);
      }
    });
    
    // Navigate to main dashboard
    await page.goto('http://localhost:3007', { waitUntil: 'networkidle0' });
    console.log('✅ Main dashboard loaded');
    
    // Wait for tabs to be visible and click Google Ads tab using text content
    await new Promise(resolve => setTimeout(resolve, 1000)); // Give time for tabs to render
    
    const googleTabClicked = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const googleTab = buttons.find(button => button.textContent?.includes('Google Ads'));
      if (googleTab) {
        googleTab.click();
        return true;
      }
      return false;
    });
    
    if (googleTabClicked) {
      console.log('✅ Clicked Google Ads tab');
    } else {
      console.log('❌ Could not find Google Ads tab');
      return false;
    }
    
    // Wait for Google dashboard to load
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Check if campaign types are now visible
    const googleContent = await page.evaluate(() => {
      return {
        hasFilters: document.body.innerText.includes('Filters'),
        hasCampaignTypes: document.body.innerText.includes('Campaign Types'),
        hasBrand: document.body.innerText.includes('Brand'),
        hasNonBrand: document.body.innerText.includes('Non-Brand'),
        hasYouTube: document.body.innerText.includes('YouTube'),
        bodySnippet: document.body.innerText.substring(0, 800)
      };
    });
    
    console.log('📊 Google Dashboard Content:');
    console.log(`  Filters found: ${googleContent.hasFilters}`);
    console.log(`  Campaign Types found: ${googleContent.hasCampaignTypes}`);
    console.log(`  Brand found: ${googleContent.hasBrand}`);
    console.log(`  Non-Brand found: ${googleContent.hasNonBrand}`);
    console.log(`  YouTube found: ${googleContent.hasYouTube}`);
    
    // Take screenshot
    await page.screenshot({ path: 'google-tab-test.png', fullPage: true });
    console.log('📸 Screenshot saved');
    
    return googleContent.hasCampaignTypes;
    
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

testGoogleTab().then(success => {
  console.log(success ? '\n✅ Campaign Types are working!' : '\n❌ Campaign Types still not showing');
  process.exit(0);
});