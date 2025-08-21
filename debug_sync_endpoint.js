const puppeteer = require('puppeteer');

async function debugSyncEndpoint() {
  console.log('🔧 Debugging sync endpoint failure...');
  
  const browser = await puppeteer.launch({ headless: false });
  
  try {
    const page = await browser.newPage();
    
    // Enable console logging from the page
    page.on('console', (msg) => {
      console.log(`BROWSER CONSOLE: ${msg.text()}`);
    });
    
    // Enable request/response logging
    page.on('request', (request) => {
      if (request.url().includes('sync')) {
        console.log(`📤 REQUEST: ${request.method()} ${request.url()}`);
      }
    });
    
    page.on('response', (response) => {
      if (response.url().includes('sync')) {
        console.log(`📥 RESPONSE: ${response.status()} ${response.url()}`);
      }
    });
    
    console.log('🔍 Testing sync endpoint with detailed error info...');
    
    // Try to get more detailed error info by making the sync request
    const syncResponse = await page.evaluate(async () => {
      try {
        const response = await fetch('https://hon-automated-reporting.onrender.com/api/reports/sync', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: '{}'
        });
        
        const data = await response.text();
        return {
          status: response.status,
          statusText: response.statusText,
          data: data
        };
      } catch (error) {
        return {
          error: error.message
        };
      }
    });
    
    console.log('\n📊 SYNC ENDPOINT RESPONSE:');
    console.log('='.repeat(50));
    console.log('Status:', syncResponse.status);
    console.log('Status Text:', syncResponse.statusText);
    console.log('Response:', syncResponse.data);
    
    // Also test if we can access the database schema endpoint
    console.log('\n🗄️  Testing database access patterns...');
    
    const schemaTests = [
      '/api/reports/categories',
      '/api/reports/campaigns',
      '/api/reports/test-connection'
    ];
    
    for (const endpoint of schemaTests) {
      try {
        await page.goto(`https://hon-automated-reporting.onrender.com${endpoint}`);
        const content = await page.content();
        
        if (content.includes('error') || content.includes('Error')) {
          console.log(`❌ ${endpoint}: Error in response`);
        } else if (content.includes('[]') || content.includes('null')) {
          console.log(`⚠️  ${endpoint}: Empty/null response`);
        } else {
          console.log(`✅ ${endpoint}: Valid response`);
        }
      } catch (error) {
        console.log(`❌ ${endpoint}: ${error.message}`);
      }
    }
    
    console.log('\n💡 LIKELY CAUSES:');
    console.log('='.repeat(50));
    console.log('1. Supabase credentials incorrect in Render environment');
    console.log('2. Database schema not properly set up in Supabase');
    console.log('3. Database permissions issue');
    console.log('4. Meta API data format incompatible with database schema');
    
    console.log('\n🔧 RECOMMENDED FIXES:');
    console.log('1. Verify SUPABASE_URL and SUPABASE_SERVICE_KEY in Render');
    console.log('2. Run database schema setup script in Supabase');
    console.log('3. Check Supabase project is active and accessible');
    console.log('4. Test database insert manually');
    
  } catch (error) {
    console.error('❌ Debug failed:', error);
  } finally {
    await browser.close();
  }
}

debugSyncEndpoint();