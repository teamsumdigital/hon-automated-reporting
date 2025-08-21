from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger
import os
from supabase import create_client
from ..services.meta_ad_level_service import MetaAdLevelService

router = APIRouter()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

supabase = create_client(supabase_url, supabase_key)

@router.get("/test-connection")
def test_meta_ad_connection():
    """
    Test Meta Ads API connection for ad-level data
    """
    try:
        service = MetaAdLevelService()
        if service.test_connection():
            return {"status": "success", "message": "Meta Ads API connection successful for ad-level data"}
        else:
            return {"status": "error", "message": "Meta Ads API connection failed"}
    except Exception as e:
        logger.error(f"Meta ad-level connection test error: {e}")
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")

@router.post("/sync-14-days")
def sync_last_14_days_ad_data():
    """
    Sync ad-level data for the last 14 days with weekly segmentation
    """
    try:
        service = MetaAdLevelService()
        
        # Get last 14 days of ad-level data
        ad_data = service.get_last_14_days_ad_data()
        
        if not ad_data:
            return {"status": "success", "message": "No ad data found for the last 14 days", "ads_synced": 0}
        
        # Clear existing data for the date range first
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=13)
        
        logger.info(f"Clearing existing ad data from {start_date} to {end_date}")
        supabase.table('meta_ad_data').delete().gte('reporting_starts', start_date.isoformat()).lte('reporting_ends', end_date.isoformat()).execute()
        
        # Insert new data
        insert_data = []
        for ad in ad_data:
            # Convert date objects to ISO format strings for Supabase
            insert_record = {
                'ad_id': ad['ad_id'],
                'ad_name': ad['ad_name'],
                'campaign_name': ad['campaign_name'],
                'reporting_starts': ad['reporting_starts'].isoformat(),
                'reporting_ends': ad['reporting_ends'].isoformat(),
                # 'week_number': ad['week_number'],  # Temporarily disabled until column is added
                'launch_date': ad['launch_date'].isoformat() if ad['launch_date'] else None,
                'days_live': ad['days_live'],
                'category': ad['category'],
                'product': ad['product'],
                'color': ad['color'],
                'content_type': ad['content_type'],
                'handle': ad['handle'],
                'format': ad['format'],
                'campaign_optimization': ad['campaign_optimization'],
                'amount_spent_usd': ad['amount_spent_usd'],
                'purchases': ad['purchases'],
                'purchases_conversion_value': ad['purchases_conversion_value'],
                'impressions': ad['impressions'],
                'link_clicks': ad['link_clicks'],
                'thumbnail_url': ad.get('thumbnail_url')
            }
            insert_data.append(insert_record)
        
        # Batch insert
        if insert_data:
            result = supabase.table('meta_ad_data').insert(insert_data).execute()
            
            if result.data:
                logger.info(f"Successfully inserted {len(result.data)} ad records")
                
                # Return summary statistics
                total_spend = sum(ad['amount_spent_usd'] for ad in ad_data)
                total_purchases = sum(ad['purchases'] for ad in ad_data)
                total_revenue = sum(ad['purchases_conversion_value'] for ad in ad_data)
                total_impressions = sum(ad['impressions'] for ad in ad_data)
                total_clicks = sum(ad['link_clicks'] for ad in ad_data)
                
                # Group by week for summary
                weekly_summary = {}
                for ad in ad_data:
                    week = ad['week_number']
                    if week not in weekly_summary:
                        weekly_summary[week] = {
                            'ads_count': 0,
                            'spend': 0,
                            'purchases': 0,
                            'revenue': 0,
                            'impressions': 0,
                            'clicks': 0
                        }
                    weekly_summary[week]['ads_count'] += 1
                    weekly_summary[week]['spend'] += ad['amount_spent_usd']
                    weekly_summary[week]['purchases'] += ad['purchases']
                    weekly_summary[week]['revenue'] += ad['purchases_conversion_value']
                    weekly_summary[week]['impressions'] += ad['impressions']
                    weekly_summary[week]['clicks'] += ad['link_clicks']
                
                return {
                    "status": "success",
                    "message": f"Successfully synced {len(result.data)} ad records for last 14 days",
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    },
                    "summary": {
                        "total_ads": len(result.data),
                        "total_spend": round(total_spend, 2),
                        "total_purchases": total_purchases,
                        "total_revenue": round(total_revenue, 2),
                        "total_impressions": total_impressions,
                        "total_clicks": total_clicks,
                        "average_roas": round(total_revenue / total_spend, 2) if total_spend > 0 else 0
                    },
                    "weekly_breakdown": weekly_summary
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to insert ad data")
        else:
            return {"status": "success", "message": "No ad data to insert", "ads_synced": 0}
            
    except Exception as e:
        logger.error(f"Error syncing 14-day ad data: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.get("/ad-data")
def get_ad_level_data(
    categories: Optional[str] = None,
    content_types: Optional[str] = None,
    formats: Optional[str] = None,
    campaign_optimizations: Optional[str] = None
):
    """
    Get ad-level data grouped by ad name with weekly periods
    """
    try:
        # Only get data from the last 14 days
        from datetime import datetime, timedelta
        cutoff_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
        
        query = supabase.table('meta_ad_data').select('*').gte('reporting_starts', cutoff_date)
        
        # Apply filters
        if categories:
            category_list = categories.split(',')
            query = query.in_('category', category_list)
        if content_types:
            content_type_list = content_types.split(',')
            query = query.in_('content_type', content_type_list)
        if formats:
            format_list = formats.split(',')
            query = query.in_('format', format_list)
        if campaign_optimizations:
            optimization_list = campaign_optimizations.split(',')
            query = query.in_('campaign_optimization', optimization_list)
        
        # Order by ad name, then by reporting date (older first)
        query = query.order('ad_name').order('reporting_starts')
        
        result = query.execute()
        
        if not result.data:
            return {
                "status": "success",
                "count": 0,
                "grouped_ads": []
            }
        
        # Group data by ad name and deduplicate by date range
        grouped_data = {}
        
        for ad in result.data:
            ad_name = ad['ad_name']
            date_key = f"{ad['reporting_starts']}_{ad['reporting_ends']}"
            
            if ad_name not in grouped_data:
                grouped_data[ad_name] = {
                    'ad_name': ad_name,
                    'in_platform_ad_name': ad.get('in_platform_ad_name', ad_name),
                    'category': ad['category'],
                    'content_type': ad['content_type'],
                    'format': ad['format'],
                    'campaign_optimization': ad['campaign_optimization'],
                    'days_live': ad['days_live'],
                    'thumbnail_url': ad.get('thumbnail_url'),
                    'weekly_periods': {},  # Use dict to prevent duplicates
                    'total_spend': 0,
                    'total_revenue': 0,
                    'total_purchases': 0,
                    'total_clicks': 0,
                    'total_impressions': 0
                }
            
            # Check if this date period already exists for this ad
            if date_key not in grouped_data[ad_name]['weekly_periods']:
                # Add weekly period data (first occurrence)
                grouped_data[ad_name]['weekly_periods'][date_key] = {
                    'reporting_starts': ad['reporting_starts'],
                    'reporting_ends': ad['reporting_ends'],
                    'spend': ad['amount_spent_usd'],
                    'revenue': ad['purchases_conversion_value'],
                    'purchases': ad['purchases'],
                    'roas': round(ad['purchases_conversion_value'] / ad['amount_spent_usd'], 2) if ad['amount_spent_usd'] > 0 else 0,
                    'cpa': round(ad['amount_spent_usd'] / ad['purchases'], 2) if ad['purchases'] > 0 else 0,
                    'cpc': round(ad['amount_spent_usd'] / ad['link_clicks'], 2) if ad['link_clicks'] > 0 else 0,
                    'clicks': ad['link_clicks'],
                    'impressions': ad['impressions']
                }
                
                # Add to totals (only for unique periods)
                grouped_data[ad_name]['total_spend'] += ad['amount_spent_usd']
                grouped_data[ad_name]['total_revenue'] += ad['purchases_conversion_value']
                grouped_data[ad_name]['total_purchases'] += ad['purchases']
                grouped_data[ad_name]['total_clicks'] += ad['link_clicks']
                grouped_data[ad_name]['total_impressions'] += ad['impressions']
            else:
                # Duplicate found - aggregate the metrics
                existing = grouped_data[ad_name]['weekly_periods'][date_key]
                existing['spend'] += ad['amount_spent_usd']
                existing['revenue'] += ad['purchases_conversion_value']
                existing['purchases'] += ad['purchases']
                existing['clicks'] += ad['link_clicks']
                existing['impressions'] += ad['impressions']
                
                # Recalculate derived metrics
                existing['roas'] = round(existing['revenue'] / existing['spend'], 2) if existing['spend'] > 0 else 0
                existing['cpa'] = round(existing['spend'] / existing['purchases'], 2) if existing['purchases'] > 0 else 0
                existing['cpc'] = round(existing['spend'] / existing['clicks'], 2) if existing['clicks'] > 0 else 0
                
                # Add to totals
                grouped_data[ad_name]['total_spend'] += ad['amount_spent_usd']
                grouped_data[ad_name]['total_revenue'] += ad['purchases_conversion_value']
                grouped_data[ad_name]['total_purchases'] += ad['purchases']
                grouped_data[ad_name]['total_clicks'] += ad['link_clicks']
                grouped_data[ad_name]['total_impressions'] += ad['impressions']
        
        # Calculate aggregate metrics for each ad
        for ad_data in grouped_data.values():
            if ad_data['total_spend'] > 0:
                ad_data['total_roas'] = round(ad_data['total_revenue'] / ad_data['total_spend'], 2)
                ad_data['total_cpa'] = round(ad_data['total_spend'] / ad_data['total_purchases'], 2) if ad_data['total_purchases'] > 0 else 0
            else:
                ad_data['total_roas'] = 0
                ad_data['total_cpa'] = 0
            
            if ad_data['total_clicks'] > 0:
                ad_data['total_cpc'] = round(ad_data['total_spend'] / ad_data['total_clicks'], 2)
            else:
                ad_data['total_cpc'] = 0
            
            # Convert weekly_periods dict back to list, sort (older week first) and keep only the most recent 2
            ad_data['weekly_periods'] = list(ad_data['weekly_periods'].values())
            ad_data['weekly_periods'].sort(key=lambda x: x['reporting_starts'])
            ad_data['weekly_periods'] = ad_data['weekly_periods'][-2:]  # Keep only the last 2 periods
        
        # Convert to list and sort by total spend (highest first)
        grouped_ads = sorted(grouped_data.values(), key=lambda x: x['total_spend'], reverse=True)
        
        return {
            "status": "success",
            "count": len(grouped_ads),
            "grouped_ads": grouped_ads
        }
            
    except Exception as e:
        logger.error(f"Error fetching ad data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ad data: {str(e)}")

@router.get("/summary")
def get_ad_level_summary(
    categories: Optional[str] = None,
    content_types: Optional[str] = None,
    formats: Optional[str] = None,
    campaign_optimizations: Optional[str] = None
):
    """
    Get overall KPI summary for ad-level dashboard
    """
    try:
        query = supabase.table('meta_ad_data').select('*')
        
        # Apply filters
        if categories:
            category_list = categories.split(',')
            query = query.in_('category', category_list)
        if content_types:
            content_type_list = content_types.split(',')
            query = query.in_('content_type', content_type_list)
        if formats:
            format_list = formats.split(',')
            query = query.in_('format', format_list)
        if campaign_optimizations:
            optimization_list = campaign_optimizations.split(',')
            query = query.in_('campaign_optimization', optimization_list)
        
        result = query.execute()
        
        if not result.data:
            return {
                "total_spend": 0,
                "total_revenue": 0,
                "avg_roas": 0,
                "avg_cpa": 0,
                "total_ads": 0
            }
        
        # Calculate totals
        total_spend = sum(ad['amount_spent_usd'] for ad in result.data)
        total_revenue = sum(ad['purchases_conversion_value'] for ad in result.data)
        total_purchases = sum(ad['purchases'] for ad in result.data)
        
        return {
            "total_spend": round(total_spend, 2),
            "total_revenue": round(total_revenue, 2),
            "avg_roas": round(total_revenue / total_spend, 2) if total_spend > 0 else 0,
            "avg_cpa": round(total_spend / total_purchases, 2) if total_purchases > 0 else 0,
            "total_ads": len(result.data)
        }
        
    except Exception as e:
        logger.error(f"Error fetching ad summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch summary: {str(e)}")

@router.get("/filters")
def get_filter_options():
    """
    Get available filter options for the ad-level dashboard
    """
    try:
        result = supabase.table('meta_ad_data').select('category, content_type, format, campaign_optimization').execute()
        
        if not result.data:
            return {
                "categories": [],
                "content_types": [],
                "formats": [],
                "campaign_optimizations": []
            }
        
        # Extract unique values for each filter
        categories = list(set(ad['category'] for ad in result.data if ad['category']))
        content_types = list(set(ad['content_type'] for ad in result.data if ad['content_type']))
        formats = list(set(ad['format'] for ad in result.data if ad['format']))
        campaign_optimizations = list(set(ad['campaign_optimization'] for ad in result.data if ad['campaign_optimization']))
        
        return {
            "categories": sorted(categories),
            "content_types": sorted(content_types),
            "formats": sorted(formats),
            "campaign_optimizations": sorted(campaign_optimizations)
        }
        
    except Exception as e:
        logger.error(f"Error fetching filter options: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch filters: {str(e)}")

@router.get("/weekly-summary")
def get_weekly_ad_summary():
    """
    Get weekly summary of ad performance for the last 14 days
    """
    try:
        # Get last 14 days date range
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=13)
        
        result = supabase.table('meta_ad_data')\
            .select('*')\
            .gte('reporting_starts', start_date.isoformat())\
            .lte('reporting_ends', end_date.isoformat())\
            .execute()
        
        if not result.data:
            return {
                "status": "success",
                "message": "No ad data found for the last 14 days",
                "weekly_summary": {}
            }
        
        # Group by week and category
        weekly_summary = {}
        category_totals = {}
        
        for ad in result.data:
            week = ad['week_number']
            category = ad['category']
            
            # Initialize week if not exists
            if week not in weekly_summary:
                weekly_summary[week] = {
                    'total_ads': 0,
                    'total_spend': 0,
                    'total_purchases': 0,
                    'total_revenue': 0,
                    'total_impressions': 0,
                    'total_clicks': 0,
                    'categories': {}
                }
            
            # Initialize category if not exists
            if category not in weekly_summary[week]['categories']:
                weekly_summary[week]['categories'][category] = {
                    'ads_count': 0,
                    'spend': 0,
                    'purchases': 0,
                    'revenue': 0,
                    'impressions': 0,
                    'clicks': 0
                }
            
            # Add to week totals
            weekly_summary[week]['total_ads'] += 1
            weekly_summary[week]['total_spend'] += ad['amount_spent_usd']
            weekly_summary[week]['total_purchases'] += ad['purchases']
            weekly_summary[week]['total_revenue'] += ad['purchases_conversion_value']
            weekly_summary[week]['total_impressions'] += ad['impressions']
            weekly_summary[week]['total_clicks'] += ad['link_clicks']
            
            # Add to category within week
            weekly_summary[week]['categories'][category]['ads_count'] += 1
            weekly_summary[week]['categories'][category]['spend'] += ad['amount_spent_usd']
            weekly_summary[week]['categories'][category]['purchases'] += ad['purchases']
            weekly_summary[week]['categories'][category]['revenue'] += ad['purchases_conversion_value']
            weekly_summary[week]['categories'][category]['impressions'] += ad['impressions']
            weekly_summary[week]['categories'][category]['clicks'] += ad['link_clicks']
            
            # Track category totals across all weeks
            if category not in category_totals:
                category_totals[category] = {
                    'ads_count': 0,
                    'spend': 0,
                    'purchases': 0,
                    'revenue': 0,
                    'impressions': 0,
                    'clicks': 0
                }
            
            category_totals[category]['ads_count'] += 1
            category_totals[category]['spend'] += ad['amount_spent_usd']
            category_totals[category]['purchases'] += ad['purchases']
            category_totals[category]['revenue'] += ad['purchases_conversion_value']
            category_totals[category]['impressions'] += ad['impressions']
            category_totals[category]['clicks'] += ad['link_clicks']
        
        # Calculate performance metrics for each week
        for week_data in weekly_summary.values():
            if week_data['total_spend'] > 0:
                week_data['roas'] = round(week_data['total_revenue'] / week_data['total_spend'], 2)
                week_data['cpa'] = round(week_data['total_spend'] / week_data['total_purchases'], 2) if week_data['total_purchases'] > 0 else 0
            else:
                week_data['roas'] = 0
                week_data['cpa'] = 0
            
            if week_data['total_clicks'] > 0:
                week_data['cpc'] = round(week_data['total_spend'] / week_data['total_clicks'], 2)
            else:
                week_data['cpc'] = 0
        
        return {
            "status": "success",
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "weekly_summary": weekly_summary,
            "category_totals": category_totals,
            "total_ads": len(result.data)
        }
        
    except Exception as e:
        logger.error(f"Error fetching weekly ad summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch weekly summary: {str(e)}")