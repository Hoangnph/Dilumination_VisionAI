import { NextRequest, NextResponse } from 'next/server';
import { getSessions } from '@/lib/db';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '100');
    
    // console.log(`[API Sessions] Fetching sessions - page: ${page}, limit: ${limit}`);
    
    // Use the database service function instead of direct client access
    const result = await getSessions(page, limit);
    
    if (result.success) {
      // console.log(`[API Sessions] Successfully fetched ${result.data.data.length} sessions`);
      return NextResponse.json({
        success: true,
        data: result.data
      });
    } else {
      // console.error('[API Sessions] Failed to fetch sessions:', result.error);
      return NextResponse.json({
        success: false,
        error: result.error || 'Failed to fetch sessions'
      }, { status: 500 });
    }
  } catch (error) {
    // console.error('[API Sessions] Error fetching sessions:', error);
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { session_name, input_source, status } = body;
    
    // console.log(`[API Sessions] Creating session: ${session_name}`);
    
    // Use database service for insertion
    const insertQuery = `
      INSERT INTO sessions (id, session_name, input_source, status, created_at, updated_at)
      VALUES (gen_random_uuid(), $1, $2, $3, NOW(), NOW())
      RETURNING *
    `;
    
    // Import executeQuery from db.ts
    const { executeQuery } = await import('@/lib/db');
    const result = await executeQuery(insertQuery, [session_name, input_source, status]);
    
    if (result.success && result.data.length > 0) {
      // console.log(`[API Sessions] Successfully created session: ${result.data[0].session_name}`);
      return NextResponse.json({
        success: true,
        data: result.data[0]
      });
    } else {
      // console.error('[API Sessions] Failed to create session:', result.error);
      return NextResponse.json({
        success: false,
        error: result.error || 'Failed to create session'
      }, { status: 500 });
    }
  } catch (error) {
    // console.error('[API Sessions] Error creating session:', error);
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}