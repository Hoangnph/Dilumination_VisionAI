'use client';

import React, { useMemo } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Badge,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  History as HistoryIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  Analytics as AnalyticsIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';

const drawerWidth = 240;

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const router = useRouter();
  const pathname = usePathname();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigation = (path: string) => {
    router.push(path);
    setMobileOpen(false); // Close mobile drawer after navigation
  };

  // Memoize styles to prevent hydration mismatch
  const mainBoxStyles = useMemo(() => ({
    display: 'flex'
  }), []);

  const appBarStyles = useMemo(() => ({
    width: { md: `calc(100% - ${drawerWidth}px)` },
    ml: { md: `${drawerWidth}px` },
    backgroundColor: 'background.paper',
    borderBottom: '1px solid',
    borderColor: 'divider',
  }), []);

  const navBoxStyles = useMemo(() => ({
    width: { md: drawerWidth },
    flexShrink: { md: 0 }
  }), []);

  const mainContentStyles = useMemo(() => ({
    flexGrow: 1,
    p: 3,
    width: { md: `calc(100% - ${drawerWidth}px)` },
    mt: 8,
    backgroundColor: 'background.default',
    minHeight: '100vh',
  }), []);

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Live Monitoring', icon: <PeopleIcon />, path: '/live' },
    { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' },
    { text: 'Session History', icon: <HistoryIcon />, path: '/sessions' },
    { text: 'Timeline', icon: <TimelineIcon />, path: '/timeline' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];

  const drawer = (
    <Box>
      <Toolbar>
        <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold' }}>
          People Counter Monitor
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem 
            key={item.text} 
            onClick={() => handleNavigation(item.path)}
            sx={{ 
              borderRadius: 1, 
              mx: 1, 
              my: 0.5, 
              cursor: 'pointer',
              backgroundColor: pathname === item.path ? 'primary.main' : 'transparent',
              color: pathname === item.path ? 'primary.contrastText' : 'text.primary',
              '&:hover': {
                backgroundColor: pathname === item.path ? 'primary.dark' : 'action.hover',
              }
            }}
          >
            <ListItemIcon sx={{ color: pathname === item.path ? 'primary.contrastText' : 'primary.main' }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={mainBoxStyles}>
      <AppBar
        position="fixed"
        sx={appBarStyles}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Real-time People Counting Dashboard
          </Typography>
          <IconButton color="inherit">
            <Badge badgeContent={4} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={navBoxStyles}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              backgroundColor: 'background.paper',
              borderRight: '1px solid',
              borderColor: 'divider',
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              backgroundColor: 'background.paper',
              borderRight: '1px solid',
              borderColor: 'divider',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={mainContentStyles}
      >
        {children}
      </Box>
    </Box>
  );
}
