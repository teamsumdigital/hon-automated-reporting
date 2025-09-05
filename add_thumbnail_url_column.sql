-- Add thumbnail_url columns to meta_ad_data table for ad creative thumbnails
-- thumbnail_url stores a lightweight version for table cells
-- thumbnail_url_high_res stores the original upload for hover previews

ALTER TABLE meta_ad_data
ADD COLUMN IF NOT EXISTS thumbnail_url TEXT,
ADD COLUMN IF NOT EXISTS thumbnail_url_high_res TEXT;