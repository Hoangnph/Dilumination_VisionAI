import { NextRequest, NextResponse } from 'next/server';
import { dbListener } from '@/lib/sse';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_name, input_source, status } = body;
    
    // Insert session into database
    const insertQuery = `
      INSERT INTO sessions (id, session_name, input_source, status, created_at, updated_at)
      VALUES (gen_random_uuid(), $1, $2, $3, NOW(), NOW())
      RETURNING *
    `;
    
    // This will trigger the database trigger and SSE notification
    const result = await dbListener.client?.query(insertQuery, [session_name, input_source, status]);
    
    return NextResponse.json({
      success: true,
      data: result?.rows[0]
    });
  } catch (error) {
    console.error('Error inserting session:', error);
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}