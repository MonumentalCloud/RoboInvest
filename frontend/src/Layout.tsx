import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Outlet, Link as RouterLink, useLocation } from 'react-router-dom';

export default function Layout() {
  const location = useLocation();
  const navItems = [
    { label: 'Dashboard', path: '/' },
    { label: 'Trades', path: '/trades' },
    { label: 'Positions', path: '/positions' },
    { label: 'Insights', path: '/insights' },
  ];

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            RoboInvest
          </Typography>
          {navItems.map(item => (
            <Button
              key={item.path}
              color={location.pathname === item.path ? 'secondary' : 'inherit'}
              component={RouterLink}
              to={item.path}
            >
              {item.label}
            </Button>
          ))}
        </Toolbar>
      </AppBar>
      <Box sx={{ mt: 2, px: 2, width: '100%' }}>
        <Outlet />
      </Box>
    </Box>
  );
} 