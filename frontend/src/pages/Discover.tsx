import { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
  Avatar,
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
} from '@mui/lab';
import {
  Psychology,
  TrendingUp,
  Search,
  Lightbulb,
  ExpandMore,
  Circle,
  AccountTree,
} from '@mui/icons-material';

// Types for research data
interface ResearchItem {
  id: number;
  title: string;
  status: string;
  progress: number;
  confidence: number;
  timeStarted: string;
  description: string;
  leads: string[];
  expectedOutcome: string;
  symbols?: string[];
}

interface AlphaOpportunity {
  symbol: string;
  confidence: number;
  thesis: string;
  timeHorizon: string;
  catalysts: string[];
  priceTarget?: number;
  currentPrice?: number;
  upside?: number;
}

interface MarketInsight {
  timestamp: string;
  insight: string;
  confidence: number;
  actionable: boolean;
}

interface ResearchData {
  activeResearch: ResearchItem[];
  discoveredAlpha: AlphaOpportunity[];
  marketInsights: MarketInsight[];
}

// Hook to fetch research data
const useResearchData = () => {
  const [data, setData] = useState<ResearchData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/research');
        const researchData = await response.json();
        setData(researchData);
      } catch (error) {
        console.error('Failed to fetch research data:', error);
        // Fallback to mock data if API fails
        setData({
          activeResearch: [
            {
              id: 1,
              title: "Market Analysis - Demo Mode",
              status: "analyzing",
              progress: 75,
              confidence: 0.82,
              timeStarted: "2 min ago",
              description: "Running in demo mode - connect API for live data",
              leads: ["Demo lead 1", "Demo lead 2"],
              expectedOutcome: "Demo outcome"
            }
          ],
          discoveredAlpha: [
            {
              symbol: "DEMO",
              confidence: 0.75,
              thesis: "Demo mode - connect backend for live alpha discovery",
              timeHorizon: "Demo",
              catalysts: ["Demo catalyst"]
            }
          ],
          marketInsights: []
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    // Refresh data every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  return { data, loading };
};

// Hook to fetch AI thinking data
const useAIThinkingData = () => {
  const [thinkingProcess, setThinkingProcess] = useState([
    { time: new Date().toLocaleTimeString(), thought: "Initializing AI research systems..." }
  ]);
  const [aiStatus, setAiStatus] = useState({ is_running: false });

  useEffect(() => {
    // Start AI thinking service when component mounts
    const startAIThinking = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/ai-thoughts/start', {
          method: 'POST'
        });
        const result = await response.json();
        console.log('AI thinking service started:', result);
      } catch (error) {
        console.error('Failed to start AI thinking service:', error);
      }
    };

    startAIThinking();

    // Fetch AI thoughts periodically
    const fetchAIThoughts = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/ai-thoughts');
        const data = await response.json();
        
        if (data.thoughts && data.thoughts.length > 0) {
          setThinkingProcess(data.thoughts);
        }
        
        if (data.status) {
          setAiStatus(data.status);
        }
      } catch (error) {
        console.error('Failed to fetch AI thoughts:', error);
        // Fallback to simulated thoughts if API fails
        setThinkingProcess(prev => [
          {
            time: new Date().toLocaleTimeString(),
            thought: "AI service offline - using fallback analysis..."
          },
          ...prev.slice(0, 9)
        ]);
      }
    };

    // Initial fetch
    fetchAIThoughts();

    // Set up interval to fetch thoughts every 5 seconds
    const interval = setInterval(fetchAIThoughts, 5000);

    return () => clearInterval(interval);
  }, []);

  return { thinkingProcess, aiStatus };
};

export default function Discover() {
  const { data: researchData, loading } = useResearchData();
  const { thinkingProcess, aiStatus } = useAIThinkingData();
  const [selectedResearch, setSelectedResearch] = useState(null);

  if (loading) {
    return (
      <Box sx={{ p: 2, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <Box sx={{ textAlign: 'center' }}>
          <LinearProgress sx={{ mb: 2, width: 300 }} />
          <Typography>Loading AI research systems...</Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Psychology sx={{ mr: 2, color: 'primary.main' }} />
        AI Research & Alpha Discovery
      </Typography>

      <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', lg: 'row' } }}>
        {/* Active Research Panel */}
        <Box sx={{ flex: 2 }}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <AccountTree sx={{ mr: 1 }} />
                Active Research Streams
                <Chip 
                  label={`${researchData?.activeResearch?.length || 0} ACTIVE`} 
                  color="primary" 
                  size="small" 
                  sx={{ ml: 'auto' }}
                />
              </Typography>
              
              {researchData?.activeResearch?.map((research) => (
                <Accordion key={research.id} sx={{ mb: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box sx={{ width: '100%' }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {research.title}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Chip 
                            label={research.status}
                            color={research.status === 'analyzing' ? 'primary' : research.status === 'validating' ? 'success' : 'warning'}
                            size="small"
                          />
                          <Chip 
                            label={`${Math.round(research.confidence * 100)}% confident`}
                            variant="outlined"
                            size="small"
                          />
                        </Box>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={research.progress} 
                        sx={{ height: 6, borderRadius: 3 }}
                      />
                      <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5 }}>
                        Started {research.timeStarted} • {research.progress}% complete
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {research.description}
                    </Typography>
                    
                    <Typography variant="subtitle2" gutterBottom>Research Leads:</Typography>
                    <Box sx={{ mb: 2 }}>
                      {research.leads?.map((lead, idx) => (
                        <Chip key={idx} label={lead} size="small" sx={{ mr: 1, mb: 1 }} />
                      ))}
                    </Box>
                    
                    {research.symbols && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>Symbols:</Typography>
                        {research.symbols.map((symbol, idx) => (
                          <Chip key={idx} label={symbol} size="small" variant="outlined" sx={{ mr: 1, mb: 1 }} />
                        ))}
                      </Box>
                    )}
                    
                    <Paper sx={{ p: 2, backgroundColor: 'action.hover' }}>
                      <Typography variant="subtitle2" gutterBottom>Expected Outcome:</Typography>
                      <Typography variant="body2">{research.expectedOutcome}</Typography>
                    </Paper>
                  </AccordionDetails>
                </Accordion>
              ))}
            </CardContent>
          </Card>

          {/* Discovered Alpha Opportunities */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <Lightbulb sx={{ mr: 1, color: 'warning.main' }} />
                Discovered Alpha Opportunities
                <Chip 
                  label={`${researchData?.discoveredAlpha?.length || 0} OPPORTUNITIES`} 
                  color="success" 
                  size="small" 
                  sx={{ ml: 'auto' }}
                />
              </Typography>
              
              {researchData?.discoveredAlpha?.map((alpha, idx) => (
                <Paper key={idx} sx={{ p: 2, mb: 2, border: '1px solid', borderColor: 'success.light' }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="h6" color="success.main" fontWeight="bold">
                      ${alpha.symbol}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Chip 
                        label={`${Math.round(alpha.confidence * 100)}% confidence`}
                        color="success"
                        size="small"
                      />
                      {alpha.upside && (
                        <Chip 
                          label={`+${alpha.upside}% upside`}
                          color="primary"
                          size="small"
                        />
                      )}
                    </Box>
                  </Box>
                  <Typography variant="subtitle2" gutterBottom>Investment Thesis:</Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>{alpha.thesis}</Typography>
                  <Typography variant="caption" color="textSecondary">
                    Time Horizon: {alpha.timeHorizon}
                  </Typography>
                  {alpha.priceTarget && alpha.currentPrice && (
                    <Typography variant="caption" color="textSecondary" sx={{ ml: 2 }}>
                      Target: ${alpha.priceTarget} (Current: ${alpha.currentPrice})
                    </Typography>
                  )}
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" fontWeight="bold">Key Catalysts: </Typography>
                    {alpha.catalysts?.map((catalyst, cidx) => (
                      <Chip key={cidx} label={catalyst} size="small" variant="outlined" sx={{ mr: 0.5 }} />
                    ))}
                  </Box>
                </Paper>
              ))}
            </CardContent>
          </Card>
        </Box>

        {/* AI Thinking Process Panel */}
        <Box sx={{ flex: 1 }}>
          <Card sx={{ height: 'fit-content' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <Search sx={{ mr: 1 }} />
                AI Thinking Process
                <Chip 
                  label={aiStatus.is_running ? "LIVE" : "OFFLINE"} 
                  color={aiStatus.is_running ? "success" : "error"} 
                  size="small" 
                  sx={{ 
                    ml: 'auto', 
                    animation: aiStatus.is_running ? 'pulse 2s infinite' : 'none' 
                  }} 
                />
              </Typography>
              
              <Timeline>
                {thinkingProcess.map((thought, idx) => (
                  <TimelineItem key={idx}>
                    <TimelineSeparator>
                      <TimelineDot 
                        color={idx === 0 ? "primary" : "grey"}
                        sx={{ animation: idx === 0 ? 'pulse 2s infinite' : 'none' }}
                      >
                        <Circle fontSize="small" />
                      </TimelineDot>
                      {idx < thinkingProcess.length - 1 && <TimelineConnector />}
                    </TimelineSeparator>
                    <TimelineContent>
                      <Typography variant="caption" color="textSecondary">
                        {thought.time}
                      </Typography>
                      <Typography variant="body2" sx={{ 
                        fontWeight: idx === 0 ? 'bold' : 'normal',
                        color: idx === 0 ? 'primary.main' : 'inherit'
                      }}>
                        {thought.thought}
                      </Typography>
                    </TimelineContent>
                  </TimelineItem>
                ))}
              </Timeline>
            </CardContent>
          </Card>

          {/* Market Insights */}
          {researchData?.marketInsights && researchData.marketInsights.length > 0 && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Market Insights
                </Typography>
                {researchData.marketInsights.map((insight, idx) => (
                  <Paper key={idx} sx={{ p: 2, mb: 1, backgroundColor: insight.actionable ? 'warning.light' : 'action.hover' }}>
                    <Typography variant="body2" fontWeight="bold">
                      {insight.insight}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Confidence: {Math.round(insight.confidence * 100)}%
                      {insight.actionable && ' • Actionable'}
                    </Typography>
                  </Paper>
                ))}
              </CardContent>
            </Card>
          )}
        </Box>
      </Box>
    </Box>
  );
} 