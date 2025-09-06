/**
 * Sessions SSE API Route
 * Using SSE Endpoint Factory for consistency
 */

import { SSEEndpointFactory } from '@/services/sse-endpoint-factory.service';

// Create sessions SSE endpoint using factory
export const GET = SSEEndpointFactory.createSessionsEndpoint();
export const OPTIONS = SSEEndpointFactory.createOptionsHandler();
