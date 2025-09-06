/**
 * Metrics SSE API Route
 * Using SSE Endpoint Factory for consistency
 */

import { SSEEndpointFactory } from '@/services/sse-endpoint-factory.service';

// Create metrics SSE endpoint using factory
export const GET = SSEEndpointFactory.createMetricsEndpoint();
export const OPTIONS = SSEEndpointFactory.createOptionsHandler();
