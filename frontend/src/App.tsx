import {
  BrowserRouter as Router,
  Routes,
  Route,
} from 'react-router-dom';
import Layout from './Layout';
import Dashboard from './pages/Dashboard';
import Trades from './pages/Trades';
import Positions from './pages/Positions';
import Insights from './pages/Insights';
import AlphaStream from './pages/AlphaStream';
import PlayExecutor from './pages/PlayExecutor';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<AlphaStream />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/trades" element={<Trades />} />
          <Route path="/positions" element={<Positions />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="/plays" element={<PlayExecutor />} />
        </Route>
      </Routes>
    </Router>
  );
}
