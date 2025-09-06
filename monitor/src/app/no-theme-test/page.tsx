'use client';

import { useState, useEffect } from 'react';

export default function NoThemeTestPage() {
  const [mounted, setMounted] = useState(false);
  const [message, setMessage] = useState('Initial state');

  useEffect(() => {
    console.log('useEffect called in no-theme test!');
    setMounted(true);
    setMessage('useEffect executed successfully!');
  }, []);

  console.log('No-theme component rendering, mounted:', mounted);

  return (
    <div style={{ padding: '20px', color: '#000', backgroundColor: '#fff', minHeight: '100vh' }}>
      <h1>No Theme Test</h1>
      <p>Mounted: {mounted ? 'YES' : 'NO'}</p>
      <p>Message: {message}</p>
    </div>
  );
}
