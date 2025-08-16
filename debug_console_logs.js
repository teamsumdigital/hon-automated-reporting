const puppeteer = require('puppeteer');

async function debugConsoleLogs() {
  let browser;
  try {
    console.log('🔍 Debugging Console Logs...');
    
    browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    
    // Capture console logs
    page.on('console', msg => {
      const type = msg.type();
      const text = msg.text();
      
      if (text.includes('Campaign types') || text.includes('Dashboard data') || text.includes('campaign_types')) {
        console.log(`📋 [${type.toUpperCase()}] ${text}`);
      }
    });
    
    // Navigate to dashboard
    console.log('🎯 Loading dashboard...');
    await page.goto('http://localhost:3007', { waitUntil: 'networkidle0' });
    
    // Wait a bit for React to render and log
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Check what's actually in the DOM
    const dashboardContent = await page.evaluate(() => {
      const filterPanel = document.querySelector('div');
      return {
        hasFilters: document.body.innerText.includes('Filters'),
        hasCampaignTypes: document.body.innerText.includes('Campaign Types'),
        bodyText: document.body.innerText.substring(0, 500)
      };
    });
    
    console.log('📄 Dashboard content check:', dashboardContent);
    
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

debugConsoleLogs().then(success => {
  console.log(success ? '\n✅ Debug completed' : '\n❌ Debug failed');
  process.exit(0);
});