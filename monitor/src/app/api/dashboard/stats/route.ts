import { NextResponse } from 'next/server';
import { getDashboardStats } from '@/lib/db';

export async function GET() {
  try {
    const result = await getDashboardStats();
    
    if (result.success) {
      return NextResponse.json({
        success: true,
        data: result.data[0]
      });
    } else {
      return NextResponse.json(
        { success: false, error: 'Failed to fetch dashboard stats' },
        { status: 500 }
      );
    }
  } catch (error) {
    // console.error('Error fetching dashboard stats:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}
