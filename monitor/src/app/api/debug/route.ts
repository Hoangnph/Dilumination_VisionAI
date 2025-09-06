import { NextResponse } from 'next/server';

export async function GET() {
  try {
    console.log('=== DEBUG API CALLED ===');
    
    // Test database connection
    const sessionsResponse = await fetch('http://localhost:3000/api/sessions?page=1&limit=5');
    const sessionsData = await sessionsResponse.json();
    
    console.log('Sessions API response:', sessionsData);
    
    return NextResponse.json({
      success: true,
      message: 'Debug API working',
      sessions_api_status: sessionsResponse.status,
      sessions_data: sessionsData,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Debug API error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}
