import React, { useState, useEffect } from 'react';
import { 
  FunnelIcon, 
  ChevronRightIcon,
  ChevronDownIcon,
  InformationCircleIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline';
import { 
  GoogleDashboardData, 
  GooglePivotTableData,
  googleAdsApi,
  formatGoogleCurrency,
  formatGoogleNumber,
  formatGoogleDecimal
} from '../services/googleApi';

interface KPICardProps {
  title: string;
  value: string | number;
  tooltip: string;
  color?: 'blue' | 'green' | 'amber' | 'purple';
  trend?: 'up' | 'down' | 'neutral';
}

const KPICard: React.FC<KPICardProps> = ({ title, value, tooltip, color = 'green', trend }) => {
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
              <div className="absolute right-0 top-6 z-10 w-64 p-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg">
                {tooltip}
              </div>
            )}
          </div>
        </div>
        
        <div className="flex items-baseline justify-between">
          <div className="text-2xl font-bold text-gray-900">{value}</div>
          {trend && (
            <div className={`
              flex items-center text-sm font-medium
              ${trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-500'}
            `}>
              {trend === 'up' && <ArrowUpIcon className="w-4 h-4 mr-1" />}
              {trend === 'down' && <ArrowDownIcon className="w-4 h-4 mr-1" />}
              {trend !== 'neutral' && trend}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};


const GoogleDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<GoogleDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedCampaignTypes, setSelectedCampaignTypes] = useState<string[]>([]);
  const [expandedMonths, setExpandedMonths] = useState<Set<string>>(new Set());
  const [filterPanelOpen, setFilterPanelOpen] = useState(true);
  const [selectedMonths, setSelectedMonths] = useState<string[]>([]);
  const [expandedTableMonths, setExpandedTableMonths] = useState<string[]>([]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params: any = {};
      // Categories filtering is now client-side only for fast response
      
      const data = await googleAdsApi.getDashboardData(params);
      setDashboardData(data);
    } catch (err) {
      console.error('Error fetching Google Ads dashboard data:', err);
      setError('Failed to load Google Ads dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []); // Remove selectedCategories dependency - use client-side filtering instead


  const handleCategoryToggle = (category: string) => {
    setSelectedCategories(prev => 
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const handleCampaignTypeToggle = (campaignType: string) => {
    setSelectedCampaignTypes(prev => 
      prev.includes(campaignType)
        ? prev.filter(ct => ct !== campaignType)
        : [...prev, campaignType]
    );
  };

  const handleMonthToggle = (month: string) => {
    setSelectedMonths(prev => 
      prev.includes(month)
        ? prev.filter(m => m !== month)
        : [...prev, month]
    );
  };

  const clearAllFilters = () => {
    setSelectedCategories([]);
    setSelectedCampaignTypes([]);
    setSelectedMonths([]);
  };

  const formatMonthDisplay = (monthString: string) => {
    try {
      const [year, month] = monthString.split('-');
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const monthIndex = parseInt(month) - 1; // Convert 1-based to 0-based
      return `${monthNames[monthIndex]} ${year}`;
    } catch {
      return monthString;
    }
  };

  // Group monthly data by month first, then years within each month (like Meta Ads)
  const groupByMonthThenYear = (monthlyData: any[]) => {
    const grouped: { [month: string]: { [year: string]: any } } = {};
    
    monthlyData.forEach(monthData => {
      const [year, month] = monthData.month.split('-');
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const monthName = monthNames[parseInt(month) - 1];
      
      if (!grouped[monthName]) {
        grouped[monthName] = {};
      }
      grouped[monthName][year] = monthData;
    });
    
    return grouped;
  };

  const handleTableMonthToggle = (monthName: string) => {
    setExpandedTableMonths(prev => 
      prev.includes(monthName) 
        ? prev.filter(m => m !== monthName)
        : [...prev, monthName]
    );
  };

  const toggleMonth = (month: string) => {
    setExpandedMonths(prev => {
      const newSet = new Set(prev);
      if (newSet.has(month)) {
        newSet.delete(month);
      } else {
        newSet.add(month);
      }
      return newSet;
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-4"></div>
          <h1 className="text-2xl font-semibold text-gray-900 mb-2">House of Noa</h1>
          <p className="text-gray-600">Loading campaign data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-lg font-medium mb-2">Error</div>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={fetchDashboardData}
            className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">No Google Ads data available</p>
      </div>
    );
  }

  // Client-side filtering for fast performance (like Meta Ads)
  const allCampaigns = dashboardData?.campaigns || [];
  
  // Apply category filtering first
  let filteredCampaigns = selectedCategories.length > 0
    ? allCampaigns.filter(campaign => selectedCategories.includes(campaign.category || ''))
    : allCampaigns;
  
  // Apply campaign type filtering
  filteredCampaigns = selectedCampaignTypes.length > 0
    ? filteredCampaigns.filter(campaign => selectedCampaignTypes.includes(campaign.campaign_type || ''))
    : filteredCampaigns;
    
  // Calculate filtered pivot data from campaigns when any filters are selected
  let filteredPivotData = dashboardData.pivot_data;
  
  if (selectedCategories.length > 0 || selectedCampaignTypes.length > 0) {
    // Recalculate pivot data from filtered campaigns
    const monthlyData: { [month: string]: any } = {};
    
    filteredCampaigns.forEach(campaign => {
      const monthKey = campaign.reporting_starts.substring(0, 7); // YYYY-MM format
      
      if (!monthlyData[monthKey]) {
        monthlyData[monthKey] = {
          month: monthKey,
          spend: 0,
          link_clicks: 0,
          purchases: 0,
          revenue: 0
        };
      }
      
      monthlyData[monthKey].spend += campaign.amount_spent_usd;
      monthlyData[monthKey].link_clicks += campaign.link_clicks;
      monthlyData[monthKey].purchases += campaign.website_purchases;
      monthlyData[monthKey].revenue += campaign.purchases_conversion_value;
    });
    
    // Convert to pivot data format with calculated metrics
    filteredPivotData = Object.values(monthlyData).map((data: any) => ({
      month: data.month,
      spend: data.spend,
      link_clicks: data.link_clicks,
      purchases: data.purchases,
      revenue: data.revenue,
      cpa: data.purchases > 0 ? data.spend / data.purchases : 0,
      roas: data.spend > 0 ? data.revenue / data.spend : 0,
      cpc: data.link_clicks > 0 ? data.spend / data.link_clicks : 0
    }));
  }
  
  // Apply month filtering
  if (selectedMonths.length > 0) {
    filteredPivotData = filteredPivotData.filter(item => selectedMonths.includes(item.month));
  }

  // Group the filtered data by month/year
  const groupedData = groupByMonthThenYear(filteredPivotData);

  // Calculate filtered summary if any filters are selected
  const displaySummary = (selectedCategories.length > 0 || selectedCampaignTypes.length > 0 || selectedMonths.length > 0)
    ? {
        ...dashboardData.summary,
        period: (selectedCategories.length > 0 || selectedCampaignTypes.length > 0) ? "Filtered" : dashboardData.summary.period,
        total_spend: filteredPivotData.reduce((sum, item) => sum + parseFloat(item.spend.toString()), 0),
        total_clicks: filteredPivotData.reduce((sum, item) => sum + item.link_clicks, 0),
        total_purchases: filteredPivotData.reduce((sum, item) => sum + item.purchases, 0),
        total_revenue: filteredPivotData.reduce((sum, item) => sum + parseFloat(item.revenue.toString()), 0),
        avg_cpa: filteredPivotData.length > 0 ? filteredPivotData.reduce((sum, item) => sum + parseFloat(item.cpa.toString()), 0) / filteredPivotData.length : 0,
        avg_roas: filteredPivotData.length > 0 ? filteredPivotData.reduce((sum, item) => sum + parseFloat(item.roas.toString()), 0) / filteredPivotData.length : 0,
        avg_cpc: filteredPivotData.length > 0 ? filteredPivotData.reduce((sum, item) => sum + parseFloat(item.cpc.toString()), 0) / filteredPivotData.length : 0,
        campaigns_count: (selectedCategories.length > 0 || selectedCampaignTypes.length > 0) ? filteredCampaigns.length : dashboardData.summary.campaigns_count
      }
    : dashboardData.summary;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <img 
              src="/house-of-noa-logo.png" 
              alt="House of Noa" 
              className="h-6 w-auto"
            />
          </div>
          <button
            onClick={() => setFilterPanelOpen(!filterPanelOpen)}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <FunnelIcon className="w-5 h-5 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Filters</span>
            {filterPanelOpen ? 
              <ChevronRightIcon className="w-4 h-4 text-gray-500" /> :
              <ChevronDownIcon className="w-4 h-4 text-gray-500" />
            }
          </button>
        </div>
      </div>

      <div className="flex">
        {/* Main Content */}
        <div className={`flex-1 p-6 transition-all duration-300 ${filterPanelOpen ? 'mr-80' : 'mr-0'}`}>
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <KPICard
              title="Total Spend"
              value={formatGoogleCurrency(displaySummary.total_spend)}
              tooltip="Total amount spent on Google Ads campaigns"
              color="blue"
            />
            <KPICard
              title="Total Revenue"
              value={formatGoogleCurrency(displaySummary.total_revenue)}
              tooltip="Total revenue generated from Google Ads campaigns"
              color="green"
            />
            <KPICard
              title="ROAS"
              value={formatGoogleDecimal(displaySummary.avg_roas, 2)}
              tooltip="Return on Ad Spend - Revenue divided by Ad Spend"
              color="amber"
            />
            <KPICard
              title="Total Purchases"
              value={formatGoogleNumber(displaySummary.total_purchases)}
              tooltip="Total number of purchases attributed to Google Ads"
              color="purple"
            />
          </div>

          {/* Table */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Google Ads Campaigns by Month</h2>
            </div>
          
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    {['Month', 'Spend', 'Clicks', 'Conversions', 'Revenue', 'CPA', 'ROAS', 'CPC'].map((header, index) => (
                      <th
                        key={header}
                        className={`px-6 py-3 ${index === 0 ? 'text-left' : 'text-right'} text-xs font-medium text-gray-500 uppercase tracking-wider`}
                      >
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].map(monthName => {
                    const yearsInMonth = groupedData[monthName] || {};
                    
                    // If months are filtered and this month has no data, don't show it
                    if (selectedMonths.length > 0 && Object.keys(yearsInMonth).length === 0) {
                      return null;
                    }
                    
                    const sortedYears = Object.keys(yearsInMonth).sort((a, b) => parseInt(a) - parseInt(b)); // Ascending years (2024 before 2025)
                    const isExpanded = expandedTableMonths.includes(monthName);
                    const rows: JSX.Element[] = [];
                    
                    // Month header row (aggregated data)
                    const totalSpend = sortedYears.length > 0 ? sortedYears.reduce((sum, year) => sum + parseFloat(yearsInMonth[year].spend), 0) : 0;
                    const totalClicks = sortedYears.length > 0 ? sortedYears.reduce((sum, year) => sum + yearsInMonth[year].link_clicks, 0) : 0;
                    const totalPurchases = sortedYears.length > 0 ? sortedYears.reduce((sum, year) => sum + yearsInMonth[year].purchases, 0) : 0;
                    const totalRevenue = sortedYears.length > 0 ? sortedYears.reduce((sum, year) => sum + parseFloat(yearsInMonth[year].revenue), 0) : 0;
                    const avgCPA = totalPurchases > 0 ? totalSpend / totalPurchases : 0;
                    const avgROAS = totalSpend > 0 ? totalRevenue / totalSpend : 0;
                    const avgCPC = totalClicks > 0 ? totalSpend / totalClicks : 0;
                    
                    rows.push(
                      <tr key={`month-${monthName}`} className="bg-green-50 hover:bg-green-100 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center space-x-3">
                            <button
                              onClick={() => handleTableMonthToggle(monthName)}
                              className="flex items-center justify-center w-6 h-6 rounded hover:bg-green-200 transition-colors"
                            >
                              {isExpanded ? 
                                <ChevronDownIcon className="w-4 h-4 text-green-600" /> : 
                                <ChevronRightIcon className="w-4 h-4 text-green-600" />
                              }
                            </button>
                            <span className="text-sm font-semibold text-gray-900">{monthName}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                          ${Math.round(totalSpend).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {totalClicks.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {totalPurchases.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          ${Math.round(totalRevenue).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          ${avgCPA.toFixed(2)}
                        </td>
                        <td className={`px-6 py-4 whitespace-nowrap text-right text-sm font-medium ${
                          avgROAS >= 4 ? 'text-green-600' : 
                          avgROAS >= 2 ? 'text-amber-600' : 'text-gray-900'
                        }`}>
                          {avgROAS.toFixed(1)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          ${avgCPC.toFixed(2)}
                        </td>
                      </tr>
                    );
                    
                    // Year detail rows (only if expanded)
                    if (isExpanded) {
                      sortedYears.forEach(year => {
                        const yearData = yearsInMonth[year];
                        rows.push(
                          <tr key={`${monthName}-${year}`} className="hover:bg-gray-50 transition-colors">
                            <td className="px-6 py-3 whitespace-nowrap pl-16">
                              <span className="text-sm text-gray-600">{year}</span>
                            </td>
                            <td className="px-6 py-3 whitespace-nowrap text-right text-sm text-gray-900">
                              ${Math.round(parseFloat(yearData.spend)).toLocaleString()}
                            </td>
                            <td className="px-6 py-3 whitespace-nowrap text-right text-sm text-gray-900">
                              {yearData.link_clicks.toLocaleString()}
                            </td>
                            <td className="px-6 py-3 whitespace-nowrap text-right text-sm text-gray-900">
                              {yearData.purchases.toLocaleString()}
                            </td>
                            <td className="px-6 py-3 whitespace-nowrap text-right text-sm text-gray-900">
                              ${Math.round(parseFloat(yearData.revenue)).toLocaleString()}
                            </td>
                            <td className="px-6 py-3 whitespace-nowrap text-right text-sm text-gray-900">
                              ${parseFloat(yearData.cpa).toFixed(2)}
                            </td>
                            <td className={`px-6 py-3 whitespace-nowrap text-right text-sm font-medium ${
                              parseFloat(yearData.roas) >= 4 ? 'text-green-600' : 
                              parseFloat(yearData.roas) >= 2 ? 'text-amber-600' : 'text-gray-900'
                            }`}>
                              {parseFloat(yearData.roas).toFixed(1)}
                            </td>
                            <td className="px-6 py-3 whitespace-nowrap text-right text-sm text-gray-900">
                              ${parseFloat(yearData.cpc).toFixed(2)}
                            </td>
                          </tr>
                        );
                      });
                    }
                    
                    return rows;
                  }).filter(rows => rows !== null)}
                </tbody>
              </table>
            </div>
            
            {filteredPivotData.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500">No Google Ads data available for the selected filters.</p>
              </div>
            )}
          </div>
        </div>

        {/* Filter Sidebar */}
        <div className={`fixed right-0 top-0 h-full w-80 bg-white border-l border-gray-200 shadow-lg transform transition-transform duration-300 z-40 ${
          filterPanelOpen ? 'translate-x-0' : 'translate-x-full'
        }`}>
          <div className="flex flex-col h-full">
            {/* Fixed Header */}
            <div className="flex-shrink-0 p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
                {(selectedCategories.length > 0 || selectedCampaignTypes.length > 0 || selectedMonths.length > 0) && (
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
            <div className="flex-1 overflow-y-auto filter-scroll">
              <div className="p-6 space-y-8">
                {/* Category Filters */}
                {dashboardData?.categories && dashboardData.categories.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-3 sticky top-0 bg-white py-2 -my-2 z-10">Categories</h4>
                    <div className="space-y-2">
                      {dashboardData.categories.filter((category: string) => category !== 'Uncategorized').map((category: string) => (
                        <button
                          key={category}
                          onClick={() => handleCategoryToggle(category)}
                          className={`w-full text-left px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                            selectedCategories.includes(category)
                              ? 'bg-green-600 text-white shadow-md'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {category}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Campaign Type Filters */}
                {dashboardData?.campaign_types && dashboardData.campaign_types.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-3 sticky top-0 bg-white py-2 -my-2 z-10">Campaign Types</h4>
                    <div className="space-y-2">
                      {dashboardData.campaign_types.filter((campaignType: string) => campaignType !== 'Unclassified').map((campaignType: string) => (
                        <button
                          key={campaignType}
                          onClick={() => handleCampaignTypeToggle(campaignType)}
                          className={`w-full text-left px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                            selectedCampaignTypes.includes(campaignType)
                              ? 'bg-blue-600 text-white shadow-md'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {campaignType}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Month Filters */}
                {dashboardData.pivot_data && dashboardData.pivot_data.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-medium text-gray-700 sticky top-0 bg-white py-2 -my-2 z-10">Months</h4>
                      {dashboardData.pivot_data.length > 8 && (
                        <span className="text-xs text-gray-400 italic">Scroll to see all</span>
                      )}
                    </div>
                    <div className="space-y-2 max-h-[16rem] overflow-y-auto filter-scroll">
                      {dashboardData.pivot_data
                        .slice()
                        .sort((a, b) => b.month.localeCompare(a.month))
                        .map((monthData: any) => (
                        <button
                          key={monthData.month}
                          onClick={() => handleMonthToggle(monthData.month)}
                          className={`w-full text-left px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 flex items-center justify-between ${
                            selectedMonths.includes(monthData.month)
                              ? 'bg-green-600 text-white shadow-md'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          <span>{formatMonthDisplay(monthData.month)}</span>
                          <span className="text-xs opacity-75">
                            {(parseFloat(monthData.roas) || 0).toFixed(1)}x
                          </span>
                        </button>
                      ))}
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

export default GoogleDashboard;