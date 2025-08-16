const puppeteer = require('puppeteer');

async function testSummaryTiles() {
  console.log('🔍 Testing Summary Tiles Update...');
  
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
    
    // Test Meta (default tab) summary tiles
    console.log('📊 Testing Meta dashboard summary tiles...');
    const metaTiles = await page.evaluate(() => {
      // Look for KPI cards or summary tiles
      const tiles = document.querySelectorAll('[class*="KPI"], [class*="card"], [class*="tile"]');
      const titles = [];
      
      // Try different selectors to find the tiles
      const possibleSelectors = [
        'h3', 'h4', 'h5', // Common title elements
        '[class*="title"]',
        '[class*="label"]',
        'div:first-child', // Often titles are first child
      ];
      
      tiles.forEach(tile => {
        possibleSelectors.forEach(selector => {
          const titleElement = tile.querySelector(selector);
          if (titleElement && titleElement.textContent) {
            const text = titleElement.textContent.trim();
            if (text && !titles.includes(text) && text.length < 50) {
              titles.push(text);
            }
          }
        });
      });
      
      // Also try direct text content approach
      const allDivs = document.querySelectorAll('div');
      allDivs.forEach(div => {
        const text = div.textContent?.trim();
        if (text && (text === 'Total Spend' || text === 'Total Revenue' || text === 'ROAS' || text === 'CPA' || text === 'Total Purchases')) {
          if (!titles.includes(text)) {
            titles.push(text);
          }
        }
      });
      
      return titles.filter(title => 
        title === 'Total Spend' || 
        title === 'Total Revenue' || 
        title === 'ROAS' || 
        title === 'CPA' || 
        title === 'Total Purchases'
      );
    });
    
    console.log('📋 Meta tiles found:', metaTiles);
    
    // Click TikTok tab
    console.log('🎯 Switching to TikTok tab...');
    await page.click('[data-tab="tiktok"], [aria-label*="TikTok"], [title*="TikTok"]');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Test TikTok summary tiles
    console.log('📊 Testing TikTok dashboard summary tiles...');
    const tiktokTiles = await page.evaluate(() => {
      const tiles = document.querySelectorAll('[class*="KPI"], [class*="card"], [class*="tile"]');
      const titles = [];
      
      const possibleSelectors = [
        'h3', 'h4', 'h5',
        '[class*="title"]',
        '[class*="label"]',
        'div:first-child',
      ];
      
      tiles.forEach(tile => {
        possibleSelectors.forEach(selector => {
          const titleElement = tile.querySelector(selector);
          if (titleElement && titleElement.textContent) {
            const text = titleElement.textContent.trim();
            if (text && !titles.includes(text) && text.length < 50) {
              titles.push(text);
            }
          }
        });
      });
      
      const allDivs = document.querySelectorAll('div');
      allDivs.forEach(div => {
        const text = div.textContent?.trim();
        if (text && (text === 'Total Spend' || text === 'Total Revenue' || text === 'ROAS' || text === 'CPA' || text === 'Total Purchases')) {
          if (!titles.includes(text)) {
            titles.push(text);
          }
        }
      });
      
      return titles.filter(title => 
        title === 'Total Spend' || 
        title === 'Total Revenue' || 
        title === 'ROAS' || 
        title === 'CPA' || 
        title === 'Total Purchases'
      );
    });
    
    console.log('📋 TikTok tiles found:', tiktokTiles);
    
    // Expected tiles
    const expectedTiles = ['Total Spend', 'Total Revenue', 'ROAS', 'CPA'];
    
    console.log('🎯 Expected tiles:', expectedTiles);
    
    // Check if both dashboards have correct tiles
    const metaCorrect = expectedTiles.every(tile => metaTiles.includes(tile)) && !metaTiles.includes('Total Purchases');
    const tiktokCorrect = expectedTiles.every(tile => tiktokTiles.includes(tile)) && !tiktokTiles.includes('Total Purchases');
    
    console.log('✅ Meta tiles correct:', metaCorrect);
    console.log('✅ TikTok tiles correct:', tiktokCorrect);
    
    if (metaCorrect && tiktokCorrect) {
      console.log('🎉 Summary tiles updated successfully!');
      return true;
    } else {
      console.log('❌ Summary tiles need fixing');
      console.log('Meta issues:', !metaCorrect ? 'Missing CPA or has Total Purchases' : 'OK');
      console.log('TikTok issues:', !tiktokCorrect ? 'Missing CPA or has Total Purchases' : 'OK');
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
testSummaryTiles().then(success => {
  console.log(success ? '🎉 Summary tiles test passed!' : '💥 Summary tiles test failed!');
  process.exit(success ? 0 : 1);
});