import React from 'react';
import { ChevronDownIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

interface CollapsibleSectionProps {
  title: string;
  isCollapsed: boolean;
  onToggle: () => void;
  children: React.ReactNode;
  className?: string;
}

const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({
  title,
  isCollapsed,
  onToggle,
  children,
  className = ''
}) => {
  return (
    <div className={className}>
      {/* Toggle Header */}
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
      
      {/* Collapsible Content */}
      <div className={`transition-all duration-300 ease-in-out ${
        isCollapsed 
          ? 'opacity-0 max-h-0 overflow-hidden transform -translate-y-2' 
          : 'opacity-100 max-h-full transform translate-y-0'
      }`}>
        {children}
      </div>
    </div>
  );
};

export default CollapsibleSection;