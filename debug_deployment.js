const puppeteer = require('puppeteer');

async function debugDeployment() {
  console.log('🔍 Starting automated deployment debugging...');
  
  const browser = await puppeteer.launch({ 
    headless: false,
    devtools: true 
  });
  
  try {
    const page = await browser.newPage();
    
    // Enable request interception to see what URLs are being called
    await page.setRequestInterception(true);
    
    const requests = [];
    page.on('request', (request) => {
      requests.push({
        url: request.url(),
        method: request.method()
      });
      request.continue();
    });
    
    // Capture console logs
    const consoleLogs = [];
    page.on('console', (msg) => {
      consoleLogs.push(`${msg.type()}: ${msg.text()}`);
    });
    
    // Capture network responses
    const responses = [];
    page.on('response', (response) => {
      responses.push({
        url: response.url(),
        status: response.status(),
        contentType: response.headers()['content-type']
      });
    });
    
    console.log('📱 Opening HON dashboard...');
    await page.goto('https://hon-automated-reporting.netlify.app', {
      waitUntil: 'networkidle0'
    });
    
    console.log('🔐 Entering password...');
    await page.waitForSelector('input[type="password"]', { timeout: 10000 });
    await page.type('input[type="password"]', 'HN$7kX9#mQ2vL8pR@2024');
    await page.click('button[type="submit"]');
    
    console.log('⏳ Waiting for dashboard to load...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Check for API URL console log
    const apiUrlLog = consoleLogs.find(log => log.includes('API_BASE_URL'));
    console.log('🚀 API URL Log:', apiUrlLog || 'NOT FOUND');
    
    // Find monthly API requests
    const monthlyRequests = responses.filter(r => r.url.includes('monthly'));
    console.log('\n📊 Monthly API Requests:');
    monthlyRequests.forEach(req => {
      console.log(`  ${req.status} ${req.url}`);
      console.log(`  Content-Type: ${req.contentType}`);
    });
    
    // Check what URLs are being called
    const apiRequests = requests.filter(r => 
      r.url.includes('api') || r.url.includes('monthly')
    );
    console.log('\n🌐 API Requests Made:');
    apiRequests.forEach(req => {
      console.log(`  ${req.method} ${req.url}`);
    });
    
    // Test direct backend connection
    console.log('\n🔗 Testing direct backend connection...');
    try {
      const backendResponse = await page.goto('https://hon-automated-reporting.onrender.com/health');
      const backendStatus = backendResponse.status();
      const backendText = await backendResponse.text();
      console.log(`  Backend Health: ${backendStatus}`);
      console.log(`  Response: ${backendText}`);
    } catch (error) {
      console.log(`  Backend Error: ${error.message}`);
    }
    
    // Check if hardcoded URL is in the deployed code
    console.log('\n🔍 Checking deployed JavaScript for hardcoded URL...');
    const jsContent = await page.evaluate(() => {
      // Look for any script tags or loaded JS that might contain our URL
      const scripts = Array.from(document.querySelectorAll('script[src]'));
      return scripts.map(s => s.src);
    });
    console.log('  JS Files:', jsContent);
    
    console.log('\n📋 DIAGNOSIS COMPLETE');
    console.log('='.repeat(50));
    
    if (!apiUrlLog) {
      console.log('❌ ISSUE: Console log not found - deploy didn\'t pick up our changes');
    } else if (monthlyRequests.some(r => r.url.includes('netlify.app'))) {
      console.log('❌ ISSUE: Still calling Netlify instead of Render backend');
    } else if (monthlyRequests.some(r => r.url.includes('onrender.com'))) {
      console.log('✅ SUCCESS: Calling correct backend URL');
    } else {
      console.log('⚠️  UNKNOWN: No monthly requests found');
    }
    
  } catch (error) {
    console.error('❌ Debug failed:', error);
  } finally {
    await browser.close();
  }
}

debugDeployment().catch(console.error);