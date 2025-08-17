import React, { useState, useEffect } from 'react';
import TabNavigation, { TabType } from '../components/TabNavigation';
import ModernDashboard from './ModernDashboard';
import GoogleDashboard from './GoogleDashboard';
import TikTokDashboard from './TikTokDashboard';

const MainDashboard: React.FC = () => {
  // Get the last active tab from localStorage, fallback to 'meta'
  const getInitialTab = (): TabType => {
    const savedTab = localStorage.getItem('activeTab');
    if (savedTab && ['meta', 'google', 'tiktok'].includes(savedTab)) {
      return savedTab as TabType;
    }
    return 'meta';
  };

  const [activeTab, setActiveTab] = useState<TabType>(getInitialTab);

  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
    // Save the active tab to localStorage
    localStorage.setItem('activeTab', tab);
  };

  // Update localStorage when activeTab changes (for any reason)
  useEffect(() => {
    localStorage.setItem('activeTab', activeTab);
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Tab Navigation - Fixed at bottom like Excel */}
      <div className="fixed bottom-0 left-0 right-0 z-50 bg-white shadow-lg border-t border-gray-200">
        <TabNavigation 
          activeTab={activeTab}
          onTabChange={handleTabChange}
          className="max-w-7xl mx-auto"
        />
      </div>
      
      {/* Dashboard Content with bottom padding for fixed tabs */}
      <div className="pb-20">
        {activeTab === 'meta' && <ModernDashboard />}
        {activeTab === 'google' && <GoogleDashboard />}
        {activeTab === 'tiktok' && <TikTokDashboard />}
      </div>
    </div>
  );
};

export default MainDashboard;