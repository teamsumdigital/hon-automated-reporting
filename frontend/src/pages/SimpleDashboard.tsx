import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const SimpleDashboard: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);

  useEffect(() => {
    fetch('/api/reports/dashboard')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Dashboard data:', data);
        setData(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching dashboard data:', error);
        setError(error.message);
        setLoading(false);
      });
  }, []);

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

  // Filter data based on selected categories
  const filteredData = data?.category_breakdown?.filter((category: any) => 
    selectedCategories.length === 0 || selectedCategories.includes(category.category)
  ) || [];

  // Calculate totals for filtered data
  const calculateFilteredTotals = (categories: any[]) => {
    if (categories.length === 0) return null;
    
    const totalSpend = categories.reduce((sum: number, cat: any) => sum + (cat.amount_spent_usd || 0), 0);
    const totalClicks = categories.reduce((sum: number, cat: any) => sum + (cat.link_clicks || 0), 0);
    const totalPurchases = categories.reduce((sum: number, cat: any) => sum + (cat.website_purchases || 0), 0);
    const totalRevenue = categories.reduce((sum: number, cat: any) => sum + (cat.purchases_conversion_value || 0), 0);
    
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

  if (loading) {
    return (
      <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
        <h1>HON Automated Reporting</h1>
        <p>Loading dashboard data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
        <h1>HON Automated Reporting</h1>
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

  // Get current totals (filtered or unfiltered)
  const currentTotals = selectedCategories.length > 0 
    ? calculateFilteredTotals(filteredData)
    : {
        totalSpend: data?.summary?.total_spend || 0,
        totalRevenue: data?.summary?.total_revenue || 0,
        totalPurchases: data?.summary?.total_purchases || 0,
        avgROAS: data?.summary?.avg_roas || 0
      };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      {/* Navigation */}
      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', alignItems: 'center' }}>
        <h1 style={{ margin: 0 }}>HON Automated Reporting</h1>
        <Link 
          to="/monthly" 
          style={{ 
            padding: '8px 16px', 
            background: '#1976d2', 
            color: 'white',
            textDecoration: 'none', 
            borderRadius: '4px',
            fontSize: '14px'
          }}
        >
          Monthly Report →
        </Link>
      </div>
      
      {/* Category Slicer */}
      <div style={{ marginBottom: '20px' }}>
        <h3>Filter by Category:</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '10px' }}>
          {data?.category_breakdown?.map((category: any) => (
            <button
              key={category.category}
              onClick={() => toggleCategory(category.category)}
              style={{
                padding: '8px 16px',
                border: '2px solid #1976d2',
                borderRadius: '20px',
                backgroundColor: selectedCategories.includes(category.category) ? '#1976d2' : 'white',
                color: selectedCategories.includes(category.category) ? 'white' : '#1976d2',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                transition: 'all 0.2s ease'
              }}
            >
              {category.category}
            </button>
          ))}
        </div>
        {selectedCategories.length > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '14px', color: '#666' }}>
              Showing {selectedCategories.length} of {data?.category_breakdown?.length} categories
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
              Clear Filters
            </button>
          </div>
        )}
      </div>
      
      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <div style={{ background: '#f5f5f5', padding: '15px', borderRadius: '8px' }}>
          <h3>Total Spend{selectedCategories.length > 0 ? ' (Filtered)' : ''}</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#1976d2' }}>
            ${Math.round(currentTotals?.totalSpend || 0).toLocaleString()}
          </p>
        </div>
        <div style={{ background: '#f5f5f5', padding: '15px', borderRadius: '8px' }}>
          <h3>Total Revenue{selectedCategories.length > 0 ? ' (Filtered)' : ''}</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#388e3c' }}>
            ${Math.round(currentTotals?.totalRevenue || 0).toLocaleString()}
          </p>
        </div>
        <div style={{ background: '#f5f5f5', padding: '15px', borderRadius: '8px' }}>
          <h3>ROAS{selectedCategories.length > 0 ? ' (Filtered)' : ''}</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#f57c00' }}>
            {currentTotals?.avgROAS?.toFixed(2) || '0.00'}
          </p>
        </div>
        <div style={{ background: '#f5f5f5', padding: '15px', borderRadius: '8px' }}>
          <h3>Total Purchases{selectedCategories.length > 0 ? ' (Filtered)' : ''}</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#7b1fa2' }}>
            {currentTotals?.totalPurchases || 0}
          </p>
        </div>
      </div>

      {/* Category Breakdown */}
      <div style={{ marginBottom: '30px' }}>
        <h2>Category Performance</h2>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', border: '1px solid #ddd' }}>
            <thead>
              <tr style={{ background: '#f5f5f5' }}>
                <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Category</th>
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
              {(selectedCategories.length > 0 ? filteredData : data?.category_breakdown)
                ?.sort((a: any, b: any) => b.amount_spent_usd - a.amount_spent_usd)
                ?.map((category: any, index: number) => {
                  const cpc = category.link_clicks > 0 ? category.amount_spent_usd / category.link_clicks : 0;
                  return (
                    <tr key={index}>
                      <td style={{ padding: '10px', border: '1px solid #ddd', fontWeight: 'bold' }}>{category.category}</td>
                      <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                        ${Math.round(category.amount_spent_usd || 0).toLocaleString()}
                      </td>
                      <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                        {(category.link_clicks || 0).toLocaleString()}
                      </td>
                      <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                        {category.website_purchases}
                      </td>
                      <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                        ${Math.round(category.purchases_conversion_value || 0).toLocaleString()}
                      </td>
                      <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                        ${category.cpa?.toFixed(2)}
                      </td>
                      <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                        {category.roas?.toFixed(1)}
                      </td>
                      <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                        ${cpc.toFixed(2)}
                      </td>
                    </tr>
                  );
                })}
              
              {/* Totals Row */}
              {((selectedCategories.length > 0 ? filteredData : data?.category_breakdown)) && (() => {
                const dataToSum = selectedCategories.length > 0 ? filteredData : data?.category_breakdown;
                const totalSpend = dataToSum.reduce((sum: number, cat: any) => sum + (cat.amount_spent_usd || 0), 0);
                const totalClicks = dataToSum.reduce((sum: number, cat: any) => sum + (cat.link_clicks || 0), 0);
                const totalPurchases = dataToSum.reduce((sum: number, cat: any) => sum + (cat.website_purchases || 0), 0);
                const totalRevenue = dataToSum.reduce((sum: number, cat: any) => sum + (cat.purchases_conversion_value || 0), 0);
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

export default SimpleDashboard;