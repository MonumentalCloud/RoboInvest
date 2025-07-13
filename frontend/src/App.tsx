import {
  BrowserRouter as Router,
  Routes,
  Route,
} from 'react-router-dom';
import Layout from './Layout';
import GovernorControlPanel from './components/GovernorControlPanel';
import AlphaStream from './pages/AlphaStream';
import Dashboard from './pages/Dashboard';
import ExperienceLearningDashboard from './components/ExperienceLearningDashboard';

export default function App() {
  return (
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
  );
}
