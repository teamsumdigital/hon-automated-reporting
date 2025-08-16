const puppeteer = require('puppeteer');

async function checkApiAndComponent() {
  console.log('🔍 Checking API vs Component rendering...');
  
  let browser;
  try {
    browser = await puppeteer.launch({ 
      headless: false,
      defaultViewport: null,
      args: ['--start-maximized']
    });
    
    const page = await browser.newPage();
    
    // Enable request interception to see API calls
    await page.setRequestInterception(true);
    
    const apiResponses = [];
    
    page.on('request', request => {
      request.continue();
    });
    
    page.on('response', async response => {
      if (response.url().includes('/api/reports/dashboard')) {
        try {
          const responseBody = await response.text();
          console.log('📡 API Response received');
          
          const data = JSON.parse(responseBody);
          if (data.pivot_data && data.pivot_data[0]) {
            console.log('📊 First pivot data item:', data.pivot_data[0]);
            console.log('📊 Pivot data keys:', Object.keys(data.pivot_data[0]));
          }
        } catch (e) {
          console.log('❌ Could not parse API response');
        }
      }
    });
    
    // Navigate to the dashboard
    console.log('📄 Navigating to dashboard...');
    await page.goto('http://localhost:3007', { waitUntil: 'networkidle0' });
    
    // Wait for React to load and API call to complete
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Check what the frontend is actually rendering
    const frontendData = await page.evaluate(() => {
      // Try to find any debug info about the data being passed to the table
      const tables = document.querySelectorAll('table');
      if (tables.length > 0) {
        const table = tables[0];
        const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
        
        // Try to get the first data row to see what data is being rendered
        const firstDataRow = table.querySelector('tbody tr');
        const firstRowCells = firstDataRow ? Array.from(firstDataRow.querySelectorAll('td')).map(td => td.textContent.trim()) : [];
        
        return {
          headers,
          firstRowCells,
          tableCount: tables.length
        };
      }
      return null;
    });
    
    console.log('🖥️ Frontend rendering:', frontendData);
    
    // Take a screenshot
    await page.screenshot({ path: 'api_vs_component.png', fullPage: true });
    console.log('📸 Screenshot saved');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

checkApiAndComponent();