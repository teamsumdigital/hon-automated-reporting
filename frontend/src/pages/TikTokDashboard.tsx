import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  RefreshCw, 
  Download, 
  Calendar,
  Filter,
  AlertCircle,
  CheckCircle,
  Settings
} from 'lucide-react';
import { tiktokApiClient, TikTokDashboardData } from '../services/tiktokApi';
import PivotTable from '../components/PivotTable';
import CategoryFilter from '../components/CategoryFilter';
import MetricsCards from '../components/MetricsCards';

const TikTokDashboard: React.FC = () => {
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [dateRange, setDateRange] = useState<{
    start_date?: string;
    end_date?: string;
  }>({});
  
  const queryClient = useQueryClient();

  // Query for categories
  const { data: categories = [], isLoading: categoriesLoading } = useQuery({
    queryKey: ['tiktok-categories'],
    queryFn: tiktokApiClient.getCategories,
  });

  // Query for dashboard data
  const { 
    data: dashboardData, 
    isLoading: dashboardLoading, 
    error: dashboardError,
    refetch: refetchDashboard 
  } = useQuery<TikTokDashboardData>({
    queryKey: ['tiktok-dashboard', selectedCategories, dateRange],
    queryFn: () => tiktokApiClient.getDashboardData({
      categories: selectedCategories.length > 0 ? selectedCategories.join(',') : undefined,
      start_date: dateRange.start_date,
      end_date: dateRange.end_date,
    }),
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });

  // Mutation for syncing TikTok data
  const syncMutation = useMutation({
    mutationFn: tiktokApiClient.syncTikTokData,
    onSuccess: (result) => {
      if (result.success) {
        queryClient.invalidateQueries({ queryKey: ['tiktok-dashboard'] });
        queryClient.invalidateQueries({ queryKey: ['tiktok-categories'] });
      }
    },
  });

  // Handle category filter changes
  const handleCategoryChange = (categories: string[]) => {
    setSelectedCategories(categories);
  };

  // Handle date range changes
  const handleDateRangeChange = (start: string, end: string) => {
    setDateRange({
      start_date: start || undefined,
      end_date: end || undefined,
    });
  };

  // Handle sync button click
  const handleSync = () => {
    syncMutation.mutate();
  };

  // Handle export (placeholder)
  const handleExport = () => {
    // TODO: Implement export functionality
    console.log('TikTok Export functionality to be implemented');
  };

  const isLoading = dashboardLoading || categoriesLoading;
  const hasError = dashboardError;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div>
              <h1 className="text-2xl font-bold text-foreground">HON Automated Reporting</h1>
              <p className="text-sm text-muted-foreground">TikTok Ads Performance Dashboard</p>
            </div>
            <div className="flex items-center gap-4">
              {syncMutation.isSuccess && (
                <div className="flex items-center gap-2 text-green-600 text-sm">
                  <CheckCircle className="w-4 h-4" />
                  Data synced successfully
                </div>
              )}
              {syncMutation.isError && (
                <div className="flex items-center gap-2 text-red-600 text-sm">
                  <AlertCircle className="w-4 h-4" />
                  Sync failed
                </div>
              )}
              <button
                onClick={handleSync}
                disabled={syncMutation.isPending}
                className="flex items-center gap-2 px-4 py-2 bg-pink-600 text-white rounded-md hover:bg-pink-700 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${syncMutation.isPending ? 'animate-spin' : ''}`} />
                {syncMutation.isPending ? 'Syncing...' : 'Sync Data'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="mb-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm font-medium">Filters</span>
            </div>
          </div>
          
          <div className="flex flex-wrap items-center gap-4">
            <CategoryFilter
              categories={categories}
              selectedCategories={selectedCategories}
              onCategoryChange={handleCategoryChange}
              loading={categoriesLoading}
            />
            
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <input
                type="date"
                value={dateRange.start_date || ''}
                onChange={(e) => handleDateRangeChange(e.target.value, dateRange.end_date || '')}
                className="px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                placeholder="Start date"
              />
              <span className="text-muted-foreground">to</span>
              <input
                type="date"
                value={dateRange.end_date || ''}
                onChange={(e) => handleDateRangeChange(dateRange.start_date || '', e.target.value)}
                className="px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                placeholder="End date"
              />
            </div>

            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-4 py-2 border border-border rounded-md hover:bg-muted/50 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-colors"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>

        {/* Error State */}
        {hasError && (
          <div className="mb-6 p-4 border border-red-200 bg-red-50 rounded-md">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="w-5 h-5" />
              <span className="font-medium">Error loading TikTok dashboard data</span>
            </div>
            <p className="text-red-600 text-sm mt-1">
              {dashboardError?.message || 'An unexpected error occurred'}
            </p>
            <button
              onClick={() => refetchDashboard()}
              className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
            >
              Try again
            </button>
          </div>
        )}

        {/* Metrics Cards */}
        <MetricsCards 
          summary={dashboardData?.summary || {
            total_spend: 0,
            total_purchases: 0,
            total_revenue: 0,
            total_impressions: 0,
            total_clicks: 0,
            avg_cpa: 0,
            avg_roas: 0,
            avg_cpc: 0,
            campaign_count: 0,
            date_range: ''
          }}
          loading={isLoading}
        />

        {/* Pivot Table */}
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Monthly Performance</h2>
            <div className="text-sm text-muted-foreground">
              {selectedCategories.length > 0 && selectedCategories.length < categories.length && (
                <span>Filtered by: {selectedCategories.join(', ')}</span>
              )}
            </div>
          </div>
          
          <PivotTable 
            data={dashboardData?.pivot_data || []}
            loading={isLoading}
          />
        </div>

        {/* Category Breakdown */}
        {dashboardData?.category_breakdown && dashboardData.category_breakdown.length > 0 && (
          <div className="mt-6 bg-card border border-border rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Category Breakdown</h2>
            <div className="overflow-x-auto">
              <table className="pivot-table">
                <thead>
                  <tr>
                    <th>Category</th>
                    <th className="text-right">Spend</th>
                    <th className="text-right">Purchases</th>
                    <th className="text-right">Revenue</th>
                    <th className="text-right">ROAS</th>
                    <th className="text-right">CPA</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboardData.category_breakdown.map((category, index) => (
                    <tr key={`${category.category}-${index}`}>
                      <td className="font-medium">{category.category}</td>
                      <td className="text-right">
                        ${category.amount_spent_usd.toFixed(2)}
                      </td>
                      <td className="text-right">{category.website_purchases}</td>
                      <td className="text-right">
                        ${category.purchases_conversion_value.toFixed(2)}
                      </td>
                      <td className="text-right">{category.roas.toFixed(2)}</td>
                      <td className="text-right">${category.cpa.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default TikTokDashboard;