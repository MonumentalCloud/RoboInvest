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

export default function App() {
  return (
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/trades" element={<Trades />} />
          <Route path="/positions" element={<Positions />} />
          <Route path="/insights" element={<Insights />} />
        </Route>
      </Routes>
    </Router>
  );
}
