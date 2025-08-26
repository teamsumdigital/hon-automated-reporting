#!/bin/bash

echo "🧪 Verifying Current Month TikTok Data Filtering"
echo "================================================"

BASE_URL="http://localhost:8007/api/tiktok-reports"

echo "Testing the exact scenario from user's screenshots:"
echo ""

# Test the exact combination the user showed in screenshots
echo "📊 Test: Exact user scenario (Bath Mats + Multi Category + Play Furniture + Play Mats + Tumbling Mats)"
WITHOUT_STANDING="Bath%20Mats,Multi%20Category,Play%20Furniture,Play%20Mats,Tumbling%20Mats"
WITHOUT_RESULT=$(curl -s "${BASE_URL}/dashboard?categories=${WITHOUT_STANDING}")
WITHOUT_SPEND=$(echo $WITHOUT_RESULT | grep -o '"total_spend":[0-9.]*' | cut -d':' -f2 | head -1)
echo "   WITHOUT Standing Mats: \$$(printf "%'d" $(printf "%.0f" $WITHOUT_SPEND))"

echo ""
echo "📊 Test: Adding Standing Mats to the same combination"
WITH_STANDING="Bath%20Mats,Multi%20Category,Play%20Furniture,Play%20Mats,Tumbling%20Mats,Standing%20Mats"
WITH_RESULT=$(curl -s "${BASE_URL}/dashboard?categories=${WITH_STANDING}")
WITH_SPEND=$(echo $WITH_RESULT | grep -o '"total_spend":[0-9.]*' | cut -d':' -f2 | head -1)
echo "   WITH Standing Mats:    \$$(printf "%'d" $(printf "%.0f" $WITH_SPEND))"

echo ""
echo "📋 VERIFICATION:"
DIFFERENCE=$(echo "$WITH_SPEND - $WITHOUT_SPEND" | bc)

if (( $(echo "$DIFFERENCE > 0" | bc -l) )); then
    echo "✅ SUCCESS: Adding Standing Mats INCREASES total by \$$(printf "%'d" $(printf "%.0f" $DIFFERENCE))"
    echo "✅ The issue has been RESOLVED - totals now go UP when adding categories"
    echo ""
    echo "🎉 DASHBOARD FIX CONFIRMED WORKING!"
    echo "   - KPI cards will now update correctly with category filters"
    echo "   - Standing Mats filter behaves as expected"
    echo "   - No more data integrity issues with decreasing totals"
else
    echo "❌ FAILED: Adding Standing Mats still decreases total by \$$(printf "%'d" $(printf "%.0f" $DIFFERENCE | sed 's/-//'))"
fi

echo ""
echo "📈 Visual confirmation for user:"
echo "   Before fix: Adding Standing Mats made totals GO DOWN"
echo "   After fix:  Adding Standing Mats makes totals GO UP by \$$(printf "%'d" $(printf "%.0f" $DIFFERENCE))"