-- TikTok Ad-Level Data Table Migration
-- This creates ad-level data collection for TikTok to enable proper categorization
-- Unlike campaign-level data, this uses ad names for product categorization

-- TikTok Ad-Level data table (similar to meta_ad_data structure)
CREATE TABLE IF NOT EXISTS tiktok_ad_data (
    id BIGSERIAL PRIMARY KEY,
    ad_id VARCHAR(50) NOT NULL,
    ad_name VARCHAR(500) NOT NULL,
    campaign_id VARCHAR(50) NOT NULL,
    campaign_name VARCHAR(255) NOT NULL,
    category VARCHAR(100), -- Auto-categorized from ad_name, not campaign_name
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
    cpm DECIMAL(10, 2) DEFAULT 0,
    thumbnail_url VARCHAR(500), -- Ad creative thumbnail
    status VARCHAR(50), -- Ad status (active, paused, etc.)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure unique records per ad per date range
    UNIQUE(ad_id, reporting_starts, reporting_ends)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_tiktok_ad_data_date_range ON tiktok_ad_data(reporting_starts, reporting_ends);
CREATE INDEX IF NOT EXISTS idx_tiktok_ad_data_category ON tiktok_ad_data(category);
CREATE INDEX IF NOT EXISTS idx_tiktok_ad_data_ad_id ON tiktok_ad_data(ad_id);
CREATE INDEX IF NOT EXISTS idx_tiktok_ad_data_campaign_id ON tiktok_ad_data(campaign_id);
CREATE INDEX IF NOT EXISTS idx_tiktok_ad_data_ad_name ON tiktok_ad_data(ad_name);

-- Function to auto-categorize TikTok ads based on ad name (not campaign name)
CREATE OR REPLACE FUNCTION auto_categorize_tiktok_ad(ad_name_input VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    result_category VARCHAR(100);
    rule_record RECORD;
    ad_name_lower VARCHAR(500);
BEGIN
    ad_name_lower := LOWER(ad_name_input);
    
    -- Check for manual override first (by ad_id if implemented later)
    -- For now, skip manual overrides and use automatic categorization
    
    -- Apply automatic rules by priority for TikTok ads
    -- TikTok ad names contain product information that campaign names don't
    
    -- Play Mats - look for "play" AND "mat" but not "tumbling"
    IF ad_name_lower LIKE '%play%' AND ad_name_lower LIKE '%mat%' AND ad_name_lower NOT LIKE '%tumbling%' THEN
        RETURN 'Play Mats';
    END IF;
    
    -- Tumbling Mats - specific keyword
    IF ad_name_lower LIKE '%tumbling%' THEN
        RETURN 'Tumbling Mats';
    END IF;
    
    -- Standing Mats - standing desk mats
    IF ad_name_lower LIKE '%standing%' OR ad_name_lower LIKE '%desk%' THEN
        RETURN 'Standing Mats';
    END IF;
    
    -- Bath Mats
    IF ad_name_lower LIKE '%bath%' THEN
        RETURN 'Bath Mats';
    END IF;
    
    -- Play Furniture
    IF ad_name_lower LIKE '%play%' AND ad_name_lower LIKE '%furniture%' THEN
        RETURN 'Play Furniture';
    END IF;
    
    -- Multi Category
    IF ad_name_lower LIKE '%multi%' THEN
        RETURN 'Multi Category';
    END IF;
    
    -- Default category if no rules match
    RETURN 'Uncategorized';
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-categorize TikTok ads on insert/update
CREATE OR REPLACE FUNCTION trigger_auto_categorize_tiktok_ad()
RETURNS TRIGGER AS $$
BEGIN
    -- Always auto-categorize based on ad name (not campaign name)
    NEW.category := auto_categorize_tiktok_ad(NEW.ad_name);
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auto_categorize_tiktok_ad_trigger
    BEFORE INSERT OR UPDATE ON tiktok_ad_data
    FOR EACH ROW
    EXECUTE FUNCTION trigger_auto_categorize_tiktok_ad();

-- Comments for documentation
COMMENT ON TABLE tiktok_ad_data IS 'TikTok ad-level performance data with categorization based on ad names instead of campaign names';
COMMENT ON COLUMN tiktok_ad_data.ad_name IS 'Ad name contains product information for categorization (unlike campaign names)';
COMMENT ON COLUMN tiktok_ad_data.category IS 'Auto-categorized from ad_name using TikTok-specific rules';
COMMENT ON FUNCTION auto_categorize_tiktok_ad(VARCHAR) IS 'Categorizes TikTok ads based on ad name patterns for product identification';

-- Final success message
SELECT 'TikTok ad-level data table migration completed successfully!' as result;