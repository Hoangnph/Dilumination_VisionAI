'use client';

import React from 'react';

export default function TestSessionsPage() {
  const [message, setMessage] = React.useState('Starting...');

  React.useEffect(() => {
    console.log('=== TEST SESSIONS PAGE MOUNTED ===');
    setMessage('Component mounted, testing fetch...');
    
    // Test basic fetch without async/await
    fetch('/api/sessions?page=1&limit=5')
      .then(response => {
        console.log('Response received:', response.status);
        setMessage(`Response status: ${response.status}`);
        return response.json();
      })
      .then(data => {
        console.log('Data received:', data);
        setMessage(`Success! Received ${data?.data?.data?.length || 0} sessions`);
      })
      .catch(error => {
        console.error('Fetch error:', error);
        setMessage(`Error: ${error.message}`);
      });
  }, []);

  return (
    <div style={{ padding: '20px', color: '#fff', backgroundColor: '#0a0a0a', minHeight: '100vh' }}>
      <h1>Simple Test Sessions Page</h1>
      <p>{message}</p>
    </div>
  );
}
