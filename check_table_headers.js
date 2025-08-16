const puppeteer = require('puppeteer');

async function checkTableHeaders() {
  console.log('🔍 Checking table headers in dashboard...');
  
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
    
    // Find the table with the most headers (likely our pivot table)
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
        const firstRow = bestTable.querySelector('tbody tr');
        const firstRowData = firstRow ? Array.from(firstRow.querySelectorAll('td')).map(td => td.textContent.trim()) : [];
        
        return {
          className: bestTable.className,
          headers: headers,
          firstRowData: firstRowData,
          totalRows: bestTable.querySelectorAll('tbody tr').length
        };
      }
      
      return null;
    });
    
    console.log('📊 Table data:', tableData);
    
    if (tableData) {
      console.log('📋 Current headers:', tableData.headers);
      
      const expectedHeaders = ['Month', 'Spend', 'Revenue', 'ROAS', 'CPA', 'CPC', 'CPM'];
      const currentHeaders = tableData.headers;
      
      console.log('🎯 Expected headers:', expectedHeaders);
      console.log('🔍 Headers match:', JSON.stringify(currentHeaders) === JSON.stringify(expectedHeaders));
      
      if (JSON.stringify(currentHeaders) !== JSON.stringify(expectedHeaders)) {
        console.log('❌ Headers mismatch detected!');
        console.log('Need to fix the frontend...');
        return false;
      } else {
        console.log('✅ Headers are correct!');
        return true;
      }
    } else {
      console.log('❌ No table found!');
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

// Run the check
checkTableHeaders().then(success => {
  console.log(success ? '🎉 Test passed!' : '💥 Test failed!');
  process.exit(success ? 0 : 1);
});