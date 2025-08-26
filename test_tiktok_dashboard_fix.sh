#!/bin/bash

echo "🧪 Testing TikTok Dashboard Category Filter Fix"
echo "==============================================="

BASE_URL="http://localhost:8007/api/tiktok-reports"
CURRENT_DATE=$(date +%Y-%m-%d)

echo ""
echo "📊 Test 1: All categories (baseline)"
ALL_RESULT=$(curl -s "${BASE_URL}/dashboard")
ALL_SPEND=$(echo $ALL_RESULT | grep -o '"total_spend":[0-9.]*' | cut -d':' -f2 | head -1)
echo "   Total spend (all categories): \$$(printf "%.0f" $ALL_SPEND)"

echo ""
echo "📊 Test 2: Without Standing Mats"
WITHOUT_CATEGORIES="Bath%20Mats,Multi%20Category,Play%20Furniture,Play%20Mats,Tumbling%20Mats"
WITHOUT_RESULT=$(curl -s "${BASE_URL}/dashboard?categories=${WITHOUT_CATEGORIES}")
WITHOUT_SPEND=$(echo $WITHOUT_RESULT | grep -o '"total_spend":[0-9.]*' | cut -d':' -f2 | head -1)
echo "   Total spend (without Standing Mats): \$$(printf "%.0f" $WITHOUT_SPEND)"

echo ""
echo "📊 Test 3: With Standing Mats added"
WITH_CATEGORIES="Bath%20Mats,Multi%20Category,Play%20Furniture,Play%20Mats,Tumbling%20Mats,Standing%20Mats"
WITH_RESULT=$(curl -s "${BASE_URL}/dashboard?categories=${WITH_CATEGORIES}")
WITH_SPEND=$(echo $WITH_RESULT | grep -o '"total_spend":[0-9.]*' | cut -d':' -f2 | head -1)
echo "   Total spend (with Standing Mats): \$$(printf "%.0f" $WITH_SPEND)"

echo ""
echo "📊 Test 4: Standing Mats only"
STANDING_ONLY="Standing%20Mats"
STANDING_RESULT=$(curl -s "${BASE_URL}/dashboard?categories=${STANDING_ONLY}")
STANDING_SPEND=$(echo $STANDING_RESULT | grep -o '"total_spend":[0-9.]*' | cut -d':' -f2 | head -1)
echo "   Total spend (Standing Mats only): \$$(printf "%.0f" $STANDING_SPEND)"

echo ""
echo "📋 ANALYSIS:"
echo "============"

if [ ! -z "$WITHOUT_SPEND" ] && [ ! -z "$WITH_SPEND" ] && [ ! -z "$STANDING_SPEND" ]; then
    DIFFERENCE=$(echo "$WITH_SPEND - $WITHOUT_SPEND" | bc)
    echo "Without Standing Mats: \$$(printf "%.0f" $WITHOUT_SPEND)"
    echo "With Standing Mats:    \$$(printf "%.0f" $WITH_SPEND)"
    echo "Difference:            \$$(printf "%.0f" $DIFFERENCE)"
    echo "Standing Mats only:    \$$(printf "%.0f" $STANDING_SPEND)"
    
    # Check if the values make sense
    TOLERANCE=100  # Allow $100 tolerance
    
    echo ""
    
    # Test 1: Adding Standing Mats should increase the total
    if (( $(echo "$DIFFERENCE > 0" | bc -l) )); then
        echo "✅ SUCCESS: Adding Standing Mats INCREASES total spend (was decreasing before)"
    else
        echo "❌ FAILED: Adding Standing Mats still decreases total spend"
    fi
    
    # Test 2: The difference should roughly match Standing Mats only value
    DIFF_CHECK=$(echo "$DIFFERENCE - $STANDING_SPEND" | bc | sed 's/-//')
    if (( $(echo "$DIFF_CHECK < $TOLERANCE" | bc -l) )); then
        echo "✅ SUCCESS: Difference matches Standing Mats value (within \$$(printf "%.0f" $TOLERANCE) tolerance)"
    else
        echo "❌ FAILED: Difference doesn't match Standing Mats value (off by \$$(printf "%.0f" $DIFF_CHECK))"
    fi
    
    # Test 3: Check if the fix actually worked by comparing to baseline
    if (( $(echo "$WITH_SPEND <= $ALL_SPEND" | bc -l) )) && (( $(echo "$WITH_SPEND > $WITHOUT_SPEND" | bc -l) )); then
        echo "✅ SUCCESS: Category filtering is working correctly"
        echo ""
        echo "🎉 TikTok Dashboard Filter Fix SUCCESSFUL!"
        echo "   - KPI cards now update based on category selection"
        echo "   - Standing Mats filter now increases totals correctly"
    else
        echo "⚠️  PARTIAL: Some improvement but may need additional debugging"
    fi
else
    echo "❌ Could not extract spend values from API responses"
    echo "Raw responses:"
    echo "All categories: $ALL_RESULT" | head -200
    echo "Without Standing: $WITHOUT_RESULT" | head -200
fi