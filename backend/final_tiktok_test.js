const puppeteer = require('puppeteer');

async function finalTikTokTest() {
  let browser;
  try {
    browser = await puppeteer.launch({ 
      headless: false,
      defaultViewport: { width: 1400, height: 900 }
    });
    
    const page = await browser.newPage();
    
    console.log('🔐 AUTHENTICATING...');
    await page.goto('http://localhost:3007', { waitUntil: 'networkidle0' });
    await page.waitForSelector('input[type="password"]');
    await page.type('input[type="password"]', 'HN$7kX9#mQ2vL8pR@2024');
    
    await page.evaluate(() => {
      const button = Array.from(document.querySelectorAll('button')).find(btn => 
        btn.textContent.includes('Access Dashboard')
      );
      if (button) button.click();
    });
    
    console.log('⏳ LOADING DASHBOARD...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    console.log('🎯 CLICKING TIKTOK TAB...');
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const tiktokButton = buttons.find(btn => 
        btn.textContent && btn.textContent.includes('TikTok Ads')
      );
      if (tiktokButton) tiktokButton.click();
    });
    
    console.log('📊 WAITING FOR TIKTOK DATA...');
    await new Promise(resolve => setTimeout(resolve, 8000));
    
    console.log('📈 GETTING JULY 2024 (NO FILTERS)...');
    const julyNoFilter = await page.evaluate(() => {
      const rows = Array.from(document.querySelectorAll('tr'));
      const julyRow = rows.find(row => {
        const text = row.textContent || '';
        return text.includes('July') && !text.includes('2025');
      });
      
      if (julyRow) {
        const cells = Array.from(julyRow.querySelectorAll('td'));
        if (cells.length > 1) {
          return cells[1].textContent.trim(); // Spend column
        }
      }
      return 'July row not found';
    });
    
    console.log(`📊 July (no filters): ${julyNoFilter}`);
    
    console.log('🔍 SELECTING CATEGORIES...');
    const categories = ['Play Mats', 'Standing Mats', 'Tumbling Mats', 'Play Furniture', 'Multi Category'];
    let selectedCount = 0;
    
    for (const category of categories) {
      const clicked = await page.evaluate((cat) => {
        const buttons = Array.from(document.querySelectorAll('button'));
        const catButton = buttons.find(btn => 
          btn.textContent && btn.textContent.trim() === cat
        );
        if (catButton && !catButton.classList.contains('bg-pink-600')) { // Not already selected
          catButton.click();
          return true;
        }
        return false;
      }, category);
      
      if (clicked) {
        console.log(`  ✅ Selected ${category}`);
        selectedCount++;
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait for API call
      } else {
        console.log(`  ❌ Could not select ${category}`);
      }
    }
    
    console.log(`📝 Selected ${selectedCount} categories`);
    console.log('⏳ WAITING FOR FILTERED DATA...');
    await new Promise(resolve => setTimeout(resolve, 8000));
    
    console.log('📈 GETTING JULY 2024 (WITH FILTERS)...');
    const julyWithFilter = await page.evaluate(() => {
      const rows = Array.from(document.querySelectorAll('tr'));
      const julyRow = rows.find(row => {
        const text = row.textContent || '';
        return text.includes('July') && !text.includes('2025');
      });
      
      if (julyRow) {
        const cells = Array.from(julyRow.querySelectorAll('td'));
        if (cells.length > 1) {
          return cells[1].textContent.trim(); // Spend column
        }
      }
      return 'July row not found';
    });
    
    console.log(`📊 July (with filters): ${julyWithFilter}`);
    
    // FINAL COMPARISON
    console.log('\n' + '='.repeat(50));
    console.log('🔍 FINAL COMPARISON RESULTS');
    console.log('='.repeat(50));
    console.log(`No filters:   ${julyNoFilter}`);
    console.log(`With filters: ${julyWithFilter}`);
    
    const extractNumber = (str) => {
      const match = str.match(/\$?([\d,]+)/);
      return match ? parseInt(match[1].replace(/,/g, '')) : 0;
    };
    
    const noFilterNum = extractNumber(julyNoFilter);
    const withFilterNum = extractNumber(julyWithFilter);
    
    console.log(`\nNumerical comparison:`);
    console.log(`No filters:   $${noFilterNum.toLocaleString()}`);
    console.log(`With filters: $${withFilterNum.toLocaleString()}`);
    console.log(`Difference:   $${(withFilterNum - noFilterNum).toLocaleString()}`);
    
    if (withFilterNum > noFilterNum) {
      console.log('\n🚨 BUG CONFIRMED - STILL EXISTS!');
      console.log('   Filtered amount is HIGHER than unfiltered amount');
      console.log('   This is mathematically impossible - the fix did NOT work');
    } else if (withFilterNum < noFilterNum) {
      console.log('\n✅ BUG IS FIXED!');
      console.log('   Filtered amount is correctly LOWER than unfiltered amount');
      console.log('   The TikTok filtering is now working properly');
    } else {
      console.log('\n⚠️  VALUES ARE EQUAL');
      console.log('   This might indicate no data or no filtering occurred');
    }
    
    await page.screenshot({ 
      path: 'tiktok_filtering_final_test.png', 
      fullPage: true 
    });
    console.log('\n📷 Screenshot saved: tiktok_filtering_final_test.png');
    
    // Keep browser open for manual verification
    console.log('\n👀 Browser staying open for manual verification (30 seconds)...');
    await new Promise(resolve => setTimeout(resolve, 30000));
    
  } catch (error) {
    console.error('💥 Error during test:', error);
  } finally {
    if (browser) await browser.close();
  }
}

finalTikTokTest();