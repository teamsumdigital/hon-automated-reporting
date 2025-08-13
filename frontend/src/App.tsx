import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ModernDashboard from './pages/ModernDashboard';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<ModernDashboard />} />
        {/* Add more routes as needed */}
      </Routes>
    </div>
  );
}

export default App;