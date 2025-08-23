import React, { useState, useEffect } from 'react';
import { 
  ChevronRightIcon,
  ChevronDownIcon,
  InformationCircleIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline';
import Header from '../components/Header';

// TikTok-specific interfaces
interface TikTokAdData {
  ad_name: string;
  campaign_name: string;
  category: string;
  status: string;
  thumbnail_url?: string;
  weekly_periods: {
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
  }[];
  total_spend: number;
  total_revenue: number;
  total_purchases: number;
  total_clicks: number;
  total_impressions: number;
  total_roas: number;
  total_cpa: number;
  total_cpc: number;
}

interface TikTokAdLevelSummary {
  total_spend: number;
  total_revenue: number;
  total_purchases: number;
  total_clicks: number;
  total_impressions: number;
  avg_roas: number;
  avg_cpa: number;
  avg_cpc: number;
  ads_count: number;
}

interface TikTokFilterOptions {
  categories: string[];
  content_types: string[];
  formats: string[];
  campaign_optimizations: string[];
}

interface KPICardProps {
  title: string;
  value: string | number;
  tooltip: string;
  color?: 'blue' | 'green' | 'amber' | 'purple';
  trend?: 'up' | 'down' | 'neutral';
}

const KPICard: React.FC<KPICardProps> = ({ title, value, tooltip, color = 'blue', trend }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50 border-blue-200',
    green: 'text-green-600 bg-green-50 border-green-200',
    amber: 'text-amber-600 bg-amber-50 border-amber-200',
    purple: 'text-purple-600 bg-purple-50 border-purple-200'
  };

  const getROASColor = (roasValue: number) => {
    if (roasValue >= 4) return 'green';
    if (roasValue >= 2) return 'amber';
    return 'blue';
  };

  const actualColor = title === 'ROAS' && typeof value === 'number' 
    ? getROASColor(value) 
    : color;

  return (
    <div className="relative">
      <div className={`
        p-6 rounded-xl border-2 shadow-sm hover:shadow-md transition-all duration-200 
        bg-white ${colorClasses[actualColor]}
      `}>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-600">{title}</h3>
          <div className="relative">
            <InformationCircleIcon 
              className="w-4 h-4 text-gray-400 hover:text-gray-600 cursor-help"
              onMouseEnter={() => setShowTooltip(true)}
              onMouseLeave={() => setShowTooltip(false)}
            />
            {showTooltip && (
              <div className="absolute z-10 bottom-full mb-2 right-0 w-48 p-2 text-xs text-white bg-gray-900 rounded-lg shadow-lg">
                {tooltip}
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center justify-between">
          <p className={`text-3xl font-bold ${actualColor === 'green' ? 'text-green-700' : 
            actualColor === 'amber' ? 'text-amber-700' : 
            actualColor === 'purple' ? 'text-purple-700' : 'text-blue-700'}`}>
            {value}
          </p>
          {trend && (
            <div className={`flex items-center ${
              trend === 'up' ? 'text-green-500' : 
              trend === 'down' ? 'text-red-500' : 'text-gray-400'
            }`}>
              {trend === 'up' && <ArrowUpIcon className="w-5 h-5" />}
              {trend === 'down' && <ArrowDownIcon className="w-5 h-5" />}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const TikTokAdLevelDashboard: React.FC = () => {
  const [adData, setAdData] = useState<TikTokAdData[]>([]);
  const [summary, setSummary] = useState<TikTokAdLevelSummary | null>(null);
  const [filterOptions, setFilterOptions] = useState<TikTokFilterOptions | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedAds, setExpandedAds] = useState<string[]>([]);
  const [filterPanelOpen, setFilterPanelOpen] = useState(true);
  const [kpiCollapsed, setKpiCollapsed] = useState(false);
  const [sortColumn, setSortColumn] = useState<string | null>('total_spend');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [isScrolled, setIsScrolled] = useState(false);

  // Filter states
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);

  // Scroll handling for KPI cards
  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      setIsScrolled(scrollY > 150);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // Check initial position
    
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Fetch data on component mount
  useEffect(() => {
    fetchData();
  }, [selectedCategories]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Build query parameters
      const params = new URLSearchParams();
      if (selectedCategories.length > 0) {
        params.append('categories', selectedCategories.join(','));
      }

      // Fetch ad-level data
      const adDataResponse = await fetch(`/api/tiktok-ad-reports/ad-data?${params.toString()}`);
      if (!adDataResponse.ok) {
        throw new Error(`Failed to fetch ad data: ${adDataResponse.status}`);
      }
      const adDataResult = await adDataResponse.json();

      // Fetch summary
      const summaryResponse = await fetch(`/api/tiktok-ad-reports/summary?${params.toString()}`);
      if (!summaryResponse.ok) {
        throw new Error(`Failed to fetch summary: ${summaryResponse.status}`);
      }
      const summaryResult = await summaryResponse.json();

      // Fetch filter options
      const filtersResponse = await fetch('/api/tiktok-ad-reports/filters');
      if (!filtersResponse.ok) {
        throw new Error(`Failed to fetch filters: ${filtersResponse.status}`);
      }
      const filtersResult = await filtersResponse.json();

      setAdData(adDataResult.grouped_ads || []);
      setSummary(summaryResult.summary || null);
      setFilterOptions(filtersResult.filters || null);

    } catch (err) {
      console.error('Error fetching TikTok ad data:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const syncData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/tiktok-ad-reports/sync-14-days', {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`Sync failed: ${response.status}`);
      }

      const result = await response.json();
      console.log('Sync result:', result);

      // Refresh data after sync
      setTimeout(() => {
        fetchData();
      }, 2000);

    } catch (err) {
      console.error('Error syncing TikTok ad data:', err);
      setError(err instanceof Error ? err.message : 'Sync failed');
    }
  };

  const toggleAdExpanded = (adName: string) => {
    setExpandedAds(prev => 
      prev.includes(adName) 
        ? prev.filter(name => name !== adName)
        : [...prev, adName]
    );
  };

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('desc');
    }
  };

  const handleCategoryChange = (category: string, checked: boolean) => {
    if (checked) {
      setSelectedCategories(prev => [...prev, category]);
    } else {
      setSelectedCategories(prev => prev.filter(c => c !== category));
    }
  };

  // Utility functions
  const formatCurrency = (value: number) => `$${Math.round(value).toLocaleString()}`;
  const formatDecimal = (value: number, decimals: number = 2) => value.toFixed(decimals);

  // Calculate week-over-week changes
  const calculateWeekOverWeekChange = (ad: TikTokAdData) => {
    if (!ad.weekly_periods || ad.weekly_periods.length < 2) {
      return { spendChange: null, roasChange: null };
    }

    // Sort periods by date (older first)
    const sortedPeriods = [...ad.weekly_periods].sort((a, b) => 
      new Date(a.reporting_starts).getTime() - new Date(b.reporting_starts).getTime()
    );

    const olderWeek = sortedPeriods[0];
    const newerWeek = sortedPeriods[1];

    // Calculate percentage changes
    const spendChange = olderWeek.spend > 0 
      ? ((newerWeek.spend - olderWeek.spend) / olderWeek.spend) * 100 
      : null;

    const roasChange = olderWeek.roas > 0 
      ? ((newerWeek.roas - olderWeek.roas) / olderWeek.roas) * 100 
      : null;

    return { spendChange, roasChange };
  };

  const formatChangeIndicator = (change: number | null, type: 'spend' | 'roas', hasInsufficientData: boolean = false) => {
    if (hasInsufficientData) {
      return (
        <span className="text-xs text-gray-400 ml-1 italic" title="Need 2+ weeks for momentum">
          --
        </span>
      );
    }
    
    if (change === null || Math.abs(change) < 1) {
      return null;
    }

    const isPositive = change > 0;
    const colorClass = isPositive ? 'text-green-600' : 'text-red-600';

    return (
      <span className={`text-xs font-medium ${colorClass} ml-1`}>
        {isPositive ? '+' : ''}{change.toFixed(0)}%
      </span>
    );
  };

  // Sort ad data
  const sortedAdData = React.useMemo(() => {
    if (!sortColumn) return adData;

    return [...adData].sort((a, b) => {
      let aVal: number;
      let bVal: number;

      switch (sortColumn) {
        case 'total_spend':
          aVal = a.total_spend;
          bVal = b.total_spend;
          break;
        case 'total_roas':
          aVal = a.total_roas;
          bVal = b.total_roas;
          break;
        case 'total_cpa':
          aVal = a.total_cpa;
          bVal = b.total_cpa;
          break;
        case 'total_cpc':
          aVal = a.total_cpc;
          bVal = b.total_cpc;
          break;
        default:
          return 0;
      }

      if (sortDirection === 'asc') {
        return aVal - bVal;
      } else {
        return bVal - aVal;
      }
    });
  }, [adData, sortColumn, sortDirection]);

  const tableHeaders = [
    { key: 'ad_name', label: 'Ad Name', align: 'left' as const },
    { key: 'total_spend', label: 'Spend', align: 'right' as const },
    { key: 'total_roas', label: 'ROAS', align: 'right' as const },
    { key: 'total_cpa', label: 'CPA', align: 'right' as const },
    { key: 'total_cpc', label: 'CPC', align: 'right' as const }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header 
        filterPanelOpen={filterPanelOpen}
        onFilterToggle={() => setFilterPanelOpen(!filterPanelOpen)}
        showFilters={false}
      />
        <div className="flex items-center justify-center h-64">
          <div className="text-lg text-gray-600">Loading TikTok ad data...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header 
        filterPanelOpen={filterPanelOpen}
        onFilterToggle={() => setFilterPanelOpen(!filterPanelOpen)}
        showFilters={false}
      />
        <div className="flex items-center justify-center h-64">
          <div className="text-lg text-red-600">Error: {error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        filterPanelOpen={filterPanelOpen}
        onFilterToggle={() => setFilterPanelOpen(!filterPanelOpen)}
        showFilters={false}
      />
      
      {/* Collapsible KPI Dashboard */}
      {summary && (
        <div className="bg-white border-b border-gray-200 p-6">
          {/* Toggle Header */}
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Performance Overview</h2>
            <button
              onClick={() => setKpiCollapsed(!kpiCollapsed)}
              className="flex items-center space-x-1 px-3 py-1 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors duration-200"
            >
              <span>{kpiCollapsed ? 'Show' : 'Hide'}</span>
              {kpiCollapsed ? (
                <ChevronRightIcon className="w-4 h-4" />
              ) : (
                <ChevronDownIcon className="w-4 h-4" />
              )}
            </button>
          </div>
          
          {/* KPI Cards */}
          <div className={`transition-all duration-300 ease-in-out ${
            kpiCollapsed 
              ? 'opacity-0 max-h-0 overflow-hidden transform -translate-y-2 pointer-events-none' 
              : 'opacity-100 max-h-full transform translate-y-0'
          }`}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <KPICard
                title="Total Spend"
                value={formatCurrency(summary.total_spend)}
                tooltip="Total ad spend across all TikTok ads"
                color="blue"
              />
              <KPICard
                title="ROAS"
                value={formatDecimal(summary.avg_roas)}
                tooltip="Return on Ad Spend - Revenue divided by Spend"
                color={summary.avg_roas >= 4 ? 'green' : summary.avg_roas >= 2 ? 'amber' : 'blue'}
              />
              <KPICard
                title="CPA"
                value={formatCurrency(summary.avg_cpa)}
                tooltip="Cost Per Acquisition - Spend divided by Purchases"
                color="purple"
              />
              <KPICard
                title="Ads Count"
                value={summary.ads_count.toLocaleString()}
                tooltip="Total number of TikTok ads with data"
                color="amber"
              />
            </div>
          </div>
        </div>
      )}

      <div className="flex h-screen">
        {/* Filter Sidebar */}
        <div className={`${filterPanelOpen ? 'w-80' : 'w-12'} bg-white border-r border-gray-200 transition-all duration-300 flex-shrink-0`}>
          <div className="p-4">
            <button
              onClick={() => setFilterPanelOpen(!filterPanelOpen)}
              className="flex items-center justify-between w-full text-left font-medium text-gray-900"
            >
              {filterPanelOpen && <span>Filters</span>}
              <ChevronRightIcon 
                className={`w-5 h-5 transition-transform ${filterPanelOpen ? 'rotate-90' : ''}`}
              />
            </button>

            {filterPanelOpen && (
              <div className="mt-6 space-y-6">
                {/* Sync Button */}
                <button
                  onClick={syncData}
                  disabled={loading}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Syncing...' : 'Sync 14 Days'}
                </button>

                {/* Category Filter */}
                {filterOptions?.categories && filterOptions.categories.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 mb-3">Category</h3>
                    <div className="space-y-2">
                      {filterOptions.categories.map((category) => (
                        <label key={category} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={selectedCategories.includes(category)}
                            onChange={(e) => handleCategoryChange(category, e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span className="ml-2 text-sm text-gray-700">{category}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}

                {/* Info about TikTok categorization */}
                <div className="text-xs text-gray-500 bg-blue-50 p-3 rounded-lg">
                  <p className="font-medium mb-1">💡 TikTok Ad Categorization</p>
                  <p>Categories are determined by ad names (not campaign names) since TikTok campaigns have broad names like "Play and Tumbling".</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-hidden">
          <div className="h-full overflow-auto">
            <div className="p-6">
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">
                    TikTok Ad Performance ({adData.length} ads)
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">
                    Individual ad performance with weekly momentum indicators
                  </p>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead>
                      <tr>
                        {tableHeaders.map((header) => (
                          <th
                            key={header.key}
                            className={`px-3 py-2 ${header.align === 'left' ? 'text-left' : 'text-right'} text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors bg-gray-50 sticky top-0 z-10 ${
                              header.key === 'ad_name' ? 'w-1/3' : 'w-auto'
                            }`}
                            onClick={() => header.key !== 'ad_name' && handleSort(header.key)}
                          >
                            <div className={`flex items-center space-x-1 ${header.align === 'left' ? 'justify-start' : 'justify-end'}`}>
                              <span>{header.label}</span>
                              {sortColumn === header.key && (
                                sortDirection === 'asc' ? 
                                <ArrowUpIcon className="w-4 h-4" /> : 
                                <ArrowDownIcon className="w-4 h-4" />
                              )}
                            </div>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {sortedAdData.map((ad) => {
                        const isExpanded = expandedAds.includes(ad.ad_name);
                        const rows: JSX.Element[] = [];

                        // Main ad row
                        rows.push(
                          <tr key={ad.ad_name} className="hover:bg-gray-50 transition-colors">
                            <td className="px-3 py-2 whitespace-nowrap">
                              <div className="flex items-center">
                                <button
                                  onClick={() => toggleAdExpanded(ad.ad_name)}
                                  className="mr-3 p-1 hover:bg-gray-200 rounded"
                                >
                                  {isExpanded ? 
                                    <ChevronDownIcon className="w-4 h-4" /> : 
                                    <ChevronRightIcon className="w-4 h-4" />
                                  }
                                </button>
                                <div>
                                  <div className="text-sm font-medium text-gray-900 max-w-xs truncate">
                                    {ad.ad_name}
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    {ad.category} • {ad.campaign_name}
                                  </div>
                                </div>
                              </div>
                            </td>
                            <td className="px-3 py-2 whitespace-nowrap text-right text-xs font-medium text-gray-900">
                              <div className="flex flex-col items-end">
                                <span>{formatCurrency(ad.total_spend)}</span>
                                {(() => {
                                  const changes = calculateWeekOverWeekChange(ad);
                                  const hasInsufficientData = !ad.weekly_periods || ad.weekly_periods.length < 2;
                                  return formatChangeIndicator(changes.spendChange, 'spend', hasInsufficientData);
                                })()}
                              </div>
                            </td>
                            <td className="px-3 py-2 whitespace-nowrap text-right text-xs text-gray-900">
                              <div className="flex flex-col items-end">
                                <span>{formatDecimal(ad.total_roas)}</span>
                                {(() => {
                                  const changes = calculateWeekOverWeekChange(ad);
                                  const hasInsufficientData = !ad.weekly_periods || ad.weekly_periods.length < 2;
                                  return formatChangeIndicator(changes.roasChange, 'roas', hasInsufficientData);
                                })()}
                              </div>
                            </td>
                            <td className="px-3 py-2 whitespace-nowrap text-right text-xs text-gray-900">
                              {formatCurrency(ad.total_cpa)}
                            </td>
                            <td className="px-3 py-2 whitespace-nowrap text-right text-xs text-gray-900">
                              ${formatDecimal(ad.total_cpc)}
                            </td>
                          </tr>
                        );

                        // Weekly period rows (only if expanded)
                        if (isExpanded && ad.weekly_periods) {
                          ad.weekly_periods.forEach((period, periodIndex) => {
                            const periodStart = new Date(period.reporting_starts).toLocaleDateString();
                            const periodEnd = new Date(period.reporting_ends).toLocaleDateString();
                            
                            rows.push(
                              <tr key={`${ad.ad_name}-period-${periodIndex}`} className="bg-blue-25 hover:bg-blue-50 transition-colors">
                                <td className="px-3 py-1 whitespace-nowrap pl-12">
                                  <span className="text-xs text-gray-600">
                                    {periodStart} - {periodEnd}
                                  </span>
                                </td>
                                <td className="px-3 py-1 whitespace-nowrap text-right text-xs text-gray-900">
                                  {formatCurrency(period.spend)}
                                </td>
                                <td className="px-3 py-1 whitespace-nowrap text-right text-xs text-gray-900">
                                  {formatDecimal(period.roas)}
                                </td>
                                <td className="px-3 py-1 whitespace-nowrap text-right text-xs text-gray-900">
                                  {formatCurrency(period.cpa)}
                                </td>
                                <td className="px-3 py-1 whitespace-nowrap text-right text-xs text-gray-900">
                                  ${formatDecimal(period.cpc)}
                                </td>
                              </tr>
                            );
                          });
                        }

                        return rows;
                      }).flat()}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TikTokAdLevelDashboard;