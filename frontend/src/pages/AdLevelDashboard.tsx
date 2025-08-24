import React, { useState, useEffect } from 'react';
import { 
  ChevronRightIcon,
  ChevronDownIcon,
  InformationCircleIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ChevronUpIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '../services/api';
import { AdData, AdLevelSummary, FilterOptions, AdLevelFilters } from '../types/adLevel';
import Header from '../components/Header';

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

const AdLevelDashboard: React.FC = () => {
  const [adData, setAdData] = useState<AdData[]>([]);
  const [summary, setSummary] = useState<AdLevelSummary | null>(null);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
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
  const [selectedContentTypes, setSelectedContentTypes] = useState<string[]>([]);
  const [selectedFormats, setSelectedFormats] = useState<string[]>([]);
  const [selectedCampaignOptimizations, setSelectedCampaignOptimizations] = useState<string[]>([]);

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    fetchAdData();
  }, [selectedCategories, selectedContentTypes, selectedFormats, selectedCampaignOptimizations]);

  // Scroll detection for hiding KPI cards
  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      setIsScrolled(scrollY > 150);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // Check initial position
    
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const fetchInitialData = async () => {
    try {
      const [filtersResponse] = await Promise.all([
        apiClient.getAdLevelFilters()
      ]);
      
      setFilterOptions(filtersResponse);
    } catch (err) {
      console.error('Error fetching initial data:', err);
      setError('Failed to load filter options');
    }
  };

  const fetchAdData = async () => {
    try {
      const filters: any = {};
      
      if (selectedCategories.length > 0) {
        filters.categories = selectedCategories.join(',');
      }
      if (selectedContentTypes.length > 0) {
        filters.content_types = selectedContentTypes.join(',');
      }
      if (selectedFormats.length > 0) {
        filters.formats = selectedFormats.join(',');
      }
      if (selectedCampaignOptimizations.length > 0) {
        filters.campaign_optimizations = selectedCampaignOptimizations.join(',');
      }

      const [adDataResponse, summaryResponse] = await Promise.all([
        apiClient.getAdLevelData(filters),
        apiClient.getAdLevelSummary(filters)
      ]);

      setAdData(adDataResponse.grouped_ads || []);
      setSummary(summaryResponse);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching ad data:', err);
      setError('Failed to load ad data');
      setLoading(false);
    }
  };

  const toggleAdExpansion = (adName: string) => {
    setExpandedAds(prev => 
      prev.includes(adName) 
        ? prev.filter(name => name !== adName)
        : [...prev, adName]
    );
  };

  const toggleFilter = (filterType: 'categories' | 'content_types' | 'formats' | 'campaign_optimizations', value: string) => {
    const setters = {
      categories: setSelectedCategories,
      content_types: setSelectedContentTypes,
      formats: setSelectedFormats,
      campaign_optimizations: setSelectedCampaignOptimizations
    };

    const currentValues = {
      categories: selectedCategories,
      content_types: selectedContentTypes,
      formats: selectedFormats,
      campaign_optimizations: selectedCampaignOptimizations
    };

    const setter = setters[filterType];
    const current = currentValues[filterType];

    setter(prev => 
      prev.includes(value) 
        ? prev.filter(v => v !== value)
        : [...prev, value]
    );
  };

  const clearAllFilters = () => {
    setSelectedCategories([]);
    setSelectedContentTypes([]);
    setSelectedFormats([]);
    setSelectedCampaignOptimizations([]);
  };

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('desc');
    }
  };

  // Status management for color coding
  const getNextStatus = (currentStatus: string | null | undefined): string | null => {
    const statusCycle = [null, 'winner', 'considering', 'paused', 'paused_last_week'];
    const currentIndex = statusCycle.indexOf(currentStatus || null);
    const nextIndex = (currentIndex + 1) % statusCycle.length;
    return statusCycle[nextIndex];
  };

  const getRowColorClass = (status: string | null | undefined): string => {
    switch (status) {
      case 'winner':
        return 'bg-green-100 hover:bg-green-200';
      case 'considering':
        return 'bg-yellow-100 hover:bg-yellow-200';
      case 'paused':
        return 'bg-red-100 hover:bg-red-200';
      case 'paused_last_week':
        return 'bg-gray-100 hover:bg-gray-200';
      default:
        return 'hover:bg-gray-50';
    }
  };

  const handleRowClick = async (adName: string, currentStatus: string | null | undefined) => {
    console.log('🔄 Row clicked:', adName, 'Current status:', currentStatus);
    const nextStatus = getNextStatus(currentStatus);
    console.log('🎯 Next status:', nextStatus);
    
    try {
      console.log('📡 Calling updateAdStatus API...');
      const result = await apiClient.updateAdStatus(adName, nextStatus);
      console.log('✅ API result:', result);
      
      // Update local state immediately for responsive UI
      setAdData(prevData => 
        prevData.map(ad => 
          ad.ad_name === adName 
            ? { ...ad, status: nextStatus }
            : ad
        )
      );
      console.log('🔄 Local state updated');
    } catch (error) {
      console.error('❌ Failed to update ad status:', error);
      console.error('Error details:', (error as any)?.response?.data || (error as Error)?.message);
      // Could add toast notification here
    }
  };

  const sortedAdData = React.useMemo(() => {
    if (!sortColumn) return adData;

    return [...adData].sort((a, b) => {
      let aValue: number;
      let bValue: number;

      switch (sortColumn) {
        case 'total_spend':
          aValue = a.total_spend;
          bValue = b.total_spend;
          break;
        case 'total_roas':
          aValue = a.total_roas;
          bValue = b.total_roas;
          break;
        case 'total_cpa':
          aValue = a.total_cpa;
          bValue = b.total_cpa;
          break;
        case 'total_cpc':
          aValue = a.total_cpc;
          bValue = b.total_cpc;
          break;
        case 'days_live':
          aValue = a.days_live;
          bValue = b.days_live;
          break;
        default:
          return 0;
      }

      if (sortDirection === 'asc') {
        return aValue - bValue;
      } else {
        return bValue - aValue;
      }
    });
  }, [adData, sortColumn, sortDirection]);

  const formatCurrency = (value: number) => `$${Math.round(value).toLocaleString()}`;
  const formatDecimal = (value: number, decimals: number = 2) => value.toFixed(decimals);

  // Calculate week-over-week changes
  const calculateWeekOverWeekChange = (ad: AdData) => {
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h1 className="text-2xl font-semibold text-gray-900 mb-2">House of Noa</h1>
          <p className="text-gray-600">Loading ad-level data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="bg-red-100 rounded-full p-3 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <InformationCircleIcon className="w-8 h-8 text-red-600" />
          </div>
          <h1 className="text-2xl font-semibold text-gray-900 mb-2">House of Noa</h1>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <h3 className="text-sm font-medium text-red-800 mb-1">Error loading data</h3>
            <p className="text-sm text-red-700">{error}</p>
          </div>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        filterPanelOpen={filterPanelOpen}
        onFilterToggle={() => setFilterPanelOpen(!filterPanelOpen)}
        kpiCollapsed={kpiCollapsed}
        onKpiToggle={() => setKpiCollapsed(!kpiCollapsed)}
      />

      <div className="flex">
        {/* Main Content */}
        <div className={`flex-1 p-6 transition-all duration-300 ${filterPanelOpen ? 'mr-80' : 'mr-0'}`}>
          {/* Collapsible KPI Dashboard */}
          <div className={`transition-all duration-300 ease-in-out overflow-hidden ${
            kpiCollapsed ? 'max-h-0' : 'max-h-96 mb-1'
          }`}>
            {/* KPI Cards */}
            <div className={`transition-all duration-300 ease-in-out ${
              kpiCollapsed 
                ? 'transform -translate-y-4 opacity-0' 
                : 'transform translate-y-0 opacity-100 mb-2'
            }`}>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <KPICard
                  title="Total Spend"
                  value={formatCurrency(summary?.total_spend || 0)}
                  tooltip="Total amount spent on Meta ads for the selected period"
                  color="blue"
                />
                <KPICard
                  title="Total Revenue"
                  value={formatCurrency(summary?.total_revenue || 0)}
                  tooltip="Total revenue generated from Meta ads for the selected period"
                  color="green"
                />
                <KPICard
                  title="ROAS"
                  value={Number(summary?.avg_roas || 0).toFixed(2)}
                  tooltip="Return on Ad Spend - Revenue divided by Ad Spend"
                  color="amber"
                />
                <KPICard
                  title="CPA"
                  value={formatCurrency(summary?.avg_cpa || 0)}
                  tooltip="Average cost per acquisition across all ads"
                  color="purple"
                />
              </div>
            </div>
            
          </div>

          {/* Table */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden max-h-[80vh]">
            <div className="px-4 py-3 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-semibold text-gray-900">Ad-Level Performance</h2>
                  <p className="text-xs text-gray-500">
                    {adData.length} ads • Click to expand weekly breakdown
                  </p>
                </div>
                
                {/* Color Key */}
                <div className="flex items-center space-x-4">
                  <span className="text-xs font-medium text-gray-700">Key:</span>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-green-500 rounded"></div>
                    <span className="text-xs text-gray-700">Winner</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-yellow-500 rounded"></div>
                    <span className="text-xs text-gray-700">Considering</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-red-500 rounded"></div>
                    <span className="text-xs text-gray-700">Paused</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-gray-500 rounded"></div>
                    <span className="text-xs text-gray-700">Paused last week</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="overflow-auto max-h-[70vh]">
              <table className="w-full">
                <thead className="bg-gray-50 sticky top-0 z-10">
                  <tr>
                    {[
                      { key: 'ad_name', label: 'Ad Name', align: 'left' },
                      { key: 'total_spend', label: 'Spend', align: 'right' },
                      { key: 'total_roas', label: 'ROAS', align: 'right' },
                      { key: 'total_cpa', label: 'CPA', align: 'right' },
                      { key: 'total_cpc', label: 'CPC', align: 'right' },
                      { key: 'days_live', label: 'Days Live', align: 'right' }
                    ].map((header, index) => (
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
                      <tr 
                        key={ad.ad_name} 
                        className={`transition-colors cursor-pointer ${getRowColorClass(ad.status)}`}
                        onClick={() => handleRowClick(ad.ad_name, ad.status)}
                      >
                        <td className="px-4 py-2 whitespace-nowrap w-1/3">
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleAdExpansion(ad.ad_name);
                              }}
                              className="flex items-center justify-center w-5 h-5 rounded hover:bg-gray-200 transition-colors"
                            >
                              {isExpanded ? 
                                <ChevronDownIcon className="w-3 h-3 text-gray-600" /> : 
                                <ChevronRightIcon className="w-3 h-3 text-gray-600" />
                              }
                            </button>
                            {ad.thumbnail_url ? (
                              <img 
                                src={ad.thumbnail_url} 
                                alt={ad.ad_name}
                                className="w-8 h-8 rounded object-cover border border-gray-200"
                                onError={(e) => {
                                  e.currentTarget.style.display = 'none';
                                }}
                              />
                            ) : (
                              <div className="w-8 h-8 rounded bg-gray-100 border border-gray-200 flex items-center justify-center">
                                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                              </div>
                            )}
                            <div className="min-w-0 max-w-xs">
                              <p className="text-xs font-medium text-gray-900 truncate">{ad.ad_name}</p>
                              <p className="text-xs text-gray-500">{ad.category}</p>
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
                        <td className="px-3 py-2 whitespace-nowrap text-right text-xs text-gray-900">
                          {ad.days_live}
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
                            <td className="px-3 py-1 whitespace-nowrap text-right text-xs text-gray-500">
                              -
                            </td>
                          </tr>
                        );
                      });
                    }
                    
                    return rows;
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Filter Sidebar */}
        <div className={`fixed right-0 top-0 h-full w-80 bg-white border-l border-gray-200 shadow-lg transform transition-transform duration-300 z-40 ${
          filterPanelOpen ? 'translate-x-0' : 'translate-x-full'
        }`}>
          <div className="flex flex-col h-full">
            {/* Fixed Header */}
            <div className="flex-shrink-0 p-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
                {(selectedCategories.length > 0 || selectedContentTypes.length > 0 || 
                  selectedFormats.length > 0 || selectedCampaignOptimizations.length > 0) && (
                  <button
                    onClick={clearAllFilters}
                    className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                  >
                    Clear All
                  </button>
                )}
              </div>
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto filter-sidebar-scroll">
              <div className="p-6 space-y-8">
                {/* Category Filter */}
                {filterOptions?.categories && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Category</h4>
                    <div className="space-y-2 max-h-64 overflow-y-auto relative">
                      {filterOptions.categories.map((category) => (
                        <button
                          key={category}
                          onClick={() => toggleFilter('categories', category)}
                          className={`w-full text-left px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                            selectedCategories.includes(category)
                              ? 'bg-blue-600 text-white shadow-md'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {category}
                        </button>
                      ))}
                      
                      {/* Fade effect for categories */}
                      {filterOptions.categories.length > 6 && (
                        <div className="absolute bottom-0 left-0 right-0 h-6 bg-gradient-to-t from-white to-transparent pointer-events-none"></div>
                      )}
                    </div>
                  </div>
                )}

                {/* Content Type Filter */}
                {filterOptions?.content_types && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Content Type</h4>
                    <div className="space-y-2 max-h-48 overflow-y-auto relative">
                      {filterOptions.content_types.map((contentType) => (
                        <button
                          key={contentType}
                          onClick={() => toggleFilter('content_types', contentType)}
                          className={`w-full text-left px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                            selectedContentTypes.includes(contentType)
                              ? 'bg-green-600 text-white shadow-md'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {contentType}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Format Filter */}
                {filterOptions?.formats && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Format</h4>
                    <div className="space-y-2 max-h-32 overflow-y-auto relative">
                      {filterOptions.formats.map((format) => (
                        <button
                          key={format}
                          onClick={() => toggleFilter('formats', format)}
                          className={`w-full text-left px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                            selectedFormats.includes(format)
                              ? 'bg-amber-600 text-white shadow-md'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {format}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Campaign Optimization Filter */}
                {filterOptions?.campaign_optimizations && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Campaign Optimization</h4>
                    <div className="space-y-2 max-h-48 overflow-y-auto relative">
                      {filterOptions.campaign_optimizations.map((optimization) => (
                        <button
                          key={optimization}
                          onClick={() => toggleFilter('campaign_optimizations', optimization)}
                          className={`w-full text-left px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                            selectedCampaignOptimizations.includes(optimization)
                              ? 'bg-purple-600 text-white shadow-md'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {optimization}
                        </button>
                      ))}
                      
                      {/* Fade effect for campaign optimization - this is the critical one! */}
                      {filterOptions.campaign_optimizations.length > 4 && (
                        <div className="absolute bottom-0 left-0 right-0 h-6 bg-gradient-to-t from-white to-transparent pointer-events-none"></div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Overlay for mobile */}
        {filterPanelOpen && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
            onClick={() => setFilterPanelOpen(false)}
          />
        )}
      </div>
    </div>
  );
};

export default AdLevelDashboard;