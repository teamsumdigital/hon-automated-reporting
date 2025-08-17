import React, { useState, useEffect } from 'react';

const MonthlyReporting: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);

  useEffect(() => {
    fetchData();
  }, [selectedCategories]);

  const fetchData = () => {
    const categoryParams = selectedCategories.length > 0 
      ? `?categories=${selectedCategories.join(',')}` 
      : '';
    
    fetch(`/api/reports/monthly${categoryParams}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Monthly data:', data);
        setData(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching monthly data:', error);
        setError(error.message);
        setLoading(false);
      });
  };

  // Helper functions for filtering
  const toggleCategory = (category: string) => {
    setSelectedCategories(prev => 
      prev.includes(category) 
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const clearFilters = () => {
    setSelectedCategories([]);
  };

  // Filter data based on selected months (for future enhancement)
  const [selectedMonths, setSelectedMonths] = useState<string[]>([]);
  
  const toggleMonth = (month: string) => {
    setSelectedMonths(prev => 
      prev.includes(month) 
        ? prev.filter(m => m !== month)
        : [...prev, month]
    );
  };

  const clearMonthFilters = () => {
    setSelectedMonths([]);
  };

  // Helper function to format month display
  const formatMonthDisplay = (monthString: string) => {
    try {
      const [year, month] = monthString.split('-');
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const monthIndex = parseInt(month) - 1;
      return `${monthNames[monthIndex]} ${year}`;
    } catch {
      return monthString; // fallback to original if parsing fails
    }
  };

  // Group monthly data by month first, then years within each month
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

  // Filter monthly data
  const filteredMonthlyData = data?.monthly_breakdown?.filter((month: any) => 
    selectedMonths.length === 0 || selectedMonths.includes(month.month)
  ) || [];

  // Create grouped structure for display
  const groupedData = groupByMonthThenYear(
    selectedMonths.length > 0 ? filteredMonthlyData : data?.monthly_breakdown || []
  );

  // State for expanded months
  const [expandedMonths, setExpandedMonths] = useState<string[]>([]);

  const toggleMonthExpansion = (monthName: string) => {
    setExpandedMonths(prev => 
      prev.includes(monthName) 
        ? prev.filter(m => m !== monthName)
        : [...prev, monthName]
    );
  };

  // Calculate totals for filtered months
  const calculateFilteredTotals = (months: any[]) => {
    if (months.length === 0) return null;
    
    const totalSpend = months.reduce((sum: number, month: any) => sum + (month.amount_spent_usd || 0), 0);
    const totalClicks = months.reduce((sum: number, month: any) => sum + (month.link_clicks || 0), 0);
    const totalPurchases = months.reduce((sum: number, month: any) => sum + (month.website_purchases || 0), 0);
    const totalRevenue = months.reduce((sum: number, month: any) => sum + (month.purchases_conversion_value || 0), 0);
    
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

  // Get current totals (filtered or unfiltered)
  const currentTotals = selectedMonths.length > 0 
    ? calculateFilteredTotals(filteredMonthlyData)
    : data?.summary;

  if (loading) {
    return (
      <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
        <h1>House of Noa - Meta Campaigns by Month</h1>
        <p>Loading monthly data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
        <h1>House of Noa - Meta Campaigns by Month</h1>
        <div style={{ background: '#ffebee', padding: '10px', borderRadius: '4px', color: '#c62828' }}>
          <h3>Error loading data:</h3>
          <p>{error}</p>
        </div>
        <button 
          onClick={() => window.location.reload()}
          style={{ padding: '10px 20px', marginTop: '10px', cursor: 'pointer' }}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      {/* Navigation */}
      <div style={{ marginBottom: '20px' }}>
        <h1 style={{ margin: 0 }}>House of Noa - Meta Campaigns by Month</h1>
      </div>
      
      {/* Category Slicer */}
      <div style={{ marginBottom: '20px' }}>
        <h3>Filter by Category:</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '10px' }}>
          {data?.available_categories?.map((category: string) => (
            <button
              key={category}
              onClick={() => toggleCategory(category)}
              style={{
                padding: '8px 16px',
                border: '2px solid #1976d2',
                borderRadius: '20px',
                backgroundColor: selectedCategories.includes(category) ? '#1976d2' : 'white',
                color: selectedCategories.includes(category) ? 'white' : '#1976d2',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                transition: 'all 0.2s ease'
              }}
            >
              {category}
            </button>
          ))}
        </div>
        {selectedCategories.length > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '14px', color: '#666' }}>
              Showing {selectedCategories.length} of {data?.available_categories?.length} categories
            </span>
            <button
              onClick={clearFilters}
              style={{
                padding: '4px 12px',
                border: '1px solid #999',
                borderRadius: '4px',
                backgroundColor: 'white',
                color: '#666',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              Clear Category Filters
            </button>
          </div>
        )}
      </div>

      {/* Month Slicer */}
      <div style={{ marginBottom: '20px' }}>
        <h3>Filter by Month:</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '10px' }}>
          {data?.monthly_breakdown?.sort((a: any, b: any) => b.month.localeCompare(a.month)).map((month: any) => (
            <button
              key={month.month}
              onClick={() => toggleMonth(month.month)}
              style={{
                padding: '8px 16px',
                border: '2px solid #388e3c',
                borderRadius: '20px',
                backgroundColor: selectedMonths.includes(month.month) ? '#388e3c' : 'white',
                color: selectedMonths.includes(month.month) ? 'white' : '#388e3c',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                transition: 'all 0.2s ease'
              }}
            >
              {formatMonthDisplay(month.month)}
            </button>
          ))}
        </div>
        {selectedMonths.length > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '14px', color: '#666' }}>
              Showing {selectedMonths.length} of {data?.monthly_breakdown?.length} months
            </span>
            <button
              onClick={clearMonthFilters}
              style={{
                padding: '4px 12px',
                border: '1px solid #999',
                borderRadius: '4px',
                backgroundColor: 'white',
                color: '#666',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              Clear Month Filters
            </button>
          </div>
        )}
      </div>
      
      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <div style={{ background: '#f5f5f5', padding: '15px', borderRadius: '8px' }}>
          <h3>Total Spend{(selectedCategories.length > 0 || selectedMonths.length > 0) ? ' (Filtered)' : ''}</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#1976d2' }}>
            ${Math.round(currentTotals?.totalSpend || currentTotals?.total_spend || 0).toLocaleString()}
          </p>
        </div>
        <div style={{ background: '#f5f5f5', padding: '15px', borderRadius: '8px' }}>
          <h3>Total Revenue{(selectedCategories.length > 0 || selectedMonths.length > 0) ? ' (Filtered)' : ''}</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#388e3c' }}>
            ${Math.round(currentTotals?.totalRevenue || currentTotals?.total_revenue || 0).toLocaleString()}
          </p>
        </div>
        <div style={{ background: '#f5f5f5', padding: '15px', borderRadius: '8px' }}>
          <h3>ROAS{(selectedCategories.length > 0 || selectedMonths.length > 0) ? ' (Filtered)' : ''}</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#f57c00' }}>
            {(currentTotals?.avgROAS || currentTotals?.avg_roas || 0).toFixed(2)}
          </p>
        </div>
        <div style={{ background: '#f5f5f5', padding: '15px', borderRadius: '8px' }}>
          <h3>Total Purchases{(selectedCategories.length > 0 || selectedMonths.length > 0) ? ' (Filtered)' : ''}</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#7b1fa2' }}>
            {(currentTotals?.totalPurchases || currentTotals?.total_purchases || 0).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Monthly Performance Table */}
      <div style={{ marginBottom: '30px' }}>
        <h2>Monthly Performance</h2>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', border: '1px solid #ddd' }}>
            <thead>
              <tr style={{ background: '#f5f5f5' }}>
                <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Month</th>
                <th style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>Spend</th>
                <th style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>Link Clicks</th>
                <th style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>Purchases</th>
                <th style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>Revenue</th>
                <th style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>CPA</th>
                <th style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>ROAS</th>
                <th style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>CPC</th>
              </tr>
            </thead>
            <tbody>
              {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].map(monthName => {
                const yearsInMonth = groupedData[monthName];
                if (!yearsInMonth || Object.keys(yearsInMonth).length === 0) return null;
                
                const sortedYears = Object.keys(yearsInMonth).sort((a, b) => parseInt(b) - parseInt(a));
                const isExpanded = expandedMonths.includes(monthName);
                const rows: JSX.Element[] = [];
                
                // Month header row
                rows.push(
                  <tr key={`month-${monthName}`} style={{ backgroundColor: '#f8f9fa' }}>
                    <td style={{ 
                      padding: '10px', 
                      border: '1px solid #ddd', 
                      fontWeight: 'bold'
                    }}>
                      <div style={{ 
                        display: 'flex', 
                        alignItems: 'center',
                        gap: '8px'
                      }}>
                        <button
                          onClick={() => toggleMonthExpansion(monthName)}
                          style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            fontSize: '12px',
                            width: '16px',
                            height: '16px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                        >
                          {isExpanded ? '▼' : '▶'}
                        </button>
                        <span>{monthName}</span>
                      </div>
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd', fontWeight: 'bold' }}>
                      ${Math.round(sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].amount_spent_usd || 0), 0)).toLocaleString()}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd', fontWeight: 'bold' }}>
                      {sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].link_clicks || 0), 0).toLocaleString()}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd', fontWeight: 'bold' }}>
                      {sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].website_purchases || 0), 0)}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd', fontWeight: 'bold' }}>
                      ${Math.round(sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].purchases_conversion_value || 0), 0)).toLocaleString()}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd', fontWeight: 'bold' }}>
                      ${(() => {
                        const totalSpend = sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].amount_spent_usd || 0), 0);
                        const totalPurchases = sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].website_purchases || 0), 0);
                        return totalPurchases > 0 ? (totalSpend / totalPurchases).toFixed(2) : '0.00';
                      })()}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd', fontWeight: 'bold' }}>
                      {(() => {
                        const totalSpend = sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].amount_spent_usd || 0), 0);
                        const totalRevenue = sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].purchases_conversion_value || 0), 0);
                        return totalSpend > 0 ? (totalRevenue / totalSpend).toFixed(1) : '0.0';
                      })()}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd', fontWeight: 'bold' }}>
                      ${(() => {
                        const totalSpend = sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].amount_spent_usd || 0), 0);
                        const totalClicks = sortedYears.reduce((sum, year) => sum + (yearsInMonth[year].link_clicks || 0), 0);
                        return totalClicks > 0 ? (totalSpend / totalClicks).toFixed(2) : '0.00';
                      })()}
                    </td>
                  </tr>
                );
                
                // Year detail rows (only if expanded)
                if (isExpanded) {
                  sortedYears.forEach(year => {
                    const yearData = yearsInMonth[year];
                    rows.push(
                      <tr key={`${monthName}-${year}`}>
                        <td style={{ 
                          padding: '10px', 
                          border: '1px solid #ddd',
                          paddingLeft: '40px'
                        }}>
                          <span>{year}</span>
                        </td>
                        <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                          ${Math.round(yearData.amount_spent_usd || 0).toLocaleString()}
                        </td>
                        <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                          {(yearData.link_clicks || 0).toLocaleString()}
                        </td>
                        <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                          {yearData.website_purchases || 0}
                        </td>
                        <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                          ${Math.round(yearData.purchases_conversion_value || 0).toLocaleString()}
                        </td>
                        <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                          ${(yearData.cpa || 0).toFixed(2)}
                        </td>
                        <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                          {(yearData.roas || 0).toFixed(1)}
                        </td>
                        <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                          ${(yearData.cpc || 0).toFixed(2)}
                        </td>
                      </tr>
                    );
                  });
                }
                
                return rows;
              }).filter(rows => rows !== null)}
              
              {/* Totals Row */}
              {((selectedMonths.length > 0 ? filteredMonthlyData : data?.monthly_breakdown)) && (() => {
                const dataToSum = selectedMonths.length > 0 ? filteredMonthlyData : data?.monthly_breakdown;
                const totalSpend = dataToSum.reduce((sum: number, month: any) => sum + (month.amount_spent_usd || 0), 0);
                const totalClicks = dataToSum.reduce((sum: number, month: any) => sum + (month.link_clicks || 0), 0);
                const totalPurchases = dataToSum.reduce((sum: number, month: any) => sum + (month.website_purchases || 0), 0);
                const totalRevenue = dataToSum.reduce((sum: number, month: any) => sum + (month.purchases_conversion_value || 0), 0);
                const avgCPA = totalPurchases > 0 ? totalSpend / totalPurchases : 0;
                const avgROAS = totalSpend > 0 ? totalRevenue / totalSpend : 0;
                const avgCPC = totalClicks > 0 ? totalSpend / totalClicks : 0;
                
                return (
                  <tr style={{ background: '#e3f2fd', fontWeight: 'bold', borderTop: '2px solid #1976d2' }}>
                    <td style={{ padding: '10px', border: '1px solid #ddd', fontWeight: 'bold' }}>Grand Total</td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                      ${Math.round(totalSpend).toLocaleString()}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                      {totalClicks.toLocaleString()}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                      {totalPurchases.toLocaleString()}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                      ${Math.round(totalRevenue).toLocaleString()}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                      ${avgCPA.toFixed(2)}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                      {avgROAS.toFixed(1)}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                      ${avgCPC.toFixed(2)}
                    </td>
                  </tr>
                );
              })()}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

export default MonthlyReporting;