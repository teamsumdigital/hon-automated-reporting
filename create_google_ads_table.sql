-- Create Google Ads campaign data table
-- This mirrors the structure of the existing Meta Ads table but for Google Ads data

CREATE TABLE IF NOT EXISTS google_campaign_data (
    id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(255) NOT NULL,
    campaign_name VARCHAR(500) NOT NULL,
    category VARCHAR(255),
    reporting_starts DATE NOT NULL,
    reporting_ends DATE NOT NULL,
    amount_spent_usd DECIMAL(15, 2) DEFAULT 0.00,
    website_purchases INTEGER DEFAULT 0,
    purchases_conversion_value DECIMAL(15, 2) DEFAULT 0.00,
    impressions INTEGER DEFAULT 0,
    link_clicks INTEGER DEFAULT 0,
    cpa DECIMAL(15, 2) DEFAULT 0.00,
    roas DECIMAL(15, 4) DEFAULT 0.0000,
    cpc DECIMAL(15, 4) DEFAULT 0.0000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_google_campaign_period UNIQUE(campaign_id, reporting_starts, reporting_ends)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_google_campaign_data_campaign_id ON google_campaign_data(campaign_id);
CREATE INDEX IF NOT EXISTS idx_google_campaign_data_reporting_dates ON google_campaign_data(reporting_starts, reporting_ends);
CREATE INDEX IF NOT EXISTS idx_google_campaign_data_category ON google_campaign_data(category);
CREATE INDEX IF NOT EXISTS idx_google_campaign_data_created_at ON google_campaign_data(created_at);

-- Add updated_at trigger (if using PostgreSQL)
CREATE OR REPLACE FUNCTION update_google_campaign_data_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_google_campaign_data_updated_at
    BEFORE UPDATE ON google_campaign_data
    FOR EACH ROW
    EXECUTE FUNCTION update_google_campaign_data_updated_at();

-- Add a comment to the table
COMMENT ON TABLE google_campaign_data IS 'Google Ads campaign performance data by date range';
COMMENT ON COLUMN google_campaign_data.campaign_id IS 'Google Ads campaign identifier';
COMMENT ON COLUMN google_campaign_data.amount_spent_usd IS 'Total spend in USD for the reporting period';
COMMENT ON COLUMN google_campaign_data.website_purchases IS 'Number of conversions (purchases)';
COMMENT ON COLUMN google_campaign_data.purchases_conversion_value IS 'Total conversion value in USD';
COMMENT ON COLUMN google_campaign_data.link_clicks IS 'Number of link clicks';
COMMENT ON COLUMN google_campaign_data.cpa IS 'Cost per acquisition (spend / purchases)';
COMMENT ON COLUMN google_campaign_data.roas IS 'Return on ad spend (revenue / spend)';
COMMENT ON COLUMN google_campaign_data.cpc IS 'Cost per click (spend / clicks)';