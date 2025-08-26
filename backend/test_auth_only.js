const puppeteer = require('puppeteer');

async function testAuthOnly() {
  let browser;
  try {
    browser = await puppeteer.launch({ 
      headless: false,
      defaultViewport: { width: 1400, height: 900 }
    });
    
    const page = await browser.newPage();
    
    console.log('Loading page...');
    await page.goto('http://localhost:3007', { waitUntil: 'networkidle0' });
    
    console.log('Looking for password field...');
    await page.waitForSelector('input[type="password"]', { timeout: 5000 });
    console.log('Found password field');
    
    console.log('Entering password...');
    await page.type('input[type="password"]', 'HN$7kX9#mQ2vL8pR@2024');
    
    console.log('Looking for submit button...');
    const buttons = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('button')).map(btn => btn.textContent?.trim());
    });
    console.log('Available buttons:', buttons);
    
    console.log('Clicking submit button...');
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const submitBtn = buttons.find(btn => 
        btn.textContent && (
          btn.textContent.includes('Access') || 
          btn.textContent.includes('Submit') ||
          btn.textContent.includes('Login')
        )
      );
      if (submitBtn) {
        submitBtn.click();
        return true;
      }
      return false;
    });
    
    console.log('Waiting for dashboard to load...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Check if we're authenticated
    const isAuthenticated = await page.evaluate(() => {
      // Look for dashboard elements
      const hasDashboard = document.querySelector('[role="tablist"]') || 
                          document.querySelector('table') ||
                          document.querySelector('.dashboard') ||
                          document.body.textContent.includes('Meta Ads') ||
                          document.body.textContent.includes('TikTok Ads');
      return hasDashboard ? true : false;
    });
    
    if (isAuthenticated) {
      console.log('✅ Authentication successful! Dashboard loaded.');
      
      // Look for tabs
      const tabs = await page.evaluate(() => {
        const tabElements = Array.from(document.querySelectorAll('button'));
        return tabElements
          .map(btn => btn.textContent?.trim())
          .filter(text => text && (
            text.includes('Meta') || 
            text.includes('Google') || 
            text.includes('TikTok')
          ));
      });
      console.log('Found tabs:', tabs);
      
    } else {
      console.log('❌ Authentication failed or dashboard not loaded');
    }
    
    await page.screenshot({ path: 'auth_test.png', fullPage: true });
    console.log('Screenshot saved: auth_test.png');
    
    // Keep browser open to see what happened
    console.log('Keeping browser open for inspection...');
    await new Promise(resolve => setTimeout(resolve, 15000));
    
  } catch (error) {
    console.error('Error during auth test:', error);
  } finally {
    if (browser) await browser.close();
  }
}

testAuthOnly();