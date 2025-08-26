#!/bin/bash

echo "🧪 Testing Standing Mats API Filter Fix"
echo "======================================="

BASE_URL="http://localhost:8007/api/tiktok-ad-reports"
DATE_PARAMS="start_date=2025-07-01&end_date=2025-07-31"

echo ""
echo "📊 Test 1: All categories (baseline)"
ALL_RESULT=$(curl -s "${BASE_URL}/summary?${DATE_PARAMS}")
ALL_SPEND=$(echo $ALL_RESULT | grep -o '"total_spend":[0-9.]*' | cut -d':' -f2)
echo "   API Response: $ALL_RESULT"
echo "   Total spend: \$$(printf "%.0f" $ALL_SPEND)"

echo ""
echo "📊 Test 2: Without Standing Mats"
WITHOUT_CATEGORIES="Play%20Furniture,Tumbling%20Mats,Play%20Mats,Bath%20Mats"
WITHOUT_RESULT=$(curl -s "${BASE_URL}/summary?categories=${WITHOUT_CATEGORIES}&${DATE_PARAMS}")
WITHOUT_SPEND=$(echo $WITHOUT_RESULT | grep -o '"total_spend":[0-9.]*' | cut -d':' -f2)
echo "   API Response: $WITHOUT_RESULT"
echo "   Total spend: \$$(printf "%.0f" $WITHOUT_SPEND)"
echo "   Expected: \$22,159"

echo ""
echo "📊 Test 3: With Standing Mats"
WITH_CATEGORIES="Play%20Furniture,Tumbling%20Mats,Play%20Mats,Bath%20Mats,Standing%20Mats"
WITH_RESULT=$(curl -s "${BASE_URL}/summary?categories=${WITH_CATEGORIES}&${DATE_PARAMS}")
WITH_SPEND=$(echo $WITH_RESULT | grep -o '"total_spend":[0-9.]*' | cut -d':' -f2)
echo "   API Response: $WITH_RESULT"
echo "   Total spend: \$$(printf "%.0f" $WITH_SPEND)"
echo "   Expected: \$30,453"

echo ""
echo "📊 Test 4: Standing Mats only"
STANDING_ONLY="Standing%20Mats"
STANDING_RESULT=$(curl -s "${BASE_URL}/summary?categories=${STANDING_ONLY}&${DATE_PARAMS}")
STANDING_SPEND=$(echo $STANDING_RESULT | grep -o '"total_spend":[0-9.]*' | cut -d':' -f2)
echo "   API Response: $STANDING_RESULT"
echo "   Total spend: \$$(printf "%.0f" $STANDING_SPEND)"
echo "   Expected: \$8,294"

echo ""
echo "📋 ANALYSIS:"
echo "============"

if [ ! -z "$WITHOUT_SPEND" ] && [ ! -z "$WITH_SPEND" ]; then
    DIFFERENCE=$(echo "$WITH_SPEND - $WITHOUT_SPEND" | bc)
    echo "Without Standing Mats: \$$(printf "%.0f" $WITHOUT_SPEND)"
    echo "With Standing Mats:    \$$(printf "%.0f" $WITH_SPEND)"
    echo "Difference:            \$$(printf "%.0f" $DIFFERENCE)"
    echo "Expected difference:   \$8,294"
    
    # Check if the values are approximately correct
    WITHOUT_EXPECTED=22158
    WITH_EXPECTED=30452
    DIFF_EXPECTED=8294
    
    WITHOUT_DIFF=$(echo "$WITHOUT_SPEND - $WITHOUT_EXPECTED" | bc | sed 's/-//')
    WITH_DIFF=$(echo "$WITH_SPEND - $WITH_EXPECTED" | bc | sed 's/-//')
    ACTUAL_DIFF=$(echo "$DIFFERENCE - $DIFF_EXPECTED" | bc | sed 's/-//')
    
    echo ""
    if (( $(echo "$WITHOUT_DIFF < 100" | bc -l) )); then
        echo "✅ Test 1 PASSED: Without Standing Mats value is correct"
    else
        echo "❌ Test 1 FAILED: Without Standing Mats value incorrect (off by \$$(printf "%.0f" $WITHOUT_DIFF))"
    fi
    
    if (( $(echo "$WITH_DIFF < 100" | bc -l) )); then
        echo "✅ Test 2 PASSED: With Standing Mats value is correct" 
    else
        echo "❌ Test 2 FAILED: With Standing Mats value incorrect (off by \$$(printf "%.0f" $WITH_DIFF))"
    fi
    
    if (( $(echo "$ACTUAL_DIFF < 100" | bc -l) )); then
        echo "✅ Test 3 PASSED: Difference matches expected Standing Mats value"
        echo ""
        echo "🎉 SUCCESS: Standing Mats filter fix is working correctly!"
    else
        echo "❌ Test 3 FAILED: Difference does not match Standing Mats value (off by \$$(printf "%.0f" $ACTUAL_DIFF))"
        echo ""
        echo "🚨 FAILURE: The fix is not working properly."
    fi
else
    echo "❌ Could not extract spend values from API responses"
    echo "🚨 FAILURE: API calls failed."
fi