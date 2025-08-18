// TikTok API client - no zod dependency needed

// TikTok API Types
export interface TikTokCampaignData {
  id: number;
  campaign_id: string;
  campaign_name: string;
  category?: string;
  campaign_type?: string;
  reporting_starts: string;
  reporting_ends: string;
  amount_spent_usd: number;
  website_purchases: number;
  purchases_conversion_value: number;
  impressions: number;
  link_clicks: number;
  cpa: number;
  roas: number;
  cpc: number;
  created_at: string;
  updated_at: string;
}

export interface TikTokPivotTableData {
  month: string;
  spend: number;
  link_clicks: number;
  purchases: number;
  revenue: number;
  cpa: number;
  roas: number;
  cpc: number;
}

export interface TikTokDashboardSummary {
  period: string;
  total_spend: number;
  total_clicks: number;
  total_purchases: number;
  total_revenue: number;
  total_impressions?: number;
  avg_cpa: number;
  avg_roas: number;
  avg_cpc: number;
  campaigns_count: number;
  date_range?: string;
  campaign_count?: number;
}

export interface TikTokCategoryBreakdown {
  category: string;
  amount_spent_usd: number;
  website_purchases: number;
  purchases_conversion_value: number;
  roas: number;
  cpa: number;
}

export interface TikTokDashboardData {
  summary: TikTokDashboardSummary;
  pivot_data: TikTokPivotTableData[];
  categories: string[];
  category_breakdown?: TikTokCategoryBreakdown[];
  campaigns?: TikTokCampaignData[];
}

export interface TikTokDashboardFilters {
  categories?: string;
  start_date?: string;
  end_date?: string;
}

export interface TikTokSyncResult {
  success: boolean;
  message: string;
  synced?: number;
}

// API Client
class TikTokApiClient {
  private baseUrl: string;

  constructor() {
    // Use environment variable or default to port 8007
    this.baseUrl = import.meta.env.VITE_API_BASE_URL || 'https://hon-automated-reporting.onrender.com';
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Request failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error(`Network error: ${String(error)}`);
    }
  }

  // Get TikTok dashboard data
  async getDashboardData(filters?: TikTokDashboardFilters): Promise<TikTokDashboardData> {
    const searchParams = new URLSearchParams();
    
    if (filters?.categories) {
      searchParams.append('categories', filters.categories);
    }
    if (filters?.start_date) {
      searchParams.append('start_date', filters.start_date);
    }
    if (filters?.end_date) {
      searchParams.append('end_date', filters.end_date);
    }
    
    const queryString = searchParams.toString();
    const endpoint = `/api/tiktok-reports/dashboard${queryString ? `?${queryString}` : ''}`;
    
    return this.request<TikTokDashboardData>(endpoint);
  }

  // Get TikTok monthly data
  async getMonthlyData(filters?: TikTokDashboardFilters): Promise<TikTokPivotTableData[]> {
    const searchParams = new URLSearchParams();
    
    if (filters?.categories) {
      searchParams.append('categories', filters.categories);
    }
    
    const queryString = searchParams.toString();
    const endpoint = `/api/tiktok-reports/monthly${queryString ? `?${queryString}` : ''}`;
    
    return this.request<TikTokPivotTableData[]>(endpoint);
  }

  // Get TikTok categories
  async getCategories(): Promise<string[]> {
    const result = await this.request<{ categories: string[] }>('/api/tiktok-reports/categories');
    return result.categories;
  }

  // Get TikTok campaigns
  async getCampaigns(filters?: TikTokDashboardFilters): Promise<TikTokCampaignData[]> {
    const searchParams = new URLSearchParams();
    
    if (filters?.start_date) {
      searchParams.append('start_date', filters.start_date);
    }
    if (filters?.end_date) {
      searchParams.append('end_date', filters.end_date);
    }
    if (filters?.categories) {
      searchParams.append('category', filters.categories);
    }
    
    const queryString = searchParams.toString();
    const endpoint = `/api/tiktok-reports/campaigns${queryString ? `?${queryString}` : ''}`;
    
    return this.request<TikTokCampaignData[]>(endpoint);
  }

  // Sync TikTok data
  async syncTikTokData(startDate?: string, endDate?: string): Promise<TikTokSyncResult> {
    const today = new Date();
    const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));
    
    const start = startDate || thirtyDaysAgo.toISOString().split('T')[0];
    const end = endDate || today.toISOString().split('T')[0];
    
    const endpoint = `/api/tiktok-reports/sync?start_date=${start}&end_date=${end}`;
    
    try {
      const result = await this.request<{ message: string; synced: number }>(endpoint, {
        method: 'POST',
      });
      
      return {
        success: true,
        message: result.message,
        synced: result.synced,
      };
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Sync failed',
      };
    }
  }

  // Test TikTok API connection
  async testConnection(): Promise<{ status: string; message: string }> {
    return this.request<{ status: string; message: string }>('/api/tiktok-reports/test-connection');
  }

  // Get TikTok campaigns list from API
  async getCampaignsList(): Promise<{ campaigns: any[] }> {
    return this.request<{ campaigns: any[] }>('/api/tiktok-reports/campaigns-list');
  }

  // Get TikTok stats
  async getStats(): Promise<any> {
    return this.request('/api/tiktok-reports/stats');
  }

  // Get TikTok performance comparison
  async getPerformanceComparison(months: number = 6): Promise<any> {
    return this.request(`/api/tiktok-reports/performance-comparison?months=${months}`);
  }
}

// Utility functions for formatting TikTok data
export const formatTikTokCurrency = (value: number): string => {
  if (value === 0) return '$0';
  if (value < 1000) return `$${value.toFixed(0)}`;
  if (value < 1000000) return `$${(value / 1000).toFixed(1)}K`;
  return `$${(value / 1000000).toFixed(1)}M`;
};

export const formatTikTokNumber = (value: number): string => {
  if (value === 0) return '0';
  if (value < 1000) return value.toString();
  if (value < 1000000) return `${(value / 1000).toFixed(1)}K`;
  return `${(value / 1000000).toFixed(1)}M`;
};

export const formatTikTokDecimal = (value: number, decimals: number = 2): string => {
  return value.toFixed(decimals);
};

// Export singleton instance
export const tiktokApiClient = new TikTokApiClient();
export default tiktokApiClient;