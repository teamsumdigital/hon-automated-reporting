import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import SimpleDashboard from './pages/SimpleDashboard';
import MonthlyReporting from './pages/MonthlyReporting';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<SimpleDashboard />} />
        <Route path="/monthly" element={<MonthlyReporting />} />
        {/* Add more routes as needed */}
      </Routes>
    </div>
  );
}

export default App;