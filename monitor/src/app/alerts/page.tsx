'use client';

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  AlertTitle,
  Snackbar,
  Grid,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import DashboardLayout from '@/components/DashboardLayout';
import { useAlerts } from '@/hooks/useDatabase';
import { AlertLog } from '@/types/database';

export default function AlertsPage() {
  const [snackbarOpen, setSnackbarOpen] = React.useState(false);
  const [snackbarMessage, setSnackbarMessage] = React.useState('');
  
  const { alerts, loading, refetch } = useAlerts(undefined, false, 1, 50);

  const handleResolveAlert = async (alertId: string) => {
    try {
      // TODO: Implement resolve alert API call
      console.log('Resolve alert:', alertId);
      setSnackbarMessage('Alert resolved successfully');
      setSnackbarOpen(true);
      refetch();
    } catch (error) {
      console.error('Error resolving alert:', error);
      setSnackbarMessage('Failed to resolve alert');
      setSnackbarOpen(true);
    }
  };

  const getAlertIcon = (alertType: string) => {
    switch (alertType) {
      case 'threshold_exceeded':
        return <WarningIcon sx={{ color: 'warning.main' }} />;
      case 'system_error':
        return <ErrorIcon sx={{ color: 'error.main' }} />;
      case 'performance_warning':
        return <InfoIcon sx={{ color: 'info.main' }} />;
      default:
        return <InfoIcon sx={{ color: 'text.secondary' }} />;
    }
  };

  const getAlertSeverity = (alertType: string) => {
    switch (alertType) {
      case 'threshold_exceeded':
        return 'warning';
      case 'system_error':
        return 'error';
      case 'performance_warning':
        return 'info';
      default:
        return 'info';
    }
  };

  const formatTime = (timeString: string) => {
    return new Date(timeString).toLocaleString();
  };

  const activeAlerts = alerts?.data?.filter((alert: AlertLog) => !alert.resolved) || [];
  const resolvedAlerts = alerts?.data?.filter((alert: AlertLog) => alert.resolved) || [];

  return (
    <DashboardLayout>
      <Box sx={{ p: 3 }}>
        <Box mb={4}>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            Alert Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Monitor and manage system alerts and notifications
          </Typography>
        </Box>

        {/* Alert Summary */}
        <Box display="flex" flexWrap="wrap" gap={3} mb={4}>
          <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
            <Card sx={{ border: '1px solid', borderColor: 'warning.main' }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                  <WarningIcon sx={{ color: 'warning.main', fontSize: 32 }} />
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                      {activeAlerts.filter((a: AlertLog) => a.alert_type === 'threshold_exceeded').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Threshold Alerts
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>

          <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
            <Card sx={{ border: '1px solid', borderColor: 'error.main' }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                  <ErrorIcon sx={{ color: 'error.main', fontSize: 32 }} />
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                      {activeAlerts.filter((a: AlertLog) => a.alert_type === 'system_error').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      System Errors
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>

          <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
            <Card sx={{ border: '1px solid', borderColor: 'info.main' }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                  <InfoIcon sx={{ color: 'info.main', fontSize: 32 }} />
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                      {activeAlerts.filter((a: AlertLog) => a.alert_type === 'performance_warning').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Performance Warnings
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>

          <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
            <Card sx={{ border: '1px solid', borderColor: 'success.main' }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                  <CheckCircleIcon sx={{ color: 'success.main', fontSize: 32 }} />
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                      {resolvedAlerts.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Resolved Alerts
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Box>

        {/* Active Alerts */}
        <Box mb={4}>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
              Active Alerts ({activeAlerts.length})
            </Typography>
            <Tooltip title="Refresh Alerts">
              <IconButton onClick={refetch} disabled={loading}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>

          {loading ? (
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" align="center">
                  Loading alerts...
                </Typography>
              </CardContent>
            </Card>
          ) : activeAlerts.length === 0 ? (
            <Alert severity="success">
              <AlertTitle>No Active Alerts</AlertTitle>
              All systems are running normally.
            </Alert>
          ) : (
            <List>
              {activeAlerts.map((alert: AlertLog) => (
                <ListItem key={alert.id} divider>
                  <ListItemIcon>
                    {getAlertIcon(alert.alert_type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                          {alert.alert_message}
                        </Typography>
                        <Chip
                          label={alert.alert_type.replace('_', ' ')}
                          color={getAlertSeverity(alert.alert_type)}
                          size="small"
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Time: {formatTime(alert.alert_time)}
                        </Typography>
                        {alert.threshold_value && (
                          <Typography variant="body2" color="text.secondary">
                            Threshold: {alert.threshold_value} | Current: {alert.current_value}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                  <Box>
                    <Tooltip title="Resolve Alert">
                      <IconButton
                        onClick={() => handleResolveAlert(alert.id)}
                        color="success"
                      >
                        <CheckCircleIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </ListItem>
              ))}
            </List>
          )}
        </Box>

        {/* Resolved Alerts */}
        {resolvedAlerts.length > 0 && (
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 2 }}>
              Recently Resolved ({resolvedAlerts.length})
            </Typography>
            <List>
              {resolvedAlerts.slice(0, 10).map((alert: AlertLog) => (
                <ListItem key={alert.id} divider>
                  <ListItemIcon>
                    <CheckCircleIcon sx={{ color: 'success.main' }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                          {alert.alert_message}
                        </Typography>
                        <Chip
                          label="Resolved"
                          color="success"
                          size="small"
                        />
                      </Box>
                    }
                    secondary={
                      <Typography variant="body2" color="text.secondary">
                        Resolved: {formatTime(alert.alert_time)}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        <Snackbar
          open={snackbarOpen}
          autoHideDuration={6000}
          onClose={() => setSnackbarOpen(false)}
          message={snackbarMessage}
          action={
            <IconButton
              size="small"
              aria-label="close"
              color="inherit"
              onClick={() => setSnackbarOpen(false)}
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          }
        />
      </Box>
    </DashboardLayout>
  );
}
