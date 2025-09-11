#!/usr/bin/env python3
"""
Google Ads Data Quality Monitor
Validates data accuracy and alerts on significant discrepancies

This script provides ongoing data quality assurance by:
1. Comparing database data with live API data
2. Detecting calculation errors and data drift
3. Generating alerts for business-critical discrepancies
4. Providing data quality reports for stakeholders
"""

import os
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from supabase import create_client
from loguru import logger
from typing import Dict, List, Tuple

# Add the app directory to the path
sys.path.append('.')

class GoogleAdsQualityMonitor:
    def __init__(self):
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_KEY')
        )
        
        from app.services.google_ads_service import GoogleAdsService
        self.google_service = GoogleAdsService()
        
        # Quality thresholds
        self.REVENUE_TOLERANCE = 0.02  # 2% tolerance
        self.ROAS_TOLERANCE = 0.05     # 5% tolerance  
        self.MAJOR_ALERT_THRESHOLD = 0.10  # 10% for major alerts
        
    def run_quality_check(self, days_back: int = 7) -> Dict:
        """
        Run comprehensive data quality check for recent data
        """
        print("🔍 GOOGLE ADS DATA QUALITY MONITOR")
        print("=" * 50)
        print(f"Checking data quality for past {days_back} days")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=days_back-1)
        
        # Get database data
        db_data = self._get_database_data(start_date, end_date)
        print(f"📊 Database records: {len(db_data)}")
        
        if not db_data:
            print("⚠️  No database records found for quality check period")
            return {"status": "no_data", "records_checked": 0}
        
        # Sample API validation (check 20% of records to balance API limits)
        sample_size = max(5, len(db_data) // 5)  # At least 5 records
        sample_dates = list(set([r['reporting_starts'] for r in db_data[:sample_size]]))
        
        print(f"🌐 API validation sample: {len(sample_dates)} unique dates")
        
        # Run quality checks
        quality_results = {
            "check_date": datetime.now().isoformat(),
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_records": len(db_data),
            "sampled_records": 0,
            "accuracy_metrics": {},
            "issues_found": [],
            "alerts": [],
            "overall_status": "unknown"
        }
        
        try:
            # Validate sample against API
            validation_results = self._validate_sample_data(sample_dates, db_data)
            quality_results.update(validation_results)
            
            # Run calculation validation
            calc_results = self._validate_calculations(db_data)
            quality_results["calculation_issues"] = calc_results
            
            # Generate overall quality assessment
            quality_results["overall_status"] = self._assess_overall_quality(quality_results)
            
            # Generate alerts if needed
            alerts = self._generate_alerts(quality_results)
            quality_results["alerts"] = alerts
            
            self._print_quality_report(quality_results)
            
            return quality_results
            
        except Exception as e:
            print(f"❌ Quality check failed: {e}")
            logger.error(f"Google Ads quality check error: {e}")
            quality_results["status"] = "error"
            quality_results["error"] = str(e)
            return quality_results
    
    def _get_database_data(self, start_date: date, end_date: date) -> List[Dict]:
        """Get database records for quality check period"""
        response = self.supabase.table('google_campaign_data')\
            .select('*')\
            .gte('reporting_starts', start_date.isoformat())\
            .lte('reporting_starts', end_date.isoformat())\
            .order('reporting_starts', desc=True)\
            .execute()
        
        return response.data if response.data else []
    
    def _validate_sample_data(self, sample_dates: List[str], db_data: List[Dict]) -> Dict:
        """Validate database data against API for sample dates"""
        validation_results = {
            "sampled_records": 0,
            "accuracy_metrics": {
                "revenue_accuracy": 0,
                "purchase_accuracy": 0,
                "spend_accuracy": 0,
                "roas_accuracy": 0
            },
            "issues_found": []
        }
        
        for date_str in sample_dates[:5]:  # Limit API calls
            try:
                check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # Get fresh API data
                api_insights = self.google_service.get_campaign_insights(check_date, check_date)
                api_data = self.google_service.convert_to_campaign_data(api_insights)
                
                # Compare with database data
                for api_campaign in api_data:
                    db_matches = [
                        r for r in db_data 
                        if (str(r['campaign_id']) == str(api_campaign.campaign_id) and
                            r['reporting_starts'] == date_str)
                    ]
                    
                    if db_matches:
                        db_record = db_matches[0]
                        validation_results["sampled_records"] += 1
                        
                        # Compare key metrics
                        discrepancies = self._compare_record(api_campaign, db_record)
                        
                        if discrepancies["has_issues"]:
                            validation_results["issues_found"].append({
                                "campaign_id": api_campaign.campaign_id,
                                "campaign_name": api_campaign.campaign_name,
                                "date": date_str,
                                "discrepancies": discrepancies
                            })
                
                print(f"    ✅ Validated {len(api_data)} campaigns for {date_str}")
                
            except Exception as e:
                print(f"    ❌ API validation failed for {date_str}: {e}")
        
        # Calculate accuracy percentages
        if validation_results["sampled_records"] > 0:
            issues_count = len(validation_results["issues_found"])
            accuracy_rate = (validation_results["sampled_records"] - issues_count) / validation_results["sampled_records"]
            
            validation_results["accuracy_metrics"]["overall_accuracy"] = accuracy_rate * 100
        
        return validation_results
    
    def _compare_record(self, api_data, db_record) -> Dict:
        """Compare API data with database record"""
        discrepancies = {
            "has_issues": False,
            "spend_diff": 0,
            "revenue_diff": 0,
            "purchase_diff": 0,
            "roas_diff": 0,
            "severity": "low"
        }
        
        # Calculate differences
        spend_diff = abs(float(api_data.amount_spent_usd) - float(db_record['amount_spent_usd'] or 0))
        revenue_diff = abs(float(api_data.purchases_conversion_value) - float(db_record['purchases_conversion_value'] or 0))
        purchase_diff = abs(api_data.website_purchases - int(db_record['website_purchases'] or 0))
        roas_diff = abs(float(api_data.roas) - float(db_record['roas'] or 0))
        
        discrepancies.update({
            "spend_diff": spend_diff,
            "revenue_diff": revenue_diff,
            "purchase_diff": purchase_diff,
            "roas_diff": roas_diff
        })
        
        # Check tolerances
        db_revenue = float(db_record['purchases_conversion_value'] or 0)
        db_roas = float(db_record['roas'] or 0)
        
        revenue_tolerance_exceeded = (
            db_revenue > 0 and 
            revenue_diff / db_revenue > self.REVENUE_TOLERANCE
        )
        
        roas_tolerance_exceeded = (
            db_roas > 0 and 
            roas_diff / db_roas > self.ROAS_TOLERANCE
        )
        
        if revenue_tolerance_exceeded or roas_tolerance_exceeded or purchase_diff > 0:
            discrepancies["has_issues"] = True
            
            # Determine severity
            if (db_revenue > 0 and revenue_diff / db_revenue > self.MAJOR_ALERT_THRESHOLD) or \
               (db_roas > 0 and roas_diff / db_roas > self.MAJOR_ALERT_THRESHOLD):
                discrepancies["severity"] = "high"
            elif revenue_tolerance_exceeded or roas_tolerance_exceeded:
                discrepancies["severity"] = "medium"
        
        return discrepancies
    
    def _validate_calculations(self, db_data: List[Dict]) -> List[Dict]:
        """Validate ROAS and CPA calculations in database"""
        calc_issues = []
        
        for record in db_data:
            spend = float(record['amount_spent_usd'] or 0)
            revenue = float(record['purchases_conversion_value'] or 0)
            purchases = int(record['website_purchases'] or 0)
            stored_roas = float(record['roas'] or 0)
            stored_cpa = float(record['cpa'] or 0)
            
            # Calculate expected values
            expected_roas = revenue / spend if spend > 0 else 0
            expected_cpa = spend / purchases if purchases > 0 else 0
            
            # Check for calculation errors
            roas_error = abs(stored_roas - expected_roas) > 0.01
            cpa_error = abs(stored_cpa - expected_cpa) > 0.01
            
            if roas_error or cpa_error:
                calc_issues.append({
                    "campaign_id": record['campaign_id'],
                    "campaign_name": record['campaign_name'],
                    "date": record['reporting_starts'],
                    "roas_error": roas_error,
                    "cpa_error": cpa_error,
                    "expected_roas": round(expected_roas, 4),
                    "stored_roas": stored_roas,
                    "expected_cpa": round(expected_cpa, 2),
                    "stored_cpa": stored_cpa
                })
        
        return calc_issues
    
    def _assess_overall_quality(self, results: Dict) -> str:
        """Assess overall data quality status"""
        issues_count = len(results.get("issues_found", []))
        calc_issues_count = len(results.get("calculation_issues", []))
        sampled_records = results.get("sampled_records", 0)
        
        if sampled_records == 0:
            return "insufficient_data"
        
        issue_rate = (issues_count + calc_issues_count) / sampled_records if sampled_records > 0 else 1
        
        if issue_rate < 0.02:  # Less than 2% issues
            return "excellent"
        elif issue_rate < 0.05:  # Less than 5% issues
            return "good"
        elif issue_rate < 0.10:  # Less than 10% issues
            return "fair"
        else:
            return "poor"
    
    def _generate_alerts(self, results: Dict) -> List[Dict]:
        """Generate alerts based on quality check results"""
        alerts = []
        
        # High severity data discrepancies
        high_severity_issues = [
            issue for issue in results.get("issues_found", [])
            if issue.get("discrepancies", {}).get("severity") == "high"
        ]
        
        if high_severity_issues:
            alerts.append({
                "type": "high_severity_discrepancy",
                "level": "critical",
                "message": f"{len(high_severity_issues)} campaigns have major data discrepancies",
                "details": high_severity_issues[:5]  # Limit details
            })
        
        # Calculation errors
        calc_issues_count = len(results.get("calculation_issues", []))
        if calc_issues_count > 0:
            alerts.append({
                "type": "calculation_error",
                "level": "high",
                "message": f"{calc_issues_count} records have ROAS/CPA calculation errors",
                "details": results.get("calculation_issues", [])[:5]
            })
        
        # Overall poor quality
        if results.get("overall_status") == "poor":
            alerts.append({
                "type": "poor_data_quality",
                "level": "high", 
                "message": "Overall data quality is poor - immediate attention required",
                "details": {
                    "issues_found": len(results.get("issues_found", [])),
                    "calculation_issues": calc_issues_count,
                    "sampled_records": results.get("sampled_records", 0)
                }
            })
        
        return alerts
    
    def _print_quality_report(self, results: Dict):
        """Print formatted quality report"""
        print("\n📊 QUALITY ASSESSMENT REPORT")
        print("-" * 40)
        
        status = results.get("overall_status", "unknown")
        status_emoji = {
            "excellent": "🟢",
            "good": "🟡", 
            "fair": "🟠",
            "poor": "🔴",
            "insufficient_data": "⚪"
        }
        
        print(f"Overall Status: {status_emoji.get(status, '❓')} {status.upper()}")
        print(f"Records Checked: {results.get('total_records', 0)}")
        print(f"API Samples Validated: {results.get('sampled_records', 0)}")
        
        issues_found = len(results.get("issues_found", []))
        calc_issues = len(results.get("calculation_issues", []))
        
        print(f"Data Discrepancies: {issues_found}")
        print(f"Calculation Issues: {calc_issues}")
        
        # Show alerts
        alerts = results.get("alerts", [])
        if alerts:
            print(f"\n🚨 ALERTS ({len(alerts)}):")
            for alert in alerts:
                level_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                print(f"  {level_emoji.get(alert['level'], '❓')} {alert['message']}")
        else:
            print(f"\n✅ No alerts - data quality within acceptable parameters")
        
        print(f"\nNext quality check recommended: {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}")

def main():
    """Main entry point for quality monitoring"""
    try:
        monitor = GoogleAdsQualityMonitor()
        results = monitor.run_quality_check(days_back=7)
        
        # Return results for external systems
        return results
        
    except Exception as e:
        print(f"❌ Quality monitoring failed: {e}")
        logger.error(f"Google Ads quality monitoring error: {e}")
        return {"status": "error", "error": str(e)}

if __name__ == '__main__':
    main()