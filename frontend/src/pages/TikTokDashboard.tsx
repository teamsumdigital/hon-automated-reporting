import React, { useState, useEffect } from 'react';
import { 
  FunnelIcon, 
  ChevronRightIcon,
  ChevronDownIcon,
  InformationCircleIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline';

interface KPICardProps {
  title: string;
  value: string | number;
  tooltip: string;
  color?: 'blue' | 'green' | 'amber' | 'purple' | 'pink';
  trend?: 'up' | 'down' | 'neutral';
}

const KPICard: React.FC<KPICardProps> = ({ title, value, tooltip, color = 'pink', trend }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50 border-blue-200',
    green: 'text-green-600 bg-green-50 border-green-200',
    amber: 'text-amber-600 bg-amber-50 border-amber-200',
    purple: 'text-purple-600 bg-purple-50 border-purple-200',
    pink: 'text-pink-600 bg-pink-50 border-pink-200'
  };

  const getROASColor = (roasValue: number) => {
    if (roasValue >= 4) return 'green';
    if (roasValue >= 2) return 'amber';
    return 'pink';
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
            actualColor === 'purple' ? 'text-purple-700' : 
            actualColor === 'pink' ? 'text-pink-700' : 'text-blue-700'}`}>
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

const TikTokDashboard: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedMonths, setSelectedMonths] = useState<string[]>([]);
  const [expandedMonths, setExpandedMonths] = useState<string[]>([]);
  const [filterPanelOpen, setFilterPanelOpen] = useState(true);
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    fetchData();
  }, [selectedCategories]);

  const fetchData = () => {
    const categoryParams = selectedCategories.length > 0 
      ? `?categories=${selectedCategories.join(',')}` 
      : '';
    
    fetch(`https://hon-automated-reporting.onrender.com/api/tiktok-reports/dashboard${categoryParams}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching TikTok data:', error);
        setError(error.message);
        setLoading(false);
      });
  };

  const toggleCategory = (category: string) => {
    setSelectedCategories(prev => 
      prev.includes(category) 
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const toggleMonth = (month: string) => {
    setSelectedMonths(prev => 
      prev.includes(month) 
        ? prev.filter(m => m !== month)
        : [...prev, month]
    );
  };

  const toggleMonthExpansion = (monthName: string) => {
    setExpandedMonths(prev => 
      prev.includes(monthName) 
        ? prev.filter(m => m !== monthName)
        : [...prev, monthName]
    );
  };

  const clearAllFilters = () => {
    setSelectedCategories([]);
    setSelectedMonths([]);
  };

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('desc');
    }
  };

  // Group monthly data by month first, then years within each month
  const groupByMonthThenYear = (monthlyData: any[]) => {
    const grouped: { [month: string]: { [year: string]: any } } = {};
    
    monthlyData.forEach(monthData => {
      const [year, month] = monthData.month.split('-');
      const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 
                         'July', 'August', 'September', 'October', 'November', 'December'];
      const monthName = monthNames[parseInt(month) - 1];
      
      if (!grouped[monthName]) {
        grouped[monthName] = {};
      }
      grouped[monthName][year] = monthData;
    });
    
    return grouped;
  };

  const groupedData = groupByMonthThenYear(
    selectedMonths.length > 0 
      ? data?.pivot_data?.filter((month: any) => selectedMonths.includes(month.month)) || []
      : data?.pivot_data || []
  );

  const formatMonthDisplay = (monthString: string) => {
    try {
      const [year, month] = monthString.split('-');
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const monthIndex = parseInt(month) - 1;
      return `${monthNames[monthIndex]} ${year}`;
    } catch {
      return monthString;
    }
  };

  // Calculate filtered totals
  const calculateFilteredTotals = (categories: any[]) => {
    if (categories.length === 0) return null;
    
    const totalSpend = categories.reduce((sum: number, cat: any) => sum + (cat.spend || 0), 0);
    const totalClicks = categories.reduce((sum: number, cat: any) => sum + (cat.link_clicks || 0), 0);
    const totalPurchases = categories.reduce((sum: number, cat: any) => sum + (cat.purchases || 0), 0);
    const totalRevenue = categories.reduce((sum: number, cat: any) => sum + (cat.revenue || 0), 0);
    
    return {
      totalSpend,
      totalClicks,
      totalPurchases,
      totalRevenue,
      avgCPA: totalPurchases > 0 ? totalSpend / totalPurchases : 0,
      avgROAS: totalSpend > 0 ? totalRevenue / totalSpend : 0,
      avgCPC: totalClicks > 0 ? totalSpend / totalClicks : 0
    };
  };

  const filteredMonthlyData = selectedMonths.length > 0 
    ? data?.pivot_data?.filter((month: any) => selectedMonths.includes(month.month)) || []
    : data?.pivot_data || [];

  const currentTotals = selectedCategories.length > 0 || selectedMonths.length > 0
    ? calculateFilteredTotals(filteredMonthlyData)
    : data?.summary;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600 mx-auto mb-4"></div>
          <h1 className="text-2xl font-semibold text-gray-900 mb-2">House of Noa</h1>
          <p className="text-gray-600">Loading campaign data...</p>
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
            className="px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

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
              value={`$${Math.round(currentTotals?.totalSpend || currentTotals?.total_spend || 0).toLocaleString()}`}
              tooltip="Total amount spent on TikTok advertising campaigns"
              color="blue"
            />
            <KPICard
              title="Total Revenue"
              value={`$${Math.round(currentTotals?.totalRevenue || currentTotals?.total_revenue || 0).toLocaleString()}`}
              tooltip="Total revenue generated from TikTok advertising campaigns"
              color="green"
            />
            <KPICard
              title="ROAS"
              value={Number(currentTotals?.avgROAS || currentTotals?.avg_roas || 0).toFixed(2)}
              tooltip="Return on Ad Spend - Revenue divided by Ad Spend"
              color="amber"
            />
            <KPICard
              title="CPA"
              value={`$${(currentTotals?.avgCPA || currentTotals?.avg_cpa || 0).toFixed(2)}`}
              tooltip="Average cost per acquisition across TikTok campaigns"
              color="purple"
            />
          </div>

          {/* Table */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">TikTok Campaigns by Month</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    {['Month', 'Spend', 'Revenue', 'ROAS', 'CPA', 'CPC', 'CPM'].map((header, index) => (
                      <th
                        key={header}
                        className={`px-6 py-3 ${index === 0 ? 'text-left' : 'text-right'} text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors`}
                        onClick={() => handleSort(header.toLowerCase())}
                      >
                        <div className={`flex items-center space-x-1 ${index === 0 ? 'justify-start' : 'justify-end'}`}>
                          <span>{header}</span>
                          {sortColumn === header.toLowerCase() && (
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
                  {['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'].map(monthName => {
                    const yearsInMonth = groupedData[monthName];
                    if (!yearsInMonth || Object.keys(yearsInMonth).length === 0) return null;
                    
                    const sortedYears = Object.keys(yearsInMonth).sort((a, b) => parseInt(a) - parseInt(b));
                    const isExpanded = expandedMonths.includes(monthName);
                    const rows: JSX.Element[] = [];
                    
                    // Month header row
                    rows.push(
                      <tr key={`month-${monthName}`} className="bg-pink-50 hover:bg-pink-100 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center space-x-3">
                            <button
                              onClick={() => toggleMonthExpansion(monthName)}
                              className="flex items-center justify-center w-6 h-6 rounded hover:bg-pink-200 transition-colors"
                            >
                              {isExpanded ? 
                                <ChevronDownIcon className="w-4 h-4 text-pink-600" /> : 
                                <ChevronRightIcon className="w-4 h-4 text-pink-600" />
                              }
                            </button>
                            <span className="text-sm font-semibold text-gray-900">{monthName}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                          ${Math.round(sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].spend || 0), 0)).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          ${Math.round(sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].revenue || 0), 0)).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {(() => {
                            const totalSpend = sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].spend || 0), 0);
                            const totalRevenue = sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].revenue || 0), 0);
                            return totalSpend > 0 ? (totalRevenue / totalSpend).toFixed(1) : '0.0';
                          })()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          ${(() => {
                            const totalSpend = sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].spend || 0), 0);
                            const totalPurchases = sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].purchases || 0), 0);
                            return totalPurchases > 0 ? (totalSpend / totalPurchases).toFixed(2) : '0.00';
                          })()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          ${(() => {
                            const totalSpend = sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].spend || 0), 0);
                            const totalClicks = sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].link_clicks || 0), 0);
                            return totalClicks > 0 ? (totalSpend / totalClicks).toFixed(2) : '0.00';
                          })()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          ${(() => {
                            const totalSpend = sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].spend || 0), 0);
                            const totalImpressions = sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].impressions || 0), 0);
                            return totalImpressions > 0 ? (totalSpend / (totalImpressions / 1000)).toFixed(2) : '0.00';
                          })()}
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
                              ${Math.round(yearData.spend || 0).toLocaleString()}
                            </td>
                            <td className="px-6 py-3 whitespace-nowrap text-right text-sm text-gray-900">
                              ${Math.round(yearData.revenue || 0).toLocaleString()}
                            </td>
                            <td className="px-6 py-3 whitespace-nowrap text-right text-sm text-gray-900">
                              {(yearData.roas || 0).toFixed(1)}
                            </td>
                            <td className="px-6 py-3 whitespace-nowrap text-right text-sm text-gray-900">
                              ${(yearData.cpa || 0).toFixed(2)}
                            </td>
                            <td className="px-6 py-3 whitespace-nowrap text-right text-sm text-gray-900">
                              ${(yearData.cpc || 0).toFixed(2)}
                            </td>
                            <td className="px-6 py-3 whitespace-nowrap text-right text-sm text-gray-900">
                              ${(() => {
                                const cpm = (yearData.impressions || 0) > 0 ? 
                                  ((yearData.spend || 0) / ((yearData.impressions || 0) / 1000)) : 0;
                                return cpm.toFixed(2);
                              })()}
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
                {(selectedCategories.length > 0 || selectedMonths.length > 0) && (
                  <button
                    onClick={clearAllFilters}
                    className="text-sm text-pink-600 hover:text-pink-800 font-medium"
                  >
                    Clear All
                  </button>
                )}
              </div>
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto filter-sidebar-scroll">
              <div className="p-6 space-y-8">
                {/* Category Filters */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-3 sticky top-0 bg-white py-2 -my-2 z-10">Categories</h4>
                  <div className="space-y-2">
                    {data?.categories?.filter((category: string) => category !== 'Uncategorized').map((category: string) => (
                      <button
                        key={category}
                        onClick={() => toggleCategory(category)}
                        className={`w-full text-left px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                          selectedCategories.includes(category)
                            ? 'bg-pink-600 text-white shadow-md'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {category}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Month Filters */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-medium text-gray-700 sticky top-0 bg-white py-2 -my-2 z-10">Months</h4>
                    {data?.pivot_data && data.pivot_data.length > 8 && (
                      <span className="text-xs text-gray-400 italic">Scroll to see all</span>
                    )}
                  </div>
                  <div className="space-y-2 month-filter-container overflow-y-auto filter-sidebar-scroll relative">
                    {data?.pivot_data?.sort((a: any, b: any) => b.month.localeCompare(a.month)).map((month: any) => (
                      <button
                        key={month.month}
                        onClick={() => toggleMonth(month.month)}
                        className={`w-full text-left px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 flex items-center justify-between ${
                          selectedMonths.includes(month.month)
                            ? 'bg-pink-600 text-white shadow-md'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        <span>{formatMonthDisplay(month.month)}</span>
                        <span className="text-xs opacity-75">
                          {(month.roas || 0).toFixed(1)}x
                        </span>
                      </button>
                    ))}
                    
                    {/* Fade effect at bottom to indicate more content */}
                    {data?.pivot_data && data.pivot_data.length > 8 && (
                      <div className="absolute bottom-0 left-0 right-0 h-6 bg-gradient-to-t from-white to-transparent pointer-events-none"></div>
                    )}
                  </div>
                </div>
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

export default TikTokDashboard;