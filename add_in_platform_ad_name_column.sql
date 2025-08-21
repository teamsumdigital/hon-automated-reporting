-- Add in_platform_ad_name column to store the original ad name from Meta platform
-- This preserves the raw ad name as it appears in Meta Ads Manager
-- while keeping our cleaned/parsed version in the ad_name field

ALTER TABLE meta_ad_data 
ADD COLUMN in_platform_ad_name TEXT;

-- Add a comment to explain the field
COMMENT ON COLUMN meta_ad_data.in_platform_ad_name IS 'Original ad name as it appears in Meta Ads platform, before parsing/cleaning';

-- Update any existing records to populate the new field
-- (This will copy current ad_name to in_platform_ad_name for existing records)
UPDATE meta_ad_data 
SET in_platform_ad_name = ad_name 
WHERE in_platform_ad_name IS NULL;