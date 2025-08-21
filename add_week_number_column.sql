-- Add missing week_number column to meta_ad_data table
ALTER TABLE meta_ad_data ADD COLUMN IF NOT EXISTS week_number VARCHAR(50);

-- Add index for the new column
CREATE INDEX IF NOT EXISTS idx_meta_ad_data_week_number ON meta_ad_data(week_number);

-- Add comment for the new column
COMMENT ON COLUMN meta_ad_data.week_number IS 'Week identifier for segmentation (e.g., Week 08/05-08/11)';