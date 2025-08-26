const puppeteer = require('puppeteer');

async function simpleTikTokTest() {
  let browser;
  try {
    browser = await puppeteer.launch({ 
      headless: false,
      defaultViewport: { width: 1400, height: 900 }
    });
    
    const page = await browser.newPage();
    
    console.log('1. Loading page...');
    await page.goto('http://localhost:3008', { waitUntil: 'networkidle0' });
    
    console.log('2. Entering password...');
    await page.waitForSelector('input[type="password"]');
    await page.type('input[type="password"]', 'HN$7kX9#mQ2vL8pR@2024');
    
    console.log('3. Clicking Access Dashboard...');
    await page.evaluate(() => {
      const button = Array.from(document.querySelectorAll('button')).find(btn => 
        btn.textContent.includes('Access Dashboard')
      );
      if (button) button.click();
    });
    
    console.log('4. Waiting for dashboard...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    console.log('5. Looking for tabs...');
    const tabs = await page.evaluate(() => {
      const allButtons = Array.from(document.querySelectorAll('button'));
      return allButtons.map(btn => btn.textContent?.trim()).filter(text => text);
    });
    console.log('Available buttons/tabs:', tabs.slice(0, 10));
    
    console.log('6. Clicking TikTok tab...');
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const tiktokButton = buttons.find(btn => 
        btn.textContent && btn.textContent.toLowerCase().includes('tiktok')
      );
      if (tiktokButton) {
        console.log('Found TikTok button, clicking...');
        tiktokButton.click();
      }
    });
    
    console.log('7. Waiting for TikTok data...');
    await new Promise(resolve => setTimeout(resolve, 8000));
    
    console.log('8. Getting July data (no filters)...');
    const julyNoFilter = await page.evaluate(() => {
      const rows = Array.from(document.querySelectorAll('tr'));
      const julyRow = rows.find(row => {
        const text = row.textContent || '';
        return text.includes('July') && !text.includes('2025');
      });
      
      if (julyRow) {
        const cells = Array.from(julyRow.querySelectorAll('td'));
        const spendCell = cells[1]; // 2nd column
        return spendCell ? spendCell.textContent.trim() : 'No spend cell';
      }
      return 'No July row found';
    });
    
    console.log('July (no filters):', julyNoFilter);
    
    console.log('9. Selecting categories...');
    const categories = ['Play Mats', 'Standing Mats', 'Tumbling Mats'];
    
    for (const category of categories) {
      const clicked = await page.evaluate((cat) => {
        const buttons = Array.from(document.querySelectorAll('button'));
        const catButton = buttons.find(btn => 
          btn.textContent && btn.textContent.trim() === cat
        );
        if (catButton) {
          catButton.click();
          return true;
        }
        return false;
      }, category);
      
      if (clicked) {
        console.log(`✓ Selected ${category}`);
        await new Promise(resolve => setTimeout(resolve, 2000));
      } else {
        console.log(`✗ Could not find ${category}`);
      }
    }
    
    console.log('10. Waiting for filtered data...');
    await new Promise(resolve => setTimeout(resolve, 8000));
    
    console.log('11. Getting July data (with filters)...');
    const julyWithFilter = await page.evaluate(() => {
      const rows = Array.from(document.querySelectorAll('tr'));
      const julyRow = rows.find(row => {
        const text = row.textContent || '';
        return text.includes('July') && !text.includes('2025');
      });
      
      if (julyRow) {
        const cells = Array.from(julyRow.querySelectorAll('td'));
        const spendCell = cells[1]; // 2nd column
        return spendCell ? spendCell.textContent.trim() : 'No spend cell';
      }
      return 'No July row found';
    });
    
    console.log('July (with filters):', julyWithFilter);
    
    // Compare
    console.log('\n=== COMPARISON ===');
    console.log('No filters:  ', julyNoFilter);
    console.log('With filters:', julyWithFilter);
    
    const extractNumber = (str) => {
      const match = str.match(/\$?([\d,]+)/);
      return match ? parseInt(match[1].replace(/,/g, '')) : 0;
    };
    
    const noFilterNum = extractNumber(julyNoFilter);
    const withFilterNum = extractNumber(julyWithFilter);
    
    console.log(`\nNumerical:`);
    console.log(`No filters:   $${noFilterNum.toLocaleString()}`);
    console.log(`With filters: $${withFilterNum.toLocaleString()}`);
    
    if (withFilterNum > noFilterNum) {
      console.log('\n🚨 BUG STILL EXISTS! Filtered > Unfiltered');
    } else if (withFilterNum < noFilterNum) {
      console.log('\n✅ BUG FIXED! Filtered < Unfiltered');
    } else {
      console.log('\n⚠️  Values are equal');
    }
    
    await page.screenshot({ path: 'final_test_result.png', fullPage: true });
    console.log('\nScreenshot: final_test_result.png');
    
    // Keep open for verification
    console.log('\nKeeping browser open for 30 seconds...');
    await new Promise(resolve => setTimeout(resolve, 30000));
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    if (browser) await browser.close();
  }
}

simpleTikTokTest();