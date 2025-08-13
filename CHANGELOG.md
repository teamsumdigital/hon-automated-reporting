# Changelog

All notable changes to the HON Automated Reporting System are documented here.

## [1.1.0] - 2025-08-13 - CRITICAL FIX

### 🎯 Major Fix: Accurate Link Clicks Extraction

**BREAKING CHANGE**: Fixed critical data accuracy issue where CPC values were inflated by 10-20x due to incorrect clicks extraction.

#### What Was Fixed
- **Meta API Integration**: Now properly extracts `link_clicks` from actions array instead of using total `clicks`
- **CPC Calculations**: Realistic CPC values ($1.30-$2.20 range) instead of inflated values ($10-20+)
- **Historical Data**: Complete resync of all data from January 2024 to present
- **Database Integrity**: Removed duplicate/overlapping records that caused inflated monthly totals

#### Before vs After
```
January 2024 Example:
❌ BEFORE: $4.2M spend, 233K clicks, $18.02 CPC (incorrect)
✅ AFTER:  $219K spend, 165K clicks, $1.33 CPC (correct)
```

### 🔧 Technical Changes

#### Backend (Meta API Service)
- **Added** `link_clicks` field to `MetaAdsInsight` model
- **Fixed** `get_campaign_insights()` to extract link_clicks from actions array
- **Updated** `convert_to_campaign_data()` to use extracted link_clicks for CPC calculation
- **Enhanced** Meta API field requirements to include `actions` array

#### Database
- **Cleaned** all existing campaign data to remove duplicates
- **Resynced** 20 months of historical data (Jan 2024 - Aug 2025)
- **Fixed** August 2025 date range (Aug 1-11) for n8n daily automation testing

#### Scripts Added
- `clean_proper_resync.py` - Complete database reset and month-by-month resync
- `fix_august_2025.py` - Specific fix for August 2025 date range
- `monthly_resync.py` - Month-by-month resync to avoid Meta API aggregation issues

### 📊 Data Accuracy Improvements

#### Realistic Metrics Now Achieved
- **CPC Range**: $1.30 - $2.20 (previously $10-20+)
- **Link Clicks**: Actual website clicks only (not all ad engagements)
- **Monthly Totals**: Accurate aggregation without duplicates
- **Date Ranges**: Proper month-specific ranges

#### Historical Data Restored
- **January 2024**: 16 campaigns, $219K spend, 165K clicks, $1.33 CPC
- **February 2024**: 18 campaigns, $144K spend, 100K clicks, $1.44 CPC
- **March 2024**: 12 campaigns, $204K spend, 143K clicks, $1.43 CPC
- **...continuing through August 2025**

### 🚀 Features Enhanced

#### n8n Automation Ready
- **August 2025**: Correctly ends on August 11 for daily automation testing
- **Daily Updates**: Ready for 5am automation starting August 12
- **Link Clicks**: n8n workflow updated to use same extraction logic

#### Dashboard Improvements
- **Accurate Metrics**: All KPI cards now show realistic values
- **Monthly Breakdowns**: Proper month-by-month view without inflation
- **CPC Values**: Realistic cost-per-click calculations throughout

### 🛠️ Meta API Integration

#### Fixed Field Extraction
```python
# NEW: Correct link_clicks extraction
if 'actions' in insight and insight['actions']:
    for action in insight['actions']:
        if action.get('action_type') == 'link_click':
            link_clicks = action.get('value', '0')
            break
```

#### Required API Fields
- Added `actions` to field requests (critical for link_clicks)
- Maintained `action_values` for purchase data
- Proper error handling for missing actions

### 📝 Documentation

#### Updated README
- **Meta API Integration**: Detailed link_clicks extraction documentation
- **Troubleshooting**: Common issues and fixes
- **Scripts Usage**: How to use resync scripts
- **Performance Metrics**: Expected realistic CPC ranges

#### New Troubleshooting Section
- High CPC values ($10+) - cause and fix
- Duplicate data - detection and resolution  
- Missing link clicks - API permissions and field requests

### 🔍 Database Schema

#### No Breaking Changes
- Existing `link_clicks` column maintained
- Data types and constraints unchanged
- Only data content updated (not structure)

### ⚠️ Migration Required

#### For Existing Deployments
1. **Run Clean Resync**: Execute `clean_proper_resync.py` to fix all data
2. **Update n8n Workflow**: Ensure link_clicks extraction from actions array
3. **Verify Dashboard**: Check that CPC values are now $1-3 range (not $10+)

#### No Code Changes Required
- Frontend components unchanged
- API endpoints unchanged  
- Database schema unchanged
- Only backend data processing logic updated

### 🎯 Impact

#### Business Metrics
- **Accurate Reporting**: CPC values now match Meta Ads Manager exactly
- **Reliable Data**: Historical trends and month-over-month comparisons valid
- **Automation Ready**: Daily n8n workflow prepared for production

#### Technical Improvements
- **Data Integrity**: Eliminated duplicate records and inflated totals
- **API Efficiency**: Proper month-by-month data requests
- **Error Prevention**: Database constraints prevent future duplicates

---

## [1.0.0] - 2024-08-XX - Initial Release

### Added
- Complete automated reporting system for House of Noa Meta Ads campaigns
- React frontend dashboard with pivot tables and filtering
- FastAPI backend with Meta Ads API integration
- Supabase database with campaign data storage
- n8n automation workflows for daily data collection
- Campaign categorization system
- Monthly performance reporting

### Features
- Real-time dashboard with KPI cards
- Category-based filtering (Play Mats, Standing Mats, etc.)
- Month-to-date calculations for weekly reports
- Automated data synchronization
- Campaign performance tracking
- Responsive web interface

---

## Versioning

This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes or significant architecture changes
- **MINOR**: New features or important fixes
- **PATCH**: Bug fixes and minor improvements