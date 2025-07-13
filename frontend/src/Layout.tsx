import { AppBar, Toolbar, Typography, Button, Box, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import { Outlet, Link as RouterLink, useLocation } from 'react-router-dom';
import { Psychology } from '@mui/icons-material';

export default function Layout() {
  const location = useLocation();
  const navItems = [
    { label: '👑 Governor Control', path: '/' },
    { label: '📊 Dashboard', path: '/dashboard' },
    { label: '🚀 Alpha Stream', path: '/alpha-stream' },
  ];

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            🧠 RoboInvest | Governor Control System
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
          <ListItem component={RouterLink} to="/experience">
            <ListItemIcon>
              <Psychology />
            </ListItemIcon>
            <ListItemText primary="Experience Learning" />
          </ListItem>
        </Toolbar>
      </AppBar>
      <Box sx={{ mt: 2, px: 2, width: '100%' }}>
        <Outlet />
      </Box>
    </Box>
  );
} 