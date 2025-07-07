import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00bfa5',
    },
    background: {
      default: '#121212',
      paper: 'rgba(30,30,30,0.8)',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backdropFilter: 'blur(12px)',
        },
      },
    },
  },
}); 