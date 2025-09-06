'use client';

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  People as PeopleIcon,
  Schedule as ScheduleIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreIcon,
} from '@mui/icons-material';
import { Session } from '@/types/database';

interface SessionCardProps {
  session: Session;
  onViewDetails?: (sessionId: string) => void;
  onStopSession?: (sessionId: string) => void;
}

function SessionCard({ session, onViewDetails, onStopSession }: SessionCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'completed':
        return 'primary';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <PlayIcon sx={{ fontSize: 16 }} />;
      case 'completed':
        return <StopIcon sx={{ fontSize: 16 }} />;
      case 'error':
        return <StopIcon sx={{ fontSize: 16 }} />;
      default:
        return <ScheduleIcon sx={{ fontSize: 16 }} />;
    }
  };

  const formatTime = (timeString: string) => {
    return new Date(timeString).toLocaleString();
  };

  const getDuration = () => {
    if (session.end_time) {
      const start = new Date(session.start_time);
      const end = new Date(session.end_time);
      const diffMs = end.getTime() - start.getTime();
      const diffMins = Math.floor(diffMs / (1000 * 60));
      return `${diffMins}m`;
    }
    return 'Ongoing';
  };

  return (
    <Card
      sx={{
        height: '100%',
        border: '1px solid',
        borderColor: 'divider',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 4,
        },
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="h6" sx={{ fontWeight: 'bold', flexGrow: 1 }}>
            {session.session_name}
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            <Chip
              icon={getStatusIcon(session.status)}
              label={session.status}
              color={getStatusColor(session.status)}
              size="small"
            />
            <IconButton size="small">
              <MoreIcon />
            </IconButton>
          </Box>
        </Box>

        <Box mb={2}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Source: {session.input_source}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Started: {formatTime(session.start_time)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Duration: {getDuration()}
          </Typography>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box display="flex" justifyContent="space-around" gap={2}>
          <Box textAlign="center" flex={1}>
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>
              {session.total_people_entered}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Entered
            </Typography>
          </Box>
          <Box textAlign="center" flex={1}>
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'error.main' }}>
              {session.total_people_exited}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Exited
            </Typography>
          </Box>
          <Box textAlign="center" flex={1}>
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
              {session.current_people_count}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Current
            </Typography>
          </Box>
        </Box>

        <Box mt={2} display="flex" gap={1}>
          <Tooltip title="View Details">
            <IconButton
              size="small"
              onClick={() => onViewDetails?.(session.id)}
              sx={{ flexGrow: 1 }}
            >
              <PeopleIcon />
            </IconButton>
          </Tooltip>
          {session.status === 'active' && (
            <Tooltip title="Stop Session">
              <IconButton
                size="small"
                onClick={() => onStopSession?.(session.id)}
                color="error"
                sx={{ flexGrow: 1 }}
              >
                <StopIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}

interface ActiveSessionsProps {
  sessions: Session[];
  loading: boolean;
  isConnected?: boolean;
  onRefresh?: () => void;
  onViewDetails?: (sessionId: string) => void;
  onStopSession?: (sessionId: string) => void;
}

export default function ActiveSessions({
  sessions,
  loading,
  isConnected,
  onRefresh,
  onViewDetails,
  onStopSession,
}: ActiveSessionsProps) {
  const activeSessions = sessions.filter(s => s.status === 'active');
  const recentSessions = sessions.filter(s => s.status !== 'active').slice(0, 3);

  return (
    <Box>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
          Sessions
        </Typography>
        {onRefresh && (
          <Tooltip title="Refresh Sessions">
            <IconButton onClick={onRefresh} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        )}
      </Box>

      {activeSessions.length > 0 && (
        <Box mb={4}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Active Sessions ({activeSessions.length})
            </Typography>
            {isConnected !== undefined && (
              <Chip 
                label={isConnected ? 'Live' : 'Disconnected'} 
                color={isConnected ? 'success' : 'error'}
                size="small"
                icon={isConnected ? <PlayIcon /> : <StopIcon />}
              />
            )}
          </Box>
          <Box display="flex" flexWrap="wrap" gap={3}>
            {activeSessions.map((session) => (
              <Box key={session.id} sx={{ flex: '1 1 300px', minWidth: '300px' }}>
                <SessionCard
                  session={session}
                  onViewDetails={onViewDetails}
                  onStopSession={onStopSession}
                />
              </Box>
            ))}
          </Box>
        </Box>
      )}

      {recentSessions.length > 0 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            Recent Sessions
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={3}>
            {recentSessions.map((session) => (
              <Box key={session.id} sx={{ flex: '1 1 300px', minWidth: '300px' }}>
                <SessionCard
                  session={session}
                  onViewDetails={onViewDetails}
                  onStopSession={onStopSession}
                />
              </Box>
            ))}
          </Box>
        </Box>
      )}

      {sessions.length === 0 && !loading && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <PeopleIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No sessions found
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Start a people counting session to see data here
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
