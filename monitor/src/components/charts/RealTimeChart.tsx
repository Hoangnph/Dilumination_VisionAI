'use client';

import React, { useEffect, useState, useRef } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  IconButton,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { TimeSeriesData, ChartDataPoint } from '@/types/database';

interface RealTimeChartProps {
  title: string;
  data: TimeSeriesData[];
  loading?: boolean;
  onRefresh?: () => void;
  height?: number;
  showLegend?: boolean;
  type?: 'line' | 'area';
}

export default function RealTimeChart({
  title,
  data,
  loading = false,
  onRefresh,
  height = 300,
  showLegend = true,
  type = 'line',
}: RealTimeChartProps) {
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // Simulate WebSocket connection status
    setIsConnected(true);
    
    // Cleanup on unmount
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const formatTooltipValue = (value: number, name: string) => {
    return [`${value}`, name];
  };

  const getChartComponent = () => {
    if (type === 'area') {
      return (
        <AreaChart data={data[0]?.data || []}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis 
            dataKey="timestamp" 
            tickFormatter={formatTime}
            stroke="#666"
            fontSize={12}
          />
          <YAxis stroke="#666" fontSize={12} />
          <RechartsTooltip 
            formatter={formatTooltipValue}
            labelFormatter={(label) => formatTime(label)}
            contentStyle={{
              backgroundColor: '#1a1a1a',
              border: '1px solid #333',
              borderRadius: '8px',
              color: '#fff',
            }}
          />
          {data.map((series, index) => (
            <Area
              key={series.label}
              type="monotone"
              dataKey="value"
              stroke={series.color || `hsl(${index * 60}, 70%, 50%)`}
              fill={series.color || `hsl(${index * 60}, 70%, 20%)`}
              fillOpacity={0.3}
              strokeWidth={2}
            />
          ))}
        </AreaChart>
      );
    }

    return (
      <LineChart data={data[0]?.data || []}>
        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
        <XAxis 
          dataKey="timestamp" 
          tickFormatter={formatTime}
          stroke="#666"
          fontSize={12}
        />
        <YAxis stroke="#666" fontSize={12} />
        <RechartsTooltip 
          formatter={formatTooltipValue}
          labelFormatter={(label) => formatTime(label)}
          contentStyle={{
            backgroundColor: '#1a1a1a',
            border: '1px solid #333',
            borderRadius: '8px',
            color: '#fff',
          }}
        />
        {data.map((series, index) => (
          <Line
            key={series.label}
            type="monotone"
            dataKey="value"
            stroke={series.color || `hsl(${index * 60}, 70%, 50%)`}
            strokeWidth={2}
            dot={{ fill: series.color || `hsl(${index * 60}, 70%, 50%)`, strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, strokeWidth: 2 }}
          />
        ))}
      </LineChart>
    );
  };

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
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            {title}
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            <Chip
              icon={isConnected ? <TrendingUpIcon /> : <TrendingDownIcon />}
              label={isConnected ? 'Live' : 'Offline'}
              color={isConnected ? 'success' : 'error'}
              size="small"
            />
            {onRefresh && (
              <Tooltip title="Refresh Data">
                <IconButton onClick={onRefresh} disabled={loading} size="small">
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        </Box>

        <Box sx={{ height: height, width: '100%' }}>
          {loading ? (
            <Box 
              display="flex" 
              alignItems="center" 
              justifyContent="center" 
              height="100%"
              sx={{ 
                background: 'linear-gradient(90deg, transparent 0%, rgba(25, 118, 210, 0.1) 50%, transparent 100%)',
                animation: 'pulse 2s ease-in-out infinite',
              }}
            >
              <Typography variant="body2" color="text.secondary">
                Loading chart data...
              </Typography>
            </Box>
          ) : data.length === 0 ? (
            <Box 
              display="flex" 
              alignItems="center" 
              justifyContent="center" 
              height="100%"
              flexDirection="column"
              gap={2}
            >
              <Typography variant="body2" color="text.secondary">
                No data available
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Start a session to see real-time data
              </Typography>
            </Box>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              {getChartComponent()}
            </ResponsiveContainer>
          )}
        </Box>

        {showLegend && data.length > 0 && (
          <Box mt={2} display="flex" flexWrap="wrap" gap={1}>
            {data.map((series, index) => (
              <Box key={series.label} display="flex" alignItems="center" gap={0.5}>
                <Box
                  sx={{
                    width: 12,
                    height: 12,
                    backgroundColor: series.color || `hsl(${index * 60}, 70%, 50%)`,
                    borderRadius: '50%',
                  }}
                />
                <Typography variant="caption" color="text.secondary">
                  {series.label}
                </Typography>
              </Box>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
