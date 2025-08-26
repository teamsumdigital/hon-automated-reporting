const puppeteer = require('puppeteer');

async function testStandingMatsFix() {
    console.log('🎭 Testing Standing Mats filter fix with direct API calls...');
    
    const browser = await puppeteer.launch({ 
        headless: false,
        slowMo: 300,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    try {
        const page = await browser.newPage();
        await page.setViewport({ width: 1400, height: 900 });
        
        // Navigate to the TikTok dashboard directly
        console.log('📱 Navigating to TikTok Ad Level dashboard...');
        await page.goto('http://localhost:3007/tiktok-ad-level');
        
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Check if password is needed
        if (await page.$('input[type="password"]')) {
            console.log('🔐 Entering password...');
            await page.type('input[type="password"]', 'HN$7kX9#mQ2vL8pR@2024');
            await page.keyboard.press('Enter');
            await new Promise(resolve => setTimeout(resolve, 3000));
        }
        
        // Wait for the dashboard to load
        console.log('⏳ Waiting for dashboard to load...');
        await page.waitForSelector('.kpi-card, [class*="grid"], [class*="dashboard"]', { timeout: 15000 });
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Test by making direct API calls and comparing the results
        console.log('🔬 Testing API endpoints directly...');
        
        const testApiCall = async (categories) => {
            const categoryParam = categories ? categories.join(',') : '';
            const url = `http://localhost:8007/api/tiktok-ad-reports/summary?categories=${categoryParam}&start_date=2025-07-01&end_date=2025-07-31`;
            
            const response = await page.evaluate(async (apiUrl) => {
                try {
                    const res = await fetch(apiUrl);
                    return await res.json();
                } catch (error) {
                    return { error: error.message };
                }
            }, url);
            
            return response;
        };
        
        // Test 1: All categories (no filter)
        console.log('\\n📊 Test 1: All categories (baseline)');
        const allCategoriesResult = await testApiCall(null);
        const baselineSpend = allCategoriesResult.summary?.total_spend || 0;
        console.log(`   Total spend: $${baselineSpend.toLocaleString()}`);
        
        // Test 2: Without Standing Mats
        console.log('\\n📊 Test 2: Without Standing Mats');
        const withoutStandingMats = ['Play Furniture', 'Tumbling Mats', 'Play Mats', 'Bath Mats'];
        const withoutResult = await testApiCall(withoutStandingMats);
        const withoutSpend = withoutResult.summary?.total_spend || 0;
        console.log(`   Total spend: $${withoutSpend.toLocaleString()}`);
        console.log(`   Expected: $22,159`);
        
        // Test 3: With Standing Mats
        console.log('\\n📊 Test 3: With Standing Mats');
        const withStandingMats = ['Play Furniture', 'Tumbling Mats', 'Play Mats', 'Bath Mats', 'Standing Mats'];
        const withResult = await testApiCall(withStandingMats);
        const withSpend = withResult.summary?.total_spend || 0;
        console.log(`   Total spend: $${withSpend.toLocaleString()}`);
        console.log(`   Expected: $30,453`);
        
        // Test 4: Standing Mats only
        console.log('\\n📊 Test 4: Standing Mats only');
        const standingMatsOnly = ['Standing Mats'];
        const standingOnlyResult = await testApiCall(standingMatsOnly);
        const standingOnlySpend = standingOnlyResult.summary?.total_spend || 0;
        console.log(`   Total spend: $${standingOnlySpend.toLocaleString()}`);
        console.log(`   Expected: $8,294`);
        
        // Analysis
        console.log('\\n📋 ANALYSIS:');
        console.log('=============');
        
        const difference = withSpend - withoutSpend;
        console.log(`Without Standing Mats: $${withoutSpend.toLocaleString()}`);
        console.log(`With Standing Mats:    $${withSpend.toLocaleString()}`);
        console.log(`Difference:            $${difference.toLocaleString()}`);
        console.log(`Standing Mats only:    $${standingOnlySpend.toLocaleString()}`);
        console.log(`Expected difference:   $8,294`);
        
        // Check if the fix worked
        const expectedWithout = 22158.75;
        const expectedWith = 30452.43;
        const expectedDifference = 8293.68;
        
        const tolerance = 100; // $100 tolerance
        
        let allTestsPassed = true;
        
        if (Math.abs(withoutSpend - expectedWithout) <= tolerance) {
            console.log('✅ Test 1 PASSED: Without Standing Mats spend is correct');
        } else {
            console.log('❌ Test 1 FAILED: Without Standing Mats spend incorrect');
            allTestsPassed = false;
        }
        
        if (Math.abs(withSpend - expectedWith) <= tolerance) {
            console.log('✅ Test 2 PASSED: With Standing Mats spend is correct');
        } else {
            console.log('❌ Test 2 FAILED: With Standing Mats spend incorrect');
            allTestsPassed = false;
        }
        
        if (Math.abs(difference - expectedDifference) <= tolerance) {
            console.log('✅ Test 3 PASSED: Difference matches expected Standing Mats value');
        } else {
            console.log('❌ Test 3 FAILED: Difference does not match Standing Mats value');
            allTestsPassed = false;
        }
        
        if (Math.abs(standingOnlySpend - expectedDifference) <= tolerance) {
            console.log('✅ Test 4 PASSED: Standing Mats only value is correct');
        } else {
            console.log('❌ Test 4 FAILED: Standing Mats only value incorrect');
            allTestsPassed = false;
        }
        
        if (allTestsPassed) {
            console.log('\\n🎉 SUCCESS: All tests passed! The Standing Mats filter fix is working correctly.');
        } else {
            console.log('\\n🚨 FAILURE: Some tests failed. The fix may not be working properly.');
        }
        
        // Test the UI as well
        console.log('\\n🖥️  Testing UI behavior...');
        await page.reload();
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Look for KPI values on the page
        const kpiValue = await page.evaluate(() => {
            // Look for spend values in KPI cards
            const elements = Array.from(document.querySelectorAll('*'));
            for (const el of elements) {
                const text = el.textContent || '';
                // Look for currency values that match our expected totals
                if (text.match(/\\$[\\d,]+/) && text.includes('$') && !text.includes('.')) {
                    const match = text.match(/\\$([\\d,]+)/);
                    if (match) {
                        const value = parseInt(match[1].replace(/,/g, ''));
                        if (value > 10000) { // Likely a total spend value
                            return value;
                        }
                    }
                }
            }
            return null;
        });
        
        if (kpiValue) {
            console.log(`🎯 Found KPI value on page: $${kpiValue.toLocaleString()}`);
            if (Math.abs(kpiValue - baselineSpend) <= tolerance) {
                console.log('✅ UI shows correct baseline spend');
            } else {
                console.log('❌ UI spend does not match API baseline');
            }
        } else {
            console.log('⚠️  Could not locate KPI spend value on page');
        }
        
        await page.screenshot({ path: 'standing_mats_api_test.png', fullPage: true });
        console.log('📸 Screenshot saved as standing_mats_api_test.png');
        
    } catch (error) {
        console.error('❌ Test failed:', error);
        try {
            await page.screenshot({ path: 'api_test_error.png' });
        } catch (e) {
            console.log('Could not save error screenshot');
        }
    } finally {
        await browser.close();
    }
}

testStandingMatsFix().catch(console.error);