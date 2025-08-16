const puppeteer = require('puppeteer');

async function testDashboard() {
  console.log('🔍 Testing Google Ads dashboard...');
  
  const browser = await puppeteer.launch({ 
    headless: false,
    defaultViewport: { width: 1920, height: 1080 }
  });
  
  const page = await browser.newPage();
  
  console.log('📱 Going to dashboard...');
  await page.goto('http://localhost:3007', { waitUntil: 'networkidle2' });
  
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Click Google Ads tab
  await page.evaluate(() => {
    const buttons = document.querySelectorAll('button');
    const googleTab = Array.from(buttons).find(btn => btn.textContent.includes('Google Ads'));
    if (googleTab) googleTab.click();
  });
  
  await new Promise(resolve => setTimeout(resolve, 5000));
  
  // Check KPI cards
  const kpiData = await page.evaluate(() => {
    const kpiCards = document.querySelectorAll('[class*="p-6 rounded-xl"]');
    const kpis = {};
    
    kpiCards.forEach(card => {
      const title = card.querySelector('h3')?.textContent;
      const value = card.querySelector('[class*="text-2xl font-bold"]')?.textContent;
      if (title && value) {
        kpis[title] = value;
      }
    });
    
    return kpis;
  });
  
  console.log('📊 KPI Cards:', kpiData);
  
  // Check table data
  const tableData = await page.evaluate(() => {
    const rows = document.querySelectorAll('tbody tr');
    return Array.from(rows).slice(0, 5).map(row => {
      const cells = row.querySelectorAll('td');
      return Array.from(cells).map(cell => cell.textContent.trim());
    });
  });
  
  console.log('📋 Table rows (first 5):');
  tableData.forEach((row, i) => {
    console.log(`  ${i + 1}:`, row);
  });
  
  // Check expected totals
  console.log('\n🎯 Expected Excel totals:');
  console.log('  Total Spend: $1,248,778');
  console.log('  Total Purchases: 44,575');
  console.log('  Total Revenue: $12,509,783');
  console.log('  ROAS: 10.0x');
  
  console.log('\n✅ Dashboard test completed!');
  
  // Keep browser open for 10 seconds to verify visually
  await new Promise(resolve => setTimeout(resolve, 10000));
  await browser.close();
}

testDashboard().catch(console.error);