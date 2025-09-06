import { NextRequest } from 'next/server';
import { dbListener, createSSEResponse, createSSEMessage, encodeSSEMessage } from '@/lib/sse';

// Sessions SSE endpoint
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const sessionId = searchParams.get('session_id');

  const stream = new ReadableStream({
    start(controller) {
      const encoder = new TextEncoder();
      let isClosed = false;
      
      // Send initial connection message
      const connectionMessage = createSSEMessage('connection', null, 'Connected to sessions SSE');
      controller.enqueue(encoder.encode(encodeSSEMessage(connectionMessage)));

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

      // Start listening
      dbListener.listen('session_changes', handleSessionChange)
        .catch(error => {
          console.error('Error starting session listener:', error);
          if (!isClosed) {
            const errorMessage = createSSEMessage('error', null, 'Failed to start session listener', error.message);
            controller.enqueue(encoder.encode(encodeSSEMessage(errorMessage)));
          }
        });

      // Handle client disconnect
      request.signal.addEventListener('abort', async () => {
        isClosed = true;
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
