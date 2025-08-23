import React from 'react';
import { 
  DollarSign, 
  ShoppingCart, 
  TrendingUp, 
  MousePointer, 
  Eye,
  Target,
  Zap
} from 'lucide-react';
import { ChevronDownIcon, ChevronRightIcon } from '@heroicons/react/24/outline';
import { MTDSummary } from '../services/api';

interface MetricsCardsProps {
  summary: MTDSummary;
  loading?: boolean;
  isCollapsed?: boolean;
  onToggle?: () => void;
  title?: string;
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('en-US').format(value);
};

const formatDecimal = (value: number, decimals: number = 2): string => {
  return value.toFixed(decimals);
};

const MetricCard: React.FC<{
  title: string;
  value: string;
  icon: React.ReactNode;
  subtitle?: string;
  loading?: boolean;
}> = ({ title, value, icon, subtitle, loading }) => {
  if (loading) {
    return (
      <div className="metric-card">
        <div className="flex items-center justify-between mb-2">
          <div className="animate-pulse h-4 bg-muted-foreground/20 rounded w-24"></div>
          <div className="animate-pulse h-5 w-5 bg-muted-foreground/20 rounded"></div>
        </div>
        <div className="animate-pulse h-8 bg-muted-foreground/20 rounded w-32 mb-1"></div>
        {subtitle && (
          <div className="animate-pulse h-3 bg-muted-foreground/20 rounded w-20"></div>
        )}
      </div>
    );
  }

  return (
    <div className="metric-card">
      <div className="flex items-center justify-between mb-2">
        <p className="metric-label">{title}</p>
        <div className="text-muted-foreground">{icon}</div>
      </div>
      <p className="metric-value">{value}</p>
      {subtitle && (
        <p className="metric-label mt-1">{subtitle}</p>
      )}
    </div>
  );
};

const MetricsCards: React.FC<MetricsCardsProps> = ({ 
  summary, 
  loading = false, 
  isCollapsed = false,
  onToggle,
  title = "Performance Overview"
}) => {
  const metrics = [
    {
      title: 'Total Spend',
      value: formatCurrency(summary.total_spend || 0),
      icon: <DollarSign className="w-5 h-5" />,
      subtitle: summary.date_range,
    },
    {
      title: 'Total Revenue',
      value: formatCurrency(summary.total_revenue || 0),
      icon: <TrendingUp className="w-5 h-5" />,
      subtitle: `${summary.total_purchases || 0} purchases`,
    },
    {
      title: 'ROAS',
      value: formatDecimal(summary.avg_roas || 0, 1),
      icon: <Target className="w-5 h-5" />,
      subtitle: 'Return on Ad Spend',
    },
    {
      title: 'CPA',
      value: `$${formatDecimal(summary.avg_cpa || 0)}`,
      icon: <ShoppingCart className="w-5 h-5" />,
      subtitle: 'Cost Per Acquisition',
    },
    {
      title: 'CPM',
      value: `$${formatDecimal(summary.avg_cpm || 0)}`,
      icon: <Zap className="w-5 h-5" />,
      subtitle: 'Cost Per Mille',
    },
    {
      title: 'Impressions',
      value: formatNumber(summary.total_impressions || 0),
      icon: <Eye className="w-5 h-5" />,
      subtitle: `${summary.campaign_count || 0} campaigns`,
    },
  ];

  return (
    <div className="mb-6">
      {/* Toggle Header */}
      {onToggle && (
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
          <button
            onClick={onToggle}
            className="flex items-center space-x-1 px-3 py-1 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors duration-200"
          >
            <span>{isCollapsed ? 'Show' : 'Hide'}</span>
            {isCollapsed ? (
              <ChevronRightIcon className="w-4 h-4" />
            ) : (
              <ChevronDownIcon className="w-4 h-4" />
            )}
          </button>
        </div>
      )}
      
      {/* Metrics Cards */}
      <div className={`transition-all duration-300 ease-in-out ${
        isCollapsed 
          ? 'opacity-0 max-h-0 overflow-hidden transform -translate-y-2 pointer-events-none' 
          : 'opacity-100 max-h-full transform translate-y-0'
      }`}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {metrics.map((metric, index) => (
            <MetricCard
              key={metric.title}
              title={metric.title}
              value={metric.value}
              icon={metric.icon}
              subtitle={metric.subtitle}
              loading={loading}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default MetricsCards;