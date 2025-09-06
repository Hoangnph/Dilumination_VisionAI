/**
 * Movements SSE API Route
 * Using SSE Endpoint Factory for consistency
 */

import { SSEEndpointFactory } from '@/services/sse-endpoint-factory.service';

// Create movements SSE endpoint using factory
export const GET = SSEEndpointFactory.createMovementsEndpoint();
export const OPTIONS = SSEEndpointFactory.createOptionsHandler();
