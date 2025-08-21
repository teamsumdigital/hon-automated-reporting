-- Create meta_ad_data table for ad-level Meta Ads data
-- This table stores detailed ad-level performance metrics from Meta Ads API

CREATE TABLE IF NOT EXISTS meta_ad_data (
    -- Primary key and unique identifier
    id BIGSERIAL PRIMARY KEY,
    
    -- Ad identification
    ad_id VARCHAR(50) NOT NULL,
    ad_name TEXT NOT NULL,
    campaign_name TEXT NOT NULL,
    
    -- Reporting period
    reporting_starts DATE NOT NULL,
    reporting_ends DATE NOT NULL,
    week_number VARCHAR(50),
    
    -- Ad lifecycle
    launch_date DATE,
    days_live INTEGER,
    
    -- Categorization and product info
    category VARCHAR(100),
    product VARCHAR(100),
    color VARCHAR(50),
    content_type VARCHAR(50),
    handle VARCHAR(100),
    format VARCHAR(50),
    
    -- Campaign settings
    campaign_optimization VARCHAR(100),
    
    -- Performance metrics
    amount_spent_usd DECIMAL(10,2) DEFAULT 0,
    purchases INTEGER DEFAULT 0,
    purchases_conversion_value DECIMAL(10,2) DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    link_clicks INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_ad_reporting_period UNIQUE (ad_id, reporting_starts, reporting_ends),
    CONSTRAINT valid_date_range CHECK (reporting_ends >= reporting_starts),
    CONSTRAINT positive_metrics CHECK (
        amount_spent_usd >= 0 AND 
        purchases >= 0 AND 
        purchases_conversion_value >= 0 AND 
        impressions >= 0 AND 
        link_clicks >= 0
    )
);

-- Create indexes for better query performance
CREATE INDEX idx_meta_ad_data_ad_id ON meta_ad_data(ad_id);
CREATE INDEX idx_meta_ad_data_reporting_period ON meta_ad_data(reporting_starts, reporting_ends);
CREATE INDEX idx_meta_ad_data_campaign_name ON meta_ad_data(campaign_name);
CREATE INDEX idx_meta_ad_data_category ON meta_ad_data(category);
CREATE INDEX idx_meta_ad_data_product ON meta_ad_data(product);
CREATE INDEX idx_meta_ad_data_launch_date ON meta_ad_data(launch_date);
CREATE INDEX idx_meta_ad_data_created_at ON meta_ad_data(created_at);
CREATE INDEX idx_meta_ad_data_week_number ON meta_ad_data(week_number);

-- Create trigger for automatically updating the updated_at timestamp
CREATE OR REPLACE FUNCTION update_meta_ad_data_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_meta_ad_data_updated_at
    BEFORE UPDATE ON meta_ad_data
    FOR EACH ROW
    EXECUTE FUNCTION update_meta_ad_data_updated_at();

-- Add comments for documentation
COMMENT ON TABLE meta_ad_data IS 'Ad-level performance data from Meta Ads platform';
COMMENT ON COLUMN meta_ad_data.ad_id IS 'Unique identifier for the Meta ad';
COMMENT ON COLUMN meta_ad_data.ad_name IS 'Display name of the ad';
COMMENT ON COLUMN meta_ad_data.campaign_name IS 'Name of the parent campaign';
COMMENT ON COLUMN meta_ad_data.reporting_starts IS 'Start date of the reporting period';
COMMENT ON COLUMN meta_ad_data.reporting_ends IS 'End date of the reporting period';
COMMENT ON COLUMN meta_ad_data.launch_date IS 'Date when the ad was first launched';
COMMENT ON COLUMN meta_ad_data.days_live IS 'Number of days the ad has been active';
COMMENT ON COLUMN meta_ad_data.category IS 'Product category (e.g., Play Mats, Standing Mats)';
COMMENT ON COLUMN meta_ad_data.product IS 'Specific product name';
COMMENT ON COLUMN meta_ad_data.color IS 'Product color variant';
COMMENT ON COLUMN meta_ad_data.content_type IS 'Type of ad content (e.g., Video, Image, Carousel)';
COMMENT ON COLUMN meta_ad_data.handle IS 'Product handle or SKU';
COMMENT ON COLUMN meta_ad_data.format IS 'Ad format specification';
COMMENT ON COLUMN meta_ad_data.campaign_optimization IS 'Campaign optimization objective';
COMMENT ON COLUMN meta_ad_data.amount_spent_usd IS 'Total amount spent in USD';
COMMENT ON COLUMN meta_ad_data.purchases IS 'Number of purchases attributed to this ad';
COMMENT ON COLUMN meta_ad_data.purchases_conversion_value IS 'Total value of purchases in USD';
COMMENT ON COLUMN meta_ad_data.impressions IS 'Number of times the ad was shown';
COMMENT ON COLUMN meta_ad_data.link_clicks IS 'Number of clicks on ad links';
COMMENT ON COLUMN meta_ad_data.week_number IS 'Week identifier for segmentation (e.g., Week 08/05-08/11)';