const puppeteer = require('puppeteer');

async function testStandingMatsFilter() {
    console.log('🎭 Starting Puppeteer test for Standing Mats filter fix...');
    
    const browser = await puppeteer.launch({ 
        headless: false,
        slowMo: 500,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    try {
        const page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });
        
        console.log('📱 Navigating to TikTok Ad Level dashboard...');
        await page.goto('http://localhost:3007/dashboard');
        
        // Wait for page to load
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Check if we need to enter password
        const passwordInput = await page.$('input[type="password"]');
        if (passwordInput) {
            console.log('🔐 Entering password...');
            await page.type('input[type="password"]', 'HN$7kX9#mQ2vL8pR@2024');
            try {
                await page.click('button[type="submit"]');
            } catch (e) {
                try {
                    await page.click('.login-button');
                } catch (e2) {
                    await page.click('button');
                }
            }
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
        
        // Navigate to TikTok Ad Level dashboard
        console.log('🎯 Going to TikTok Ad Level page...');
        await page.goto('http://localhost:3007/tiktok-ad-level');
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Wait for the page to load completely
        await page.waitForSelector('.filter-panel, [data-testid="category-filter"], input[type="checkbox"]', { timeout: 10000 });
        
        console.log('📊 Testing filter combinations...');
        
        // Test 1: Get baseline (all categories) total spend
        console.log('\n🔍 Test 1: Getting baseline total spend (all categories)');
        await page.waitForSelector('[data-testid="total-spend"], .kpi-card:contains("Total Spend"), .text-3xl', { timeout: 5000 });
        
        let baselineSpend = await page.evaluate(() => {
            // Look for total spend in various possible locations
            const selectors = [
                '[data-testid="total-spend"]',
                '.kpi-card:first-child .text-3xl',
                'div:contains("Total Spend") + * .text-3xl',
                '.text-3xl'
            ];
            
            for (const selector of selectors) {
                const element = document.querySelector(selector);
                if (element) {
                    const text = element.textContent || element.innerText;
                    const match = text.match(/\$?([\d,]+)/);
                    if (match) return match[1].replace(/,/g, '');
                }
            }
            
            // Fallback: get all elements with currency format
            const allElements = Array.from(document.querySelectorAll('*'));
            for (const el of allElements) {
                const text = el.textContent || '';
                if (text.match(/^\$[\d,]+$/) && !text.includes('.')) {
                    const match = text.match(/\$([\d,]+)/);
                    if (match) return match[1].replace(/,/g, '');
                }
            }
            return null;
        });
        
        if (!baselineSpend) {
            console.log('❌ Could not find baseline spend value');
            await page.screenshot({ path: 'debug_baseline.png' });
            return;
        }
        
        console.log(`   Baseline total spend: $${parseInt(baselineSpend).toLocaleString()}`);
        
        // Test 2: Filter to working combination (without Standing Mats)
        console.log('\n🔍 Test 2: Filtering to working combination (Play Furniture, Tumbling Mats, Play Mats, Bath Mats)');
        
        // Clear all filters first
        await page.evaluate(() => {
            const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
            checkboxes.forEach(cb => cb.click());
        });
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Select the working combination categories
        const workingCategories = ['Play Furniture', 'Tumbling Mats', 'Play Mats', 'Bath Mats'];
        
        for (const category of workingCategories) {
            try {
                // Try multiple selector approaches
                const selectors = [
                    `input[type="checkbox"][value="${category}"]`,
                    `label:contains(${category}) input[type="checkbox"]`,
                    `label:contains("${category}") input[type="checkbox"]`,
                    `*:contains("${category}") input[type="checkbox"]`
                ];
                
                let found = false;
                for (const selector of selectors) {
                    try {
                        await page.click(selector);
                        found = true;
                        break;
                    } catch (e) {
                        continue;
                    }
                }
                
                if (!found) {
                    // Manual approach: find checkbox by associated text
                    await page.evaluate((cat) => {
                        const elements = Array.from(document.querySelectorAll('*'));
                        for (const el of elements) {
                            if ((el.textContent || '').includes(cat)) {
                                const checkbox = el.querySelector('input[type="checkbox"]') || 
                                               el.parentElement?.querySelector('input[type="checkbox"]') ||
                                               el.previousElementSibling?.querySelector('input[type="checkbox"]');
                                if (checkbox && !checkbox.checked) {
                                    checkbox.click();
                                    return;
                                }
                            }
                        }
                    }, category);
                }
                
                await new Promise(resolve => setTimeout(resolve, 500));
                console.log(`   ✅ Selected: ${category}`);
            } catch (error) {
                console.log(`   ⚠️  Could not select: ${category} - ${error.message}`);
            }
        }
        
        // Wait for data to update
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Get the filtered spend
        let workingSpend = await page.evaluate(() => {
            const selectors = [
                '[data-testid="total-spend"]',
                '.kpi-card:first-child .text-3xl',
                'div:contains("Total Spend") + * .text-3xl',
                '.text-3xl'
            ];
            
            for (const selector of selectors) {
                const element = document.querySelector(selector);
                if (element) {
                    const text = element.textContent || element.innerText;
                    const match = text.match(/\$?([\d,]+)/);
                    if (match) return match[1].replace(/,/g, '');
                }
            }
            return null;
        });
        
        console.log(`   Working combination spend: $${parseInt(workingSpend).toLocaleString()}`);
        console.log(`   Expected: $22,159`);
        
        // Test 3: Add Standing Mats and see if it increases correctly
        console.log('\n🔍 Test 3: Adding Standing Mats to the filter');
        
        try {
            // Add Standing Mats
            const standingMatsSelectors = [
                'input[type="checkbox"][value="Standing Mats"]',
                'input[type="checkbox"] + label:contains("Standing Mats")',
                'label:contains("Standing Mats") input[type="checkbox"]'
            ];
            
            let standingMatsFound = false;
            for (const selector of standingMatsSelectors) {
                try {
                    await page.click(selector);
                    standingMatsFound = true;
                    break;
                } catch (e) {
                    continue;
                }
            }
            
            if (!standingMatsFound) {
                await page.evaluate(() => {
                    const elements = Array.from(document.querySelectorAll('*'));
                    for (const el of elements) {
                        if ((el.textContent || '').includes('Standing Mats')) {
                            const checkbox = el.querySelector('input[type="checkbox"]') || 
                                           el.parentElement?.querySelector('input[type="checkbox"]') ||
                                           el.previousElementSibling?.querySelector('input[type="checkbox"]');
                            if (checkbox && !checkbox.checked) {
                                checkbox.click();
                                return;
                            }
                        }
                    }
                });
            }
            
            console.log('   ✅ Added Standing Mats filter');
            
            // Wait for data to update
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            // Get the new total
            let problematicSpend = await page.evaluate(() => {
                const selectors = [
                    '[data-testid="total-spend"]',
                    '.kpi-card:first-child .text-3xl',
                    'div:contains("Total Spend") + * .text-3xl',
                    '.text-3xl'
                ];
                
                for (const selector of selectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        const text = element.textContent || element.innerText;
                        const match = text.match(/\$?([\d,]+)/);
                        if (match) return match[1].replace(/,/g, '');
                    }
                }
                return null;
            });
            
            console.log(`   With Standing Mats spend: $${parseInt(problematicSpend).toLocaleString()}`);
            console.log(`   Expected: $30,453`);
            
            // Analysis
            console.log('\n📋 TEST RESULTS:');
            console.log('================');
            
            const workingSpendNum = parseInt(workingSpend);
            const problematicSpendNum = parseInt(problematicSpend);
            const difference = problematicSpendNum - workingSpendNum;
            
            console.log(`Baseline (all categories): $${parseInt(baselineSpend).toLocaleString()}`);
            console.log(`Without Standing Mats: $${workingSpendNum.toLocaleString()}`);
            console.log(`With Standing Mats: $${problematicSpendNum.toLocaleString()}`);
            console.log(`Difference: $${difference.toLocaleString()}`);
            console.log(`Expected difference: $8,294`);
            
            // Check if fix worked
            const expectedDifference = 8294;
            const tolerancePercent = 5; // 5% tolerance
            const tolerance = expectedDifference * (tolerancePercent / 100);
            
            if (Math.abs(difference - expectedDifference) <= tolerance) {
                console.log('✅ SUCCESS: Standing Mats filter fix is working correctly!');
                console.log(`   The difference of $${difference.toLocaleString()} is within expected range.`);
            } else if (difference < 100) {
                console.log('❌ FAILED: Standing Mats filter is still broken.');
                console.log(`   The spend barely changed ($${difference.toLocaleString()}), indicating the KPI is not being filtered.`);
            } else {
                console.log('⚠️  PARTIAL: Unexpected result.');
                console.log(`   Got difference of $${difference.toLocaleString()}, expected $${expectedDifference.toLocaleString()}`);
            }
            
        } catch (error) {
            console.log(`❌ Error adding Standing Mats filter: ${error.message}`);
        }
        
        // Take a final screenshot
        await page.screenshot({ path: 'standing_mats_test_result.png', fullPage: true });
        console.log('📸 Final screenshot saved as standing_mats_test_result.png');
        
    } catch (error) {
        console.error('❌ Test failed:', error);
        try {
            await page.screenshot({ path: 'error_screenshot.png' });
        } catch (screenshotError) {
            console.error('Could not take screenshot:', screenshotError.message);
        }
    } finally {
        await browser.close();
    }
}

// Run the test
testStandingMatsFilter().catch(console.error);