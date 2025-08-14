-- Google Ads Campaign Data Table Migration
-- Adds Google Ads support alongside existing Meta Ads data

-- Google Campaign data table to store Google Ads metrics
CREATE TABLE IF NOT EXISTS google_campaign_data (
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
    
    -- Ensure unique records per campaign per daily date
    UNIQUE(campaign_id, reporting_starts)
);

-- Google Ads monthly reporting snapshots
CREATE TABLE IF NOT EXISTS google_monthly_reports (
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

-- Indexes for performance (same as Meta ads structure)
CREATE INDEX IF NOT EXISTS idx_google_campaign_data_date_range ON google_campaign_data(reporting_starts, reporting_ends);
CREATE INDEX IF NOT EXISTS idx_google_campaign_data_category ON google_campaign_data(category);
CREATE INDEX IF NOT EXISTS idx_google_campaign_data_campaign_id ON google_campaign_data(campaign_id);

-- Function to auto-categorize Google campaigns (reuse existing logic)
CREATE OR REPLACE FUNCTION auto_categorize_google_campaign(campaign_name_input VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    result_category VARCHAR(100);
    rule_record RECORD;
BEGIN
    -- Check for manual override first
    SELECT category INTO result_category 
    FROM category_overrides 
    WHERE campaign_id = (SELECT campaign_id FROM google_campaign_data WHERE campaign_name = campaign_name_input LIMIT 1);
    
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

-- Trigger to auto-categorize Google campaigns on insert/update
CREATE OR REPLACE FUNCTION trigger_auto_categorize_google()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.category IS NULL OR NEW.category = '' THEN
        NEW.category := auto_categorize_google_campaign(NEW.campaign_name);
    END IF;
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auto_categorize_google_trigger
    BEFORE INSERT OR UPDATE ON google_campaign_data
    FOR EACH ROW
    EXECUTE FUNCTION trigger_auto_categorize_google();

-- Add platform field to distinguish data sources in reports if needed
ALTER TABLE category_overrides ADD COLUMN IF NOT EXISTS platform VARCHAR(20) DEFAULT 'meta';
CREATE INDEX IF NOT EXISTS idx_category_overrides_platform ON category_overrides(platform);

-- Comments for documentation
COMMENT ON TABLE google_campaign_data IS 'Google Ads campaign performance data with same structure as Meta Ads';
COMMENT ON TABLE google_monthly_reports IS 'Monthly Google Ads performance snapshots';
COMMENT ON COLUMN category_overrides.platform IS 'Platform identifier: meta or google';