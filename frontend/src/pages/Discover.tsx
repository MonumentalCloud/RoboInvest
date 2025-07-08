import React, { useState, useEffect, useRef } from "react";
import { Activity, Brain, TrendingUp, Users, ChevronRight, Play, Pause, Wifi, WifiOff } from "lucide-react";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  IconButton
} from '@mui/material';
import { useBudget, usePerformance, useTrades, useLessons } from '../hooks';

export default function Discover() {
  const [isRunning, setIsRunning] = useState(false);
  const [researchProgress, setResearchProgress] = useState(0);
  const { data: perf } = usePerformance();
  const { data: budget } = useBudget();
  const { data: trades } = useTrades(50);
  const { data: lessons } = useLessons();

  // Simulate research progress
  useEffect(() => {
    if (isRunning) {
      const interval = setInterval(() => {
        setResearchProgress(prev => (prev + 1) % 100);
      }, 100);
      return () => clearInterval(interval);
    }
  }, [isRunning]);

  const toggleResearch = () => {
    setIsRunning(!isRunning);
  };

  return (
    <Box sx={{ p: 2, width: '100%' }}>
      <Typography variant="h4" gutterBottom>
        🤖 Autonomous Alpha Discovery
      </Typography>
      
      <Grid container spacing={3}>
        {/* Left Panel - Discovery & Research */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Brain color="#1976d2" />
                  Discovery & Research
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {isRunning ? <Wifi color="green" /> : <WifiOff color="gray" />}
                  <IconButton onClick={toggleResearch} color={isRunning ? "secondary" : "primary"}>
                    {isRunning ? <Pause /> : <Play />}
                  </IconButton>
                </Box>
              </Box>

              {/* Research Status */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Research Status: {isRunning ? 'Active Alpha Hunting' : 'Idle'}
                </Typography>
                {isRunning && (
                  <LinearProgress 
                    variant="determinate" 
                    value={researchProgress} 
                    sx={{ mb: 1 }}
                  />
                )}
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Chip 
                    icon={<Activity />}
                    label={`${budget?.tokens || 0} LLM Calls Today`}
                    size="small"
                    color="primary"
                  />
                  <Chip 
                    icon={<TrendingUp />}
                    label={`${lessons?.length || 0} Insights`}
                    size="small"
                    color="secondary"
                  />
                </Box>
              </Box>

              {/* Active Research Areas */}
              <Typography variant="h6" gutterBottom>
                🔍 Active Research Areas
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText 
                    primary="Market Sentiment Analysis"
                    secondary="Analyzing news sentiment for alpha opportunities"
                  />
                  <ChevronRight />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Earnings Season Momentum"
                    secondary="Researching post-earnings moves and catalysts"
                  />
                  <ChevronRight />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Sector Rotation Signals"
                    secondary="Identifying rotation opportunities across sectors"
                  />
                  <ChevronRight />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Technical Pattern Recognition"
                    secondary="AI-powered chart pattern identification"
                  />
                  <ChevronRight />
                </ListItem>
              </List>

              <Divider sx={{ my: 2 }} />

              {/* Latest Insights */}
              <Typography variant="h6" gutterBottom>
                💡 Latest AI Insights
              </Typography>
              <List dense>
                {lessons?.slice(0, 3).map((lesson: any, idx: number) => (
                  <ListItem key={idx}>
                    <ListItemText 
                      primary={lesson.text || lesson.lesson || "Market analysis completed"}
                      secondary={lesson.time || lesson.t || new Date().toLocaleString()}
                    />
                  </ListItem>
                )) || (
                  <ListItem>
                    <ListItemText 
                      primary="Autonomous research system active"
                      secondary="Continuously scanning for alpha opportunities"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Panel - Profitability */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <TrendingUp color="#2e7d32" />
                Profitability Analysis
              </Typography>

              {/* Key Metrics */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color={perf?.total_pnl > 0 ? 'success.main' : 'error.main'}>
                        ${perf?.total_pnl?.toFixed(2) || '0.00'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total P&L
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">
                        ${budget?.cost_usd?.toFixed(3) || '0.000'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        AI Research Cost
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {/* Performance Breakdown */}
              <Typography variant="h6" gutterBottom>
                📊 Performance Breakdown
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText 
                    primary="Win Rate"
                    secondary={`${((trades?.filter((t: any) => t.pnl > 0).length / (trades?.length || 1)) * 100).toFixed(1)}%`}
                  />
                  <Typography variant="body2">
                    {trades?.filter((t: any) => t.pnl > 0).length || 0}/{trades?.length || 0}
                  </Typography>
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Avg Trade"
                    secondary="Average profit per trade"
                  />
                  <Typography variant="body2">
                    ${trades?.length ? (perf?.total_pnl / trades.length).toFixed(2) : '0.00'}
                  </Typography>
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Research ROI"
                    secondary="Profit vs AI research cost"
                  />
                  <Typography variant="body2" color={perf?.total_pnl > (budget?.cost_usd || 0) ? 'success.main' : 'error.main'}>
                    {budget?.cost_usd ? ((perf?.total_pnl || 0) / budget.cost_usd).toFixed(1) : '∞'}x
                  </Typography>
                </ListItem>
              </List>

              <Divider sx={{ my: 2 }} />

              {/* Recent Trades */}
              <Typography variant="h6" gutterBottom>
                💰 Recent Trading Activity
              </Typography>
              <List dense>
                {trades?.slice(0, 5).map((trade: any, idx: number) => (
                  <ListItem key={idx}>
                    <ListItemText 
                      primary={`${trade.side} ${trade.symbol || 'Unknown'}`}
                      secondary={`Qty: ${trade.qty || 0} @ $${trade.price || 0}`}
                    />
                    <Typography 
                      variant="body2" 
                      color={trade.pnl > 0 ? 'success.main' : 'error.main'}
                    >
                      ${trade.pnl?.toFixed(2) || '0.00'}
                    </Typography>
                  </ListItem>
                )) || (
                  <ListItem>
                    <ListItemText 
                      primary="No trades yet"
                      secondary="AI is researching opportunities"
                    />
                  </ListItem>
                )}
              </List>

              {/* Action Button */}
              <Box sx={{ mt: 3, textAlign: 'center' }}>
                <Button 
                  variant="contained" 
                  size="large"
                  startIcon={<Brain />}
                  onClick={() => window.location.href = '/insights'}
                >
                  View Detailed Analysis
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
} 