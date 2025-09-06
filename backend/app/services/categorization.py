from typing import List, Optional
from supabase import create_client, Client
import os
from loguru import logger
from ..models.campaign_data import CategoryRule, CategoryOverride

class CategorizationService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase: Client = create_client(url, key)
    
    def categorize_campaign(self, campaign_name: str, campaign_id: str) -> str:
        """
        Categorize a campaign based on rules and overrides
        """
        try:
            # Check for manual override first
            override_result = self.supabase.table("category_overrides").select("category").eq("campaign_id", campaign_id).execute()
            
            if override_result.data:
                return override_result.data[0]['category']
            
            # Apply automatic rules
            rules_result = self.supabase.table("category_rules").select("*").eq("is_active", True).order("priority", desc=True).execute()
            
            for rule in rules_result.data:
                pattern = rule['pattern'].replace('%', '')  # Convert SQL LIKE pattern to Python
                if pattern.lower() in campaign_name.lower():
                    logger.info(f"Campaign '{campaign_name}' matched rule '{rule['rule_name']}' -> '{rule['category']}'")
                    return rule['category']
            
            # Default category
            logger.info(f"Campaign '{campaign_name}' -> 'Uncategorized' (no rules matched)")
            return 'Uncategorized'
            
        except Exception as e:
            logger.error(f"Error categorizing campaign {campaign_name}: {e}")
            return 'Uncategorized'
    
    def categorize_ad(self, ad_name: str, ad_id: str, platform: str = "tiktok", campaign_name: str = "") -> str:
        """
        Categorize an ad based on ad name and campaign name (TikTok uses structured format)
        """
        try:
            logger.debug(f"Categorizing {platform} ad '{ad_name}' with campaign '{campaign_name}'")
            
            # For TikTok ads with structured format: "Date - Category - Product - Color - etc."
            # STRUCTURED FORMAT TAKES ABSOLUTE PRECEDENCE - NO FALLBACK OVERRIDES
            if platform == "tiktok" and " - " in ad_name:
                parts = ad_name.split(" - ")
                if len(parts) >= 2:
                    # The SECOND part is the category indicator
                    category_part = parts[1].strip().lower()
                    
                    # Direct mapping based on structured format - FINAL DECISION
                    if category_part == "standing mat":
                        category = 'Standing Mats'
                        logger.info(f"Ad '{ad_name}' -> '{category}' (STRUCTURED FORMAT MATCH: standing mat)")
                        return category
                    elif category_part == "playmat":
                        category = 'Play Mats'
                        logger.info(f"Ad '{ad_name}' -> '{category}' (STRUCTURED FORMAT MATCH: playmat)")
                        return category
                    elif category_part == "bath":
                        category = 'Bath Mats'
                        logger.info(f"Ad '{ad_name}' -> '{category}' (STRUCTURED FORMAT MATCH: bath)")
                        return category
                    elif category_part == "tumbling mat":
                        category = 'Tumbling Mats'
                        logger.info(f"Ad '{ad_name}' -> '{category}' (STRUCTURED FORMAT MATCH: tumbling mat)")
                        return category
                    elif category_part == "play furniture":
                        category = 'Play Furniture'
                        logger.info(f"Ad '{ad_name}' -> '{category}' (STRUCTURED FORMAT MATCH: play furniture)")
                        return category
                    elif category_part == "multi":
                        category = 'Multi Category'
                        logger.info(f"Ad '{ad_name}' -> '{category}' (STRUCTURED FORMAT MATCH: multi)")
                        return category
                    else:
                        logger.info(f"Ad '{ad_name}' -> structured format found but no category match for '{category_part}', continuing to fallback")
            
            # Fallback to keyword-based categorization ONLY if structured format didn't match
            ad_name_lower = ad_name.lower()
            campaign_name_lower = campaign_name.lower() if campaign_name else ""
            
            # For campaigns with multiple categories, use the FIRST one mentioned
            if campaign_name_lower:
                if "play and tumbling" in campaign_name_lower:
                    category = 'Play Mats'  # Play is mentioned first
                    logger.info(f"Ad '{ad_name}' -> '{category}' (campaign: play and tumbling)")
                    return category
                elif "standing and bath" in campaign_name_lower:
                    category = 'Standing Mats'  # Standing is mentioned first
                    logger.info(f"Ad '{ad_name}' -> '{category}' (campaign: standing and bath)")
                    return category
            
            # Simple keyword matching as last resort
            if 'tumbling' in ad_name_lower or 'tumbling' in campaign_name_lower:
                category = 'Tumbling Mats'
                source = "ad_name" if 'tumbling' in ad_name_lower else "campaign_name"
                logger.info(f"Ad '{ad_name}' -> '{category}' (tumbling keyword in {source})")
                return category
            
            if 'standing' in ad_name_lower or 'standing' in campaign_name_lower:
                category = 'Standing Mats'
                source = "ad_name" if 'standing' in ad_name_lower else "campaign_name"
                logger.info(f"Ad '{ad_name}' -> '{category}' (standing keyword in {source})")
                return category
            
            if 'bath' in ad_name_lower or 'bath' in campaign_name_lower:
                category = 'Bath Mats'
                source = "ad_name" if 'bath' in ad_name_lower else "campaign_name"
                logger.info(f"Ad '{ad_name}' -> '{category}' (bath keyword in {source})")
                return category
            
            if (('play' in ad_name_lower and 'mat' in ad_name_lower) or 
                ('play' in campaign_name_lower)):
                category = 'Play Mats'
                source = "ad_name" if ('play' in ad_name_lower and 'mat' in ad_name_lower) else "campaign_name"
                logger.info(f"Ad '{ad_name}' -> '{category}' (play+mat pattern in {source})")
                return category
            
            
            # Play Furniture
            if 'play' in ad_name_lower and 'furniture' in ad_name_lower:
                category = 'Play Furniture'
                logger.info(f"Ad '{ad_name}' -> '{category}' (play+furniture pattern)")
                return category
            
            # Multi Category
            if 'multi' in ad_name_lower:
                category = 'Multi Category'
                logger.info(f"Ad '{ad_name}' -> '{category}' (multi pattern)")
                return category
            
            # Default category
            logger.info(f"Ad '{ad_name}' -> 'Uncategorized' (no patterns matched)")
            return 'Uncategorized'
            
        except Exception as e:
            logger.error(f"Error categorizing ad {ad_name}: {e}")
            return 'Uncategorized'
    
    def get_all_categories(self) -> List[str]:
        """
        Get all unique categories from the database
        """
        try:
            # Get categories from rules
            rules_result = self.supabase.table("category_rules").select("category").eq("is_active", True).execute()
            rules_categories = [rule['category'] for rule in rules_result.data]
            
            # Get categories from overrides
            overrides_result = self.supabase.table("category_overrides").select("category").execute()
            override_categories = [override['category'] for override in overrides_result.data]
            
            # Get categories from actual campaign data
            campaigns_result = self.supabase.table("campaign_data").select("category").execute()
            campaign_categories = [campaign['category'] for campaign in campaigns_result.data if campaign['category']]
            
            # Combine and deduplicate
            all_categories = list(set(rules_categories + override_categories + campaign_categories))
            all_categories.sort()
            
            return all_categories
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    def add_category_rule(self, rule: CategoryRule) -> bool:
        """
        Add a new categorization rule
        """
        try:
            result = self.supabase.table("category_rules").insert({
                "rule_name": rule.rule_name,
                "pattern": f"%{rule.pattern}%",  # Convert to SQL LIKE pattern
                "category": rule.category,
                "priority": rule.priority,
                "is_active": rule.is_active
            }).execute()
            
            logger.info(f"Added category rule: {rule.rule_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding category rule: {e}")
            return False
    
    def add_category_override(self, override: CategoryOverride) -> bool:
        """
        Add a manual category override for a specific campaign
        """
        try:
            result = self.supabase.table("category_overrides").upsert({
                "campaign_id": override.campaign_id,
                "category": override.category,
                "created_by": override.created_by
            }).execute()
            
            logger.info(f"Added category override for campaign {override.campaign_id}: {override.category}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding category override: {e}")
            return False
    
    def get_category_rules(self) -> List[dict]:
        """
        Get all active category rules
        """
        try:
            result = self.supabase.table("category_rules").select("*").eq("is_active", True).order("priority", desc=True).execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Error getting category rules: {e}")
            return []
    
    def delete_category_rule(self, rule_id: int) -> bool:
        """
        Delete a category rule
        """
        try:
            result = self.supabase.table("category_rules").delete().eq("id", rule_id).execute()
            logger.info(f"Deleted category rule with id: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting category rule: {e}")
            return False
    
    def update_category_rule(self, rule_id: int, updates: dict) -> bool:
        """
        Update a category rule
        """
        try:
            result = self.supabase.table("category_rules").update(updates).eq("id", rule_id).execute()
            logger.info(f"Updated category rule with id: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating category rule: {e}")
            return False