import { NextRequest, NextResponse } from 'next/server';
import { databaseService } from '@/lib/database';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  try {
    const { sessionId } = await params;
    const { searchParams } = new URL(request.url);
    const hours = parseInt(searchParams.get('hours') || '24');

    const response = await databaseService.getMetricsHistory(sessionId, hours);
    
    if (response.success) {
      return NextResponse.json(response);
    } else {
      return NextResponse.json(
        { success: false, error: response.error },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Error fetching metrics history:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}
