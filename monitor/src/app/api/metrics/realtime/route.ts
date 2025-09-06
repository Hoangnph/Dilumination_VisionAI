import { NextRequest, NextResponse } from 'next/server';
import { getRealtimeMetrics } from '@/lib/db';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('session_id');

    const result = await getRealtimeMetrics(sessionId || undefined);
    
    if (result.success) {
      return NextResponse.json({
        success: true,
        data: result.data
      });
    } else {
      return NextResponse.json(
        { success: false, error: 'Failed to fetch realtime metrics' },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Error fetching realtime metrics:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}
