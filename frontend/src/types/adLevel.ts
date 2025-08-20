// Ad-level dashboard specific types

export interface WeeklyPeriod {
  reporting_starts: string;
  reporting_ends: string;
  spend: number;
  revenue: number;
  purchases: number;
  roas: number;
  cpa: number;
  cpc: number;
  clicks: number;
  impressions: number;
}

export interface AdData {
  ad_name: string;
  in_platform_ad_name?: string;
  category: string;
  content_type: string;
  format: string;
  campaign_optimization: string;
  days_live: number;
  weekly_periods: WeeklyPeriod[];
  total_spend: number;
  total_revenue: number;
  total_purchases: number;
  total_clicks: number;
  total_impressions: number;
  total_roas: number;
  total_cpa: number;
  total_cpc: number;
}

export interface AdLevelSummary {
  total_spend: number;
  total_revenue: number;
  avg_roas: number;
  avg_cpa: number;
  total_ads: number;
}

export interface AdLevelFilters {
  categories?: string[];
  content_types?: string[];
  formats?: string[];
  campaign_optimizations?: string[];
}

export interface FilterOptions {
  categories: string[];
  content_types: string[];
  formats: string[];
  campaign_optimizations: string[];
}

export interface AdDataResponse {
  status: string;
  count: number;
  grouped_ads: AdData[];
}