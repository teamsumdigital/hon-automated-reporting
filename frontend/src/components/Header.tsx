import React, { useState, useEffect } from 'react';
import { 
  FunnelIcon, 
  ChevronRightIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

interface HeaderProps {
  filterPanelOpen: boolean;
  onFilterToggle: () => void;
  showFilters?: boolean;
  kpiCollapsed?: boolean;
  onKpiToggle?: () => void;
  showKpiToggle?: boolean;
}

const Header: React.FC<HeaderProps> = ({ 
  filterPanelOpen, 
  onFilterToggle, 
  showFilters = true,
  kpiCollapsed = false,
  onKpiToggle,
  showKpiToggle = true
}) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // Trigger load animation
    setIsLoaded(true);

    // Scroll detection for logo scaling
    const handleScroll = () => {
      const scrollY = window.scrollY;
      setIsScrolled(scrollY > 100);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        {/* Logo Section */}
        <div className={`
          transition-all duration-300 ease-in-out
          ${isScrolled ? 'scale-80' : 'scale-100'}
          ${isLoaded ? 'animate-fade-in' : 'opacity-0'}
        `}>
          {/* Desktop Logo */}
          <img 
            src="/house-of-noa-logo.png" 
            alt="House of Noa" 
            className="h-5 w-auto hover:scale-105 hover:brightness-110 transition-all duration-200 ease-in-out hidden sm:block"
          />
          
          {/* Mobile Icon */}
          <div className="block sm:hidden">
            <span className="text-lg font-bold text-blue-600 hover:text-blue-700 transition-colors duration-200">
              H of N
            </span>
          </div>
        </div>

        {/* Control Buttons */}
        <div className="flex items-center space-x-3">
          {/* KPI Toggle */}
          {showKpiToggle && onKpiToggle && (
            <button
              onClick={onKpiToggle}
              className="flex items-center justify-center w-10 h-10 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200"
              title={kpiCollapsed ? "Show KPI Dashboard" : "Hide KPI Dashboard"}
            >
              <ChartBarIcon className={`w-5 h-5 ${kpiCollapsed ? 'text-gray-400' : 'text-gray-600'}`} />
            </button>
          )}

          {/* Filter Toggle */}
          {showFilters && (
            <button
              onClick={onFilterToggle}
              className="flex items-center justify-center w-10 h-10 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200"
              title={filterPanelOpen ? "Hide Filters" : "Show Filters"}
            >
              <FunnelIcon className={`w-5 h-5 ${filterPanelOpen ? 'text-gray-600' : 'text-gray-400'}`} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Header;