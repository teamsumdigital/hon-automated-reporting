const puppeteer = require('puppeteer');

async function testTikTokFilteringWithAuth() {
  console.log('TESTING TIKTOK FILTERING WITH AUTHENTICATION');
  console.log('=' * 60);
  
  let browser;
  let page;
  
  try {
    // Launch browser
    browser = await puppeteer.launch({ 
      headless: false,
      defaultViewport: { width: 1400, height: 900 }
    });
    
    page = await browser.newPage();
    
    // Go to dashboard
    console.log('\n1. Loading dashboard and authenticating...');
    await page.goto('http://localhost:3008', { waitUntil: 'networkidle0' });
    
    // Enter password
    await page.waitForSelector('input[type="password"]', { timeout: 10000 });
    await page.type('input[type="password"]', 'HN$7kX9#mQ2vL8pR@2024');
    
    // Click Access Dashboard
    const accessButton = await page.$x("//button[contains(text(), 'Access Dashboard')]");
    if (accessButton.length > 0) {
      await accessButton[0].click();
    } else {
      throw new Error('Access Dashboard button not found');
    }
    
    // Wait for dashboard to load
    await page.waitForSelector('[role="tablist"]', { timeout: 15000 });
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    console.log('Dashboard loaded successfully!');
    
    // Click TikTok Ads tab (3rd tab)
    console.log('\n2. Clicking TikTok Ads tab...');
    const tabs = await page.$$('[role="tablist"] button');
    console.log(`Found ${tabs.length} tabs`);
    
    if (tabs.length > 2) {
      await tabs[2].click(); // TikTok Ads tab (index 2)
      console.log('Clicked TikTok Ads tab');
    } else {
      throw new Error('TikTok Ads tab not found');
    }
    
    // Wait for TikTok data to load
    await page.waitForSelector('table', { timeout: 15000 });
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Get July 2024 spend with NO filters
    console.log('\n3. Getting July 2024 spend with NO filters...');
    const julyNoFilters = await page.evaluate(() => {
      const rows = Array.from(document.querySelectorAll('tr'));
      const julyRow = rows.find(row => {
        const text = row.textContent || '';
        return text.includes('July') && !text.includes('2025');
      });
      
      if (julyRow) {
        const cells = julyRow.querySelectorAll('td');
        const spendCell = cells[1]; // 2nd column should be spend
        return spendCell ? spendCell.textContent.trim() : 'Spend cell not found';
      }
      return 'July row not found';
    });
    
    console.log(`July 2024 spend (no filters): ${julyNoFilters}`);
    
    // Now select multiple categories
    console.log('\n4. Selecting multiple categories...');
    
    const categories = ['Play Mats', 'Standing Mats', 'Tumbling Mats', 'Play Furniture', 'Multi Category'];
    let selectedCount = 0;
    
    for (const category of categories) {
      try {
        const button = await page.$x(`//button[contains(text(), "${category}")]`);
        if (button.length > 0) {
          await button[0].click();
          console.log(`✓ Selected ${category}`);
          selectedCount++;
          await new Promise(resolve => setTimeout(resolve, 1000));
        } else {
          console.log(`✗ Could not find button for ${category}`);
        }
      } catch (e) {
        console.log(`✗ Error selecting ${category}: ${e.message}`);
      }
    }
    
    console.log(`Selected ${selectedCount} categories`);
    
    // Wait for filtered data to load
    console.log('\n5. Waiting for filtered data to load...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Get July 2024 spend with filters
    const julyWithFilters = await page.evaluate(() => {
      const rows = Array.from(document.querySelectorAll('tr'));
      const julyRow = rows.find(row => {
        const text = row.textContent || '';
        return text.includes('July') && !text.includes('2025');
      });
      
      if (julyRow) {
        const cells = julyRow.querySelectorAll('td');
        const spendCell = cells[1]; // 2nd column should be spend
        return spendCell ? spendCell.textContent.trim() : 'Spend cell not found';
      }
      return 'July row not found';
    });
    
    console.log(`July 2024 spend (with filters): ${julyWithFilters}`);
    
    // Compare results
    console.log('\n6. COMPARISON RESULTS:');
    console.log('=' * 40);
    console.log(`No filters:   ${julyNoFilters}`);
    console.log(`With filters: ${julyWithFilters}`);
    
    // Extract numeric values for comparison
    const extractNumber = (str) => {
      const match = str.match(/\$?([\d,]+)/);
      return match ? parseInt(match[1].replace(/,/g, '')) : 0;
    };
    
    const noFilterAmount = extractNumber(julyNoFilters);
    const filteredAmount = extractNumber(julyWithFilters);
    
    console.log(`\nNumeric comparison:`);
    console.log(`No filters:   $${noFilterAmount.toLocaleString()}`);
    console.log(`With filters: $${filteredAmount.toLocaleString()}`);
    console.log(`Difference:   $${(filteredAmount - noFilterAmount).toLocaleString()}`);
    
    if (filteredAmount > noFilterAmount) {
      console.log('\n🚨 BUG CONFIRMED - STILL EXISTS!');
      console.log('Filtered amount is HIGHER than no filter amount');
      console.log('The fix did NOT work - frontend issue persists');
    } else if (filteredAmount < noFilterAmount) {
      console.log('\n✅ BUG IS FIXED!');
      console.log('Filtered amount is correctly LOWER than no filter amount');
      console.log('Filtering is working as expected');
    } else {
      console.log('\n⚠️ AMOUNTS ARE EQUAL');
      console.log('This might indicate no filtering occurred or other issues');
    }
    
    // Take screenshot for evidence
    await page.screenshot({ 
      path: 'tiktok_filtering_test_result.png', 
      fullPage: true 
    });
    console.log('\nScreenshot saved: tiktok_filtering_test_result.png');
    
    // Keep browser open for manual verification
    console.log('\nBrowser staying open for manual verification (30 seconds)...');
    await new Promise(resolve => setTimeout(resolve, 30000));
    
  } catch (error) {
    console.error('Error during testing:', error);
    
    // Take error screenshot
    if (page) {
      await page.screenshot({ 
        path: 'tiktok_test_error.png', 
        fullPage: true 
      });
      console.log('Error screenshot saved: tiktok_test_error.png');
    }
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// Run the test
testTikTokFilteringWithAuth();