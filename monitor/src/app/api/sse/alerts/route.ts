import { NextRequest } from 'next/server';
import { dbListener, createSSEResponse, createSSEMessage, encodeSSEMessage } from '@/lib/sse';

// Alerts SSE endpoint
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const sessionId = searchParams.get('session_id');
  const resolved = searchParams.get('resolved');

  const stream = new ReadableStream({
    start(controller) {
      const encoder = new TextEncoder();
      let isClosed = false;
      
      // Send initial connection message
      const connectionMessage = createSSEMessage('connection', null, 'Connected to alerts SSE');
      controller.enqueue(encoder.encode(encodeSSEMessage(connectionMessage)));

      // Listen for alert changes
      const handleAlertChange = (data: any) => {
        // Filter by session_id if provided
        if (sessionId && data.data?.session_id !== sessionId) {
          return;
        }

        // Filter by resolved status if provided
        if (resolved !== null && data.data?.is_resolved !== (resolved === 'true')) {
          return;
        }

        if (!isClosed) {
          const message = createSSEMessage('data', data);
          controller.enqueue(encoder.encode(encodeSSEMessage(message)));
        }
      };

      // Start listening
      dbListener.listen('alert_changes', handleAlertChange)
        .catch(error => {
          console.error('Error starting alert listener:', error);
          if (!isClosed) {
            const errorMessage = createSSEMessage('error', null, 'Failed to start alert listener', error.message);
            controller.enqueue(encoder.encode(encodeSSEMessage(errorMessage)));
          }
        });

      // Handle client disconnect
      request.signal.addEventListener('abort', async () => {
        isClosed = true;
        await dbListener.unlisten('alert_changes', handleAlertChange);
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
