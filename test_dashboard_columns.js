const puppeteer = require('puppeteer');

async function testDashboardColumns() {
  console.log('🚀 Starting Puppeteer test for dashboard columns...');
  
  let browser;
  try {
    browser = await puppeteer.launch({ 
      headless: false,
      defaultViewport: null,
      args: ['--start-maximized']
    });
    
    const page = await browser.newPage();
    
    // Navigate to the dashboard
    console.log('📄 Navigating to dashboard...');
    await page.goto('http://localhost:3007', { waitUntil: 'networkidle0' });
    
    // Wait for the table to load
    console.log('⏳ Waiting for pivot table to load...');
    await page.waitForSelector('.pivot-table', { timeout: 10000 });
    
    // Get table headers
    console.log('📊 Extracting table headers...');
    const headers = await page.evaluate(() => {
      const headerCells = document.querySelectorAll('.pivot-table thead th');
      return Array.from(headerCells).map(cell => cell.textContent.trim());
    });
    
    console.log('📋 Current table headers:', headers);
    
    // Expected headers
    const expectedHeaders = ['Month', 'Spend', 'Revenue', 'ROAS', 'CPA', 'CPC', 'CPM'];
    
    // Check if headers match
    const headersMatch = JSON.stringify(headers) === JSON.stringify(expectedHeaders);
    
    if (headersMatch) {
      console.log('✅ Headers match expected structure!');
      return true;
    } else {
      console.log('❌ Headers do not match!');
      console.log('Expected:', expectedHeaders);
      console.log('Actual:', headers);
      
      // Take a screenshot for debugging
      await page.screenshot({ path: 'dashboard_debug.png', fullPage: true });
      console.log('📸 Screenshot saved as dashboard_debug.png');
      
      return false;
    }
    
  } catch (error) {
    console.error('❌ Error during test:', error.message);
    return false;
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// Run the test
testDashboardColumns().then(success => {
  if (success) {
    console.log('🎉 Test passed!');
    process.exit(0);
  } else {
    console.log('💥 Test failed!');
    process.exit(1);
  }
});