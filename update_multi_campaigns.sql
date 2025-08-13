-- Update campaign names to append " - Multi" for campaigns that don't already contain "multi"
-- This will help ensure proper categorization as "Multi Category"

UPDATE campaign_data 
SET campaign_name = campaign_name || ' - Multi',
    category = 'Multi Category'
WHERE campaign_name NOT ILIKE '%multi%' 
AND campaign_name IN (
    'High Chair Mats - Advantage+ - Prospecting Campaign',
    'Memorial Day Sale 2025',
    'TRAFFIC REDUX',
    '4th of July Sale',
    'BB - Adv+ - Evg - Standing & Bath Mats - Sales - Volume - 202406',
    'BB - RT - Evg - Standing & Bath Mats - Sales - Volume - 202406',
    'BB - RT - Evg - Play & Tumbling Mats - Sales - Volume - 202406',
    'BB - Adv+ - Evg - Play & Tumbling Mats - Sales - Volume - 202406',
    'BB - ACQ - Evg - Play & Tumbling Mats - Sales - Volume - Interest - 202406',
    'BB - ACQ - Evg - Standing & Bath Mats - Sales - Volume - LAL - 202406',
    'BB - ACQ - Evg - Play & Tumbling Mats - Sales - Volume - LAL - 202406',
    'BB - ACQ - Evg - Standing & Bath Mats - Sales - Volume - Interest - 202406',
    'BB - RT DPA - Evg - All Products - Sales - Volume - 202406',
    'BB - Adv+ - Creative Testing - Standing & Bath Mats - Sales - Volume - 202408',
    'BB - Adv+ - Creative Testing - Play & Tumbling Mats - Sales - Volume - 202408'
);

-- Check what will be updated (run this first to preview)
/*
SELECT campaign_name, category,
       campaign_name || ' - Multi' as new_name,
       'Multi Category' as new_category
FROM campaign_data 
WHERE campaign_name NOT ILIKE '%multi%' 
AND campaign_name IN (
    'High Chair Mats - Advantage+ - Prospecting Campaign',
    'Memorial Day Sale 2025',
    'TRAFFIC REDUX',
    '4th of July Sale',
    'BB - Adv+ - Evg - Standing & Bath Mats - Sales - Volume - 202406',
    'BB - RT - Evg - Standing & Bath Mats - Sales - Volume - 202406',
    'BB - RT - Evg - Play & Tumbling Mats - Sales - Volume - 202406',
    'BB - Adv+ - Evg - Play & Tumbling Mats - Sales - Volume - 202406',
    'BB - ACQ - Evg - Play & Tumbling Mats - Sales - Volume - Interest - 202406',
    'BB - ACQ - Evg - Standing & Bath Mats - Sales - Volume - LAL - 202406',
    'BB - ACQ - Evg - Play & Tumbling Mats - Sales - Volume - LAL - 202406',
    'BB - ACQ - Evg - Standing & Bath Mats - Sales - Volume - Interest - 202406',
    'BB - RT DPA - Evg - All Products - Sales - Volume - 202406',
    'BB - Adv+ - Creative Testing - Standing & Bath Mats - Sales - Volume - 202408',
    'BB - Adv+ - Creative Testing - Play & Tumbling Mats - Sales - Volume - 202408'
);
*/

-- Verify the updates after running
/*
SELECT campaign_name, category
FROM campaign_data 
WHERE campaign_name LIKE '% - Multi'
ORDER BY campaign_name;
*/