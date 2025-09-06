import { NextRequest, NextResponse } from 'next/server';
import { databaseService } from '@/lib/database';

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const response = await databaseService.resolveAlert(id);
    
    if (response.success) {
      return NextResponse.json(response);
    } else {
      return NextResponse.json(
        { success: false, error: response.error },
        { status: 400 }
      );
    }
  } catch (error) {
    console.error('Error resolving alert:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}
