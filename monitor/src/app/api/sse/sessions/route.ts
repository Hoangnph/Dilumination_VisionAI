import { NextRequest } from 'next/server';
import { dbListener, createSSEResponse, createSSEMessage, encodeSSEMessage } from '@/lib/sse';

// Sessions SSE endpoint
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const sessionId = searchParams.get('session_id');

  const stream = new ReadableStream({
    start(controller) {
      const encoder = new TextEncoder();
      
      // Send initial connection message
      const connectionMessage = createSSEMessage('connection', null, 'Connected to sessions SSE');
      controller.enqueue(encoder.encode(encodeSSEMessage(connectionMessage)));

      // Listen for session changes
      const handleSessionChange = (data: any) => {
        // Filter by session_id if provided
        if (sessionId && data.data?.id !== sessionId) {
          return;
        }

        const message = createSSEMessage('data', data);
        controller.enqueue(encoder.encode(encodeSSEMessage(message)));
      };

      // Start listening
      dbListener.listen('session_changes', handleSessionChange)
        .catch(error => {
          console.error('Error starting session listener:', error);
          const errorMessage = createSSEMessage('error', null, 'Failed to start session listener', error.message);
          controller.enqueue(encoder.encode(encodeSSEMessage(errorMessage)));
        });

      // Handle client disconnect
      request.signal.addEventListener('abort', async () => {
        await dbListener.unlisten('session_changes', handleSessionChange);
        controller.close();
      });
    }
  });

  return createSSEResponse(stream);
}
