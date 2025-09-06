'use client';

import React from 'react';
import { Box, Container, Typography } from '@mui/material';
import DashboardLayout from '@/components/DashboardLayout';
import RealTimeChart from '@/components/charts/RealTimeChart';
import LiveMetrics from '@/components/charts/LiveMetrics';
import { useRealtimeMetrics, useActiveSessions } from '@/hooks/useDatabase';

export default function LiveMonitoringPage() {
  const { metrics, loading: metricsLoading, refetch: refetchMetrics } = useRealtimeMetrics();
  const { sessions, refetch: refetchSessions } = useActiveSessions();

  const handleRefreshAll = () => {
    refetchMetrics();
    refetchSessions();
  };

  // Transform metrics data for charts
  const chartData = React.useMemo(() => {
    if (!metrics || metrics.length === 0) return [];

    const peopleEnteredData = metrics.map(metric => ({
      timestamp: metric.timestamp,
      value: metric.people_entered_last_minute,
    }));

    const peopleExitedData = metrics.map(metric => ({
      timestamp: metric.timestamp,
      value: metric.people_exited_last_minute,
    }));

    const currentCountData = metrics.map(metric => ({
      timestamp: metric.timestamp,
      value: metric.current_people_count,
    }));

    return [
      {
        label: 'People Entered',
        data: peopleEnteredData,
        color: '#4caf50',
      },
      {
        label: 'People Exited',
        data: peopleExitedData,
        color: '#f44336',
      },
      {
        label: 'Current Count',
        data: currentCountData,
        color: '#2196f3',
      },
    ];
  }, [metrics]);

  const activeSession = sessions.find(session => session.status === 'active');

  return (
    <DashboardLayout>
      <Container maxWidth="xl">
        <Box mb={4}>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            Live Monitoring
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real-time people counting metrics and analytics
          </Typography>
        </Box>

        <Box mb={4}>
          <LiveMetrics
            metrics={metrics}
            loading={metricsLoading}
            onRefresh={handleRefreshAll}
          />
        </Box>

        <Box display="flex" flexWrap="wrap" gap={3} mb={4}>
          <Box sx={{ flex: '1 1 400px', minWidth: '400px' }}>
            <RealTimeChart
              title="People Flow Over Time"
              data={chartData}
              loading={metricsLoading}
              onRefresh={refetchMetrics}
              height={350}
              type="area"
            />
          </Box>

          <Box sx={{ flex: '1 1 400px', minWidth: '400px' }}>
            <RealTimeChart
              title="Current People Count"
              data={chartData.filter(item => item.label === 'Current Count')}
              loading={metricsLoading}
              onRefresh={refetchMetrics}
              height={350}
              type="line"
            />
          </Box>
        </Box>

        <Box display="flex" flexWrap="wrap" gap={3}>
          <Box sx={{ flex: '1 1 400px', minWidth: '400px' }}>
            <RealTimeChart
              title="Entry Rate"
              data={chartData.filter(item => item.label === 'People Entered')}
              loading={metricsLoading}
              onRefresh={refetchMetrics}
              height={300}
              type="line"
            />
          </Box>

          <Box sx={{ flex: '1 1 400px', minWidth: '400px' }}>
            <RealTimeChart
              title="Exit Rate"
              data={chartData.filter(item => item.label === 'People Exited')}
              loading={metricsLoading}
              onRefresh={refetchMetrics}
              height={300}
              type="line"
            />
          </Box>
        </Box>

        {activeSession && (
          <Box mt={4}>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
              Active Session: {activeSession.session_name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Source: {activeSession.input_source} | 
              Started: {new Date(activeSession.start_time).toLocaleString()} |
              Duration: {Math.floor((Date.now() - new Date(activeSession.start_time).getTime()) / (1000 * 60))} minutes
            </Typography>
          </Box>
        )}
      </Container>
    </DashboardLayout>
  );
}
