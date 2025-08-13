-- HON Automated Reporting Database Schema

-- Campaign data table to store Meta Ads metrics
CREATE TABLE IF NOT EXISTS campaign_data (
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

-- Category mapping table for auto-categorization rules
CREATE TABLE IF NOT EXISTS category_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    pattern VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Manual category overrides
CREATE TABLE IF NOT EXISTS category_overrides (
    id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL,
    created_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(campaign_id)
);

-- Monthly reporting snapshots
CREATE TABLE IF NOT EXISTS monthly_reports (
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

-- Insert default category rules based on the data shown
INSERT INTO category_rules (rule_name, pattern, category, priority) VALUES
    ('Bath Mats Pattern', '%Bath%', 'Bath Mats', 1),
    ('Play Furniture Pattern', '%Play Furniture%', 'Play Furniture', 1),
    ('Play Mats Pattern', '%Play%Mat%', 'Play Mats', 2),
    ('Standing Mats Pattern', '%Standing%', 'Standing Mats', 1),
    ('Tumbling Mats Pattern', '%Tumbling%', 'Tumbling Mats', 1),
    ('Multi Category Pattern', '%Creative Testing%', 'Multi Category', 1),
    ('High Chair Pattern', '%High Chair%', 'High Chair Mats', 1)
ON CONFLICT DO NOTHING;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_campaign_data_date_range ON campaign_data(reporting_starts, reporting_ends);
CREATE INDEX IF NOT EXISTS idx_campaign_data_category ON campaign_data(category);
CREATE INDEX IF NOT EXISTS idx_campaign_data_campaign_id ON campaign_data(campaign_id);
CREATE INDEX IF NOT EXISTS idx_category_rules_pattern ON category_rules(pattern) WHERE is_active = true;

-- Function to auto-categorize campaigns
CREATE OR REPLACE FUNCTION auto_categorize_campaign(campaign_name_input VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    result_category VARCHAR(100);
    rule_record RECORD;
BEGIN
    -- Check for manual override first
    SELECT category INTO result_category 
    FROM category_overrides 
    WHERE campaign_id = (SELECT campaign_id FROM campaign_data WHERE campaign_name = campaign_name_input LIMIT 1);
    
    IF result_category IS NOT NULL THEN
        RETURN result_category;
    END IF;
    
    -- Apply automatic rules by priority
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

-- Trigger to auto-categorize on insert/update
CREATE OR REPLACE FUNCTION trigger_auto_categorize()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.category IS NULL OR NEW.category = '' THEN
        NEW.category := auto_categorize_campaign(NEW.campaign_name);
    END IF;
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auto_categorize_trigger
    BEFORE INSERT OR UPDATE ON campaign_data
    FOR EACH ROW
    EXECUTE FUNCTION trigger_auto_categorize();