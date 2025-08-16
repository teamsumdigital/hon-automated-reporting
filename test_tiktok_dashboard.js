const puppeteer = require('puppeteer');

(async () => {
  console.log('🚀 Starting TikTok Dashboard Test...');
  
  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: { width: 1920, height: 1080 },
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();
    
    console.log('📱 Navigating to TikTok Dashboard...');
    await page.goto('http://localhost:3007/tiktok', { 
      waitUntil: 'networkidle0',
      timeout: 30000
    });

    console.log('⏳ Waiting for dashboard to load...');
    // Wait for the main content to load
    await page.waitForSelector('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-4', { timeout: 15000 });
    
    // Wait for the table to load
    await page.waitForSelector('table', { timeout: 10000 });

    // Wait a bit more for any data to populate
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    console.log('📸 Taking screenshot...');
    await page.screenshot({ 
      path: 'tiktok-dashboard-final.png',
      fullPage: true
    });
    
    console.log('✅ Screenshot saved as tiktok-dashboard-final.png');
    
    // Let's also check if data is loading properly
    const hasData = await page.evaluate(() => {
      const table = document.querySelector('table tbody');
      return table && table.children.length > 0;
    });
    
    console.log(`📊 Dashboard has data: ${hasData}`);
    
    if (hasData) {
      console.log('✨ TikTok Dashboard is working with data!');
    } else {
      console.log('⚠️ Dashboard loaded but no data visible yet');
    }

  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await browser.close();
    console.log('🏁 Test completed');
  }
})();