import React from 'react';
import { 
  ChartBarIcon,
  ChartPieIcon,
  PlayIcon as VideoIcon,
  RectangleStackIcon
} from '@heroicons/react/24/outline';

export type TabType = 'meta' | 'google' | 'tiktok' | 'ad-level';

interface Tab {
  id: TabType;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  description: string;
}

interface TabNavigationProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  className?: string;
}

const tabs: Tab[] = [
  {
    id: 'meta',
    label: 'Meta Ads',
    icon: ChartBarIcon,
    color: 'blue',
    description: 'Facebook & Instagram advertising data'
  },
  {
    id: 'google',
    label: 'Google Ads',
    icon: ChartPieIcon, 
    color: 'green',
    description: 'Google advertising data'
  },
  {
    id: 'tiktok',
    label: 'TikTok Ads',
    icon: VideoIcon,
    color: 'pink',
    description: 'TikTok advertising data'
  },
  {
    id: 'ad-level',
    label: 'Meta Ad Level',
    icon: RectangleStackIcon,
    color: 'purple',
    description: 'Individual Meta ad performance with thumbnails and weekly breakdown'
  }
];

const TabNavigation: React.FC<TabNavigationProps> = ({ 
  activeTab, 
  onTabChange, 
  className = '' 
}) => {
  const getTabClasses = (tab: Tab, isActive: boolean) => {
    const baseClasses = `
      flex items-center gap-2 px-4 py-3 text-sm font-medium rounded-t-lg 
      border-b-2 transition-all duration-200 hover:bg-gray-50 cursor-pointer
      min-w-[160px] justify-center relative
    `;
    
    if (isActive) {
      const activeColors = {
        blue: 'text-blue-600 border-blue-500 bg-blue-50',
        green: 'text-green-600 border-green-500 bg-green-50',
        pink: 'text-pink-600 border-pink-500 bg-pink-50',
        purple: 'text-purple-600 border-purple-500 bg-purple-50'
      };
      return `${baseClasses} ${activeColors[tab.color as keyof typeof activeColors]}`;
    }
    
    return `${baseClasses} text-gray-500 border-gray-200 hover:text-gray-700`;
  };

  return (
    <div className={`bg-white ${className}`}>
      {/* Tab Container */}
      <div className="flex items-end justify-center border-b border-gray-200 bg-gray-50">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          const IconComponent = tab.icon;
          
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={getTabClasses(tab, isActive)}
              title={tab.description}
            >
              <IconComponent className="w-4 h-4" />
              <span>{tab.label}</span>
              
              {/* Active indicator */}
              {isActive && (
                <div 
                  className={`
                    absolute bottom-0 left-0 right-0 h-0.5 
                    ${tab.color === 'blue' ? 'bg-blue-500' : 
                      tab.color === 'green' ? 'bg-green-500' : 
                      tab.color === 'pink' ? 'bg-pink-500' : 'bg-purple-500'}
                  `} 
                />
              )}
            </button>
          );
        })}
      </div>
      
      {/* Tab Content Description */}
      <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
        <div className="text-center">
          {tabs.map((tab) => (
            activeTab === tab.id && (
              <p key={tab.id} className="text-xs text-gray-600">
                {tab.description}
              </p>
            )
          ))}
        </div>
      </div>
    </div>
  );
};

export default TabNavigation;