# Dashboard Column Update Process

## Overview
Process to update dashboard tables from old column structure to new simplified structure:

**FROM:** `Month | Spend | Link Clicks | Purchases | Revenue | CPA | ROAS | CPC`  
**TO:** `Month | Spend | Revenue | ROAS | CPA | CPC | CPM`

## Step-by-Step Process

### 1. Backend Model Updates
Update the data models to include CPM and reflect new structure:

**Files to Update:**
- `backend/app/models/[platform]_campaign_data.py`

**Changes:**
```python
# Add CPM field to data models
class CampaignData(BaseModel):
    # ... existing fields ...
    cpm: Decimal = Field(default=0, decimal_places=4)

class PivotTableData(BaseModel):
    month: str
    spend: Decimal
    revenue: Decimal        # Remove: link_clicks, purchases
    roas: Decimal
    cpa: Decimal
    cpc: Decimal
    cpm: Decimal           # Add CPM as last column
```

### 2. Backend Service Updates
Update reporting and API services to calculate CPM and remove old dependencies:

**Files to Update:**
- `backend/app/services/reporting.py`
- `backend/app/services/[platform]_ads_service.py`

**Key Changes:**
```python
# In convert_to_campaign_data():
# Calculate CPM
cpm = (spend / (Decimal(impressions) / 1000)).quantize(Decimal('0.0001')) if impressions > 0 else Decimal('0')

# Add to CampaignData constructor:
campaign_data = CampaignData(
    # ... existing fields ...
    cpm=cpm
)

# In reporting service pivot table generation:
# Remove link_clicks from aggregation
# Add CPM calculation:
monthly_agg['cpm'] = (monthly_agg['amount_spent_usd'] / (monthly_agg['impressions'] / 1000))
monthly_agg['cpm'] = monthly_agg['cpm'].fillna(0)

# Update PivotTableData creation to remove old fields and add CPM
pivot_data.append(PivotTableData(
    month=row['month'],
    spend=Decimal(str(row['amount_spent_usd'])),
    revenue=Decimal(str(row['purchases_conversion_value'])),
    roas=Decimal(str(row['roas'])),
    cpa=Decimal(str(row['cpa'])),
    cpc=Decimal(str(row['cpc'])),
    cpm=Decimal(str(row['cpm']))
))
```

### 3. Frontend TypeScript Interface Updates
Update API interfaces to match new structure:

**Files to Update:**
- `frontend/src/services/api.ts`

**Changes:**
```typescript
export interface PivotTableData {
  month: string;
  spend: number;
  revenue: number;    // Remove: link_clicks, purchases
  roas: number;
  cpa: number;
  cpc: number;
  cpm: number;       // Add CPM
}

export interface MTDSummary {
  // ... existing fields ...
  avg_cpm: number;   // Add avg_cpm
}
```

### 4. Frontend Component Updates
Update the actual dashboard component that renders the table:

**Critical:** Find the correct component! Use this process:

```bash
# 1. Find which component is actually rendering the table
grep -r "Link Clicks" frontend/src/pages/

# 2. Look at routing to understand which component loads
# Check: frontend/src/App.tsx and frontend/src/pages/MainDashboard.tsx
```

**Files to Update:**
- `frontend/src/pages/[Platform]Dashboard.tsx` (the actual rendering component)
- `frontend/src/components/PivotTable.tsx` (if used)

**Key Changes:**
```typescript
// Update hardcoded header array:
['Month', 'Spend', 'Link Clicks', 'Purchases', 'Revenue', 'CPA', 'ROAS', 'CPC']
// TO:
['Month', 'Spend', 'Revenue', 'ROAS', 'CPA', 'CPC', 'CPM']

// Update table body rendering to match new column structure:
// Remove Link Clicks and Purchases <td> elements
// Reorder remaining columns
// Add CPM calculation as last column:

<td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
  ${(() => {
    const totalSpend = /* calculate total spend */;
    const totalImpressions = /* calculate total impressions */;
    return totalImpressions > 0 ? (totalSpend / (totalImpressions / 1000)).toFixed(2) : '0.00';
  })()}
</td>
```

### 5. Database Schema Update
Add CPM column to database (if needed):

**SQL Script:**
```sql
-- Add CPM column
ALTER TABLE [platform]_campaign_data 
ADD COLUMN IF NOT EXISTS cpm DECIMAL(10, 4) DEFAULT 0;

-- Calculate CPM for existing records
UPDATE [platform]_campaign_data 
SET cmp = CASE 
    WHEN impressions > 0 THEN 
        ROUND((amount_spent_usd / (impressions / 1000.0))::NUMERIC, 4)
    ELSE 0 
END
WHERE cpm = 0 OR cpm IS NULL;

-- Add index
CREATE INDEX IF NOT EXISTS idx_[platform]_campaign_data_cpm ON [platform]_campaign_data(cpm);
```

### 6. Testing & Debugging Process

**A. Backend API Testing:**
```bash
# Test API response structure
curl -s "http://localhost:8007/api/reports/dashboard" | jq '.pivot_data[0]'

# Should return:
{
  "month": "2024-01",
  "spend": "219375.08", 
  "revenue": "1600507.69",
  "roas": "7.295",
  "cpa": "31.61", 
  "cpc": "1.32",
  "cpm": "13.88"    # ← CPM should be present
}
```

**B. Frontend Puppeteer Testing:**
```javascript
// Create test script to verify headers
const puppeteer = require('puppeteer');

async function testHeaders() {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  await page.goto('http://localhost:3007');
  
  const headers = await page.evaluate(() => {
    const table = document.querySelector('table');
    const headerCells = table.querySelectorAll('thead th');
    return Array.from(headerCells).map(cell => cell.textContent.trim());
  });
  
  console.log('Headers:', headers);
  console.log('Expected:', ['Month', 'Spend', 'Revenue', 'ROAS', 'CPA', 'CPC', 'CPM']);
  console.log('Match:', JSON.stringify(headers) === JSON.stringify(['Month', 'Spend', 'Revenue', 'ROAS', 'CPA', 'CPC', 'CPM']));
  
  await browser.close();
}
```

### 7. Common Issues & Solutions

**Issue 1: Changes not reflected in browser**
- **Cause:** Frontend cache or wrong component being updated
- **Solution:** 
  ```bash
  # Force rebuild and restart
  cd frontend
  rm -rf dist/ node_modules/.vite/
  npm run build
  npm run dev -- --port 3007 --force
  ```

**Issue 2: TypeScript compilation errors**
- **Cause:** Interface mismatches between API and components
- **Solution:** Update all TypeScript interfaces consistently
- **Check:** `npm run build` should pass without errors

**Issue 3: Wrong component being updated**
- **Cause:** Multiple dashboard components exist (ModernDashboard, SimpleDashboard, etc.)
- **Solution:** Use grep to find actual component with hardcoded headers:
  ```bash
  grep -r "Link Clicks" frontend/src/pages/
  ```

**Issue 4: API returns correct data but UI shows old structure**
- **Cause:** Frontend component has hardcoded headers instead of using API data
- **Solution:** Find and update the hardcoded header arrays in the rendering component

### 8. Verification Checklist

Before considering the update complete:

- [ ] **Backend API:** Returns correct structure with CPM
- [ ] **TypeScript:** Build passes without errors (`npm run build`)
- [ ] **Frontend Display:** Puppeteer test shows correct headers
- [ ] **Data Accuracy:** First row shows reasonable CPM values
- [ ] **Responsive:** Table works on different screen sizes
- [ ] **No Console Errors:** Browser developer tools show no JavaScript errors

### 9. Files Changed Summary

For each platform update, expect to modify:

1. **Backend (4-5 files):**
   - `backend/app/models/[platform]_campaign_data.py`
   - `backend/app/services/reporting.py`
   - `backend/app/services/[platform]_ads_service.py`
   - `database/add_cpm_column_[platform].sql` (optional)

2. **Frontend (2-3 files):**
   - `frontend/src/services/api.ts`
   - `frontend/src/pages/[Platform]Dashboard.tsx` (main component)
   - `frontend/src/components/PivotTable.tsx` (if used)

### 10. Time Estimate
- **Backend changes:** 15-20 minutes
- **Frontend changes:** 10-15 minutes  
- **Testing & debugging:** 10-15 minutes
- **Total:** ~45 minutes per platform

## Next: Apply to TikTok Dashboard

Now that we have the process documented, we can efficiently apply the same changes to:
- TikTokDashboard.tsx
- TikTok-related backend services
- TikTok API interfaces

The process should be much faster since we know exactly what to look for and change!