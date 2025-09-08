"""
Ad Pause Automation Service
Automatically detects completely paused ads and applies dark red status
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from supabase import create_client, Client
import os

logger = logging.getLogger("ad-pause-automation")

class AdPauseAutomationService:
    """Service for automated ad pause status detection and coloring"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
    
    def analyze_ad_pause_status(self, ad_data_list: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze ads to determine complete pause status across all campaigns/adsets
        
        Args:
            ad_data_list: List of ad data from Meta API sync
            
        Returns:
            Dict mapping ad_name to pause analysis
        """
        try:
            # Group ads by ad_name to analyze across all placements
            ad_groups = {}
            
            for ad in ad_data_list:
                ad_name = ad.get('ad_name', '')
                ad_status = ad.get('effective_status', '').upper()  # Ad status
                # Handle nested campaign/adset status fields from Meta API
                campaign_status = ''
                adset_status = ''
                
                # Extract campaign status from nested structure
                if 'campaign' in ad and isinstance(ad['campaign'], dict):
                    campaign_status = ad['campaign'].get('effective_status', '').upper()
                
                # Extract adset status and details from nested structure  
                adset_name = ''
                adset_id = ''
                if 'adset' in ad and isinstance(ad['adset'], dict):
                    adset_status = ad['adset'].get('effective_status', '').upper()
                    adset_name = ad['adset'].get('name', '')
                    adset_id = ad['adset'].get('id', '')
                
                if ad_name not in ad_groups:
                    ad_groups[ad_name] = {
                        'placements': [],
                        'active_count': 0,
                        'paused_count': 0,
                        'total_count': 0,
                        'spend': 0
                    }
                
                # Determine if this specific placement is active
                is_active = all([
                    ad_status == 'ACTIVE',
                    campaign_status == 'ACTIVE', 
                    adset_status == 'ACTIVE'
                ])
                
                ad_groups[ad_name]['placements'].append({
                    'ad_id': ad.get('ad_id'),
                    'campaign_name': ad.get('campaign_name', ''),
                    'adset_name': adset_name,
                    'adset_id': adset_id,
                    'ad_status': ad_status,
                    'campaign_status': campaign_status,
                    'adset_status': adset_status,
                    'is_active': is_active
                })
                
                if is_active:
                    ad_groups[ad_name]['active_count'] += 1
                else:
                    ad_groups[ad_name]['paused_count'] += 1
                    
                ad_groups[ad_name]['total_count'] += 1
                ad_groups[ad_name]['spend'] += float(ad.get('spend', 0))
            
            # Analyze pause status for each ad
            pause_analysis = {}
            for ad_name, data in ad_groups.items():
                pause_analysis[ad_name] = self._determine_pause_status(ad_name, data)
            
            return pause_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing ad pause status: {e}")
            return {}
    
    def _determine_pause_status(self, ad_name: str, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the appropriate pause status for an ad"""
        
        active_count = ad_data['active_count']
        paused_count = ad_data['paused_count']
        total_count = ad_data['total_count']
        
        # Determine automation status
        if total_count == 0:
            status = 'unknown'
            action = 'none'
        elif active_count == 0:
            # Completely paused in ALL locations - apply dark red
            status = 'paused_automated'
            action = 'apply_dark_red'
        elif paused_count == 0:
            # Completely active in ALL locations
            status = 'active'
            action = 'clear_automated_status'
        else:
            # Mixed status - paused in some locations, active in others
            status = 'mixed'
            action = 'preserve_manual_status'
        
        return {
            'ad_name': ad_name,
            'status': status,
            'action': action,
            'active_placements': active_count,
            'paused_placements': paused_count,
            'total_placements': total_count,
            'placement_details': ad_data['placements'],
            'total_spend': ad_data['spend']
        }
    
    async def apply_automated_status_updates(self, pause_analysis: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Apply automated status updates to database"""
        try:
            updates_applied = 0
            updates_cleared = 0
            preserved_manual = 0
            errors = []
            
            for ad_name, analysis in pause_analysis.items():
                action = analysis['action']
                
                try:
                    if action == 'apply_dark_red':
                        # Apply automated pause status (dark red)
                        await self._update_ad_status(ad_name, 'paused_automated', analysis)
                        updates_applied += 1
                        logger.info(f"Applied automated pause status to: {ad_name}")
                        
                    elif action == 'clear_automated_status':
                        # Clear automated status if ad is now active
                        await self._clear_automated_status_if_set(ad_name)
                        updates_cleared += 1
                        
                    elif action == 'preserve_manual_status':
                        # Don't change anything for mixed status ads
                        preserved_manual += 1
                        
                except Exception as e:
                    error_msg = f"Failed to update {ad_name}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            return {
                'updates_applied': updates_applied,
                'updates_cleared': updates_cleared,
                'preserved_manual': preserved_manual,
                'errors': errors,
                'total_analyzed': len(pause_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error applying automated status updates: {e}")
            return {'error': str(e)}
    
    async def _update_ad_status(self, ad_name: str, new_status: str, analysis: Dict[str, Any]):
        """Update ad status in database only if not manually set"""
        try:
            # First check current status - don't override manual settings
            current_response = self.supabase.table("meta_ad_data").select("status").eq("ad_name", ad_name).limit(1).execute()
            
            current_status = None
            if current_response.data:
                current_status = current_response.data[0].get('status')
            
            # Only apply automated status if:
            # 1. Current status is null (no manual setting)
            # 2. Current status is already 'paused_automated' (updating existing automation)
            if current_status is None or current_status == 'paused_automated':
                update_data = {
                    'status': new_status,
                    'status_updated_at': datetime.now().isoformat(),
                    'status_automation_reason': f"Completely paused in all {analysis['total_placements']} placements"
                }
                
                response = self.supabase.table("meta_ad_data").update(update_data).eq("ad_name", ad_name).execute()
                
                if response.data:
                    logger.info(f"Updated {ad_name} to {new_status} (was {current_status})")
                else:
                    logger.warning(f"No rows updated for {ad_name}")
            else:
                logger.info(f"Preserving manual status '{current_status}' for {ad_name}")
                
        except Exception as e:
            logger.error(f"Error updating status for {ad_name}: {e}")
            raise
    
    async def _clear_automated_status_if_set(self, ad_name: str):
        """Clear automated status if ad becomes active again"""
        try:
            # Only clear if status is currently automated
            current_response = self.supabase.table("meta_ad_data").select("status").eq("ad_name", ad_name).limit(1).execute()
            
            if current_response.data:
                current_status = current_response.data[0].get('status')
                if current_status == 'paused_automated':
                    update_data = {
                        'status': None,  # Clear automated status
                        'status_updated_at': datetime.now().isoformat(),
                        'status_automation_reason': 'Ad became active - cleared automated pause status'
                    }
                    
                    response = self.supabase.table("meta_ad_data").update(update_data).eq("ad_name", ad_name).execute()
                    logger.info(f"Cleared automated pause status for active ad: {ad_name}")
                    
        except Exception as e:
            logger.error(f"Error clearing automated status for {ad_name}: {e}")
    
    def get_pause_status_summary(self, pause_analysis: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of pause analysis results"""
        try:
            summary = {
                'completely_paused': 0,
                'completely_active': 0, 
                'mixed_status': 0,
                'automated_updates_needed': 0,
                'manual_status_preserved': 0,
                'total_ads_analyzed': len(pause_analysis)
            }
            
            for ad_name, analysis in pause_analysis.items():
                status = analysis['status']
                
                if status == 'paused_automated':
                    summary['completely_paused'] += 1
                    summary['automated_updates_needed'] += 1
                elif status == 'active':
                    summary['completely_active'] += 1
                elif status == 'mixed':
                    summary['mixed_status'] += 1
                    summary['manual_status_preserved'] += 1
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating pause status summary: {e}")
            return {'error': str(e)}