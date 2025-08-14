import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8007';

// Google Ads Data Types (mirroring backend models)
export interface GoogleCampaignData {
  id: number;
  campaign_id: string;
  campaign_name: string;
  category: string | null;
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

export interface GooglePivotTableData {
  month: string;
  spend: number;
  link_clicks: number;
  purchases: number;
  revenue: number;
  cpa: number;
  roas: number;
  cpc: number;
}

export interface GoogleMTDSummary {
  period: string;
  total_spend: number;
  total_clicks: number;
  total_purchases: number;
  total_revenue: number;
  avg_cpa: number;
  avg_roas: number;
  avg_cpc: number;
  campaigns_count: number;
}

export interface GoogleDashboardData {
  summary: GoogleMTDSummary;
  pivot_data: GooglePivotTableData[];
  categories: string[];
  filters?: {
    categories?: string[];
    start_date?: string;
    end_date?: string;
  };
}

export interface GoogleConnectionStatus {
  status: string;
  message: string;
}

export interface GoogleSyncResponse {
  message: string;
  synced: number;
}

export interface GoogleCampaignsList {
  campaigns: {
    id: string;
    name: string;
    status: string;
  }[];
}

export interface GoogleDataStats {
  total_campaigns: number;
  earliest_date: string | null;
  latest_date: string | null;
  unique_categories: number;
  last_updated: string;
}

class GoogleAdsApiService {
  private axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json'
    }
  });

  constructor() {
    // Request interceptor for logging
    this.axiosInstance.interceptors.request.use((config) => {
      console.log(`🔍 Google Ads API Request: ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    });

    // Response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => {
        console.log(`✅ Google Ads API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error(`❌ Google Ads API Error: ${error.message}`);
        if (error.response) {
          console.error(`Status: ${error.response.status}, Data:`, error.response.data);
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get dashboard data with optional filters
   */
  async getDashboardData(params?: {
    categories?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<GoogleDashboardData> {
    const response = await this.axiosInstance.get('/api/google-reports/dashboard', { params });
    return response.data;
  }

  /**
   * Get monthly breakdown data
   */
  async getMonthlyData(categories?: string): Promise<GooglePivotTableData[]> {
    const params = categories ? { categories } : {};
    const response = await this.axiosInstance.get('/api/google-reports/monthly', { params });
    return response.data;
  }

  /**
   * Get campaign-level data
   */
  async getCampaignsData(params?: {
    start_date?: string;
    end_date?: string;
    category?: string;
  }): Promise<GoogleCampaignData[]> {
    const response = await this.axiosInstance.get('/api/google-reports/campaigns', { params });
    return response.data;
  }

  /**
   * Test Google Ads API connection
   */
  async testConnection(): Promise<GoogleConnectionStatus> {
    const response = await this.axiosInstance.get('/api/google-reports/test-connection');
    return response.data;
  }

  /**
   * Manually sync Google Ads data
   */
  async syncData(start_date: string, end_date: string): Promise<GoogleSyncResponse> {
    const response = await this.axiosInstance.post(
      `/api/google-reports/sync?start_date=${start_date}&end_date=${end_date}`
    );
    return response.data;
  }

  /**
   * Get available categories
   */
  async getCategories(): Promise<{ categories: string[] }> {
    const response = await this.axiosInstance.get('/api/google-reports/categories');
    return response.data;
  }

  /**
   * Get Google Ads campaigns list from account
   */
  async getCampaignsList(): Promise<GoogleCampaignsList> {
    const response = await this.axiosInstance.get('/api/google-reports/campaigns-list');
    return response.data;
  }

  /**
   * Get Google Ads data statistics
   */
  async getDataStats(): Promise<GoogleDataStats> {
    const response = await this.axiosInstance.get('/api/google-reports/stats');
    return response.data;
  }

  /**
   * Add category rule
   */
  async addCategoryRule(rule: {
    rule_name: string;
    pattern: string;
    category: string;
    priority?: number;
    is_active?: boolean;
  }): Promise<{ message: string }> {
    const response = await this.axiosInstance.post('/api/google-reports/categories/rules', rule);
    return response.data;
  }

  /**
   * Add category override for specific campaign
   */
  async addCategoryOverride(override: {
    campaign_id: string;
    category: string;
    created_by?: string;
  }): Promise<{ message: string }> {
    const response = await this.axiosInstance.post('/api/google-reports/categories/overrides', override);
    return response.data;
  }

  /**
   * Health check for Google Ads service
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await this.axiosInstance.get('/api/google-reports/health');
    return response.data;
  }
}

// Export singleton instance
export const googleAdsApi = new GoogleAdsApiService();

// Export utility functions for formatting
export const formatGoogleCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

export const formatGoogleNumber = (value: number): string => {
  return new Intl.NumberFormat('en-US').format(value);
};

export const formatGooglePercentage = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value / 100);
};

export const formatGoogleDecimal = (value: number, decimals: number = 2): string => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

// Export hook for React components
export const useGoogleAdsApi = () => {
  return googleAdsApi;
};