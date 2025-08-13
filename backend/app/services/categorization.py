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