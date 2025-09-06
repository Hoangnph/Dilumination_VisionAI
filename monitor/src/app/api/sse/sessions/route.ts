import { NextRequest } from 'next/server';
import { dbListener, createSSEResponse, createSSEMessage, encodeSSEMessage } from '@/lib/sse';

// Sessions SSE endpoint
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const sessionId = searchParams.get('session_id');

  console.log(`[SSE Sessions] Client connected. Session ID filter: ${sessionId || 'none'}`);

  const stream = new ReadableStream({
    start(controller) {
      const encoder = new TextEncoder();
      let isClosed = false;
      
      // Send initial connection message
      const connectionMessage = createSSEMessage('connection', null, 'Connected to sessions SSE');
      controller.enqueue(encoder.encode(encodeSSEMessage(connectionMessage)));

      // Send heartbeat every 30 seconds to keep connection alive
      const heartbeatInterval = setInterval(() => {
        if (!isClosed) {
          const heartbeatMessage = createSSEMessage('heartbeat', null, 'Heartbeat');
          controller.enqueue(encoder.encode(encodeSSEMessage(heartbeatMessage)));
        }
      }, 30000);

      // Listen for session changes
      const handleSessionChange = (data: any) => {
        // Filter by session_id if provided
        if (sessionId && data.data?.id !== sessionId) {
          return;
        }

        if (!isClosed) {
          const message = createSSEMessage('data', data);
          controller.enqueue(encoder.encode(encodeSSEMessage(message)));
        }
      };

      // Start listening with timeout
      console.log('[SSE Sessions] Starting database listener...');
      const listenPromise = dbListener.listen('session_changes', handleSessionChange);
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Database listener timeout')), 10000);
      });
      
      Promise.race([listenPromise, timeoutPromise])
        .then(() => {
          console.log('[SSE Sessions] Database listener started successfully');
        })
        .catch(error => {
          console.error('[SSE Sessions] Error starting session listener:', error);
          if (!isClosed) {
            const errorMessage = createSSEMessage('error', null, 'Failed to start session listener', error.message);
            controller.enqueue(encoder.encode(encodeSSEMessage(errorMessage)));
          }
        });

      // Handle client disconnect
      request.signal.addEventListener('abort', async () => {
        console.log('[SSE Sessions] Client disconnected (abort signal).');
        isClosed = true;
        clearInterval(heartbeatInterval);
        await dbListener.unlisten('session_changes', handleSessionChange);
        try {
          controller.close();
        } catch (error) {
          // Controller might already be closed, ignore error
        }
      });
    }
  });

  return createSSEResponse(stream);
}

// Handle OPTIONS request for CORS
export async function OPTIONS() {
  return new Response(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Cache-Control, Content-Type',
    },
  });
}
