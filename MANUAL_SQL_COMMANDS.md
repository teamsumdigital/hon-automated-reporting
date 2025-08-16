# Manual SQL Commands for TikTok CPM Column

Please run these SQL commands in your Supabase Dashboard > SQL Editor:

## 1. Add CPM Column to TikTok Campaign Data Table

```sql
-- Add CPM column to tiktok_campaign_data table
ALTER TABLE tiktok_campaign_data 
ADD COLUMN IF NOT EXISTS cpm DECIMAL(10, 4) DEFAULT 0;

-- Add comment for documentation
COMMENT ON COLUMN tiktok_campaign_data.cpm IS 'Cost per mille (thousand impressions) = cost / (impressions / 1000)';
```

## 2. Calculate CPM for Existing Records

```sql
-- Update existing records to calculate CPM
UPDATE tiktok_campaign_data 
SET cpm = CASE 
    WHEN impressions > 0 THEN ROUND((amount_spent_usd / (impressions::decimal / 1000)), 4)
    ELSE 0 
END
WHERE cpm = 0 OR cpm IS NULL;
```

## 3. Add CPM to Monthly Reports Table

```sql
-- Add avg_cpm column to monthly reports
ALTER TABLE tiktok_monthly_reports 
ADD COLUMN IF NOT EXISTS avg_cpm DECIMAL(10, 4) DEFAULT 0;

-- Add comment for documentation
COMMENT ON COLUMN tiktok_monthly_reports.avg_cpm IS 'Average cost per mille for the month';
```

## 4. Create Index for Performance

```sql
-- Create index for CPM filtering
CREATE INDEX IF NOT EXISTS idx_tiktok_campaign_data_cpm ON tiktok_campaign_data(cpm);
```

## 5. Verify the Changes

```sql
-- Check if CPM column was added successfully
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'tiktok_campaign_data' 
AND column_name = 'cpm';

-- Check sample CPM calculations
SELECT 
    campaign_name,
    amount_spent_usd,
    impressions,
    cpm,
    CASE 
        WHEN impressions > 0 THEN ROUND((amount_spent_usd / (impressions::decimal / 1000)), 4)
        ELSE 0 
    END as calculated_cpm
FROM tiktok_campaign_data 
WHERE amount_spent_usd > 0 
LIMIT 5;
```

After running these commands, the CPM column will be available and calculated for all existing TikTok campaign data!