'use client';

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  IconButton,
  Tooltip,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  People as PeopleIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip } from 'recharts';
import { RealtimeMetrics } from '@/types/database';

interface MetricsCardProps {
  title: string;
  value: number;
  subtitle?: string;
  icon: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  loading?: boolean;
}

function MetricsCard({
  title,
  value,
  subtitle,
  icon,
  color = 'primary',
  trend,
  trendValue,
  loading = false,
}: MetricsCardProps) {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUpIcon sx={{ color: 'success.main', fontSize: 16 }} />;
      case 'down':
        return <TrendingDownIcon sx={{ color: 'error.main', fontSize: 16 }} />;
      default:
        return null;
    }
  };

  return (
    <Card
      sx={{
        height: '100%',
        border: '1px solid',
        borderColor: 'divider',
        background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.1) 0%, rgba(25, 118, 210, 0.05) 100%)',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 4,
        },
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box
            sx={{
              p: 1,
              borderRadius: 2,
              backgroundColor: `${color}.main`,
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
          {trend && (
            <Box display="flex" alignItems="center" gap={0.5}>
              {getTrendIcon()}
              <Typography variant="caption" sx={{ fontWeight: 600 }}>
                {trendValue}
              </Typography>
            </Box>
          )}
        </Box>

        <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
          {loading ? (
            <LinearProgress sx={{ height: 8, borderRadius: 4 }} />
          ) : (
            value
          )}
        </Typography>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {title}
        </Typography>

        {subtitle && (
          <Typography variant="caption" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

interface PeopleFlowChartProps {
  data: { name: string; value: number; color: string }[];
  loading?: boolean;
}

function PeopleFlowChart({ data, loading = false }: PeopleFlowChartProps) {
  return (
    <Card
      sx={{
        height: '100%',
        border: '1px solid',
        borderColor: 'divider',
        background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.05) 0%, rgba(25, 118, 210, 0.02) 100%)',
      }}
    >
      <CardContent>
        <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
          People Flow Distribution
        </Typography>
        
        <Box sx={{ height: 200, width: '100%' }}>
          {loading ? (
            <Box 
              display="flex" 
              alignItems="center" 
              justifyContent="center" 
              height="100%"
            >
              <LinearProgress sx={{ width: '100%' }} />
            </Box>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{
                    backgroundColor: '#1a1a1a',
                    border: '1px solid #333',
                    borderRadius: '8px',
                    color: '#fff',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </Box>

        <Box mt={2} display="flex" flexWrap="wrap" gap={1}>
          {data.map((item, index) => (
            <Box key={item.name} display="flex" alignItems="center" gap={0.5}>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  backgroundColor: item.color,
                  borderRadius: '50%',
                }}
              />
              <Typography variant="caption" color="text.secondary">
                {item.name}: {item.value}
              </Typography>
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
}

interface HourlyActivityChartProps {
  data: { hour: string; people: number }[];
  loading?: boolean;
}

function HourlyActivityChart({ data, loading = false }: HourlyActivityChartProps) {
  return (
    <Card
      sx={{
        height: '100%',
        border: '1px solid',
        borderColor: 'divider',
        background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.05) 0%, rgba(25, 118, 210, 0.02) 100%)',
      }}
    >
      <CardContent>
        <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
          Hourly Activity
        </Typography>
        
        <Box sx={{ height: 200, width: '100%' }}>
          {loading ? (
            <Box 
              display="flex" 
              alignItems="center" 
              justifyContent="center" 
              height="100%"
            >
              <LinearProgress sx={{ width: '100%' }} />
            </Box>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis 
                  dataKey="hour" 
                  stroke="#666"
                  fontSize={12}
                />
                <YAxis stroke="#666" fontSize={12} />
                <RechartsTooltip 
                  contentStyle={{
                    backgroundColor: '#1a1a1a',
                    border: '1px solid #333',
                    borderRadius: '8px',
                    color: '#fff',
                  }}
                />
                <Bar 
                  dataKey="people" 
                  fill="#1976d2"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}

interface LiveMetricsProps {
  metrics: RealtimeMetrics[];
  loading: boolean;
  onRefresh?: () => void;
}

export default function LiveMetrics({
  metrics,
  loading,
  onRefresh,
}: LiveMetricsProps) {
  const latestMetrics = metrics[metrics.length - 1] || null;

  const peopleFlowData = [
    { name: 'Entered', value: latestMetrics?.people_entered_last_minute || 0, color: '#4caf50' },
    { name: 'Exited', value: latestMetrics?.people_exited_last_minute || 0, color: '#f44336' },
    { name: 'Current', value: latestMetrics?.current_people_count || 0, color: '#2196f3' },
  ];

  const hourlyData = [
    { hour: '00:00', people: 12 },
    { hour: '01:00', people: 8 },
    { hour: '02:00', people: 5 },
    { hour: '03:00', people: 3 },
    { hour: '04:00', people: 2 },
    { hour: '05:00', people: 4 },
    { hour: '06:00', people: 15 },
    { hour: '07:00', people: 28 },
    { hour: '08:00', people: 45 },
    { hour: '09:00', people: 52 },
    { hour: '10:00', people: 48 },
    { hour: '11:00', people: 41 },
  ];

  return (
    <Box>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
          Live Metrics
        </Typography>
        {onRefresh && (
          <Tooltip title="Refresh Metrics">
            <IconButton onClick={onRefresh} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        )}
      </Box>

      <Box display="flex" flexWrap="wrap" gap={3} mb={4}>
        <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
          <MetricsCard
            title="People Entered"
            value={latestMetrics?.people_entered_last_minute || 0}
            subtitle="Last minute"
            icon={<TrendingUpIcon />}
            color="success"
            loading={loading}
            trend="up"
            trendValue="Live"
          />
        </Box>

        <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
          <MetricsCard
            title="People Exited"
            value={latestMetrics?.people_exited_last_minute || 0}
            subtitle="Last minute"
            icon={<TrendingDownIcon />}
            color="error"
            loading={loading}
            trend="down"
            trendValue="Live"
          />
        </Box>

        <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
          <MetricsCard
            title="Current Count"
            value={latestMetrics?.current_people_count || 0}
            subtitle="Inside now"
            icon={<PeopleIcon />}
            color="primary"
            loading={loading}
            trend="neutral"
            trendValue="Live"
          />
        </Box>

        <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
          <MetricsCard
            title="Processing FPS"
            value={Math.round(latestMetrics?.average_processing_fps || 0)}
            subtitle="Average FPS"
            icon={<ScheduleIcon />}
            color="secondary"
            loading={loading}
            trend="up"
            trendValue="30+"
          />
        </Box>
      </Box>

      <Box display="flex" flexWrap="wrap" gap={3}>
        <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
          <PeopleFlowChart data={peopleFlowData} loading={loading} />
        </Box>

        <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
          <HourlyActivityChart data={hourlyData} loading={loading} />
        </Box>
      </Box>
    </Box>
  );
}
