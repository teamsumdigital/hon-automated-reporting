/**
 * Ad Status Color System Component
 * Enhanced color coding system with automated pause detection
 */

import React from 'react';

// Enhanced status type including automated pause
export type AdStatus = 
  | 'winner' 
  | 'considering' 
  | 'paused' 
  | 'active'  // Active ads (opposite of paused)
  | null;

/**
 * Get the appropriate CSS class for ad row coloring
 * Now includes darker red for automated pause detection
 */
export const getRowColorClass = (status: AdStatus): string => {
  switch (status) {
    case 'winner':
      return 'bg-green-100 hover:bg-green-200 border-l-4 border-l-green-400';
    case 'considering':
      return 'bg-yellow-100 hover:bg-yellow-200 border-l-4 border-l-yellow-400';
    case 'paused':
      // Red for paused ads
      return 'bg-red-200 hover:bg-red-300 border-l-4 border-l-red-600';
    case 'active':
      // No background color for active ads - keep them neutral
      return 'hover:bg-gray-50 border-l-4 border-l-transparent';
    default:
      return 'hover:bg-gray-50 border-l-4 border-l-transparent';
  }
};

/**
 * Get status display name for UI
 */
export const getStatusDisplayName = (status: AdStatus): string => {
  switch (status) {
    case 'winner': return 'Winner';
    case 'considering': return 'Considering';
    case 'paused': return 'Paused';
    case 'active': return 'Active';
    default: return 'No Status';
  }
};

/**
 * Get the next status in the manual click cycle
 * Note: automated status is excluded from manual cycling
 */
export const getNextStatus = (currentStatus: AdStatus): AdStatus => {
  switch (currentStatus) {
    case null:
    case undefined:
      return 'winner';
    case 'winner':
      return 'considering';
    case 'considering':
      return 'paused';
    case 'paused':
      return null;
    case 'active':
      return 'winner';
    default:
      return 'winner';
  }
};

/**
 * Check if a status is automated (should not be overridden lightly)
 */
export const isAutomatedStatus = (status: AdStatus): boolean => {
  return status === 'active';
};

/**
 * Enhanced Color Legend Component
 */
export const AdStatusColorLegend: React.FC = () => {
  return (
    <div className="flex flex-wrap items-center gap-4 text-sm">
      <div className="font-medium text-gray-700">Ad Status:</div>
      
      {/* Winner */}
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 bg-green-100 border border-green-200 rounded"></div>
        <span className="text-green-700">Winner</span>
      </div>
      
      {/* Considering */}
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 bg-yellow-100 border border-yellow-200 rounded"></div>
        <span className="text-yellow-700">Considering</span>
      </div>
      
      {/* Paused */}
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 bg-red-200 border border-red-300 rounded"></div>
        <span className="text-red-700">Paused</span>
      </div>
      
      {/* Active */}
      <div className="flex items-center gap-2">
        <div className="w-4 h-4 bg-white border border-gray-300 rounded"></div>
        <span className="text-gray-700">Active</span>
      </div>
      
      {/* Click instruction */}
      <div className="ml-auto text-xs text-gray-500">
        Click row to cycle status
      </div>
    </div>
  );
};

/**
 * Status Badge Component for individual ads
 */
export const AdStatusBadge: React.FC<{ status: AdStatus; className?: string }> = ({ 
  status, 
  className = "" 
}) => {
  const baseClasses = "px-2 py-1 rounded-full text-xs font-medium";
  
  const statusClasses = {
    'winner': 'bg-green-100 text-green-800',
    'considering': 'bg-yellow-100 text-yellow-800',
    'paused': 'bg-red-200 text-red-800',
    'active': 'bg-gray-100 text-gray-800',
  };
  
  if (!status) return null;
  
  return (
    <span className={`${baseClasses} ${statusClasses[status]} ${className}`}>
      {getStatusDisplayName(status)}
    </span>
  );
};

/**
 * Status Override Warning Component
 * Shows when user tries to override automated status
 */
export const StatusOverrideWarning: React.FC<{ 
  adName: string;
  currentStatus: AdStatus;
  onConfirm: () => void;
  onCancel: () => void;
}> = ({ adName, currentStatus, onConfirm, onCancel }) => {
  if (currentStatus !== 'active') return null;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md mx-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Override Active Status?
        </h3>
        <p className="text-gray-600 mb-4">
          This ad is automatically marked as active. Are you sure you want to manually override this status?
        </p>
        <p className="text-sm text-gray-500 mb-6">
          Ad: <span className="font-medium">{adName}</span>
        </p>
        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-md"
          >
            Override Status
          </button>
        </div>
      </div>
    </div>
  );
};

export default {
  getRowColorClass,
  getStatusDisplayName,
  getNextStatus,
  isAutomatedStatus,
  AdStatusColorLegend,
  AdStatusBadge,
  StatusOverrideWarning
};