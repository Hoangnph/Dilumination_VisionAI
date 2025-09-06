'use client';

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  People as PeopleIcon,
  Schedule as ScheduleIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { DashboardStats } from '@/types/database';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  loading?: boolean;
}

function StatCard({
  title,
  value,
  subtitle,
  trend,
  trendValue,
  icon,
  color = 'primary',
  loading = false,
}: StatCardProps) {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUpIcon sx={{ color: 'success.main' }} />;
      case 'down':
        return <TrendingDownIcon sx={{ color: 'error.main' }} />;
      default:
        return null;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'success.main';
      case 'down':
        return 'error.main';
      default:
        return 'text.secondary';
    }
  };

  return (
    <Card
      sx={{
        height: '100%',
        background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.1) 0%, rgba(25, 118, 210, 0.05) 100%)',
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
          <Box
            sx={{
              p: 1.5,
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
              <Typography
                variant="caption"
                sx={{ color: getTrendColor(), fontWeight: 600 }}
              >
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

interface DashboardStatsCardsProps {
  stats: DashboardStats | null;
  loading: boolean;
  onRefresh?: () => void;
}

export default function DashboardStatsCards({
  stats,
  loading,
  onRefresh,
}: DashboardStatsCardsProps) {
  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const formatUptime = (hours: number) => {
    const days = Math.floor(hours / 24);
    const hrs = hours % 24;
    return days > 0 ? `${days}d ${hrs}h` : `${hrs}h`;
  };

  return (
    <Box>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
          System Overview
        </Typography>
        {onRefresh && (
          <Tooltip title="Refresh Data">
            <IconButton onClick={onRefresh} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        )}
      </Box>

      <Box display="flex" flexWrap="wrap" gap={3}>
        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <StatCard
            title="Total Sessions"
            value={stats?.total_sessions || 0}
            subtitle="All time sessions"
            icon={<ScheduleIcon />}
            color="primary"
            loading={loading}
          />
        </Box>

        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <StatCard
            title="Active Sessions"
            value={stats?.active_sessions || 0}
            subtitle="Currently running"
            icon={<PeopleIcon />}
            color="success"
            loading={loading}
            trend={stats?.active_sessions && stats.active_sessions > 0 ? 'up' : 'neutral'}
            trendValue={stats?.active_sessions ? 'Live' : 'None'}
          />
        </Box>

        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <StatCard
            title="People Today"
            value={stats?.total_people_today || 0}
            subtitle="Total count today"
            icon={<TrendingUpIcon />}
            color="secondary"
            loading={loading}
            trend="up"
            trendValue="+12%"
          />
        </Box>

        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <StatCard
            title="Peak Hour"
            value={stats?.peak_hour || 'N/A'}
            subtitle="Busiest time"
            icon={<TrendingUpIcon />}
            color="warning"
            loading={loading}
          />
        </Box>

        <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
          <StatCard
            title="Avg Session Duration"
            value={formatDuration(stats?.average_session_duration || 0)}
            subtitle="Average time per session"
            icon={<ScheduleIcon />}
            color="primary"
            loading={loading}
          />
        </Box>

        <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
          <StatCard
            title="System Uptime"
            value={formatUptime(stats?.system_uptime || 0)}
            subtitle="Continuous operation"
            icon={<TrendingUpIcon />}
            color="success"
            loading={loading}
            trend="up"
            trendValue="99.9%"
          />
        </Box>
      </Box>
    </Box>
  );
}
