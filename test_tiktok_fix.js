const puppeteer = require('puppeteer');

async function testTikTokFix() {
  console.log('🎯 Testing TikTok dashboard fix...');
  
  // Wait for deployment
  console.log('⏳ Waiting 60 seconds for Netlify to deploy...');
  await new Promise(resolve => setTimeout(resolve, 60000));
  
  const browser = await puppeteer.launch({ headless: false });
  
  try {
    const page = await browser.newPage();
    
    // Capture network requests
    const requests = [];
    page.on('response', (response) => {
      if (response.url().includes('tiktok-reports') || response.url().includes('api')) {
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
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    console.log('🎯 Clicking TikTok tab...');
    await page.waitForSelector('button[title="TikTok advertising data"]');
    await page.click('button[title="TikTok advertising data"]');
    
    console.log('⏳ Waiting for TikTok dashboard to load...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Check results
    const tiktokRequests = requests.filter(r => r.url.includes('tiktok-reports'));
    const renderRequests = requests.filter(r => r.url.includes('onrender.com'));
    const netlifyApiRequests = requests.filter(r => 
      r.url.includes('netlify.app') && r.url.includes('api')
    );
    
    console.log('\n📊 TIKTOK TEST RESULTS:');
    console.log('='.repeat(50));
    
    if (tiktokRequests.length > 0) {
      console.log('✅ TikTok API requests made:');
      tiktokRequests.forEach(req => {
        console.log(`   ${req.status} ${req.url}`);
      });
    } else {
      console.log('❌ No TikTok API requests found');
    }
    
    if (renderRequests.some(r => r.url.includes('tiktok-reports'))) {
      console.log('✅ SUCCESS! TikTok dashboard calling Render backend!');
    } else if (netlifyApiRequests.some(r => r.url.includes('tiktok'))) {
      console.log('❌ TikTok dashboard still calling Netlify instead of Render');
    } else {
      console.log('⚠️  No clear TikTok API requests detected');
    }
    
    if (renderRequests.length > 0 && 
        renderRequests.some(r => r.url.includes('tiktok-reports')) &&
        !netlifyApiRequests.some(r => r.url.includes('tiktok'))) {
      console.log('\n🎉 PERFECT! TikTok dashboard is now correctly calling Render backend!');
      console.log('🚀 All dashboards should be working correctly now!');
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    await browser.close();
  }
}

testTikTokFix();