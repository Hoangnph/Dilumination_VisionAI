'use client';

import { useState, useEffect } from 'react';

export default function BasicClientPage() {
  const [mounted, setMounted] = useState(false);
  const [message, setMessage] = useState('Initial state');

  useEffect(() => {
    console.log('useEffect called!');
    setMounted(true);
    setMessage('useEffect executed successfully!');
  }, []);

  console.log('Component rendering, mounted:', mounted);

  return (
    <div style={{ padding: '20px', color: '#fff', backgroundColor: '#0a0a0a', minHeight: '100vh' }}>
      <h1>Basic Client Test</h1>
      <p>Mounted: {mounted ? 'YES' : 'NO'}</p>
      <p>Message: {message}</p>
    </div>
  );
}
