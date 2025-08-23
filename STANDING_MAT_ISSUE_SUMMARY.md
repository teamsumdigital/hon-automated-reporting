# Standing Mat Categorization Issue - Meta Ad Level Dashboard

## User's Original Question

The user noticed a critical data inconsistency in the Meta Ad Level dashboard at `http://localhost:3007`. They observed that high-spending Standing Mat ads were disappearing when switching between filtered and unfiltered views.

**Key User Observations:**
- Standing Mat ads represent about one-third of all account spend
- When "Standing Mats" filter is selected, high-spending ads appear normally
- When switching to "All Categories" (no filter), these same high-spending Standing Mat ads completely disappear from the table
- This creates a data visibility issue where significant spend is hidden in the unfiltered view

## Screenshot Evidence Provided

### Image #1: "Standing Mats" Filter Applied
- Shows the Meta Ad Level dashboard with "Standing Mats" filter selected
- Displays 85 ads with the top 10 highlighted in green by spend
- Top spenders visible:
  - Standing Mats Video Ad Don't Buy Iteration: ~$5,213 spend
  - Standing Mat Launch Swatch Lifestyle Devon: ~$4,222 spend  
  - Standing Mat Launch Multiple Styles Video Ad V1: ~$3,497 spend
- Clear data showing substantial Standing Mat ad performance

### Image #2: "All Categories" View (No Filter)
- Shows the same dashboard with no category filter applied (all categories)
- The high-spending Standing Mat ads highlighted in Image #1 are completely missing
- Different ads appear in the table, none of which are the top Standing Mat spenders
- Total spend and metrics show different values than when filtered

## Technical Investigation Results

### Initial Incorrect Diagnosis
- **Claude's Error**: Initially diagnosed as empty Meta Ad Level table requiring sync
- **Reality**: Table contained 233 ads with substantial Standing Mat data

### Confirmed Issue Through API Testing
Using `/api/meta-ad-reports/ad-data` endpoint:

**Unfiltered ("All Categories"):**
- Returns 41 Standing Mat ads
- Total Standing Mat spend: $10,232
- Missing the top spending Standing Mat ads

**Filtered ("Standing Mats" selected):**
- Returns 87 Standing Mat ads  
- Includes high-spend ads like $5,237, $4,225, $3,517 spend ads
- More than double the number of ads compared to unfiltered view

### Root Cause Identified
This is a **backend filtering logic bug** in the Meta Ad Level API. When no category filter is applied ("All Categories"), the backend incorrectly excludes certain Standing Mat ads that are properly included when the "Standing Mats" filter is specifically requested.

**Specific Evidence:**
- Top 3 Standing Mat ads by spend are missing from "All Categories" view
- "Standing Mats Video Ad Don't Buy Iteration" ($5,237 spend) - Missing in unfiltered
- "Standing Mat Launch Swatch Lifestyle Devon" ($4,225 spend) - Missing in unfiltered  
- "Standing Mat Launch Multiple Styles Video Ad V1" ($3,517 spend) - Missing in unfiltered

## Impact Assessment

**Business Impact:**
- High-spend Standing Mat performance is hidden in default dashboard view
- Users cannot see true account performance without applying specific filters
- Standing Mat category appears to have lower spend than reality (~$10K vs actual higher amount)
- Decision-making based on "All Categories" view would be incorrect

**Technical Impact:**
- Data inconsistency between filtered and unfiltered API responses
- Backend API returning different datasets for same underlying data
- Frontend displays incomplete information in default state

## Next Steps Required

1. **Investigate Backend API Logic**: Examine why `/api/meta-ad-reports/ad-data` returns different Standing Mat results when filtered vs unfiltered
2. **Fix Filtering Logic**: Ensure "All Categories" view includes all ads that appear in individual category filters
3. **Verify Data Consistency**: Confirm all high-spend Standing Mat ads appear in both views
4. **Test Other Categories**: Check if similar issues exist with other product categories

## Technical Context

- **Project**: HON Automated Reporting  
- **Frontend Port**: 3007
- **Backend Port**: 8007
- **Affected API**: `/api/meta-ad-reports/ad-data`
- **Data Structure**: Returns `grouped_ads` array with 233 total ads
- **Environment**: Development server (localhost)

## Status: CONFIRMED BUG
This is a legitimate backend filtering logic issue, not a data sync or categorization problem. The inconsistent results between filtered and unfiltered views represent a critical bug affecting data visibility and business decision-making.