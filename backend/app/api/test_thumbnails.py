"""
Test endpoint for the new thumbnail system
"""

from fastapi import APIRouter
from app.services.meta_ad_level_service import MetaAdLevelService
from typing import Dict, List
import logging

router = APIRouter()

@router.get("/test-thumbnails")
async def test_thumbnails():
    """Test the new high-resolution thumbnail system"""
    
    try:
        service = MetaAdLevelService()
        
        # Get 3 recent ads for testing  
        recent_ads = service.ad_account.get_ads(fields=['id', 'name'], params={'limit': 3})
        test_ad_ids = [ad['id'] for ad in list(recent_ads)]
        
        if not test_ad_ids:
            return {"error": "No ads found for testing"}
        
        # Test the new thumbnail system
        thumbnails = service.get_ad_thumbnails(test_ad_ids)
        
        # Analyze results
        results = []
        for ad_id, thumbnail_url in thumbnails.items():
            # Determine likely quality based on URL patterns
            if any(size in thumbnail_url for size in ['1080x1080', '600x600', '400x400']):
                quality = "HIGH-RES (400x400+)"
                status = "success"
            elif any(size in thumbnail_url for size in ['320x320', '192x192']):
                quality = "MEDIUM-RES (192x192+)"
                status = "good"
            elif 'p64x64' in thumbnail_url:
                quality = "LOW-RES (64x64)"
                status = "fallback"
            else:
                quality = "UNKNOWN"
                status = "unknown"
                
            results.append({
                "ad_id": ad_id,
                "thumbnail_url": thumbnail_url,
                "estimated_quality": quality,
                "status": status
            })
        
        # Summary
        high_res_count = sum(1 for r in results if r['status'] == 'success')
        total_count = len(results)
        
        return {
            "test_summary": {
                "total_ads_tested": total_count,
                "high_res_thumbnails": high_res_count,
                "success_rate": f"{(high_res_count/total_count)*100:.1f}%" if total_count > 0 else "0%",
                "system_working": high_res_count > 0
            },
            "thumbnail_results": results,
            "next_steps": [
                "Copy a thumbnail URL and test in browser",
                "If image is large/clear, run full N8N sync",
                "Check dashboard for improved hover zoom quality"
            ]
        }
        
    except Exception as e:
        logging.error(f"Thumbnail test error: {e}")
        return {"error": str(e)}