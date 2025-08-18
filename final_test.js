const puppeteer = require('puppeteer');

async function finalTest() {
  console.log('🏁 FINAL TEST: Checking if ModernDashboard fix works...');
  
  // Wait a bit for deployment
  console.log('⏳ Waiting 60 seconds for Netlify to deploy...');
  await new Promise(resolve => setTimeout(resolve, 60000));
  
  const browser = await puppeteer.launch({ headless: false });
  
  try {
    const page = await browser.newPage();
    
    // Capture network requests
    const requests = [];
    page.on('response', (response) => {
      if (response.url().includes('monthly') || response.url().includes('api')) {
        requests.push({
          url: response.url(),
          status: response.status(),
          size: response.headers()['content-length'] || 'unknown'
        });
        console.log(`NETWORK: ${response.status()} ${response.url()}`);
      }
    });
    
    console.log('📱 Loading HON dashboard...');
    await page.goto('https://hon-automated-reporting.netlify.app', {
      waitUntil: 'networkidle0'
    });
    
    console.log('🔐 Logging in...');
    await page.waitForSelector('input[type="password"]');
    await page.type('input[type="password"]', 'HN$7kX9#mQ2vL8pR@2024');
    await page.click('button[type="submit"]');
    
    console.log('⏳ Waiting for dashboard to load...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Check results
    const renderRequests = requests.filter(r => r.url.includes('onrender.com'));
    const netlifyApiRequests = requests.filter(r => 
      r.url.includes('netlify.app') && r.url.includes('api')
    );
    
    console.log('\n📊 RESULTS:');
    console.log('='.repeat(50));
    
    if (renderRequests.length > 0) {
      console.log('✅ SUCCESS! Found requests to Render backend:');
      renderRequests.forEach(req => {
        console.log(`   ${req.status} ${req.url}`);
      });
    } else {
      console.log('❌ No requests to Render backend found');
    }
    
    if (netlifyApiRequests.length > 0) {
      console.log('⚠️  Still found requests to Netlify API:');
      netlifyApiRequests.forEach(req => {
        console.log(`   ${req.status} ${req.url}`);
      });
    } else {
      console.log('✅ No incorrect Netlify API requests');
    }
    
    if (renderRequests.length > 0 && netlifyApiRequests.length === 0) {
      console.log('\n🎉 PERFECT! Frontend is now correctly calling the Render backend!');
      console.log('🚀 Your HON automated reporting system is FULLY OPERATIONAL!');
    } else {
      console.log('\n⚠️  Still needs attention - check the network requests above');
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    await browser.close();
  }
}

finalTest();