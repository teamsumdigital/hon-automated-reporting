-- Add Campaign Type Support to Google Campaign Data
-- Adds campaign type classification (Brand, Non-Brand, YouTube) to existing google_campaign_data table

-- Add campaign_type column to existing google_campaign_data table
ALTER TABLE google_campaign_data ADD COLUMN IF NOT EXISTS campaign_type VARCHAR(50);

-- Create campaign type rules table for pattern-based classification
CREATE TABLE IF NOT EXISTS campaign_type_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    pattern VARCHAR(255) NOT NULL,
    campaign_type VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default campaign type rules based on naming patterns
INSERT INTO campaign_type_rules (rule_name, pattern, campaign_type, priority) VALUES
    ('Brand Campaign Pattern', '%Brand%', 'Brand', 1),
    ('Non-Brand Campaign Pattern', '%Non-Brand%', 'Non-Brand', 1),
    ('YouTube Campaign Pattern', '%YouTube%', 'YouTube', 1),
    ('Brand Dash Pattern', '% - Brand - %', 'Brand', 2),
    ('Non-Brand Dash Pattern', '% - Non-Brand - %', 'Non-Brand', 2),
    ('YouTube Dash Pattern', '% - YouTube - %', 'YouTube', 2)
ON CONFLICT DO NOTHING;

-- Function to auto-classify campaign type based on campaign name
CREATE OR REPLACE FUNCTION auto_classify_campaign_type(campaign_name_input VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    result_type VARCHAR(50);
    rule_record RECORD;
BEGIN
    -- Apply automatic rules by priority (highest priority first)
    FOR rule_record IN 
        SELECT campaign_type, pattern 
        FROM campaign_type_rules 
        WHERE is_active = true 
        ORDER BY priority DESC, id ASC
    LOOP
        IF campaign_name_input ILIKE rule_record.pattern THEN
            RETURN rule_record.campaign_type;
        END IF;
    END LOOP;
    
    -- Default type if no rules match
    RETURN 'Unclassified';
END;
$$ LANGUAGE plpgsql;

-- Update existing trigger to also classify campaign type
CREATE OR REPLACE FUNCTION trigger_auto_categorize_google()
RETURNS TRIGGER AS $$
BEGIN
    -- Auto-categorize if category is null or empty
    IF NEW.category IS NULL OR NEW.category = '' THEN
        NEW.category := auto_categorize_google_campaign(NEW.campaign_name);
    END IF;
    
    -- Auto-classify campaign type if type is null or empty
    IF NEW.campaign_type IS NULL OR NEW.campaign_type = '' THEN
        NEW.campaign_type := auto_classify_campaign_type(NEW.campaign_name);
    END IF;
    
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_google_campaign_data_campaign_type ON google_campaign_data(campaign_type);
CREATE INDEX IF NOT EXISTS idx_campaign_type_rules_pattern ON campaign_type_rules(pattern) WHERE is_active = true;

-- Update existing records to classify campaign types
UPDATE google_campaign_data 
SET campaign_type = auto_classify_campaign_type(campaign_name) 
WHERE campaign_type IS NULL OR campaign_type = '';

-- Comments for documentation
COMMENT ON COLUMN google_campaign_data.campaign_type IS 'Campaign type classification: Brand, Non-Brand, YouTube, or Unclassified';
COMMENT ON TABLE campaign_type_rules IS 'Rules for automatically classifying campaign types based on naming patterns';