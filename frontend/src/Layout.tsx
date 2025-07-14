import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Box, 
  Container,
  Chip,
  IconButton,
  Tooltip,
  Avatar,
  Divider
} from '@mui/material';
import { 
  Outlet, 
  Link as RouterLink, 
  useLocation 
} from 'react-router-dom';
import { 
  Psychology, 
  Dashboard as DashboardIcon,
  TrendingUp,
  AutoGraph,
  Settings,
  Notifications
} from '@mui/icons-material';
import { customColors } from './theme';

export default function Layout() {
  const location = useLocation();
  
  const navItems = [
    { 
      label: 'Governor Control', 
      path: '/', 
      icon: <Psychology sx={{ mr: 1 }} />,
      description: 'AI Administrative Interface'
    },
    { 
      label: 'Dashboard', 
      path: '/dashboard', 
      icon: <DashboardIcon sx={{ mr: 1 }} />,
      description: 'Performance Analytics'
    },
    { 
      label: 'Alpha Stream', 
      path: '/alpha-stream', 
      icon: <TrendingUp sx={{ mr: 1 }} />,
      description: 'Real-time Alpha Signals'
    },
    { 
      label: 'Experience Learning', 
      path: '/experience', 
      icon: <AutoGraph sx={{ mr: 1 }} />,
      description: 'AI Learning & Insights'
    },
  ];

  const getStatusColor = () => {
    return customColors.success; // Mock status - could be dynamic
  };

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0A0A0A 0%, #1A1A1A 100%)' }}>
      <AppBar 
        position="static" 
        elevation={0}
        sx={{
          background: 'rgba(26, 26, 26, 0.8)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <Container maxWidth="xl">
          <Toolbar sx={{ px: 0 }}>
            {/* Logo and Title */}
            <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
              <Avatar 
                sx={{ 
                  mr: 2, 
                  background: 'linear-gradient(135deg, #00D4AA 0%, #009B7A 100%)',
                  width: 40,
                  height: 40
                }}
              >
                <Psychology />
              </Avatar>
              <Box>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    fontWeight: 700,
                    background: 'linear-gradient(135deg, #00D4AA 0%, #6366F1 100%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    letterSpacing: '-0.02em'
                  }}
                >
                  RoboInvest
                </Typography>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    color: 'text.secondary',
                    fontWeight: 500,
                    letterSpacing: '0.05em',
                    textTransform: 'uppercase'
                  }}
                >
                  Autonomous Trading System
                </Typography>
              </Box>
            </Box>

            {/* Navigation */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {navItems.map(item => (
                <Tooltip 
                  key={item.path} 
                  title={item.description}
                  placement="bottom"
                >
                  <Button
                    component={RouterLink}
                    to={item.path}
                    startIcon={item.icon}
                    sx={{
                      color: location.pathname === item.path ? 'primary.main' : 'text.secondary',
                      backgroundColor: location.pathname === item.path ? 'rgba(0, 212, 170, 0.1)' : 'transparent',
                      border: location.pathname === item.path ? '1px solid rgba(0, 212, 170, 0.3)' : '1px solid transparent',
                      borderRadius: 2,
                      px: 2,
                      py: 1,
                      fontWeight: 600,
                      textTransform: 'none',
                      '&:hover': {
                        backgroundColor: location.pathname === item.path 
                          ? 'rgba(0, 212, 170, 0.15)' 
                          : 'rgba(255, 255, 255, 0.05)',
                        borderColor: location.pathname === item.path 
                          ? 'rgba(0, 212, 170, 0.5)' 
                          : 'rgba(255, 255, 255, 0.2)',
                      },
                      transition: 'all 0.2s ease-in-out',
                    }}
                  >
                    {item.label}
                  </Button>
                </Tooltip>
              ))}
            </Box>

            <Divider orientation="vertical" flexItem sx={{ mx: 2, borderColor: 'rgba(255, 255, 255, 0.1)' }} />

            {/* Status and Actions */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                label="System Online"
                size="small"
                sx={{
                  backgroundColor: 'rgba(16, 185, 129, 0.2)',
                  color: customColors.success,
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  fontWeight: 600,
                  '& .MuiChip-label': {
                    px: 1,
                  },
                }}
              />
              
              <Tooltip title="Notifications">
                <IconButton 
                  size="small"
                  sx={{ 
                    color: 'text.secondary',
                    '&:hover': { color: 'primary.main' }
                  }}
                >
                  <Notifications />
                </IconButton>
              </Tooltip>
              
              <Tooltip title="Settings">
                <IconButton 
                  size="small"
                  sx={{ 
                    color: 'text.secondary',
                    '&:hover': { color: 'primary.main' }
                  }}
                >
                  <Settings />
                </IconButton>
              </Tooltip>
            </Box>
          </Toolbar>
        </Container>
      </AppBar>
      
      <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
        <Outlet />
      </Container>
    </Box>
  );
} 