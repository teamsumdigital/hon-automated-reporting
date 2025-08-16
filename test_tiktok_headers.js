const puppeteer = require('puppeteer');

async function testTikTokHeaders() {
  console.log('🔍 Testing TikTok Dashboard Headers...');
  
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
    
    // Wait for React to load
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Click on TikTok tab
    console.log('🎯 Clicking TikTok tab...');
    await page.click('[data-tab="tiktok"], [aria-label*="TikTok"], [title*="TikTok"]');
    
    // Wait for TikTok dashboard to load
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Find the table with the most headers (likely our TikTok table)
    const tableData = await page.evaluate(() => {
      const tables = document.querySelectorAll('table');
      let bestTable = null;
      let maxHeaders = 0;
      
      tables.forEach(table => {
        const headers = table.querySelectorAll('thead th');
        if (headers.length > maxHeaders) {
          maxHeaders = headers.length;
          bestTable = table;
        }
      });
      
      if (bestTable) {
        const headers = Array.from(bestTable.querySelectorAll('thead th')).map(th => th.textContent.trim());
        
        return {
          className: bestTable.className,
          headers: headers,
          totalRows: bestTable.querySelectorAll('tbody tr').length
        };
      }
      
      return null;
    });
    
    console.log('📊 TikTok Table data:', tableData);
    
    if (tableData) {
      console.log('📋 TikTok headers:', tableData.headers);
      
      const expectedHeaders = ['Month', 'Spend', 'Revenue', 'ROAS', 'CPA', 'CPC', 'CPM'];
      const currentHeaders = tableData.headers;
      
      console.log('🎯 Expected headers:', expectedHeaders);
      console.log('🔍 Headers match:', JSON.stringify(currentHeaders) === JSON.stringify(expectedHeaders));
      
      if (JSON.stringify(currentHeaders) !== JSON.stringify(expectedHeaders)) {
        console.log('❌ TikTok headers mismatch!');
        return false;
      } else {
        console.log('✅ TikTok headers are correct!');
        return true;
      }
    } else {
      console.log('❌ No TikTok table found!');
      return false;
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    return false;
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// Run the test
testTikTokHeaders().then(success => {
  console.log(success ? '🎉 TikTok test passed!' : '💥 TikTok test failed!');
  process.exit(success ? 0 : 1);
});