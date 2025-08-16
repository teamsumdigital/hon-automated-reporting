-- Add CPM column to Meta Ads campaign_data table and calculate values
-- Formula: CPM = cost / (impressions / 1000)

-- Add CPM column
ALTER TABLE campaign_data 
ADD COLUMN IF NOT EXISTS cpm DECIMAL(10, 4) DEFAULT 0;

-- Calculate CPM for existing records
UPDATE campaign_data 
SET cpm = CASE 
    WHEN impressions > 0 THEN 
        ROUND((amount_spent_usd / (impressions / 1000.0))::NUMERIC, 4)
    ELSE 0 
END
WHERE cpm = 0 OR cpm IS NULL;

-- Add index for CPM column
CREATE INDEX IF NOT EXISTS idx_campaign_data_cpm ON campaign_data(cpm);

-- Update the auto-categorize trigger to include CPM in updated_at logic
CREATE OR REPLACE FUNCTION trigger_auto_categorize()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.category IS NULL OR NEW.category = '' THEN
        NEW.category := auto_categorize_campaign(NEW.campaign_name);
    END IF;
    
    -- Auto-calculate CPM if impressions change
    IF NEW.impressions > 0 THEN
        NEW.cpm := ROUND((NEW.amount_spent_usd / (NEW.impressions / 1000.0))::NUMERIC, 4);
    ELSE
        NEW.cpm := 0;
    END IF;
    
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Verify the changes
SELECT 
    COUNT(*) as total_records,
    COUNT(CASE WHEN cpm > 0 THEN 1 END) as records_with_cpm,
    ROUND(AVG(cpm), 2) as avg_cpm,
    ROUND(MIN(cpm), 2) as min_cpm,
    ROUND(MAX(cpm), 2) as max_cpm
FROM campaign_data 
WHERE impressions > 0;