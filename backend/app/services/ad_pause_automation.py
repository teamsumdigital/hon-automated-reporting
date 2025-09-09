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
                ad_status = ad.get('effective_status', '').upper()  # Ad-level status only
                
                if ad_name not in ad_groups:
                    ad_groups[ad_name] = {
                        'placements': [],
                        'active_count': 0,
                        'paused_count': 0,
                        'total_count': 0,
                        'spend': 0
                    }
                
                # Determine if this specific ad instance is active (simplified logic)
                # Handle UNKNOWN status as active for now (until status fetching is optimized)
                is_active = (ad_status in ['ACTIVE', 'UNKNOWN'])
                
                ad_groups[ad_name]['placements'].append({
                    'ad_id': ad.get('ad_id'),
                    'campaign_name': ad.get('campaign_name', ''),
                    'campaign_id': ad.get('campaign_id', ''),
                    'ad_status': ad_status,
                    'is_active': is_active,
                    'date_start': ad.get('date_start', ''),
                    'date_stop': ad.get('date_stop', '')
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
            # Completely paused in ALL locations - set as paused
            status = 'paused'
            action = 'apply_paused_status'
        elif paused_count == 0:
            # Completely active in ALL locations
            status = 'active'
            action = 'apply_active_status'
        else:
            # Mixed status - paused in some locations, active in others
            # For now, treat mixed as active (we'll enhance this in Phase 2)
            status = 'active'
            action = 'apply_active_status'
        
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
                    if action == 'apply_paused_status':
                        # Set status to paused
                        await self._update_ad_status(ad_name, 'paused', analysis)
                        updates_applied += 1
                        logger.info(f"Applied paused status to: {ad_name}")
                        
                    elif action == 'apply_active_status':
                        # Set status to active (or clear to null)
                        await self._update_ad_status(ad_name, 'active', analysis)
                        updates_applied += 1
                        logger.info(f"Applied active status to: {ad_name}")
                        
                    elif action == 'none':
                        # Unknown status - don't change anything
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
            # 2. Current status is already automated (updating existing automation)
            if current_status is None or current_status in ['paused', 'active']:
                if new_status == 'paused':
                    reason = f"Paused in all {analysis['total_placements']} ad instances"
                else:
                    reason = f"Active in {analysis['active_placements']} of {analysis['total_placements']} ad instances"
                
                update_data = {
                    'status': new_status,
                    'status_updated_at': datetime.now().isoformat(),
                    'status_automation_reason': reason
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
                if current_status in ['paused', 'active']:
                    update_data = {
                        'status': None,  # Clear automated status
                        'status_updated_at': datetime.now().isoformat(),
                        'status_automation_reason': 'Ad status changed - cleared automated status'
                    }
                    
                    response = self.supabase.table("meta_ad_data").update(update_data).eq("ad_name", ad_name).execute()
                    logger.info(f"Cleared automated status for ad: {ad_name}")
                    
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
                
                if status == 'paused':
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