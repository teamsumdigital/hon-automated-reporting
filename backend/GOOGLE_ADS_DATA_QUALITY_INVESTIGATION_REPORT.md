# 🚨 GOOGLE ADS DATA QUALITY INVESTIGATION REPORT
**Critical Data Accuracy Issue - August 1-26, 2025**

## Executive Summary

**CRITICAL FINDING**: Google Ads data in the `google_campaign_data` table contains **correct spend amounts** but **incorrect ROAS and CPA calculations** due to stale revenue and conversion data. This creates a significant business intelligence issue where performance metrics are systematically underreported.

## Root Cause Analysis

### Issue Identified: **Data Freshness Discrepancy**

The investigation reveals that while **spend data is current and accurate**, the **revenue and conversion data is stale/outdated** in the database compared to what the Google Ads API currently returns.

### Evidence from August 13, 2025 Sample:

| Campaign | API Revenue | DB Revenue | Revenue Gap | API ROAS | DB ROAS | ROAS Gap |
|----------|-------------|------------|-------------|----------|---------|-----------|
| Multiple - Search - Brand | $15,380.36 | $13,757.87 | **-$1,622.49** | 152.89 | 136.75 | **-16.13** |
| Playmats - Shopping - Brand | $6,429.02 | $4,218.81 | **-$2,210.21** | 86.19 | 56.56 | **-29.63** |
| Playmats - Shopping - Non-Brand | $4,178.27 | $3,311.87 | **-$866.40** | 5.96 | 4.72 | **-1.24** |
| Playmats - Search - Non-Brand | $1,673.07 | $611.34 | **-$1,061.73** | 5.14 | 1.88 | **-3.26** |
| Multiple - Search - Brand - Categories | $3,449.02 | $2,913.18 | **-$535.84** | 36.09 | 30.48 | **-5.61** |

### Data Quality Statistics (August 1-26, 2025):
- **Total Records**: 255 campaigns
- **Issues Found**: 118 campaigns (46% of records)
- **Spend Accuracy**: 100% (perfect match)
- **Revenue Accuracy**: ~85% (systematic underreporting)
- **Purchase Count Accuracy**: ~90% (missing conversions)

## Technical Root Cause

### 1. **Google Ads Attribution Window Issue**
- Google Ads uses attribution windows (7-day, 30-day, etc.)
- Conversions can be attributed to past campaign dates after the initial data sync
- The current sync process doesn't refresh historical conversion data

### 2. **Partial Data Update Problem**
- **Spend data**: Updates correctly (immediate in Google Ads)
- **Conversion data**: Not refreshed (requires historical data re-sync)
- **Database**: Contains stale conversion values from initial sync

### 3. **API Field Mapping Analysis**
The Google Ads service correctly maps:
```python
# Correct API field mapping
cost_micros -> amount_spent_usd  # ✅ Working
conversions -> website_purchases  # ❌ Stale data  
conversions_value -> purchases_conversion_value  # ❌ Stale data
```

### 4. **Calculation Logic Verification**
The ROAS/CPA calculation logic is correct:
```python
# Correct calculations using wrong data
roas = conversion_value / spend  # ✅ Logic correct, data stale
cpa = spend / conversions        # ✅ Logic correct, data stale
```

## Business Impact

### Immediate Business Risks:
- **Underreported Performance**: Campaigns appear less profitable than reality
- **Incorrect Budget Allocation**: May reduce spend on actually profitable campaigns  
- **Strategic Misguidance**: C-level decisions based on incorrect ROAS data
- **Client Reporting Issues**: External reports contain inaccurate performance data

### Financial Impact Example (Aug 13 alone):
- **Reported ROAS**: 8.85 (database)
- **Actual ROAS**: ~12.5 (estimated from API)
- **Performance Gap**: ~40% underreported

## Recommended Solutions

### IMMEDIATE FIX (Priority 1 - Implement within 24 hours):

#### 1. **Historical Data Refresh**
```python
# Re-sync conversion data for August 1-26, 2025
# This will update stale conversion values with current attribution
python refresh_historical_conversions.py --start-date 2025-08-01 --end-date 2025-08-26
```

#### 2. **Daily Conversion Refresh**
Implement daily refresh of past 30 days conversion data to capture attribution updates:
```python
# Add to daily sync process
def refresh_conversion_data():
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    # Re-sync conversion data only
```

### LONG-TERM FIX (Priority 2 - Implement within 1 week):

#### 1. **Attribution Window Handling**
- Modify sync process to refresh past 7-30 days on each run
- Implement conversion data versioning to track changes
- Add attribution window metadata to database schema

#### 2. **Data Freshness Monitoring**
- Add data quality checks comparing API vs database
- Implement alerts for significant ROAS/CPA discrepancies
- Create daily data integrity reports

#### 3. **Enhanced Sync Strategy**
```python
# Proposed enhanced sync logic
def enhanced_google_sync():
    # 1. Sync new data (current day)
    sync_new_data(date.today())
    
    # 2. Refresh conversion data (past 30 days)
    refresh_historical_conversions(days_back=30)
    
    # 3. Validate data quality
    run_data_quality_checks()
    
    # 4. Alert on discrepancies > 5%
    alert_on_major_discrepancies()
```

## Implementation Scripts

### Script 1: Fix Current Data
```python
# /backend/fix_google_ads_conversion_data.py
# Re-sync August 1-26, 2025 conversion data
```

### Script 2: Daily Conversion Refresh  
```python
# /backend/daily_conversion_refresh.py  
# Add to cron/scheduled tasks
```

### Script 3: Data Quality Monitor
```python
# /backend/monitor_google_ads_quality.py
# Daily validation and alerting
```

## Validation Plan

### Phase 1: Fix Validation (24 hours)
1. Run historical refresh for August 1-26, 2025
2. Compare pre/post ROAS values
3. Validate against direct API calls
4. Update dashboard and verify metrics

### Phase 2: Monitoring Validation (1 week)
1. Implement daily quality checks
2. Monitor for new discrepancies
3. Validate attribution window handling
4. Confirm business metric accuracy

## Quality Assurance Measures

### Daily Checks:
- [ ] API vs Database revenue comparison (tolerance: 2%)
- [ ] ROAS calculation validation  
- [ ] Conversion count accuracy
- [ ] Missing attribution detection

### Weekly Audits:
- [ ] Historical data integrity review
- [ ] Performance trend validation
- [ ] Client reporting accuracy check
- [ ] Attribution window impact analysis

## Critical Success Metrics

### Before Fix (Current State):
- **Data Accuracy**: 54% of records accurate
- **ROAS Reporting**: ~40% underreported
- **Business Confidence**: Low due to data inconsistency

### After Fix (Target State):
- **Data Accuracy**: >98% of records accurate
- **ROAS Reporting**: <2% variance from API
- **Business Confidence**: High with validated data

---

## Action Items

### URGENT (Next 24 hours):
1. ✅ **Completed**: Root cause analysis and documentation
2. 🔄 **In Progress**: Implement historical conversion data refresh
3. ⏳ **Pending**: Validate fix against API data
4. ⏳ **Pending**: Update dashboard with corrected metrics

### SHORT-TERM (Next week):
1. ⏳ **Pending**: Implement daily conversion refresh
2. ⏳ **Pending**: Add data quality monitoring
3. ⏳ **Pending**: Create attribution window handling
4. ⏳ **Pending**: Business stakeholder validation

### LONG-TERM (Next month):
1. ⏳ **Pending**: Enhanced sync architecture
2. ⏳ **Pending**: Automated quality assurance
3. ⏳ **Pending**: Historical data versioning
4. ⏳ **Pending**: Attribution analytics

---

**Report Generated**: August 28, 2025  
**Investigator**: Data Quality Sentinel Agent  
**Priority**: CRITICAL - Business Impact  
**Status**: Root cause identified, fix implementation in progress

---

*This investigation reveals a critical data freshness issue that systematically underreports Google Ads performance. Immediate action is required to restore data integrity and business confidence in the reporting system.*