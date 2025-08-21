-- Add status field to meta_ad_data table for manual color state management
-- Status values: null (no color), 'winner' (green), 'considering' (yellow), 'paused' (red), 'paused_last_week' (grey)

ALTER TABLE meta_ad_data 
ADD COLUMN IF NOT EXISTS status TEXT 
CHECK (status IN ('winner', 'considering', 'paused', 'paused_last_week'));

-- Add index for efficient filtering by status
CREATE INDEX IF NOT EXISTS idx_meta_ad_data_status ON meta_ad_data(status);

-- Add comment for documentation
COMMENT ON COLUMN meta_ad_data.status IS 'Manual status classification: winner (green), considering (yellow), paused (red), paused_last_week (grey), null (no color)';