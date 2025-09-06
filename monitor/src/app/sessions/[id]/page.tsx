'use client';

import React from 'react';
import { Box, Container, Typography, Card, CardContent } from '@mui/material';
import DashboardLayout from '@/components/DashboardLayout';
import RealTimeChart from '@/components/charts/RealTimeChart';
import { useTimeSeriesData } from '@/hooks/useDatabase';

interface SessionDetailsPageProps {
  params: Promise<{ id: string }>;
}

export default function SessionDetailsPage({ params }: SessionDetailsPageProps) {
  return (
    <DashboardLayout>
      <Container maxWidth="xl">
        <Box mb={4}>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            Session Details
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Detailed view of session
          </Typography>
        </Box>

        <SessionDetailsContent params={params} />
      </Container>
    </DashboardLayout>
  );
}

function SessionDetailsContent({ params }: { params: Promise<{ id: string }> }) {
  const [sessionId, setSessionId] = React.useState<string>('');
  
  React.useEffect(() => {
    params.then(({ id }) => setSessionId(id));
  }, [params]);

  const { data: chartData, loading, refetch } = useTimeSeriesData(sessionId, 24);

  return (
    <Box>
      <Box display="flex" flexWrap="wrap" gap={3}>
        <Box sx={{ flex: '1 1 400px', minWidth: '400px' }}>
          <RealTimeChart
            title="Session Timeline"
            data={chartData}
            loading={loading}
            onRefresh={refetch}
            height={400}
            type="area"
          />
        </Box>
        
        <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
                Session Information
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Session ID: {sessionId}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Status: Loading...
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Duration: Loading...
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
}
