const puppeteer = require('puppeteer');

async function simpleTest() {
  let browser;
  try {
    console.log('🔍 Simple Dashboard Test...');
    
    // Test backend first
    const apiResponse = await fetch('http://localhost:8007/api/google-reports/dashboard');
    const data = await apiResponse.json();
    console.log(`✅ Backend: ${data.campaigns?.length || 0} campaigns, types: ${data.campaign_types?.join(', ')}`);
    
    // Test frontend
    browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    
    const response = await page.goto('http://localhost:3007', { waitUntil: 'domcontentloaded' });
    console.log(`📄 Frontend response: ${response.status()}`);
    
    // Get page title and content
    const title = await page.title();
    console.log(`📋 Page title: ${title}`);
    
    // Check for any error messages
    const bodyText = await page.evaluate(() => document.body.innerText);
    if (bodyText.includes('Error') || bodyText.includes('error')) {
      console.log('⚠️  Page contains error messages');
      console.log(bodyText.substring(0, 200));
    } else {
      console.log('✅ Page loaded without obvious errors');
    }
    
    // Take screenshot
    await page.screenshot({ path: 'test-screenshot.png' });
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

simpleTest().then(success => {
  console.log(success ? '\n✅ Test completed' : '\n❌ Test failed');
  process.exit(0);
});