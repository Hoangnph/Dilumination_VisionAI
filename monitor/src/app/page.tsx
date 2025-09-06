'use client';

import React from 'react';
import { Box, Container, Typography } from '@mui/material';
import DashboardLayout from '@/components/DashboardLayout';
import DashboardStatsCards from '@/components/dashboard/StatsCards';
import ActiveSessions from '@/components/dashboard/ActiveSessions';
import { useDashboardStats } from '@/hooks/useDatabase';
import { useSessionsSSE } from '@/hooks/useSSE';

export default function DashboardPage() {
  const { stats, loading: statsLoading, refetch: refetchStats } = useDashboardStats();
  const { sessions, loading: sessionsLoading, isConnected } = useSessionsSSE();

  const handleRefreshAll = () => {
    refetchStats();
    // SSE automatically updates sessions
  };

  const handleViewDetails = (sessionId: string) => {
    console.log('View details for session:', sessionId);
    // TODO: Navigate to session details page
  };

  const handleStopSession = (sessionId: string) => {
    console.log('Stop session:', sessionId);
    // TODO: Implement stop session functionality
  };

  return (
    <DashboardLayout>
      <Container maxWidth="xl">
        <Box mb={4}>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            People Counter Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real-time monitoring and analytics for people counting system
          </Typography>
        </Box>

        <Box mb={4}>
          <DashboardStatsCards
            stats={stats}
            loading={statsLoading}
            onRefresh={handleRefreshAll}
          />
        </Box>

        <Box>
          <ActiveSessions
            sessions={sessions}
            loading={sessionsLoading}
            isConnected={isConnected}
            onViewDetails={handleViewDetails}
            onStopSession={handleStopSession}
          />
        </Box>
      </Container>
    </DashboardLayout>
  );
}