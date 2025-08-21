const puppeteer = require('puppeteer');

async function testAfterCredentialsFix() {
  console.log('🔧 Testing after Supabase credentials fix...');
  
  console.log('⏳ Waiting 2 minutes for Render deployment...');
  await new Promise(resolve => setTimeout(resolve, 120000));
  
  const tests = [
    {
      name: 'Health Check',
      url: 'https://hon-automated-reporting.onrender.com/health',
      expect: 'healthy'
    },
    {
      name: 'Meta Connection',
      url: 'https://hon-automated-reporting.onrender.com/api/reports/test-connection',
      expect: 'connected'
    },
    {
      name: 'Campaign Data Count',
      url: 'https://hon-automated-reporting.onrender.com/api/reports/campaigns',
      expect: 'data_array'
    },
    {
      name: 'Monthly Data',
      url: 'https://hon-automated-reporting.onrender.com/api/reports/monthly',
      expect: 'monthly_breakdown'
    }
  ];
  
  console.log('\n📊 RUNNING TESTS:');
  console.log('='.repeat(50));
  
  for (const test of tests) {
    try {
      const response = await fetch(test.url);
      const data = await response.text();
      
      if (test.expect === 'healthy' && data.includes('"status":"healthy"')) {
        console.log(`✅ ${test.name}: Working`);
      } else if (test.expect === 'connected' && data.includes('"status":"connected"')) {
        console.log(`✅ ${test.name}: Working`);
      } else if (test.expect === 'data_array' && data.includes('[') && !data.includes('[]')) {
        console.log(`✅ ${test.name}: Has data! (${data.length} chars)`);
      } else if (test.expect === 'monthly_breakdown' && data.includes('monthly_breakdown') && !data.includes('"monthly_breakdown":[]')) {
        console.log(`✅ ${test.name}: Has data!`);
      } else {
        console.log(`❌ ${test.name}: Still empty or error`);
        console.log(`   Response: ${data.substring(0, 100)}...`);
      }
    } catch (error) {
      console.log(`❌ ${test.name}: ${error.message}`);
    }
  }
  
  // Test sync endpoint
  console.log('\n🔄 Testing sync endpoint...');
  try {
    const syncResponse = await fetch('https://hon-automated-reporting.onrender.com/api/reports/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{}'
    });
    
    const syncData = await syncResponse.text();
    
    if (syncData.includes('success') || syncData.includes('Synced')) {
      console.log('✅ Sync: Working! Data should now appear in dashboard');
    } else {
      console.log('❌ Sync: Still failing');
      console.log(`   Response: ${syncData}`);
    }
  } catch (error) {
    console.log(`❌ Sync: ${error.message}`);
  }
  
  console.log('\n🎯 EXPECTED RESULT:');
  console.log('After fixing credentials, you should see:');
  console.log('- Campaign data endpoint returns actual campaign records');
  console.log('- Monthly endpoint returns actual monthly breakdowns');
  console.log('- Dashboard shows real numbers instead of all zeros');
}

// Export for manual use
if (typeof module !== 'undefined') {
  module.exports = testAfterCredentialsFix;
}

// Run if called directly
if (require.main === module) {
  testAfterCredentialsFix();
}