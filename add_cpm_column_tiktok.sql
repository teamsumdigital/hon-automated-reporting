-- Add CPM column to TikTok campaign data table
-- CPM = Cost Per Mille (cost per thousand impressions)

-- Add CPM column if it doesn't exist
DO $$ 
BEGIN
    -- Add cpm column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'tiktok_campaign_data' AND column_name = 'cpm') THEN
        ALTER TABLE tiktok_campaign_data ADD COLUMN cpm DECIMAL(10, 4) DEFAULT 0;
        
        COMMENT ON COLUMN tiktok_campaign_data.cpm IS 'Cost per mille (thousand impressions) = cost / (impressions / 1000)';
        
        -- Create index for CPM filtering
        CREATE INDEX IF NOT EXISTS idx_tiktok_campaign_data_cpm ON tiktok_campaign_data(cpm);
        
        -- Update existing records to calculate CPM
        UPDATE tiktok_campaign_data 
        SET cpm = CASE 
            WHEN impressions > 0 THEN ROUND((amount_spent_usd / (impressions::decimal / 1000)), 4)
            ELSE 0 
        END
        WHERE cpm = 0 OR cpm IS NULL;
        
        RAISE NOTICE 'CPM column added and calculated for existing TikTok campaign data';
    ELSE
        RAISE NOTICE 'CPM column already exists in tiktok_campaign_data table';
    END IF;
END $$;

-- Also add to monthly reports table
DO $$ 
BEGIN
    -- Add avg_cpm column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'tiktok_monthly_reports' AND column_name = 'avg_cpm') THEN
        ALTER TABLE tiktok_monthly_reports ADD COLUMN avg_cpm DECIMAL(10, 4) DEFAULT 0;
        
        COMMENT ON COLUMN tiktok_monthly_reports.avg_cpm IS 'Average cost per mille for the month';
        
        RAISE NOTICE 'avg_cpm column added to tiktok_monthly_reports table';
    ELSE
        RAISE NOTICE 'avg_cpm column already exists in tiktok_monthly_reports table';
    END IF;
END $$;

-- Update the unified view to include CPM
CREATE OR REPLACE VIEW unified_campaign_data AS
SELECT 
    'meta' as platform,
    campaign_id,
    campaign_name,
    category,
    NULL as campaign_type,  -- Meta doesn't have campaign_type yet
    reporting_starts,
    reporting_ends,
    amount_spent_usd,
    website_purchases,
    purchases_conversion_value,
    impressions,
    link_clicks,
    cpa,
    roas,
    cpc,
    NULL::decimal(10,4) as cpm,  -- Meta table doesn't have CPM yet
    created_at,
    updated_at
FROM campaign_data

UNION ALL

SELECT 
    'google' as platform,
    campaign_id,
    campaign_name,
    category,
    campaign_type,
    reporting_starts,
    reporting_ends,
    amount_spent_usd,
    website_purchases,
    purchases_conversion_value,
    impressions,
    link_clicks,
    cpa,
    roas,
    cpc,
    NULL::decimal(10,4) as cpm,  -- Google table doesn't have CPM yet
    created_at,
    updated_at
FROM google_campaign_data

UNION ALL

SELECT 
    'tiktok' as platform,
    campaign_id,
    campaign_name,
    category,
    campaign_type,
    reporting_starts,
    reporting_ends,
    amount_spent_usd,
    website_purchases,
    purchases_conversion_value,
    impressions,
    link_clicks,
    cpa,
    roas,
    cpc,
    cpm,
    created_at,
    updated_at
FROM tiktok_campaign_data;

SELECT 'CPM column migration completed successfully!' as result;