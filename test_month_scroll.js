const puppeteer = require('puppeteer');

async function testMonthScroll() {
  let browser;
  try {
    console.log('🔍 Testing Month Filter Scrolling...');
    
    browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    
    // Navigate to main dashboard
    await page.goto('http://localhost:3007', { waitUntil: 'networkidle0' });
    console.log('✅ Main dashboard loaded');
    
    // Click Google Ads tab
    await new Promise(resolve => setTimeout(resolve, 1000));
    const tabClicked = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const googleTab = buttons.find(button => button.textContent?.includes('Google Ads'));
      if (googleTab) {
        googleTab.click();
        return true;
      }
      return false;
    });
    
    if (!tabClicked) {
      throw new Error('Could not find Google Ads tab');
    }
    console.log('✅ Google Ads tab clicked');
    
    // Wait for Google dashboard to load
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Test month filter scrolling
    const scrollTest = await page.evaluate(() => {
      // Find all possible month container selectors
      const containers = {
        filterScroll: document.querySelector('.filter-scroll'),
        spaceY2: document.querySelector('.space-y-2'),
        maxH16: document.querySelector('.max-h-\\[16rem\\]'),
        allSpaceY2: document.querySelectorAll('.space-y-2')
      };
      
      // Find the correct month container (the one with max-h-[16rem])
      let monthContainer = null;
      const allSpaceY2 = Array.from(document.querySelectorAll('.space-y-2'));
      for (let container of allSpaceY2) {
        if (container.classList.contains('max-h-[16rem]') || 
            container.closest('.max-h-\\[16rem\\]') ||
            container.style.maxHeight ||
            container.querySelector('button')) {
          const buttons = container.querySelectorAll('button');
          if (buttons.length > 0) {
            // Check if buttons contain month-like text
            const firstButtonText = buttons[0]?.textContent?.trim();
            if (firstButtonText && (firstButtonText.includes('2024') || firstButtonText.includes('2025') || 
                firstButtonText.match(/^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)/))) {
              monthContainer = container;
              break;
            }
          }
        }
      }
      
      if (!monthContainer) {
        return { 
          error: 'Month container not found',
          containerTypes: Object.keys(containers).filter(k => containers[k]),
          allSpaceY2Count: allSpaceY2.length,
          allButtonCounts: allSpaceY2.map(c => c.querySelectorAll('button').length)
        };
      }
      
      // Get all month buttons
      const monthButtons = Array.from(monthContainer.querySelectorAll('button'));
      
      // Check if container is scrollable
      const containerHeight = monthContainer.clientHeight;
      const scrollHeight = monthContainer.scrollHeight;
      const isScrollable = scrollHeight > containerHeight;
      
      // Get text of all month buttons
      const monthTexts = monthButtons.map(btn => btn.textContent?.trim());
      
      // Scroll to bottom to test scrolling
      monthContainer.scrollTop = monthContainer.scrollHeight;
      
      return {
        totalMonths: monthButtons.length,
        containerHeight,
        scrollHeight, 
        isScrollable,
        monthTexts: monthTexts.slice(0, 10), // First 10 for debugging
        allMonthTexts: monthTexts, // All months
        scrolledToBottom: monthContainer.scrollTop > 0,
        containerClasses: monthContainer.className
      };
    });
    
    console.log('\n📊 Month Filter Scroll Test Results:');
    console.log(`  📅 Total months: ${scrollTest.totalMonths}`);
    console.log(`  📏 Container height: ${scrollTest.containerHeight}px`);
    console.log(`  📏 Scroll height: ${scrollTest.scrollHeight}px`);
    console.log(`  🔄 Is scrollable: ${scrollTest.isScrollable}`);
    console.log(`  ⬇️  Scrolled to bottom: ${scrollTest.scrolledToBottom}`);
    console.log(`  📋 Month list: ${scrollTest.monthTexts?.slice(0, 5).join(', ')}...`);
    
    // Take screenshot
    await page.screenshot({ path: 'month-scroll-test.png', fullPage: true });
    console.log('\n📸 Screenshot saved as month-scroll-test.png');
    
    return scrollTest.isScrollable && scrollTest.totalMonths > 0;
    
  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
    return false;
  } finally {
    if (browser) await browser.close();
  }
}

// Add fetch if not available
if (typeof fetch === 'undefined') {
  global.fetch = require('node-fetch');
}

testMonthScroll().then(success => {
  console.log(success ? '\n✅ Month filter scrolling is working!' : '\n❌ Month filter scrolling needs attention');
  process.exit(0);
});