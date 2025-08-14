from typing import List, Optional
from supabase import create_client, Client
import os
from loguru import logger

class CampaignTypeService:
    """Service for managing campaign type classification rules and logic"""
    
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase: Client = create_client(url, key)
    
    def classify_campaign_type(self, campaign_name: str) -> str:
        """
        Classify a campaign type based on naming patterns
        Returns: Brand, Non-Brand, YouTube, or Unclassified
        """
        try:
            # Apply automatic rules by priority (highest priority first)
            rules_result = self.supabase.table("campaign_type_rules").select("*").eq("is_active", True).order("priority", desc=True).execute()
            
            for rule in rules_result.data:
                pattern = rule['pattern'].replace('%', '').lower()  # Convert SQL LIKE pattern to Python
                campaign_lower = campaign_name.lower()
                
                # Use more precise matching for patterns with dashes
                if ' - ' in pattern:
                    # For dash patterns, check exact phrase match
                    if pattern in campaign_lower:
                        logger.info(f"Campaign '{campaign_name}' matched type rule '{rule['rule_name']}' -> '{rule['campaign_type']}'")
                        return rule['campaign_type']
                else:
                    # For simple patterns, use word boundary matching to avoid substring issues
                    import re
                    # Create word boundary pattern to avoid "Brand" matching "Non-Brand"
                    word_pattern = r'\b' + re.escape(pattern) + r'\b'
                    if re.search(word_pattern, campaign_lower):
                        logger.info(f"Campaign '{campaign_name}' matched type rule '{rule['rule_name']}' -> '{rule['campaign_type']}'")
                        return rule['campaign_type']
            
            # Default type if no rules match
            logger.info(f"Campaign '{campaign_name}' -> 'Unclassified' (no type rules matched)")
            return 'Unclassified'
            
        except Exception as e:
            logger.error(f"Error classifying campaign type for {campaign_name}: {e}")
            return 'Unclassified'
    
    def get_all_campaign_types(self) -> List[str]:
        """
        Get all unique campaign types from the database
        """
        try:
            # Get types from rules
            rules_result = self.supabase.table("campaign_type_rules").select("campaign_type").eq("is_active", True).execute()
            rules_types = [rule['campaign_type'] for rule in rules_result.data]
            
            # Get types from actual campaign data
            campaigns_result = self.supabase.table("google_campaign_data").select("campaign_type").execute()
            campaign_types = [campaign['campaign_type'] for campaign in campaigns_result.data if campaign['campaign_type']]
            
            # Combine and deduplicate
            all_types = list(set(rules_types + campaign_types))
            all_types.sort()
            
            return all_types
            
        except Exception as e:
            logger.error(f"Error getting campaign types: {e}")
            return []
    
    def add_campaign_type_rule(self, rule_name: str, pattern: str, campaign_type: str, priority: int = 0) -> bool:
        """
        Add a new campaign type classification rule
        """
        try:
            result = self.supabase.table("campaign_type_rules").insert({
                "rule_name": rule_name,
                "pattern": f"%{pattern}%",  # Convert to SQL LIKE pattern
                "campaign_type": campaign_type,
                "priority": priority,
                "is_active": True
            }).execute()
            
            logger.info(f"Added campaign type rule: {rule_name} -> {campaign_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding campaign type rule: {e}")
            return False
    
    def get_campaign_type_rules(self) -> List[dict]:
        """
        Get all active campaign type rules
        """
        try:
            result = self.supabase.table("campaign_type_rules").select("*").eq("is_active", True).order("priority", desc=True).execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Error getting campaign type rules: {e}")
            return []
    
    def delete_campaign_type_rule(self, rule_id: int) -> bool:
        """
        Delete a campaign type rule
        """
        try:
            result = self.supabase.table("campaign_type_rules").delete().eq("id", rule_id).execute()
            logger.info(f"Deleted campaign type rule with id: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting campaign type rule: {e}")
            return False
    
    def update_campaign_type_rule(self, rule_id: int, updates: dict) -> bool:
        """
        Update a campaign type rule
        """
        try:
            result = self.supabase.table("campaign_type_rules").update(updates).eq("id", rule_id).execute()
            logger.info(f"Updated campaign type rule with id: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating campaign type rule: {e}")
            return False
    
    def classify_existing_campaigns(self) -> int:
        """
        Classify all existing campaigns that don't have a campaign_type set
        Returns number of campaigns updated
        """
        try:
            # Get campaigns without campaign_type
            result = self.supabase.table("google_campaign_data").select("id, campaign_name").is_("campaign_type", "null").execute()
            unclassified_campaigns = result.data
            
            if not unclassified_campaigns:
                # Also check for empty strings
                result = self.supabase.table("google_campaign_data").select("id, campaign_name").eq("campaign_type", "").execute()
                unclassified_campaigns = result.data
            
            updated_count = 0
            for campaign in unclassified_campaigns:
                campaign_type = self.classify_campaign_type(campaign['campaign_name'])
                
                # Update the campaign with the classified type
                update_result = self.supabase.table("google_campaign_data").update({
                    "campaign_type": campaign_type
                }).eq("id", campaign['id']).execute()
                
                if update_result.data:
                    updated_count += 1
            
            logger.info(f"Classified {updated_count} campaigns")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error classifying existing campaigns: {e}")
            return 0