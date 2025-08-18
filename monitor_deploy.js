const puppeteer = require('puppeteer');

async function waitForDeployAndTest() {
  console.log('🔄 Monitoring deployment and testing when ready...');
  
  let attempt = 0;
  const maxAttempts = 20; // Check for 10 minutes (30s intervals)
  
  while (attempt < maxAttempts) {
    attempt++;
    console.log(`\n🔍 Attempt ${attempt}/${maxAttempts} - Testing deployment...`);
    
    const browser = await puppeteer.launch({ headless: true });
    
    try {
      const page = await browser.newPage();
      
      // Capture console logs
      const consoleLogs = [];
      page.on('console', (msg) => {
        consoleLogs.push(msg.text());
      });
      
      // Capture network requests
      const requests = [];
      page.on('response', (response) => {
        if (response.url().includes('monthly')) {
          requests.push({
            url: response.url(),
            status: response.status()
          });
        }
      });
      
      console.log('  📱 Loading site...');
      await page.goto('https://hon-automated-reporting.netlify.app', {
        waitUntil: 'networkidle0',
        timeout: 30000
      });
      
      // Check for deployment marker
      const deploymentMarker = consoleLogs.find(log => 
        log.includes('DEPLOYMENT UPDATE')
      );
      
      // Check for API URL log
      const apiUrlLog = consoleLogs.find(log => 
        log.includes('API_BASE_URL')
      );
      
      console.log('  🚀 Deployment marker:', deploymentMarker ? '✅ FOUND' : '❌ NOT FOUND');
      console.log('  🌐 API URL log:', apiUrlLog ? '✅ FOUND' : '❌ NOT FOUND');
      
      if (deploymentMarker && apiUrlLog) {
        console.log('\n🎉 NEW DEPLOYMENT DETECTED! Testing login...');
        
        // Test login and API calls
        await page.waitForSelector('input[type="password"]', { timeout: 5000 });
        await page.type('input[type="password"]', 'HN$7kX9#mQ2vL8pR@2024');
        await page.click('button[type="submit"]');
        
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Check API requests
        const monthlyRequests = requests.filter(r => r.url.includes('monthly'));
        
        console.log('  📊 Monthly requests:', monthlyRequests);
        
        if (monthlyRequests.some(r => r.url.includes('onrender.com'))) {
          console.log('\n🎉 SUCCESS! Frontend is now calling Render backend!');
          console.log('✅ The deployment is working correctly!');
          break;
        } else if (monthlyRequests.some(r => r.url.includes('netlify.app'))) {
          console.log('\n⚠️  Still calling Netlify instead of Render...');
        }
      }
      
    } catch (error) {
      console.log(`  ❌ Error: ${error.message}`);
    } finally {
      await browser.close();
    }
    
    if (attempt < maxAttempts) {
      console.log('  ⏳ Waiting 30 seconds before next check...');
      await new Promise(resolve => setTimeout(resolve, 30000));
    }
  }
  
  if (attempt >= maxAttempts) {
    console.log('\n⏰ Monitoring timeout reached. Manual investigation needed.');
  }
}

waitForDeployAndTest().catch(console.error);