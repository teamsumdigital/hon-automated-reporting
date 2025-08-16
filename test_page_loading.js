const puppeteer = require('puppeteer');

async function testPageLoading() {
  let browser;
  try {
    console.log('🔍 Testing HON Dashboard Loading...');
    
    browser = await puppeteer.launch({ 
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // Test backend API first
    console.log('📡 Testing backend API...');
    const apiResponse = await fetch('http://localhost:8007/api/google-reports/dashboard');
    if (apiResponse.ok) {
      const data = await apiResponse.json();
      console.log(`✅ Backend API working - ${data.campaigns?.length || 0} campaigns loaded`);
      console.log(`✅ Campaign types available: ${data.campaign_types?.join(', ') || 'none'}`);
    } else {
      console.log('❌ Backend API failed');
      return false;
    }
    
    // Test frontend loading
    console.log('🎨 Testing frontend loading...');
    
    // Set longer timeout for page load
    await page.goto('http://localhost:3007', { 
      waitUntil: 'networkidle0',
      timeout: 10000 
    });
    
    console.log('✅ Page loaded successfully');
    
    // Check if the main dashboard elements are present
    await page.waitForSelector('h3:contains("Filters")', { timeout: 5000 });
    console.log('✅ Filters panel found');
    
    // Check for campaign type filters specifically
    const campaignTypeSection = await page.$('text=Campaign Types');
    if (campaignTypeSection) {
      console.log('✅ Campaign Types section found');
    } else {
      console.log('⚠️  Campaign Types section not found');
    }
    
    // Check for filter buttons
    const filterButtons = await page.$$('button');
    console.log(`✅ Found ${filterButtons.length} filter buttons`);
    
    // Take a screenshot for verification
    await page.screenshot({ path: 'dashboard-test.png', fullPage: true });
    console.log('📸 Screenshot saved as dashboard-test.png');
    
    return true;
    
  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
    return false;
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// For Node.js compatibility
if (typeof fetch === 'undefined') {
  const { default: fetch } = require('node-fetch');
  global.fetch = fetch;
}

testPageLoading().then(success => {
  if (success) {
    console.log('\n🎉 Dashboard is working! You can visit http://localhost:3007');
  } else {
    console.log('\n❌ Dashboard has issues - check the logs above');
  }
  process.exit(success ? 0 : 1);
});