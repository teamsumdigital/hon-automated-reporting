# HON Meta Ad Sync July Data Investigation Report

**Date**: September 11, 2025  
**Issue**: Meta ad sync pulling data from July instead of just the last 14 days  
**Status**: Root cause identified with solution recommendations  

## Executive Summary

The investigation found that there is currently **NO July data** in the database. However, a critical inconsistency in database clearing logic across two different sync functions was identified as the potential cause of intermittent July data appearing in the system.

## Current Database State

✅ **Good News**: No July data currently exists
- **Records**: 1,000 total Meta ad records
- **Date Range**: August 28, 2025 to September 10, 2025 (14-day window)
- **Distribution**: Most records concentrated around August 28-30 (peak activity)

## Root Cause Analysis

### 🚨 Critical Issue: Inconsistent Database Clearing Logic

The system has **TWO different sync functions** with **completely different** database clearing strategies:

#### 1. Webhook Sync (`app/api/webhook.py` line 195)
```python
# ❌ PROBLEM: Clears ALL data regardless of date range
supabase.table('meta_ad_data').delete().gt('id', 0).execute()
```
- **Impact**: Removes ALL historical data, then inserts 14-day window
- **Risk**: If this fails mid-process, database could be empty
- **Used by**: N8N webhook triggers (`sync_14_day_ad_data`)

#### 2. Meta Ad Reports Sync (`app/api/meta_ad_reports.py` line 162)
```python
# ✅ CORRECT: Clears only the date range being synced
supabase.table('meta_ad_data').delete()
  .gte('reporting_starts', start_date.isoformat())
  .lte('reporting_ends', end_date.isoformat())
  .execute()
```
- **Impact**: Removes only data within sync period, preserves other data
- **Safer**: If sync fails, only affected date range is lost
- **Used by**: Direct API calls (`/sync-14-days`)

## How July Data Could Appear

### Scenario 1: Historical Backfill
If someone ran a historical sync script or backfill process that inserted July data, it would persist until:
- The webhook sync runs (clears everything)
- Manual database maintenance

### Scenario 2: Date Range Calculation Error
Although the current date calculation is correct (August 28 - September 10), there may be edge cases where:
- Timezone issues cause incorrect date ranges
- Emergency fix logic triggers inappropriately
- Manual target_date parameters include July dates

### Scenario 3: Mixed Sync Usage
Different sync functions being called could lead to:
- July data inserted by one process
- Preserved by scoped clearing in meta_ad_reports.py
- Only cleared when webhook sync runs

## Meta API Analysis

✅ **API Parameters are Correct**:
```python
params = {
    'time_range': {
        'since': start_date.strftime('%Y-%m-%d'),  # 2025-08-28
        'until': end_date.strftime('%Y-%m-%d')     # 2025-09-10
    },
    'level': 'ad',
    'time_increment': 7,  # Weekly segmentation
    'limit': 100
}
```

The Meta API is being called with proper 14-day date constraints. The issue is not with data fetching but with database management.

## Date Calculation Logic

✅ **Current Calculation Works Correctly**:
```
Target date: 2025-09-11 (Pacific timezone)
End date: 2025-09-10 (yesterday)  
Start date: 2025-08-28 (14 days back)
Total range: 14 days ✓
```

The emergency fix logic that would use recent data instead of old dates is not currently triggering.

## Recommended Solutions

### 🎯 Immediate Fix: Standardize Database Clearing

**Option 1 (Recommended): Update webhook.py to use scoped clearing**
```python
# Fix in webhook.py around line 195
# Calculate the actual date range being synced
from datetime import date, timedelta

# Calculate 14-day window 
end_date = date.today() - timedelta(days=1)
start_date = end_date - timedelta(days=13)

# Clear only data in the sync period (safer approach)
supabase.table('meta_ad_data').delete().gte(
    'reporting_starts', start_date.isoformat()
).lte(
    'reporting_ends', end_date.isoformat()
).execute()
```

**Option 2 (Alternative): Update meta_ad_reports.py to use full clearing**
- Less recommended as it's riskier
- Could lose data if sync fails

### 🔧 Additional Improvements

1. **Add Logging for Database Operations**
   ```python
   logger.info(f"🧹 Clearing records from {start_date} to {end_date}")
   result = supabase.table('meta_ad_data').delete()...
   logger.info(f"✅ Cleared {result.count if result.count else 'unknown'} records")
   ```

2. **Add Date Range Validation**
   ```python
   # Prevent accidental historical syncs
   if (date.today() - start_date).days > 30:
       logger.warning(f"⚠️ Unusual date range detected: {start_date} to {end_date}")
   ```

3. **Add Data Integrity Checks**
   ```python
   # Verify inserted data is within expected range
   if inserted_data:
       actual_range = check_inserted_date_range(inserted_data)
       logger.info(f"📊 Inserted data range: {actual_range}")
   ```

## Testing Plan

### Phase 1: Immediate Verification
1. ✅ **Completed**: Verify current database state (no July data found)
2. **Monitor**: Check if July data reappears over next few syncs
3. **Document**: Log which sync function is being called when

### Phase 2: Fix Implementation
1. **Backup**: Export current meta_ad_data table
2. **Fix**: Implement scoped clearing in webhook.py
3. **Test**: Run webhook sync and verify behavior
4. **Validate**: Ensure only 14-day window remains

### Phase 3: Validation
1. **Multiple Syncs**: Run several sync cycles to ensure consistency
2. **Edge Cases**: Test with different time zones and target dates
3. **Monitor**: Check logs for any unusual date ranges

## Preventive Measures

### 1. Monitoring Alerts
- Alert if database contains data older than 20 days
- Alert if sync date ranges exceed expected windows
- Alert if clearing operations affect more than expected records

### 2. Data Validation
- Add database constraints on reporting_starts/reporting_ends
- Implement date range sanity checks in sync functions
- Add automated data quality checks

### 3. Operational Procedures
- Document which sync function to use for different scenarios
- Establish clear procedures for historical data management
- Regular database cleanup and validation

## Conclusion

While no July data currently exists in the database, the inconsistent clearing logic between sync functions creates a significant risk for data quality issues. The recommended fix is to standardize the database clearing approach using scoped deletion based on the actual date range being synced.

**Priority**: High - Fix should be implemented to prevent future data integrity issues  
**Complexity**: Low - Single line change with proper testing  
**Impact**: High - Ensures consistent 14-day data window as intended  

## Next Steps

1. **Immediate**: Implement scoped clearing fix in webhook.py
2. **Short-term**: Add enhanced logging and validation
3. **Long-term**: Implement monitoring and alerting system
4. **Follow-up**: Document operational procedures for data management

---
*Report generated by Claude Code on 2025-09-11*