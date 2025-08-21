const puppeteer = require('puppeteer');

async function testCorrectCredentials() {
  console.log('🎯 Testing with correct Supabase credentials...');
  
  // Wait for Render deployment
  console.log('⏳ Waiting 90 seconds for Render to deploy with new credentials...');
  await new Promise(resolve => setTimeout(resolve, 90000));
  
  console.log('\n📊 TESTING DATABASE CONNECTION:');
  console.log('='.repeat(50));
  
  const tests = [
    {
      name: 'Backend Health',
      url: 'https://hon-automated-reporting.onrender.com/health',
      expect: '"status":"healthy"'
    },
    {
      name: 'Meta API Connection', 
      url: 'https://hon-automated-reporting.onrender.com/api/reports/test-connection',
      expect: '"status":"connected"'
    },
    {
      name: 'Campaign Data Access',
      url: 'https://hon-automated-reporting.onrender.com/api/reports/campaigns',
      expect: 'campaign_id'
    },
    {
      name: 'Monthly Data Access',
      url: 'https://hon-automated-reporting.onrender.com/api/reports/monthly',
      expect: 'monthly_breakdown'
    },
    {
      name: 'Available Categories',
      url: 'https://hon-automated-reporting.onrender.com/api/reports/categories',
      expect: 'Bath Mats'
    }
  ];
  
  const results = {};
  
  for (const test of tests) {
    try {
      const response = await fetch(test.url);
      const data = await response.text();
      
      if (data.includes(test.expect)) {
        console.log(`✅ ${test.name}: Working!`);
        results[test.name] = 'success';
        
        // Show sample data for data endpoints
        if (test.name.includes('Data') || test.name.includes('Categories')) {
          const preview = data.length > 200 ? data.substring(0, 200) + '...' : data;
          console.log(`   Sample: ${preview}`);
        }
      } else {
        console.log(`❌ ${test.name}: Not working`);
        console.log(`   Expected: ${test.expect}`);
        console.log(`   Got: ${data.substring(0, 100)}...`);
        results[test.name] = 'failed';
      }
    } catch (error) {
      console.log(`❌ ${test.name}: Error - ${error.message}`);
      results[test.name] = 'error';
    }
  }
  
  // Test sync endpoint if basic connection works
  if (results['Backend Health'] === 'success' && results['Meta API Connection'] === 'success') {
    console.log('\n🔄 TESTING DATA SYNC:');
    console.log('='.repeat(30));
    
    try {
      const syncResponse = await fetch('https://hon-automated-reporting.onrender.com/api/reports/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{}'
      });
      
      const syncData = await syncResponse.text();
      console.log(`Sync Response: ${syncData}`);
      
      if (syncData.includes('success') || syncData.includes('Synced')) {
        console.log('✅ Data sync working! Dashboard should now show real data');
      } else if (syncData.includes('Failed to store')) {
        console.log('❌ Still getting database storage error - credentials may still be wrong');
      } else {
        console.log('⚠️  Unexpected sync response');
      }
    } catch (error) {
      console.log(`❌ Sync test failed: ${error.message}`);
    }
  }
  
  console.log('\n🎯 SUMMARY:');
  console.log('='.repeat(50));
  
  const allWorking = Object.values(results).every(r => r === 'success');
  
  if (allWorking) {
    console.log('🎉 SUCCESS! All database connections working');
    console.log('📊 Your dashboard should now show real campaign data');
    console.log('🔄 Data sync should work for fresh updates');
  } else {
    console.log('⚠️  Some issues remain:');
    Object.entries(results).forEach(([test, result]) => {
      if (result !== 'success') {
        console.log(`   - ${test}: ${result}`);
      }
    });
  }
}

testCorrectCredentials();