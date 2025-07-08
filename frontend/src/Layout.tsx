import { AppBar, Toolbar, Typography, Button, Box, Chip } from '@mui/material';
import { Outlet, Link as RouterLink, useLocation } from 'react-router-dom';
import { Search as SearchIcon, TrendingUp as TrendingUpIcon } from '@mui/icons-material';

export default function Layout() {
  const location = useLocation();
  const navItems = [
    { 
      label: 'Discover', 
      path: '/', 
      icon: <SearchIcon />,
      description: 'AI Research & Alpha Discovery'
    },
    { 
      label: 'Profitability', 
      path: '/profitability', 
      icon: <TrendingUpIcon />,
      description: 'Performance & Analytics'
    },
  ];

  return (
    <Box>
      <AppBar position="static" sx={{ background: 'linear-gradient(45deg, #1a237e 30%, #3949ab 90%)' }}>
        <Toolbar>
          <Typography variant="h5" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            🤖 Autonomous Alpha Hunter
          </Typography>
          <Chip 
            label="LIVE" 
            color="success" 
            size="small" 
            sx={{ mr: 2, animation: 'pulse 2s infinite' }}
          />
          {navItems.map(item => (
            <Button
              key={item.path}
              color={location.pathname === item.path ? 'secondary' : 'inherit'}
              component={RouterLink}
              to={item.path}
              startIcon={item.icon}
              sx={{ 
                mx: 1, 
                fontWeight: location.pathname === item.path ? 'bold' : 'normal',
                textTransform: 'none',
                fontSize: '1rem'
              }}
            >
              {item.label}
            </Button>
          ))}
        </Toolbar>
      </AppBar>
      <Box sx={{ mt: 1, px: 1, width: '100%', minHeight: 'calc(100vh - 64px)' }}>
        <Outlet />
      </Box>
    </Box>
  );
} 