/**
 * Alerts SSE API Route
 * Using SSE Endpoint Factory for consistency
 */

import { SSEEndpointFactory } from '@/services/sse-endpoint-factory.service';

// Create alerts SSE endpoint using factory
export const GET = SSEEndpointFactory.createAlertsEndpoint();
export const OPTIONS = SSEEndpointFactory.createOptionsHandler();
