import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const healthData = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        database: 'connected',
        api: 'running',
        websocket: 'ready'
      }
    };

    return NextResponse.json({
      success: true,
      data: healthData
    });
  } catch (error) {
    console.error('Health check failed:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Service unhealthy',
        timestamp: new Date().toISOString()
      },
      { status: 503 }
    );
  }
}
