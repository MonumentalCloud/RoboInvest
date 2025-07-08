import {
  BrowserRouter as Router,
  Routes,
  Route,
} from 'react-router-dom';
import Layout from './Layout';
import Discover from './pages/Discover';
import Profitability from './pages/Profitability';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Discover />} />
          <Route path="/profitability" element={<Profitability />} />
        </Route>
      </Routes>
    </Router>
  );
}
