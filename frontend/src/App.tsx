import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MonthlyReporting from './pages/MonthlyReporting';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<Navigate to="/monthly" replace />} />
        <Route path="/monthly" element={<MonthlyReporting />} />
        {/* Add more routes as needed */}
      </Routes>
    </div>
  );
}

export default App;