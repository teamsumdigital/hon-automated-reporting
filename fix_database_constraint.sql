-- Fix Google Ads database constraint issue
-- This script needs to be run in Supabase SQL Editor

-- Drop the problematic constraint that causes data overwrites
ALTER TABLE google_campaign_data 
DROP CONSTRAINT IF EXISTS google_campaign_data_campaign_id_reporting_starts_reporting_ends_key;

-- Add the correct constraint for daily data uniqueness
ALTER TABLE google_campaign_data 
ADD CONSTRAINT google_campaign_data_daily_unique 
UNIQUE(campaign_id, reporting_starts);

-- Verify the constraint was created
SELECT constraint_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_name = 'google_campaign_data' 
AND constraint_type = 'UNIQUE';