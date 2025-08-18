const puppeteer = require('puppeteer');

async function quickTest() {
  console.log('🔍 Quick deployment test...');
  
  const browser = await puppeteer.launch({ headless: false });
  
  try {
    const page = await browser.newPage();
    
    // Capture console logs
    const consoleLogs = [];
    page.on('console', (msg) => {
      console.log(`CONSOLE: ${msg.text()}`);
    });
    
    // Capture network requests
    page.on('response', (response) => {
      if (response.url().includes('monthly') || response.url().includes('api')) {
        console.log(`NETWORK: ${response.status()} ${response.url()}`);
      }
    });
    
    console.log('📱 Loading site...');
    await page.goto('https://hon-automated-reporting.netlify.app', {
      waitUntil: 'networkidle0'
    });
    
    console.log('🔐 Entering password...');
    await page.waitForSelector('input[type="password"]');
    await page.type('input[type="password"]', 'HN$7kX9#mQ2vL8pR@2024');
    await page.click('button[type="submit"]');
    
    console.log('⏳ Waiting for dashboard...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    console.log('✅ Test complete - check output above');
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    await browser.close();
  }
}

quickTest();