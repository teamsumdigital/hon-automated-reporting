/**
 * Test momentum indicators functionality
 * Run this in browser console while on Ad Level Dashboard
 */

console.log('🧪 Testing momentum indicators...');

// Test the API data structure
fetch('http://localhost:8007/api/meta-ad-reports/ad-data')
  .then(response => response.json())
  .then(data => {
    console.log(`📊 Total ads: ${data.count}`);
    
    if (data.grouped_ads && data.grouped_ads.length > 0) {
      const firstAd = data.grouped_ads[0];
      console.log(`🎯 Testing ad: ${firstAd.ad_name}`);
      console.log(`🗓️ Weekly periods: ${firstAd.weekly_periods ? firstAd.weekly_periods.length : 0}`);
      
      if (firstAd.weekly_periods && firstAd.weekly_periods.length >= 2) {
        const periods = firstAd.weekly_periods.sort((a, b) => 
          new Date(a.reporting_starts).getTime() - new Date(b.reporting_starts).getTime()
        );
        
        const olderWeek = periods[0];
        const newerWeek = periods[1];
        
        console.log('📈 Week 1 (older):', {
          dates: `${olderWeek.reporting_starts} to ${olderWeek.reporting_ends}`,
          spend: olderWeek.spend,
          roas: olderWeek.roas
        });
        
        console.log('📈 Week 2 (newer):', {
          dates: `${newerWeek.reporting_starts} to ${newerWeek.reporting_ends}`,
          spend: newerWeek.spend,
          roas: newerWeek.roas
        });
        
        // Calculate momentum manually
        const spendChange = olderWeek.spend > 0 
          ? ((newerWeek.spend - olderWeek.spend) / olderWeek.spend) * 100 
          : null;
        
        const roasChange = olderWeek.roas > 0 
          ? ((newerWeek.roas - olderWeek.roas) / olderWeek.roas) * 100 
          : null;
        
        console.log('🚀 Calculated momentum:');
        console.log(`   Spend change: ${spendChange ? spendChange.toFixed(1) + '%' : 'N/A'}`);
        console.log(`   ROAS change: ${roasChange ? roasChange.toFixed(1) + '%' : 'N/A'}`);
        
        if (Math.abs(spendChange) >= 1) {
          console.log('✅ Momentum should be visible for spend!');
        } else {
          console.log('⚠️ Spend change too small (< 1%) - momentum hidden');
        }
        
        if (Math.abs(roasChange) >= 1) {
          console.log('✅ Momentum should be visible for ROAS!');
        } else {
          console.log('⚠️ ROAS change too small (< 1%) - momentum hidden');
        }
        
      } else {
        console.log('❌ Not enough weekly periods for momentum calculation');
      }
    } else {
      console.log('❌ No ads found');
    }
  })
  .catch(error => {
    console.error('❌ API Error:', error);
  });

// Check if momentum indicators are visible in the DOM
setTimeout(() => {
  const momentumElements = document.querySelectorAll('[class*="text-green-600"], [class*="text-red-600"]');
  console.log(`🔍 Found ${momentumElements.length} potential momentum indicators in DOM`);
  
  const spendColumns = document.querySelectorAll('td:has(.text-green-600), td:has(.text-red-600)');
  console.log(`📊 Momentum indicators in spend/ROAS columns: ${spendColumns.length}`);
  
  if (spendColumns.length === 0) {
    console.log('❌ No momentum indicators found in table - there might be an issue');
  } else {
    console.log('✅ Momentum indicators are displaying correctly');
  }
}, 2000);