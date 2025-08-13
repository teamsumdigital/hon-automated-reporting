import React from 'react';

function TestApp() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>HON Automated Reporting - Test Page</h1>
      <p>If you can see this, React is working!</p>
      <div style={{ background: '#f0f0f0', padding: '10px', margin: '10px 0' }}>
        <h3>Test Data:</h3>
        <p>Backend URL: http://localhost:8007</p>
        <p>Frontend URL: http://localhost:3007</p>
      </div>
      <button onClick={() => alert('Button clicked!')}>Test Button</button>
    </div>
  );
}

export default TestApp;