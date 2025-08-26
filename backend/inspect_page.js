const puppeteer = require('puppeteer');

async function inspectPage() {
  let browser;
  let page;
  
  try {
    browser = await puppeteer.launch({ 
      headless: false,
      defaultViewport: { width: 1400, height: 900 }
    });
    
    page = await browser.newPage();
    
    console.log('Loading page...');
    await page.goto('http://localhost:3008', { waitUntil: 'networkidle0' });
    
    // Wait a bit for the page to fully load
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Get page title and check what tabs exist
    const title = await page.title();
    console.log('Page title:', title);
    
    // Get all buttons
    const buttons = await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      return btns.map(btn => btn.textContent?.trim()).slice(0, 10); // First 10 buttons
    });
    console.log('First 10 buttons found:', buttons);
    
    // Check if there are tabs
    const tabs = await page.evaluate(() => {
      const tabElements = document.querySelectorAll('[role="tab"], .tab, button[data-tab]');
      return Array.from(tabElements).map(tab => tab.textContent?.trim());
    });
    console.log('Tab elements found:', tabs);
    
    // Look for TikTok specifically
    const tiktokElements = await page.evaluate(() => {
      const elements = document.querySelectorAll('*');
      const tiktokElements = [];
      elements.forEach(el => {
        if (el.textContent && el.textContent.toLowerCase().includes('tiktok')) {
          tiktokElements.push({
            tag: el.tagName,
            text: el.textContent.trim().substring(0, 50),
            class: el.className
          });
        }
      });
      return tiktokElements.slice(0, 5); // First 5 matches
    });
    console.log('TikTok elements found:', tiktokElements);
    
    // Take a screenshot
    await page.screenshot({ 
      path: 'page_inspection.png', 
      fullPage: true 
    });
    console.log('Screenshot saved as: page_inspection.png');
    
    // Keep browser open for manual inspection
    console.log('Browser will stay open for manual inspection...');
    await new Promise(resolve => setTimeout(resolve, 30000)); // Wait 30 seconds
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

inspectPage();