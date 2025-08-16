import React from 'react';
import { PivotTableData } from '../services/api';

interface PivotTableProps {
  data: PivotTableData[];
  loading?: boolean;
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(value);
};

const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('en-US').format(value);
};

const formatDecimal = (value: number, decimals: number = 2): string => {
  return value.toFixed(decimals);
};

const PivotTable: React.FC<PivotTableProps> = ({ data, loading = false }) => {
  if (loading) {
    return (
      <div className="w-full h-64 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="w-full h-64 flex items-center justify-center text-muted-foreground">
        No data available
      </div>
    );
  }

  // Calculate totals for grand total row
  const grandTotal = data.reduce(
    (acc, row) => ({
      spend: acc.spend + row.spend,
      revenue: acc.revenue + row.revenue,
    }),
    { spend: 0, revenue: 0 }
  );

  const grandTotalROAS = grandTotal.spend > 0 ? grandTotal.revenue / grandTotal.spend : 0;
  // Calculate weighted averages for CPA, CPC, and CPM from the data
  const totalCPA = data.reduce((sum, row) => sum + (row.cpa * row.spend), 0);
  const totalCPC = data.reduce((sum, row) => sum + (row.cpc * row.spend), 0);
  const totalCPM = data.reduce((sum, row) => sum + (row.cpm * row.spend), 0);
  const grandTotalCPA = grandTotal.spend > 0 ? totalCPA / grandTotal.spend : 0;
  const grandTotalCPC = grandTotal.spend > 0 ? totalCPC / grandTotal.spend : 0;
  const grandTotalCPM = grandTotal.spend > 0 ? totalCPM / grandTotal.spend : 0;

  return (
    <div className="w-full overflow-x-auto">
      <table className="pivot-table">
        <thead>
          <tr>
            <th className="text-left">Month</th>
            <th className="text-right">Spend</th>
            <th className="text-right">Revenue</th>
            <th className="text-right">ROAS</th>
            <th className="text-right">CPA</th>
            <th className="text-right">CPC</th>
            <th className="text-right">CPM</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={`${row.month}-${index}`}>
              <td className="font-medium">{row.month}</td>
              <td className="text-right">{formatCurrency(row.spend)}</td>
              <td className="text-right">{formatCurrency(row.revenue)}</td>
              <td className="text-right">{formatDecimal(row.roas, 1)}</td>
              <td className="text-right">${formatDecimal(row.cpa)}</td>
              <td className="text-right">${formatDecimal(row.cpc)}</td>
              <td className="text-right">${formatDecimal(row.cpm)}</td>
            </tr>
          ))}
          {data.length > 1 && (
            <tr className="border-t-2 border-primary bg-muted/50 font-semibold">
              <td>Grand Total</td>
              <td className="text-right">{formatCurrency(grandTotal.spend)}</td>
              <td className="text-right">{formatCurrency(grandTotal.revenue)}</td>
              <td className="text-right">{formatDecimal(grandTotalROAS, 1)}</td>
              <td className="text-right">${formatDecimal(grandTotalCPA)}</td>
              <td className="text-right">${formatDecimal(grandTotalCPC)}</td>
              <td className="text-right">${formatDecimal(grandTotalCPM)}</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default PivotTable;