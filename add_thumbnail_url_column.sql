-- Add thumbnail_url column to meta_ad_data table for ad creative thumbnails
-- This enables displaying visual thumbnails in the ad-level dashboard

ALTER TABLE meta_ad_data 
ADD COLUMN IF NOT EXISTS thumbnail_url TEXT;