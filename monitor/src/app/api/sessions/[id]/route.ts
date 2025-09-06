import { NextRequest, NextResponse } from 'next/server';
import { databaseService } from '@/lib/database';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const response = await databaseService.getSessionById(id);
    
    if (response.success) {
      return NextResponse.json(response);
    } else {
      return NextResponse.json(
        { success: false, error: response.error },
        { status: 404 }
      );
    }
  } catch (error) {
    console.error('Error fetching session:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const body = await request.json();
    const response = await databaseService.updateSession(id, body);
    
    if (response.success) {
      return NextResponse.json(response);
    } else {
      return NextResponse.json(
        { success: false, error: response.error },
        { status: 400 }
      );
    }
  } catch (error) {
    console.error('Error updating session:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}
