import { NextRequest } from 'next/server';
import { dbListener, createSSEResponse, createSSEMessage, encodeSSEMessage } from '@/lib/sse';

// Movements SSE endpoint
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const sessionId = searchParams.get('session_id');

  const stream = new ReadableStream({
    start(controller) {
      const encoder = new TextEncoder();
      
      // Send initial connection message
      const connectionMessage = createSSEMessage('connection', null, 'Connected to movements SSE');
      controller.enqueue(encoder.encode(encodeSSEMessage(connectionMessage)));

      // Listen for movement changes
      const handleMovementChange = (data: any) => {
        // Filter by session_id if provided
        if (sessionId && data.data?.session_id !== sessionId) {
          return;
        }

        const message = createSSEMessage('data', data);
        controller.enqueue(encoder.encode(encodeSSEMessage(message)));
      };

      // Start listening
      dbListener.listen('movement_changes', handleMovementChange)
        .catch(error => {
          console.error('Error starting movement listener:', error);
          const errorMessage = createSSEMessage('error', null, 'Failed to start movement listener', error.message);
          controller.enqueue(encoder.encode(encodeSSEMessage(errorMessage)));
        });

      // Handle client disconnect
      request.signal.addEventListener('abort', async () => {
        await dbListener.unlisten('movement_changes', handleMovementChange);
        controller.close();
      });
    }
  });

  return createSSEResponse(stream);
}
