-- TikTok Ads Campaign Data Table Migration
-- Adds TikTok Ads support alongside existing Meta Ads and Google Ads data

-- TikTok Campaign data table to store TikTok Ads metrics
CREATE TABLE IF NOT EXISTS tiktok_campaign_data (
    id BIGSERIAL PRIMARY KEY,
    campaign_id VARCHAR(50) NOT NULL,
    campaign_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    reporting_starts DATE NOT NULL,
    reporting_ends DATE NOT NULL,
    amount_spent_usd DECIMAL(10, 2) DEFAULT 0,
    website_purchases INTEGER DEFAULT 0,
    purchases_conversion_value DECIMAL(10, 2) DEFAULT 0,
    impressions BIGINT DEFAULT 0,
    link_clicks INTEGER DEFAULT 0,
    cpa DECIMAL(10, 2) DEFAULT 0,
    roas DECIMAL(10, 4) DEFAULT 0,
    cpc DECIMAL(10, 4) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure unique records per campaign per date range
    UNIQUE(campaign_id, reporting_starts, reporting_ends)
);

-- TikTok Ads monthly reporting snapshots
CREATE TABLE IF NOT EXISTS tiktok_monthly_reports (
    id SERIAL PRIMARY KEY,
    report_month DATE NOT NULL, -- First day of the month
    report_date DATE NOT NULL,  -- Actual report generation date
    total_spend DECIMAL(12, 2) DEFAULT 0,
    total_purchases INTEGER DEFAULT 0,
    total_revenue DECIMAL(12, 2) DEFAULT 0,
    total_impressions BIGINT DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,
    avg_cpa DECIMAL(10, 2) DEFAULT 0,
    avg_roas DECIMAL(10, 4) DEFAULT 0,
    avg_cpc DECIMAL(10, 4) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(report_month, report_date)
);

-- Indexes for performance (same as Meta/Google structure)
CREATE INDEX IF NOT EXISTS idx_tiktok_campaign_data_date_range ON tiktok_campaign_data(reporting_starts, reporting_ends);
CREATE INDEX IF NOT EXISTS idx_tiktok_campaign_data_category ON tiktok_campaign_data(category);
CREATE INDEX IF NOT EXISTS idx_tiktok_campaign_data_campaign_id ON tiktok_campaign_data(campaign_id);

-- Function to auto-categorize TikTok campaigns (reuse existing logic)
CREATE OR REPLACE FUNCTION auto_categorize_tiktok_campaign(campaign_name_input VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    result_category VARCHAR(100);
    rule_record RECORD;
BEGIN
    -- Check for manual override first (will need platform-specific overrides)
    SELECT category INTO result_category 
    FROM category_overrides 
    WHERE campaign_id = (SELECT campaign_id FROM tiktok_campaign_data WHERE campaign_name = campaign_name_input LIMIT 1)
      AND (platform = 'tiktok' OR platform IS NULL);
    
    IF result_category IS NOT NULL THEN
        RETURN result_category;
    END IF;
    
    -- Apply automatic rules by priority (reuse existing category_rules)
    FOR rule_record IN 
        SELECT category, pattern 
        FROM category_rules 
        WHERE is_active = true 
        ORDER BY priority DESC
    LOOP
        IF campaign_name_input ILIKE rule_record.pattern THEN
            RETURN rule_record.category;
        END IF;
    END LOOP;
    
    -- Default category if no rules match
    RETURN 'Uncategorized';
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-categorize TikTok campaigns on insert/update
CREATE OR REPLACE FUNCTION trigger_auto_categorize_tiktok()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.category IS NULL OR NEW.category = '' THEN
        NEW.category := auto_categorize_tiktok_campaign(NEW.campaign_name);
    END IF;
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auto_categorize_tiktok_trigger
    BEFORE INSERT OR UPDATE ON tiktok_campaign_data
    FOR EACH ROW
    EXECUTE FUNCTION trigger_auto_categorize_tiktok();

-- Update category_overrides table to support platform distinction
-- This allows platform-specific category overrides
DO $$ 
BEGIN
    -- Add platform column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'category_overrides' AND column_name = 'platform') THEN
        ALTER TABLE category_overrides ADD COLUMN platform VARCHAR(20) DEFAULT 'meta';
    END IF;
END $$;

-- Update unique constraint to include platform
DO $$
BEGIN
    -- Drop old constraint if it exists
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints 
               WHERE constraint_name = 'category_overrides_campaign_id_key' 
               AND table_name = 'category_overrides') THEN
        ALTER TABLE category_overrides DROP CONSTRAINT category_overrides_campaign_id_key;
    END IF;
    
    -- Add new constraint with platform
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE constraint_name = 'category_overrides_campaign_platform_key' 
                   AND table_name = 'category_overrides') THEN
        ALTER TABLE category_overrides ADD CONSTRAINT category_overrides_campaign_platform_key 
        UNIQUE(campaign_id, platform);
    END IF;
END $$;

-- Create index for platform-specific lookups
CREATE INDEX IF NOT EXISTS idx_category_overrides_platform_campaign 
ON category_overrides(platform, campaign_id);

-- Comments for documentation
COMMENT ON TABLE tiktok_campaign_data IS 'TikTok Ads campaign performance data with same structure as Meta/Google Ads';
COMMENT ON TABLE tiktok_monthly_reports IS 'Monthly TikTok Ads performance snapshots';
COMMENT ON COLUMN category_overrides.platform IS 'Platform identifier: meta, google, or tiktok';

-- Add example category rules specific to TikTok if needed
-- (These would be the same as existing rules since we use unified categorization)
INSERT INTO category_rules (rule_name, pattern, category, priority) VALUES
    ('TikTok Play Mats Pattern', '%Play%Mat%', 'Play Mats', 2),
    ('TikTok Standing Mats Pattern', '%Standing%', 'Standing Mats', 1),
    ('TikTok Bath Mats Pattern', '%Bath%', 'Bath Mats', 1),
    ('TikTok Tumbling Pattern', '%Tumbling%', 'Tumbling Mats', 1),
    ('TikTok High Chair Pattern', '%High Chair%', 'High Chair Mats', 1),
    ('TikTok Multi Category Pattern', '%Creative Testing%', 'Multi Category', 1)
ON CONFLICT (rule_name) DO NOTHING;

-- Create view for unified campaign data across all platforms (optional)
CREATE OR REPLACE VIEW unified_campaign_data AS
SELECT 
    'meta' as platform,
    campaign_id,
    campaign_name,
    category,
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
    created_at,
    updated_at
FROM campaign_data

UNION ALL

SELECT 
    'google' as platform,
    campaign_id,
    campaign_name,
    category,
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
    created_at,
    updated_at
FROM google_campaign_data

UNION ALL

SELECT 
    'tiktok' as platform,
    campaign_id,
    campaign_name,
    category,
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
    created_at,
    updated_at
FROM tiktok_campaign_data;

COMMENT ON VIEW unified_campaign_data IS 'Unified view of campaign data across Meta, Google, and TikTok platforms';