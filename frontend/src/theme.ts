import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00D4AA', // Modern teal
      light: '#33DDBB',
      dark: '#009B7A',
      contrastText: '#000000',
    },
    secondary: {
      main: '#6366F1', // Indigo
      light: '#818CF8',
      dark: '#4F46E5',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#0A0A0A', // Very dark background
      paper: '#1A1A1A', // Slightly lighter for cards
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#A0A0A0',
    },
    success: {
      main: '#10B981', // Green
      light: '#34D399',
      dark: '#059669',
    },
    error: {
      main: '#EF4444', // Red
      light: '#F87171',
      dark: '#DC2626',
    },
    warning: {
      main: '#F59E0B', // Amber
      light: '#FBBF24',
      dark: '#D97706',
    },
    info: {
      main: '#3B82F6', // Blue
      light: '#60A5FA',
      dark: '#2563EB',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    h5: {
      fontSize: '1.125rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
    },
    body1: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.75rem',
      lineHeight: 1.4,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
      fontSize: '0.875rem',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #1A1A1A 0%, #2A2A2A 100%)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '8px 16px',
          fontWeight: 600,
          textTransform: 'none',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #00D4AA 0%, #009B7A 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #33DDBB 0%, #00D4AA 100%)',
          },
        },
        outlined: {
          borderColor: 'rgba(255, 255, 255, 0.2)',
          '&:hover': {
            borderColor: 'rgba(255, 255, 255, 0.4)',
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #1A1A1A 0%, #2A2A2A 100%)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
        },
      },
    },
    MuiTableHead: {
      styleOverrides: {
        root: {
          '& .MuiTableCell-head': {
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            fontWeight: 600,
            color: '#FFFFFF',
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          fontWeight: 600,
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
        },
        bar: {
          borderRadius: 4,
        },
      },
    },
  },
});

// Custom colors for specific use cases
export const customColors = {
  positive: '#10B981',
  negative: '#EF4444',
  neutral: '#6B7280',
  accent: '#8B5CF6',
  highlight: '#F59E0B',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
  primary: '#00D4AA',
  secondary: '#6366F1',
}; 