import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  Button,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  Paper
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Psychology,
  School,
  Analytics,
  Timeline,
  Assessment,
  Insights,
  AutoGraph
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

interface ExperienceData {
  shared_experiences: any[];
  agent_feedback: any[];
  relevant_insights: any[];
}

interface PerformanceTrends {
  rating_trend: string;
  win_rate_trend: string;
  pnl_trend: string;
  overall_trend: string;
  sample_size: number;
}

interface LearningInsights {
  experience_data: ExperienceData;
  performance_trends: PerformanceTrends;
  execution_stats: {
    total_decisions: number;
    execution_rate: number;
    avg_confidence: number;
    success_rate: number;
    recent_insights: number;
  };
  learning_focus: string;
}

interface SystemInsights {
  insights: any[];
  lessons_learned: any[];
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const ExperienceLearningDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [agentInsights, setAgentInsights] = useState<Record<string, LearningInsights>>({});
  const [systemInsights, setSystemInsights] = useState<SystemInsights | null>(null);
  const [performanceTrends, setPerformanceTrends] = useState<PerformanceTrends | null>(null);
  const [analysisHistory, setAnalysisHistory] = useState<any[]>([]);

  const agents = [
    'enhanced_trade_executor',
    'world_monitor',
    'strategy_agent',
    'risk_assessor'
  ];

  useEffect(() => {
    loadExperienceData();
  }, []);

  const loadExperienceData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load agent insights
      const agentPromises = agents.map(async (agentId) => {
        const response = await fetch(`/api/experience/agent/${agentId}/learning`);
        if (response.ok) {
          const data = await response.json();
          return [agentId, data.insights];
        }
        return [agentId, null];
      });

      const agentResults = await Promise.all(agentPromises);
      const insights: Record<string, LearningInsights> = {};
      
      agentResults.forEach(([agentId, data]) => {
        if (data) {
          insights[agentId as string] = data;
        }
      });

      setAgentInsights(insights);

      // Load system insights
      const systemResponse = await fetch('/api/experience/system/insights');
      if (systemResponse.ok) {
        const systemData = await systemResponse.json();
        setSystemInsights(systemData.insights);
      }

      // Load performance trends
      const trendsResponse = await fetch('/api/experience/performance/trends');
      if (trendsResponse.ok) {
        const trendsData = await trendsResponse.json();
        setPerformanceTrends(trendsData.trends);
      }

      // Load analysis history
      const historyResponse = await fetch('/api/experience/performance/history?limit=10');
      if (historyResponse.ok) {
        const historyData = await historyResponse.json();
        setAnalysisHistory(historyData.history);
      }

    } catch (err) {
      setError('Failed to load experience data');
      console.error('Error loading experience data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return <TrendingUp color="success" />;
      case 'declining':
        return <TrendingDown color="error" />;
      case 'stable':
        return <TrendingFlat color="warning" />;
      default:
        return <TrendingFlat color="disabled" />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'improving':
        return 'success';
      case 'declining':
        return 'error';
      case 'stable':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatAgentName = (agentId: string) => {
    return agentId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const renderAgentCard = (agentId: string, insights: LearningInsights) => {
    const { performance_trends, execution_stats, learning_focus } = insights;

    return (
      <Card key={agentId} sx={{ height: '100%' }}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <Psychology color="primary" sx={{ mr: 1 }} />
            <Typography variant="h6" component="h3">
              {formatAgentName(agentId)}
            </Typography>
          </Box>

          <Grid container spacing={2} mb={2}>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">
                Total Decisions
              </Typography>
              <Typography variant="h6">
                {execution_stats.total_decisions}
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">
                Execution Rate
              </Typography>
              <Typography variant="h6">
                {execution_stats.execution_rate}%
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">
                Avg Confidence
              </Typography>
              <Typography variant="h6">
                {(execution_stats.avg_confidence * 100).toFixed(1)}%
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">
                Success Rate
              </Typography>
              <Typography variant="h6">
                {execution_stats.success_rate}%
              </Typography>
            </Grid>
          </Grid>

          <Divider sx={{ my: 2 }} />

          <Box mb={2}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Performance Trends
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              <Chip
                icon={getTrendIcon(performance_trends.rating_trend)}
                label={`Rating: ${performance_trends.rating_trend}`}
                color={getTrendColor(performance_trends.rating_trend) as any}
                size="small"
              />
              <Chip
                icon={getTrendIcon(performance_trends.win_rate_trend)}
                label={`Win Rate: ${performance_trends.win_rate_trend}`}
                color={getTrendColor(performance_trends.win_rate_trend) as any}
                size="small"
              />
              <Chip
                icon={getTrendIcon(performance_trends.pnl_trend)}
                label={`PnL: ${performance_trends.pnl_trend}`}
                color={getTrendColor(performance_trends.pnl_trend) as any}
                size="small"
              />
            </Box>
          </Box>

          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Learning Focus
            </Typography>
            <Chip
              icon={<School />}
              label={learning_focus.replace(/_/g, ' ')}
              color="primary"
              variant="outlined"
            />
          </Box>
        </CardContent>
      </Card>
    );
  };

  const renderSystemInsights = () => {
    if (!systemInsights) return null;

    return (
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <Insights color="primary" sx={{ mr: 1 }} />
            <Typography variant="h6" component="h3">
              System Insights
            </Typography>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                Key Insights
              </Typography>
              <List dense>
                {systemInsights.insights.slice(0, 5).map((insight, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={insight.title || 'Insight'}
                      secondary={insight.description || insight.insight || 'No description available'}
                    />
                  </ListItem>
                ))}
              </List>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                Lessons Learned
              </Typography>
              <List dense>
                {systemInsights.lessons_learned.slice(0, 5).map((lesson, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={lesson.lesson || lesson.title || 'Lesson'}
                      secondary={lesson.application || lesson.description || 'No application details'}
                    />
                  </ListItem>
                ))}
              </List>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  const renderPerformanceTrends = () => {
    if (!performanceTrends) return null;

    const trendData = [
      { name: 'Rating', trend: performanceTrends.rating_trend },
      { name: 'Win Rate', trend: performanceTrends.win_rate_trend },
      { name: 'PnL', trend: performanceTrends.pnl_trend }
    ];

    return (
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <Timeline color="primary" sx={{ mr: 1 }} />
            <Typography variant="h6" component="h3">
              Performance Trends
            </Typography>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={12} md={8}>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="trend" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary">
                  {performanceTrends.sample_size}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Analysis Samples
                </Typography>
                <Box mt={2}>
                  <Chip
                    icon={getTrendIcon(performanceTrends.overall_trend)}
                    label={`Overall: ${performanceTrends.overall_trend}`}
                    color={getTrendColor(performanceTrends.overall_trend) as any}
                    size="medium"
                  />
                </Box>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  const renderAnalysisHistory = () => {
    if (!analysisHistory.length) return null;

    return (
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <Assessment color="primary" sx={{ mr: 1 }} />
            <Typography variant="h6" component="h3">
              Recent Analysis History
            </Typography>
          </Box>

          <List>
            {analysisHistory.slice(0, 5).map((analysis, index) => (
              <React.Fragment key={index}>
                <ListItem>
                  <ListItemText
                    primary={`Play ${analysis.play_id}`}
                    secondary={
                      <Box>
                        <Typography variant="body2">
                          Status: {analysis.status}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {new Date(analysis.timestamp).toLocaleString()}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
                {index < analysisHistory.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
        <Button onClick={loadExperienceData} sx={{ ml: 2 }}>
          Retry
        </Button>
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" alignItems="center" mb={3}>
        <AutoGraph color="primary" sx={{ mr: 1, fontSize: 32 }} />
        <Typography variant="h4" component="h1">
          Experience Learning Dashboard
        </Typography>
        <Button
          variant="outlined"
          onClick={loadExperienceData}
          sx={{ ml: 'auto' }}
        >
          Refresh
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Agent Performance Cards */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom>
            Agent Performance & Learning
          </Typography>
        </Grid>
        {agents.map(agentId => {
          const insights = agentInsights[agentId];
          if (!insights) return null;
          
          return (
            <Grid item xs={12} sm={6} md={3} key={agentId}>
              {renderAgentCard(agentId, insights)}
            </Grid>
          );
        })}

        {/* System Insights */}
        <Grid item xs={12} md={6}>
          {renderSystemInsights()}
        </Grid>

        {/* Performance Trends */}
        <Grid item xs={12} md={6}>
          {renderPerformanceTrends()}
        </Grid>

        {/* Analysis History */}
        <Grid item xs={12}>
          {renderAnalysisHistory()}
        </Grid>
      </Grid>
    </Box>
  );
};

export default ExperienceLearningDashboard; 