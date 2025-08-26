const puppeteer = require('puppeteer');

async function testTikTokFiltering() {
  console.log('TESTING TIKTOK FILTERING WITH PUPPETEER');
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
    
    // Go to TikTok dashboard
    console.log('\n1. Loading TikTok Dashboard...');
    await page.goto('http://localhost:3008', { waitUntil: 'networkidle0' });
    
    // Click TikTok Ads tab
    await page.waitForSelector('[role="tablist"] button', { timeout: 10000 });
    const tabs = await page.$$('[role="tablist"] button');
    
    // Click the TikTok Ads tab (should be the 3rd tab - index 2)
    if (tabs.length > 2) {
      await tabs[2].click(); // TikTok Ads tab
    } else {
      throw new Error('TikTok Ads tab not found');
    }
    
    // Wait for data to load
    await page.waitForSelector('table', { timeout: 15000 });
    await page.waitForTimeout(3000); // Give data time to load
    
    // Get July 2024 spend with NO filters
    console.log('\n2. Testing NO FILTERS (all categories)...');
    const julyNoFilters = await page.evaluate(() => {
      const julyRow = Array.from(document.querySelectorAll('tr')).find(row => 
        row.textContent.includes('July') && !row.textContent.includes('2025')
      );
      if (julyRow) {
        const spendCell = julyRow.querySelector('td:nth-child(2)');
        return spendCell ? spendCell.textContent.trim() : 'Not found';
      }
      return 'July row not found';
    });
    
    console.log(`July 2024 spend (no filters): ${julyNoFilters}`);
    
    // Now select multiple categories
    console.log('\n3. Selecting multiple categories...');
    
    // Find and click category buttons (they should be in the filter sidebar)
    const categoryButtons = await page.$$('button');
    
    const categories = ['Play Mats', 'Standing Mats', 'Tumbling Mats', 'Play Furniture', 'Multi Category'];
    
    for (const category of categories) {
      const button = await page.$x(`//button[contains(text(), "${category}")]`);
      if (button.length > 0) {
        await button[0].click();
        console.log(`Selected ${category}`);
        await page.waitForTimeout(500);
      } else {
        console.log(`Could not find button for ${category}`);
      }
    }
    
    // Wait for data to reload after filtering
    await page.waitForTimeout(3000);
    
    // Get July 2024 spend with filters
    console.log('\n4. Testing WITH FILTERS...');
    const julyWithFilters = await page.evaluate(() => {
      const julyRow = Array.from(document.querySelectorAll('tr')).find(row => 
        row.textContent.includes('July') && !row.textContent.includes('2025')
      );
      if (julyRow) {
        const spendCell = julyRow.querySelector('td:nth-child(2)');
        return spendCell ? spendCell.textContent.trim() : 'Not found';
      }
      return 'July row not found';
    });
    
    console.log(`July 2024 spend (with filters): ${julyWithFilters}`);
    
    // Compare results
    console.log('\n5. COMPARISON:');
    console.log(`No filters:   ${julyNoFilters}`);
    console.log(`With filters: ${julyWithFilters}`);
    
    // Extract numeric values for comparison
    const extractNumber = (str) => {
      const match = str.match(/\$?([\d,]+)/);
      return match ? parseInt(match[1].replace(/,/g, '')) : 0;
    };
    
    const noFilterAmount = extractNumber(julyNoFilters);
    const filteredAmount = extractNumber(julyWithFilters);
    
    if (filteredAmount > noFilterAmount) {
      console.log('\n🚨 BUG STILL EXISTS!');
      console.log(`Filtered amount (${filteredAmount}) > No filter amount (${noFilterAmount})`);
      console.log('The fix did not work.');
    } else if (filteredAmount < noFilterAmount) {
      console.log('\n✅ BUG IS FIXED!');
      console.log(`Filtered amount (${filteredAmount}) < No filter amount (${noFilterAmount})`);
      console.log('Filtering is working correctly.');
    } else {
      console.log('\n⚠️ AMOUNTS ARE EQUAL');
      console.log('This might indicate an issue with filtering or data.');
    }
    
    // Take screenshot for verification
    await page.screenshot({ 
      path: 'tiktok_filtering_test.png', 
      fullPage: true 
    });
    console.log('\nScreenshot saved as: tiktok_filtering_test.png');
    
  } catch (error) {
    console.error('Error during testing:', error);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// Run the test
testTikTokFiltering();