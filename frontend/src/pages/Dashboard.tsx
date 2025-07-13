import React, { useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api';
import * as d3 from 'd3';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ComposedChart
} from 'recharts';
import {
  Box, Card, CardContent, Typography, Paper, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Tabs, Tab, IconButton, Tooltip as MuiTooltip, Badge
} from '@mui/material';
import {
  TrendingUp, TrendingDown, AccountBalance, ShowChart,
  Timeline, PieChart as PieChartIcon, TableChart, BubbleChart
} from '@mui/icons-material';

// Types
interface Trade {
  symbol: string;
  quantity: number;
  entry_price: number;
  exit_price?: number;
  entry_time: string;
  exit_time?: string;
  side: string;
  pnl?: number;
  pnl_pct?: number;
  confidence?: number;
}

interface Position {
  symbol: string;
  quantity: number;
  entry_price: number;
  entry_time: string;
  side: string;
  current_price?: number;
  unrealized_pnl?: number;
  unrealized_pnl_pct?: number;
}

interface Performance {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_pnl: number;
  avg_pnl: number;
  max_drawdown: number;
  sharpe_ratio: number;
  current_positions: number;
  unrealized_pnl: number;
}

interface GraphNode {
  id: string;
  name: string;
  type: string;
  value: number;
  group: number;
  x?: number;
  y?: number;
}

interface GraphLink {
  source: string;
  target: string;
  value: number;
  type: string;
}

// Custom hooks
const usePerformance = () =>
  useQuery({
    queryKey: ['performance'],
    queryFn: () => api.get('/performance').then(r => r.data.performance),
    refetchInterval: 10000
  });

const useTrades = (limit = 100) =>
  useQuery({
    queryKey: ['trades', limit],
    queryFn: () => api.get(`/trades?limit=${limit}`).then(r => r.data.trades),
    refetchInterval: 10000
  });

const usePositions = () =>
  useQuery({
    queryKey: ['positions'],
    queryFn: () => api.get('/positions').then(r => r.data.positions),
    refetchInterval: 10000
  });

// Force Directed Graph Component
const ForceDirectedGraph: React.FC<{ data: { nodes: GraphNode[], links: GraphLink[] } }> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const width = 800;
    const height = 600;

    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id((d: any) => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(30));

    const link = svg.append("g")
      .selectAll("line")
      .data(data.links)
      .enter().append("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", (d: any) => Math.sqrt(d.value));

    const node = svg.append("g")
      .selectAll("circle")
      .data(data.nodes)
      .enter().append("circle")
      .attr("r", (d: any) => Math.sqrt(d.value) * 2 + 5)
      .attr("fill", (d: any) => d3.schemeCategory10[d.group % 10])
      .call(d3.drag<any, any>()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    const label = svg.append("g")
      .selectAll("text")
      .data(data.nodes)
      .enter().append("text")
      .text((d: any) => d.name)
      .attr("font-size", "12px")
      .attr("text-anchor", "middle")
      .attr("dy", "0.35em");

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node
        .attr("cx", (d: any) => d.x)
        .attr("cy", (d: any) => d.y);

      label
        .attr("x", (d: any) => d.x)
        .attr("y", (d: any) => d.y);
    });

    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    return () => {
      simulation.stop();
    };
  }, [data]);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <BubbleChart sx={{ mr: 1 }} />
          Trading Network Graph
        </Typography>
        <Box sx={{ overflow: 'auto' }}>
          <svg ref={svgRef} width={800} height={600} />
        </Box>
      </CardContent>
    </Card>
  );
};

// Performance Charts Component
const PerformanceCharts: React.FC<{ performance: Performance; trades: Trade[] }> = ({ performance, trades }) => {
  const chartData = trades.map(trade => ({
    date: new Date(trade.entry_time).toLocaleDateString(),
    pnl: trade.pnl || 0,
    pnl_pct: trade.pnl_pct || 0,
    symbol: trade.symbol,
    side: trade.side
  }));

  const cumulativeData = chartData.reduce((acc, trade, index) => {
    const prevCumulative = acc.length > 0 ? acc[acc.length - 1].cumulative : 0;
    acc.push({
      ...trade,
      cumulative: prevCumulative + trade.pnl
    });
    return acc;
  }, [] as any[]);

  const winLossData = [
    { name: 'Wins', value: performance.winning_trades, fill: '#4caf50' },
    { name: 'Losses', value: performance.losing_trades, fill: '#f44336' }
  ];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Charts Row */}
      <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
        {/* Cumulative PnL Chart */}
        <Box sx={{ flex: '2 1 600px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <TrendingUp sx={{ mr: 1 }} />
                Cumulative PnL
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={cumulativeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="cumulative" stroke="#8884d8" fill="#8884d8" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Box>

        {/* Win/Loss Distribution */}
        <Box sx={{ flex: '1 1 300px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <PieChartIcon sx={{ mr: 1 }} />
                Win/Loss Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={winLossData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {winLossData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Performance Metrics */}
      <Box>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Timeline sx={{ mr: 1 }} />
              Performance Metrics
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Box sx={{ flex: '1 1 200px', textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {performance.win_rate.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Win Rate
                </Typography>
              </Box>
              <Box sx={{ flex: '1 1 200px', textAlign: 'center' }}>
                <Typography variant="h4" color={performance.total_pnl >= 0 ? "success.main" : "error.main"}>
                  ${performance.total_pnl.toFixed(2)}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Total PnL
                </Typography>
              </Box>
              <Box sx={{ flex: '1 1 200px', textAlign: 'center' }}>
                <Typography variant="h4" color="info.main">
                  {performance.sharpe_ratio.toFixed(2)}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Sharpe Ratio
                </Typography>
              </Box>
              <Box sx={{ flex: '1 1 200px', textAlign: 'center' }}>
                <Typography variant="h4" color="warning.main">
                  {performance.max_drawdown.toFixed(2)}%
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Max Drawdown
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

// Stylized Trades Table Component
const StylizedTradesTable: React.FC<{ trades: Trade[] }> = ({ trades }) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <TableChart sx={{ mr: 1 }} />
          Recent Trades
        </Typography>
        <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell>Side</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Entry Price</TableCell>
                <TableCell>Exit Price</TableCell>
                <TableCell>PnL</TableCell>
                <TableCell>PnL %</TableCell>
                <TableCell>Confidence</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {trades.map((trade, index) => (
                <TableRow key={index} sx={{
                  backgroundColor: trade.pnl && trade.pnl > 0 ? 'rgba(76, 175, 80, 0.1)' : 
                                  trade.pnl && trade.pnl < 0 ? 'rgba(244, 67, 54, 0.1)' : 'inherit'
                }}>
                  <TableCell>
                    <Typography variant="body2" fontWeight="bold">
                      {trade.symbol}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={trade.side}
                      size="small"
                      color={trade.side === 'BUY' ? 'primary' : 'secondary'}
                    />
                  </TableCell>
                  <TableCell>{trade.quantity}</TableCell>
                  <TableCell>${trade.entry_price.toFixed(2)}</TableCell>
                  <TableCell>
                    {trade.exit_price ? `$${trade.exit_price.toFixed(2)}` : '-'}
                  </TableCell>
                  <TableCell>
                    <Typography
                      variant="body2"
                      color={trade.pnl && trade.pnl > 0 ? 'success.main' : 'error.main'}
                      fontWeight="bold"
                    >
                      {trade.pnl ? `$${trade.pnl.toFixed(2)}` : '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography
                      variant="body2"
                      color={trade.pnl_pct && trade.pnl_pct > 0 ? 'success.main' : 'error.main'}
                    >
                      {trade.pnl_pct ? `${trade.pnl_pct.toFixed(2)}%` : '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Box
                        sx={{
                          width: 60,
                          height: 8,
                          backgroundColor: 'grey.300',
                          borderRadius: 4,
                          overflow: 'hidden'
                        }}
                      >
                        <Box
                          sx={{
                            width: `${(trade.confidence || 0) * 100}%`,
                            height: '100%',
                            backgroundColor: trade.confidence && trade.confidence > 0.7 ? 'success.main' :
                                            trade.confidence && trade.confidence > 0.4 ? 'warning.main' : 'error.main'
                          }}
                        />
                      </Box>
                      <Typography variant="caption" sx={{ ml: 1 }}>
                        {(trade.confidence || 0) * 100}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={trade.exit_price ? 'Closed' : 'Open'}
                      size="small"
                      color={trade.exit_price ? 'default' : 'warning'}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

// Positions Table Component
const PositionsTable: React.FC<{ positions: Position[] }> = ({ positions }) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <AccountBalance sx={{ mr: 1 }} />
          Current Positions
        </Typography>
        <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell>Side</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Entry Price</TableCell>
                <TableCell>Current Price</TableCell>
                <TableCell>Unrealized PnL</TableCell>
                <TableCell>Unrealized PnL %</TableCell>
                <TableCell>Duration</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {positions.map((position, index) => {
                const duration = new Date().getTime() - new Date(position.entry_time).getTime();
                const days = Math.floor(duration / (1000 * 60 * 60 * 24));
                
                return (
                  <TableRow key={index} sx={{
                    backgroundColor: position.unrealized_pnl && position.unrealized_pnl > 0 ? 'rgba(76, 175, 80, 0.1)' : 
                                    position.unrealized_pnl && position.unrealized_pnl < 0 ? 'rgba(244, 67, 54, 0.1)' : 'inherit'
                  }}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {position.symbol}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={position.side}
                        size="small"
                        color={position.side === 'BUY' ? 'primary' : 'secondary'}
                      />
                    </TableCell>
                    <TableCell>{position.quantity}</TableCell>
                    <TableCell>${position.entry_price.toFixed(2)}</TableCell>
                    <TableCell>
                      {position.current_price ? `$${position.current_price.toFixed(2)}` : '-'}
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        color={position.unrealized_pnl && position.unrealized_pnl > 0 ? 'success.main' : 'error.main'}
                        fontWeight="bold"
                      >
                        {position.unrealized_pnl ? `$${position.unrealized_pnl.toFixed(2)}` : '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        color={position.unrealized_pnl_pct && position.unrealized_pnl_pct > 0 ? 'success.main' : 'error.main'}
                      >
                        {position.unrealized_pnl_pct ? `${position.unrealized_pnl_pct.toFixed(2)}%` : '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {days}d
                      </Typography>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

// Main Dashboard Component
const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const { data: performance } = usePerformance();
  const { data: trades = [] } = useTrades();
  const { data: positions = [] } = usePositions();

  // Generate sample graph data (replace with real data when available)
  const graphData = {
    nodes: [
      { id: "SPY", name: "SPY", type: "ETF", value: 100, group: 0 },
      { id: "AAPL", name: "AAPL", type: "Stock", value: 80, group: 1 },
      { id: "TSLA", name: "TSLA", type: "Stock", value: 60, group: 1 },
      { id: "NVDA", name: "NVDA", type: "Stock", value: 90, group: 1 },
      { id: "AI", name: "AI Sector", type: "Sector", value: 70, group: 2 },
      { id: "Tech", name: "Tech Sector", type: "Sector", value: 85, group: 2 },
    ],
    links: [
      { source: "SPY", target: "AAPL", value: 1, type: "correlation" },
      { source: "SPY", target: "TSLA", value: 1, type: "correlation" },
      { source: "SPY", target: "NVDA", value: 1, type: "correlation" },
      { source: "AAPL", target: "Tech", value: 1, type: "sector" },
      { source: "TSLA", target: "Tech", value: 1, type: "sector" },
      { source: "NVDA", target: "AI", value: 1, type: "sector" },
      { source: "AI", target: "Tech", value: 1, type: "correlation" },
    ]
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  if (!performance) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Loading Dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <ShowChart sx={{ mr: 2, verticalAlign: 'middle' }} />
        Trading Dashboard
      </Typography>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Performance Charts" icon={<TrendingUp />} />
        <Tab label="Trading Network" icon={<BubbleChart />} />
        <Tab label="Trades Table" icon={<TableChart />} />
        <Tab label="Positions" icon={<AccountBalance />} />
      </Tabs>

      {activeTab === 0 && (
        <PerformanceCharts performance={performance} trades={trades} />
      )}

      {activeTab === 1 && (
        <ForceDirectedGraph data={graphData} />
      )}

      {activeTab === 2 && (
        <StylizedTradesTable trades={trades} />
      )}

      {activeTab === 3 && (
        <PositionsTable positions={positions} />
      )}
    </Box>
  );
};

export default Dashboard; 