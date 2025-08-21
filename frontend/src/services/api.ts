import axios from 'axios';

// Environment-based API URL
const API_BASE_URL = import.meta.env.DEV 
  ? 'http://localhost:8007' 
  : 'https://hon-automated-reporting.onrender.com';

console.log('🚀 API_BASE_URL:', API_BASE_URL);
console.log(`🔧 ${import.meta.env.DEV ? 'DEVELOPMENT' : 'PRODUCTION'} MODE`);

// Force immediate console output
if (typeof window !== 'undefined') {
  console.warn('⚠️ API CLIENT LOADED - URL:', API_BASE_URL);
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Types
export interface CampaignData {
  id: number;
  campaign_id: string;
  campaign_name: string;
  category: string;
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
  cpm: number;
  created_at: string;
  updated_at: string;
}

export interface PivotTableData {
  month: string;
  spend: number;
  revenue: number;
  roas: number;
  cpa: number;
  cpc: number;
  cpm: number;
}

export interface MTDSummary {
  total_spend: number;
  total_purchases: number;
  total_revenue: number;
  total_impressions: number;
  total_clicks: number;
  avg_cpa: number;
  avg_roas: number;
  avg_cpc: number;
  avg_cpm: number;
  campaign_count: number;
  date_range: string;
}

export interface CategoryBreakdown {
  category: string;
  amount_spent_usd: number;
  website_purchases: number;
  purchases_conversion_value: number;
  impressions: number;
  cpa: number;
  roas: number;
  cpm: number;
}

export interface DashboardData {
  summary: MTDSummary;
  pivot_data: PivotTableData[];
  category_breakdown: CategoryBreakdown[];
  filters_applied: {
    categories: string[] | null;
    start_date: string | null;
    end_date: string | null;
  };
}

export interface CategoryRule {
  id?: number;
  rule_name: string;
  pattern: string;
  category: string;
  priority: number;
  is_active: boolean;
}

export interface SyncResult {
  success: boolean;
  message: string;
  data_count?: number;
  summary?: MTDSummary;
}

// API Functions
export const apiClient = {
  // Dashboard data
  getDashboardData: async (params?: {
    categories?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<DashboardData> => {
    const response = await api.get('/api/reports/dashboard', { params });
    return response.data;
  },

  // Pivot table data
  getPivotTableData: async (params?: {
    categories?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<PivotTableData[]> => {
    const response = await api.get('/api/reports/pivot-table', { params });
    return response.data;
  },

  // Month-to-date summary
  getMTDSummary: async (target_date?: string): Promise<MTDSummary> => {
    const response = await api.get('/api/reports/month-to-date', {
      params: target_date ? { target_date } : {},
    });
    return response.data;
  },

  // Campaign data
  getCampaigns: async (params?: {
    categories?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<CampaignData[]> => {
    const response = await api.get('/api/reports/campaigns', { params });
    return response.data;
  },

  // Categories
  getCategories: async (): Promise<string[]> => {
    const response = await api.get('/api/reports/categories');
    return response.data;
  },

  // Category breakdown
  getCategoryBreakdown: async (params?: {
    categories?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<CategoryBreakdown[]> => {
    const response = await api.get('/api/reports/category-breakdown', { params });
    return response.data;
  },

  // Sync Meta data
  syncMetaData: async (target_date?: string): Promise<SyncResult> => {
    const response = await api.post('/api/reports/sync', 
      target_date ? { target_date } : {}
    );
    return response.data;
  },

  // Category rules
  getCategoryRules: async (): Promise<CategoryRule[]> => {
    const response = await api.get('/api/reports/category-rules');
    return response.data;
  },

  addCategoryRule: async (rule: Omit<CategoryRule, 'id'>): Promise<{ message: string }> => {
    const response = await api.post('/api/reports/category-rules', rule);
    return response.data;
  },

  // Test connection
  testConnection: async (): Promise<{ status: string; message: string }> => {
    const response = await api.get('/api/reports/test-connection');
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<{ status: string; environment: string }> => {
    const response = await api.get('/health');
    return response.data;
  },

  // Ad-level dashboard endpoints
  getAdLevelData: async (filters?: {
    categories?: string;
    content_types?: string;
    formats?: string;
    campaign_optimizations?: string;
  }): Promise<any> => {
    const response = await api.get('/api/meta-ad-reports/ad-data', { params: filters });
    return response.data;
  },

  getAdLevelSummary: async (filters?: {
    categories?: string;
    content_types?: string;
    formats?: string;
    campaign_optimizations?: string;
  }): Promise<any> => {
    const response = await api.get('/api/meta-ad-reports/summary', { params: filters });
    return response.data;
  },

  getAdLevelFilters: async (): Promise<any> => {
    const response = await api.get('/api/meta-ad-reports/filters');
    return response.data;
  },

  syncAdLevel14Days: async (): Promise<any> => {
    const response = await api.post('/api/meta-ad-reports/sync-14-days');
    return response.data;
  },
};

export default api;