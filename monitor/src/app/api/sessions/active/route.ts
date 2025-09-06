import { NextResponse } from 'next/server';
import { getActiveSessions } from '@/lib/db';

export async function GET() {
  try {
    const result = await getActiveSessions();
    
    if (result.success) {
      return NextResponse.json({
        success: true,
        data: result.data
      });
    } else {
      return NextResponse.json(
        { success: false, error: 'Failed to fetch active sessions' },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Error fetching active sessions:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}
