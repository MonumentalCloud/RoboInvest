import {
  BrowserRouter as Router,
  Routes,
  Route,
} from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { theme } from './theme';
import Layout from './Layout';
import GovernorControlPanel from './components/GovernorControlPanel';
import AlphaStream from './pages/AlphaStream';
import Dashboard from './pages/Dashboard';
import ExperienceLearningDashboard from './components/ExperienceLearningDashboard';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/" element={<GovernorControlPanel />} />
              <Route path="/governor" element={<GovernorControlPanel />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/alpha-stream" element={<AlphaStream />} />
              <Route path="/experience" element={<ExperienceLearningDashboard />} />
            </Route>
          </Routes>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
