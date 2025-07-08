import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Paper,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
} from '@mui/material';
import {
  TrendingUp,
  Analytics,
  Assessment,
  AccountBalance,
  ShowChart,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useBudget, usePerformance } from '../hooks';

// Mock performance data
const mockPerformanceData = {
  portfolioValue: 105420.50,
  totalReturn: 5420.50,
  returnPercentage: 5.42,
  sharpeRatio: 1.85,
  maxDrawdown: -2.1,
  winRate: 0.68,
  trades: 147,
  avgHoldTime: "3.2 days",
  equity_curve: [
    { date: '2025-01-01', value: 100000, pnl: 0 },
    { date: '2025-01-08', value: 101200, pnl: 1200 },
    { date: '2025-01-15', value: 102800, pnl: 2800 },
    { date: '2025-01-22', value: 101900, pnl: 1900 },
    { date: '2025-01-29', value: 103500, pnl: 3500 },
    { date: '2025-02-05', value: 105420, pnl: 5420 },
  ],
  sectorAllocation: [
    { sector: 'Technology', value: 35, amount: 36897 },
    { sector: 'Healthcare', value: 22, amount: 23192 },
    { sector: 'Finance', value: 18, amount: 18976 },
    { sector: 'Energy', value: 15, amount: 15813 },
    { sector: 'Consumer', value: 10, amount: 10542 },
  ],
  topPositions: [
    { symbol: 'PLTR', value: 12500, return: 8.4, score: 92 },
    { symbol: 'NVDA', value: 11800, return: 15.2, score: 88 },
    { symbol: 'SOFI', value: 9200, return: -2.1, score: 76 },
    { symbol: 'AMD', value: 8500, return: 12.7, score: 84 },
    { symbol: 'TSLA', value: 7900, return: -5.3, score: 71 },
  ],
  fundamentalScores: {
    momentum: 85,
    value: 72,
    quality: 88,
    volatility: 65,
    sentiment: 91,
  }
};

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function Profitability() {
  const [tabValue, setTabValue] = useState(0);
  const [performanceData] = useState(mockPerformanceData);
  const { data: budget } = useBudget();
  const { data: perf } = usePerformance();

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Analytics sx={{ mr: 2, color: 'primary.main' }} />
        Performance & Analytics
      </Typography>

      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Portfolio Value</Typography>
              <Typography variant="h4" color="primary.main">
                ${performanceData.portfolioValue.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="success.main">
                +{performanceData.returnPercentage}% Overall
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Return</Typography>
              <Typography variant="h4" color="success.main">
                +${performanceData.totalReturn.toLocaleString()}
              </Typography>
              <Typography variant="body2">
                Sharpe: {performanceData.sharpeRatio}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Win Rate</Typography>
              <Typography variant="h4" color="primary.main">
                {Math.round(performanceData.winRate * 100)}%
              </Typography>
              <Typography variant="body2">
                {performanceData.trades} trades
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Max Drawdown</Typography>
              <Typography variant="h4" color="error.main">
                {performanceData.maxDrawdown}%
              </Typography>
              <Typography variant="body2">
                Avg Hold: {performanceData.avgHoldTime}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs for different views */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab icon={<ShowChart />} label="Performance" />
            <Tab icon={<Assessment />} label="Allocation" />
            <Tab icon={<AccountBalance />} label="Positions" />
            <Tab icon={<TrendingUp />} label="Fundamentals" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          {/* Performance Charts */}
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, lg: 8 }}>
              <Typography variant="h6" gutterBottom>Equity Curve</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={performanceData.equity_curve}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Portfolio Value']} />
                  <Area 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#8884d8" 
                    fill="#8884d8" 
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Grid>
            <Grid size={{ xs: 12, lg: 4 }}>
              <Typography variant="h6" gutterBottom>P&L Distribution</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={performanceData.equity_curve}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`$${value}`, 'P&L']} />
                  <Bar dataKey="pnl" fill="#00C49F" />
                </BarChart>
              </ResponsiveContainer>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {/* Sector Allocation */}
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, lg: 6 }}>
              <Typography variant="h6" gutterBottom>Sector Allocation</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={performanceData.sectorAllocation}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ sector, value }) => `${sector} ${value}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {performanceData.sectorAllocation.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value}%`, 'Allocation']} />
                </PieChart>
              </ResponsiveContainer>
            </Grid>
            <Grid size={{ xs: 12, lg: 6 }}>
              <Typography variant="h6" gutterBottom>Allocation Details</Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Sector</TableCell>
                      <TableCell align="right">Allocation</TableCell>
                      <TableCell align="right">Value</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {performanceData.sectorAllocation.map((row) => (
                      <TableRow key={row.sector}>
                        <TableCell>{row.sector}</TableCell>
                        <TableCell align="right">{row.value}%</TableCell>
                        <TableCell align="right">${row.amount.toLocaleString()}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {/* Top Positions */}
          <Typography variant="h6" gutterBottom>Top Positions</Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Symbol</TableCell>
                  <TableCell align="right">Value</TableCell>
                  <TableCell align="right">Return</TableCell>
                  <TableCell align="right">AI Score</TableCell>
                  <TableCell align="right">Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {performanceData.topPositions.map((position) => (
                  <TableRow key={position.symbol}>
                    <TableCell>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {position.symbol}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">${position.value.toLocaleString()}</TableCell>
                    <TableCell align="right">
                      <Typography 
                        color={position.return > 0 ? 'success.main' : 'error.main'}
                        fontWeight="bold"
                      >
                        {position.return > 0 ? '+' : ''}{position.return}%
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                        <Box sx={{ width: 60, mr: 1 }}>
                          <LinearProgress 
                            variant="determinate" 
                            value={position.score} 
                            color={position.score > 80 ? 'success' : position.score > 60 ? 'warning' : 'error'}
                          />
                        </Box>
                        <Typography variant="body2">{position.score}</Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Chip 
                        label={position.return > 0 ? 'Winning' : 'Losing'}
                        color={position.return > 0 ? 'success' : 'error'}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          {/* Fundamental Analysis */}
          <Typography variant="h6" gutterBottom>Fundamental Analysis Scores</Typography>
          <Grid container spacing={3}>
            {Object.entries(performanceData.fundamentalScores).map(([metric, score]) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={metric}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" sx={{ textTransform: 'capitalize', mb: 2 }}>
                      {metric}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress 
                          variant="determinate" 
                          value={score} 
                          sx={{ height: 10, borderRadius: 5 }}
                          color={score > 80 ? 'success' : score > 60 ? 'warning' : 'error'}
                        />
                      </Box>
                      <Typography variant="h6" color="text.secondary">
                        {score}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {score > 80 ? 'Excellent' : score > 60 ? 'Good' : 'Needs Improvement'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>
      </Card>
    </Box>
  );
} 