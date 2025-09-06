import { NextRequest, NextResponse } from 'next/server';
import { dbListener } from '@/lib/sse';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '100');
    const offset = (page - 1) * limit;
    
    // Get sessions from database
    const query = `
      SELECT * FROM sessions 
      ORDER BY created_at DESC 
      LIMIT $1 OFFSET $2
    `;
    
    const result = await dbListener.client?.query(query, [limit, offset]);
    
    // Get total count
    const countQuery = 'SELECT COUNT(*) FROM sessions';
    const countResult = await dbListener.client?.query(countQuery);
    const total = parseInt(countResult?.rows[0]?.count || '0');
    
    return NextResponse.json({
      success: true,
      data: {
        data: result?.rows || [],
        pagination: {
          page,
          limit,
          total,
          totalPages: Math.ceil(total / limit)
        }
      }
    });
  } catch (error) {
    console.error('Error fetching sessions:', error);
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