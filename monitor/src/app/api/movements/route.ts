import { NextRequest, NextResponse } from 'next/server';
import { databaseService } from '@/lib/database';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('session_id');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '50');

    const response = await databaseService.getMovements(
      sessionId || undefined, 
      page, 
      limit
    );
    
    if (response.success) {
      return NextResponse.json(response);
    } else {
      return NextResponse.json(
        { success: false, error: response.error },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Error fetching movements:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}
