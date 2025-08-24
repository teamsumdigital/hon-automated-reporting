import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AuthGate from './components/AuthGate';
import MainDashboard from './pages/MainDashboard';
import ModernDashboard from './pages/ModernDashboard';
import GoogleDashboard from './pages/GoogleDashboard';
import TikTokDashboard from './pages/TikTokDashboard';
import AdLevelDashboard from './pages/AdLevelDashboard';

function App() {
  return (
    <div className="App">
      <AuthGate>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<MainDashboard />} />
          {/* Individual dashboard routes for direct access */}
          <Route path="/meta" element={<ModernDashboard />} />
          <Route path="/google" element={<GoogleDashboard />} />
          <Route path="/tiktok" element={<TikTokDashboard />} />
          <Route path="/ad-level" element={<AdLevelDashboard />} />
          {/* Add more routes as needed */}
        </Routes>
      </AuthGate>
    </div>
  );
}

export default App;