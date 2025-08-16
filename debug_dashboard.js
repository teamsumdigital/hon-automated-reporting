const puppeteer = require('puppeteer');

async function debugDashboard() {
  console.log('🔍 Debugging dashboard loading...');
  
  let browser;
  try {
    browser = await puppeteer.launch({ 
      headless: false,
      defaultViewport: null,
      args: ['--start-maximized']
    });
    
    const page = await browser.newPage();
    
    // Listen for console messages
    page.on('console', msg => {
      console.log('🖥️ Browser console:', msg.text());
    });
    
    // Listen for errors
    page.on('pageerror', error => {
      console.log('❌ Page error:', error.message);
    });
    
    // Navigate to the dashboard
    console.log('📄 Navigating to dashboard...');
    await page.goto('http://localhost:3007', { waitUntil: 'networkidle0' });
    
    // Wait a bit for React to load
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Check what's actually on the page
    console.log('📄 Page title:', await page.title());
    
    // Look for any tables
    const tables = await page.evaluate(() => {
      const tables = document.querySelectorAll('table');
      return Array.from(tables).map(table => ({
        className: table.className,
        headerCount: table.querySelectorAll('th').length,
        rowCount: table.querySelectorAll('tr').length
      }));
    });
    
    console.log('📊 Tables found:', tables);
    
    // Look for the specific pivot-table class
    const pivotTableExists = await page.evaluate(() => {
      return document.querySelector('.pivot-table') !== null;
    });
    
    console.log('🎯 Pivot table exists:', pivotTableExists);
    
    // Get all elements with table-related classes
    const tableElements = await page.evaluate(() => {
      const elements = document.querySelectorAll('[class*="table"], [class*="pivot"]');
      return Array.from(elements).map(el => ({
        tagName: el.tagName,
        className: el.className,
        textContent: el.textContent?.substring(0, 100)
      }));
    });
    
    console.log('🔍 Table-related elements:', tableElements);
    
    // Check if there are any loading states
    const loadingElements = await page.evaluate(() => {
      const loading = document.querySelectorAll('[class*="loading"], [class*="spinner"], [class*="animate"]');
      return Array.from(loading).map(el => el.className);
    });
    
    console.log('⏳ Loading elements:', loadingElements);
    
    // Take a screenshot
    await page.screenshot({ path: 'debug_dashboard.png', fullPage: true });
    console.log('📸 Screenshot saved as debug_dashboard.png');
    
    // Wait for user to see what's happening
    await new Promise(resolve => setTimeout(resolve, 5000));
    
  } catch (error) {
    console.error('❌ Error during debug:', error.message);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// Run the debug
debugDashboard();