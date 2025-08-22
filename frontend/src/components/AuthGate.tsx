import React, { useState, useEffect } from 'react';

interface AuthGateProps {
  children: React.ReactNode;
}

const AuthGate: React.FC<AuthGateProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Check if user is already authenticated on component mount
  useEffect(() => {
    const savedAuth = localStorage.getItem('hon_authenticated');
    if (savedAuth === 'true') {
      setIsAuthenticated(true);
    }
    setIsLoading(false);
  }, []);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Simple password check - in production, this should be environment variable
    const correctPassword = 'HN$7kX9#mQ2vL8pR@2024'; // TODO: Move to environment variable

    if (password === correctPassword) {
      setIsAuthenticated(true);
      localStorage.setItem('hon_authenticated', 'true');
      setPassword('');
    } else {
      setError('Incorrect password. Please try again.');
      setPassword('');
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('hon_authenticated');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full space-y-8 p-8">
          <div className="text-center">
            <img 
              src="/house-of-noa-logo.svg" 
              alt="House of Noa" 
              className="mx-auto h-10 w-auto mb-6 animate-fade-in hover:scale-105 transition-transform duration-200"
              onError={(e) => {
                // Fallback if logo doesn't exist
                e.currentTarget.style.display = 'none';
              }}
            />
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              HON Automated Reporting
            </h2>
            <p className="text-gray-600">
              Enter password to access advertising dashboard
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="relative block w-full px-3 py-3 border border-gray-300 rounded-lg placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter password"
                autoFocus
              />
            </div>

            {error && (
              <div className="text-red-600 text-sm text-center">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Access Dashboard
            </button>
          </form>

          <div className="text-xs text-gray-500 text-center">
            Internal use only - Authorized personnel only
          </div>
        </div>
      </div>
    );
  }

  // Authenticated - show the main application with logout option
  return (
    <div className="relative">
      <div className="absolute top-4 right-4 z-50">
        <button
          onClick={handleLogout}
          className="text-sm text-gray-500 hover:text-gray-700 underline bg-white px-2 py-1 rounded shadow-sm"
        >
          Logout
        </button>
      </div>
      {children}
    </div>
  );
};

export default AuthGate;