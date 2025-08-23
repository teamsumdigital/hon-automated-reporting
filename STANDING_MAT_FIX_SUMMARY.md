# Standing Mat Issue Fix Summary

## Problem Identified
The Meta Ad Level dashboard was missing high-spending Standing Mat ads when viewing "All Categories" (unfiltered), but these ads appeared correctly when the "Standing Mats" filter was applied.

## Root Cause
The issue was caused by Supabase's default query limit of 1000 records. When the API endpoint fetched unfiltered data ordered by `ad_name` and `reporting_starts`, it hit this limit and truncated results. Standing Mat ads (alphabetically later) were being cut off.

### Evidence:
- Total records in 14-day range: 1,262
- Default query returned: 1,000 (truncated)
- Standing Mat ads in truncated results: 41 unique ads
- Standing Mat ads when filtered: 87 unique ads
- Missing high-spend ads like "Standing Mats Video Ad Don't Buy Iteration" ($5,237)

## Solution Implemented
Added explicit `.limit(10000)` to all Supabase queries in the Meta Ad Level API endpoints:

1. **`/api/meta-ad-reports/ad-data`** (line 214)
   ```python
   query = query.order('ad_name').order('reporting_starts').limit(10000)
   ```

2. **`/api/meta-ad-reports/summary`** (line 354)
   ```python
   result = query.limit(10000).execute()
   ```

3. **`/api/meta-ad-reports/filters`** (line 388)
   ```python
   result = supabase.table('meta_ad_data').select('category, content_type, format, campaign_optimization').limit(10000).execute()
   ```

## Testing
Created comprehensive test scripts that confirmed:
- Default Supabase queries were truncating at 1,000 records
- High-spending Standing Mat ads were in positions 1,001+ when ordered alphabetically
- The fix ensures all 1,262 records are retrieved

## To Apply the Fix
1. Restart the backend server:
   ```bash
   cd backend
   source venv_new/bin/activate
   uvicorn main:app --reload --port 8007
   ```

2. Verify the fix works by:
   - Navigate to http://localhost:3007 (Meta Ad Level dashboard)
   - Check "All Categories" view shows ~87 Standing Mat ads
   - Confirm high-spend ads like "Standing Mats Video Ad Don't Buy Iteration" appear
   - Switch to "Standing Mats" filter and verify the same ads are present

## Impact
This fix ensures:
- All Standing Mat ads (representing ~1/3 of account spend) are visible in default view
- Data consistency between filtered and unfiltered views
- Accurate business reporting and decision-making
- No more "disappearing" high-spend ads

## File Modified
`/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend/app/api/meta_ad_reports.py`