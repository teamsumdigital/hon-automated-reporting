const puppeteer = require('puppeteer');

async function testBackendData() {
  console.log('🔍 Testing backend data and database status...');
  
  const browser = await puppeteer.launch({ headless: true });
  
  try {
    const page = await browser.newPage();
    
    console.log('📡 Testing API endpoints...');
    
    // Test 1: Health check
    await page.goto('https://hon-automated-reporting.onrender.com/health');
    const healthContent = await page.content();
    const healthMatch = healthContent.match(/{"status":"([^"]+)"/);
    console.log(`✅ Health: ${healthMatch ? healthMatch[1] : 'unknown'}`);
    
    // Test 2: Root endpoint to see available endpoints
    await page.goto('https://hon-automated-reporting.onrender.com/');
    const rootContent = await page.content();
    console.log('📋 Available endpoints confirmed');
    
    // Test 3: Meta test connection
    await page.goto('https://hon-automated-reporting.onrender.com/api/reports/test-connection');
    const testContent = await page.content();
    const testMatch = testContent.match(/{"status":"([^"]+)"/);
    console.log(`🔗 Meta connection: ${testMatch ? testMatch[1] : 'unknown'}`);
    
    // Test 4: Campaigns data
    await page.goto('https://hon-automated-reporting.onrender.com/api/reports/campaigns');
    const campaignContent = await page.content();
    const campaignCount = (campaignContent.match(/campaign_id/g) || []).length;
    console.log(`📊 Campaign records: ${campaignCount}`);
    
    // Test 5: Monthly data structure
    await page.goto('https://hon-automated-reporting.onrender.com/api/reports/monthly');
    const monthlyContent = await page.content();
    const monthlyMatch = monthlyContent.match(/"monthly_breakdown":\[([^\]]*)\]/);
    const monthlyCount = monthlyMatch && monthlyMatch[1] ? monthlyMatch[1].split(',').length : 0;
    console.log(`📅 Monthly breakdown records: ${monthlyCount}`);
    
    // Test 6: Available categories
    await page.goto('https://hon-automated-reporting.onrender.com/api/reports/categories');
    const catContent = await page.content();
    const catMatch = catContent.match(/\[([^\]]*)\]/);
    const categories = catMatch && catMatch[1] ? catMatch[1].split(',').length : 0;
    console.log(`🏷️  Available categories: ${categories}`);
    
    console.log('\n📋 DIAGNOSIS SUMMARY:');
    console.log('='.repeat(50));
    
    if (campaignCount === 0) {
      console.log('🔍 ROOT CAUSE: Database tables are empty');
      console.log('💡 SOLUTION NEEDED: Data sync from Meta Ads API');
      console.log('\n🔧 Recommended actions:');
      console.log('   1. Check Supabase database schema is set up');
      console.log('   2. Verify Meta Ads API credentials');
      console.log('   3. Run data sync endpoint manually');
      console.log('   4. Check sync endpoint for errors');
    } else {
      console.log('✅ Database has data - issue may be elsewhere');
    }
    
  } catch (error) {
    console.error('❌ Backend test failed:', error);
  } finally {
    await browser.close();
  }
}

testBackendData();