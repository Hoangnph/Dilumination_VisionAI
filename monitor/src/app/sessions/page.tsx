'use client';

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Pagination,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Schedule as ScheduleIcon,
  People as PeopleIcon,
} from '@mui/icons-material';
import DashboardLayout from '@/components/DashboardLayout';
import { useSessionsSSE } from '@/hooks/useSSE';
import { Session } from '@/types/database';

export default function SessionsPage() {
  const [page, setPage] = React.useState(1);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [statusFilter, setStatusFilter] = React.useState('all');
  
  const { sessions, loading, isConnected, error, refetch } = useSessionsSSE();

  // Debug logging
  React.useEffect(() => {
    console.log('=== SESSIONS PAGE DEBUG (SSE) ===');
    console.log('Sessions data:', sessions);
    console.log('Loading:', loading);
    console.log('Error:', error);
    console.log('SSE Connected:', isConnected);
    console.log('Sessions length:', sessions?.length || 0);
  }, [sessions, loading, error, isConnected]);

  // Add component mount debug
  React.useEffect(() => {
    console.log('=== SESSIONS PAGE MOUNTED ===');
  }, []);

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const handleViewSession = (sessionId: string) => {
    console.log('View session:', sessionId);
    // TODO: Navigate to session details
  };

  const handleStopSession = (sessionId: string) => {
    console.log('Stop session:', sessionId);
    // TODO: Implement stop session
  };

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

  const getDuration = (session: Session) => {
    if (session.end_time) {
      const start = new Date(session.start_time);
      const end = new Date(session.end_time);
      const diffMs = end.getTime() - start.getTime();
      const diffMins = Math.floor(diffMs / (1000 * 60));
      return `${diffMins}m`;
    }
    return 'Ongoing';
  };

  const filteredSessions = sessions?.filter((session: Session) => {
    const matchesSearch = session.session_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         session.input_source.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || session.status === statusFilter;
    return matchesSearch && matchesStatus;
  }) || [];

  return (
    <DashboardLayout>
      <Box sx={{ p: 3 }}>
        <Box mb={4}>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            Session Management
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body1" color="text.secondary">
              View and manage all people counting sessions
            </Typography>
            <Chip 
              label={isConnected ? 'Live' : 'Disconnected'} 
              color={isConnected ? 'success' : 'error'}
              size="small"
              icon={isConnected ? <PlayIcon /> : <StopIcon />}
            />
          </Box>
        </Box>

        {/* Filters */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
              <TextField
                placeholder="Search sessions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
                sx={{ minWidth: 200 }}
              />
              
              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  label="Status"
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="error">Error</MenuItem>
                </Select>
              </FormControl>

              <Box sx={{ flexGrow: 1 }} />
              
              <Tooltip title="Refresh Sessions">
                <IconButton onClick={refetch} disabled={loading}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </CardContent>
        </Card>

        {/* Sessions Table */}
        <Card>
          <CardContent>
            <TableContainer component={Paper} sx={{ backgroundColor: 'transparent' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Session Name</TableCell>
                    <TableCell>Source</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Start Time</TableCell>
                    <TableCell>Duration</TableCell>
                    <TableCell>People Count</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography variant="body2" color="text.secondary">
                          Loading sessions...
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : error ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography variant="body2" color="error">
                          Error: {error}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : filteredSessions.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Box py={4}>
                          <PeopleIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                          <Typography variant="h6" color="text.secondary">
                            No sessions found
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {searchTerm || statusFilter !== 'all' 
                              ? 'Try adjusting your search criteria'
                              : 'Start a people counting session to see data here'
                            }
                          </Typography>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredSessions.map((session: Session) => (
                      <TableRow key={session.id} hover>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {session.session_name}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {session.input_source}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={getStatusIcon(session.status)}
                            label={session.status}
                            color={getStatusColor(session.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {formatTime(session.start_time)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {getDuration(session)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box display="flex" gap={1}>
                            <Typography variant="body2" color="success.main">
                              +{session.total_people_entered}
                            </Typography>
                            <Typography variant="body2" color="error.main">
                              -{session.total_people_exited}
                            </Typography>
                            <Typography variant="body2" color="primary.main">
                              ={session.current_people_count}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box display="flex" gap={1}>
                            <Tooltip title="View Details">
                              <IconButton
                                size="small"
                                onClick={() => handleViewSession(session.id)}
                              >
                                <ViewIcon />
                              </IconButton>
                            </Tooltip>
                            {session.status === 'active' && (
                              <Tooltip title="Stop Session">
                                <IconButton
                                  size="small"
                                  onClick={() => handleStopSession(session.id)}
                                  color="error"
                                >
                                  <StopIcon />
                                </IconButton>
                              </Tooltip>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Pagination */}
            {sessions && sessions.total > 10 && (
              <Box display="flex" justifyContent="center" mt={3}>
                <Pagination
                  count={Math.ceil(sessions.total / 10)}
                  page={page}
                  onChange={handlePageChange}
                  color="primary"
                />
              </Box>
            )}
          </CardContent>
        </Card>
      </Box>
    </DashboardLayout>
  );
}
