import React, { useEffect, useState, useRef } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Chip, 
  CircularProgress, 
  Alert
} from '@mui/material';
import {
  TreeView,
  TreeItem,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent
} from '@mui/lab';
import {
  Psychology as PsychologyIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  PlayArrow as PlayArrowIcon,
  ExpandMore,
  ChevronRight,
  Warning as WarningIcon,
  Info as InfoIcon,
  Error as ErrorIcon,
  Notifications as NotificationsIcon,
  Event as EventIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Code as CodeIcon
} from '@mui/icons-material';
import { useDecisionTrees } from '../hooks';
import { api } from '../api';

interface ResearchTree {
  id: string;
  type: string;
  title: string;
  content: string;
  status: string;
  parent?: string;
  timestamp: string;
  metadata: any;
}

interface CentralEvent {
  event_id: string;
  event_type: string;
  priority: string;
  timestamp: string;
  source: string;
  title: string;
  message: string;
  metadata: any;
  tags: string[];
}

const AlphaStream: React.FC = () => {
  const [allResearchTrees, setAllResearchTrees] = useState<ResearchTree[]>([]);
  const [centralEvents, setCentralEvents] = useState<CentralEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [eventFilter, setEventFilter] = useState<string>('all');
  const [eventStatistics, setEventStatistics] = useState<any>(null);
  
  const { data: decisionTreesData } = useDecisionTrees();
  const wsRef = useRef<WebSocket | null>(null);

  // Fetch all research trees and central events on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch all research trees
        const treesResponse = await api.get('/research/decision-trees/all');
        if (treesResponse.data.status === 'success') {
          setAllResearchTrees(treesResponse.data.data || []);
        }
        
        // Fetch recent central events
        const eventsResponse = await api.get('/events/recent?limit=100');
        if (eventsResponse.data.status === 'success') {
          setCentralEvents(eventsResponse.data.data || []);
        }
        
        // Fetch event statistics
        const statsResponse = await api.get('/events/statistics');
        if (statsResponse.data.status === 'success') {
          setEventStatistics(statsResponse.data.data);
        }
        
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // WebSocket connection for real-time central events
  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket(`ws://${window.location.hostname}:8081/ws/central-events`);
      
      ws.onopen = () => {
        console.log('Connected to central events WebSocket');
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'central_event') {
            setCentralEvents(prev => [data.event, ...prev.slice(0, 99)]); // Keep last 100
          } else if (data.type === 'initial_events') {
            setCentralEvents(data.events || []);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected, attempting to reconnect...');
        setTimeout(connectWebSocket, 5000);
      };
      
      wsRef.current = ws;
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const getEventIcon = (eventType: string, priority: string) => {
    const isHighPriority = priority === 'high' || priority === 'critical';
    
    switch (eventType) {
      case 'ai_thought':
        return <PsychologyIcon color={isHighPriority ? 'error' : 'primary'} />;
      case 'trade_event':
        return <TrendingUpIcon color={isHighPriority ? 'error' : 'success'} />;
      case 'play_event':
        return <PlayArrowIcon color={isHighPriority ? 'error' : 'primary'} />;
      case 'meta_agent':
        return <SecurityIcon color={isHighPriority ? 'error' : 'secondary'} />;
      case 'notification':
        return <NotificationsIcon color={isHighPriority ? 'error' : 'info'} />;
      case 'performance':
        return <SpeedIcon color={isHighPriority ? 'error' : 'success'} />;
      case 'research':
        return <MemoryIcon color={isHighPriority ? 'error' : 'primary'} />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return <EventIcon color="action" />;
    }
  };

  const getEventColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getNodeIcon = (nodeType: string, status: string) => {
    const isActive = status === 'active';
    
    switch (nodeType) {
      case 'decision':
        return <AssessmentIcon color={isActive ? 'primary' : 'action'} />;
      case 'analysis':
        return <AnalyticsIcon color={isActive ? 'primary' : 'action'} />;
      case 'research':
        return <MemoryIcon color={isActive ? 'primary' : 'action'} />;
      case 'strategy':
        return <TrendingUpIcon color={isActive ? 'primary' : 'action'} />;
      case 'execution':
        return <PlayArrowIcon color={isActive ? 'primary' : 'action'} />;
      default:
        return <CodeIcon color={isActive ? 'primary' : 'action'} />;
    }
  };

  const renderTreeNodes = (nodes: ResearchTree[], parentId?: string) => {
    return nodes
      .filter(node => node.parent === parentId)
      .map(node => (
        <TreeItem
          key={node.id}
          nodeId={node.id}
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {getNodeIcon(node.type, node.status)}
              <Typography
                variant="body2"
                sx={{
                  fontWeight: node.status === 'active' ? 'bold' : 'normal',
                  color: node.status === 'active' ? 'primary.main' : 'text.primary'
                }}
              >
                {node.title}
              </Typography>
              <Chip
                label={node.status}
                size="small"
                color={node.status === 'active' ? 'primary' : 'default'}
                variant={node.status === 'active' ? 'filled' : 'outlined'}
              />
            </Box>
          }
        >
          {renderTreeNodes(nodes, node.id)}
        </TreeItem>
      ));
  };

  const filteredEvents = centralEvents.filter(event => {
    if (eventFilter === 'all') return true;
    return event.event_type === eventFilter;
  });

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2, height: '100vh', overflow: 'hidden' }}>
      <Typography variant="h4" gutterBottom>
        🧠 Alpha Stream - Research Trees & Central Event Monitor
      </Typography>
      
      <Grid container spacing={2} sx={{ height: 'calc(100vh - 120px)' }}>
        {/* Research Trees Panel */}
        <Grid xs={12} md={6}>
          <Paper sx={{ height: '100%', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
              <Typography variant="h6">
                🌳 Research Decision Trees
                <Chip 
                  label={`${allResearchTrees.length} trees`} 
                  size="small" 
                  sx={{ ml: 1 }} 
                />
              </Typography>
            </Box>
            
            <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
              {allResearchTrees.length > 0 ? (
                <TreeView
                  defaultCollapseIcon={<ExpandMore />}
                  defaultExpandIcon={<ChevronRight />}
                  defaultExpanded={['root']}
                >
                  {renderTreeNodes(allResearchTrees)}
                </TreeView>
              ) : (
                <Typography color="text.secondary" align="center">
                  No research trees available
                </Typography>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Central Event Monitor Panel */}
        <Grid xs={12} md={6}>
          <Paper sx={{ height: '100%', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
              <Typography variant="h6">
                📊 Central Event Monitor
                {eventStatistics && (
                  <Chip 
                    label={`${eventStatistics.total_events} total events`} 
                    size="small" 
                    sx={{ ml: 1 }} 
                  />
                )}
              </Typography>
              
              {/* Event Type Filter */}
              <Box sx={{ mt: 1 }}>
                <Chip
                  label="All"
                  onClick={() => setEventFilter('all')}
                  color={eventFilter === 'all' ? 'primary' : 'default'}
                  size="small"
                  sx={{ mr: 1 }}
                />
                <Chip
                  label="AI Thoughts"
                  onClick={() => setEventFilter('ai_thought')}
                  color={eventFilter === 'ai_thought' ? 'primary' : 'default'}
                  size="small"
                  sx={{ mr: 1 }}
                />
                <Chip
                  label="Trades"
                  onClick={() => setEventFilter('trade_event')}
                  color={eventFilter === 'trade_event' ? 'primary' : 'default'}
                  size="small"
                  sx={{ mr: 1 }}
                />
                <Chip
                  label="Plays"
                  onClick={() => setEventFilter('play_event')}
                  color={eventFilter === 'play_event' ? 'primary' : 'default'}
                  size="small"
                  sx={{ mr: 1 }}
                />
                <Chip
                  label="System"
                  onClick={() => setEventFilter('system_log')}
                  color={eventFilter === 'system_log' ? 'primary' : 'default'}
                  size="small"
                />
              </Box>
            </Box>
            
            <Box sx={{ flex: 1, overflow: 'auto' }}>
              <Timeline position="right">
                {filteredEvents.map((event, index) => (
                  <TimelineItem key={event.event_id}>
                    <TimelineOppositeContent sx={{ m: 'auto 0' }} variant="body2" color="text.secondary">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </TimelineOppositeContent>
                    <TimelineSeparator>
                      <TimelineDot color={getEventColor(event.priority) as any}>
                        {getEventIcon(event.event_type, event.priority)}
                      </TimelineDot>
                      {index < filteredEvents.length - 1 && <TimelineConnector />}
                    </TimelineSeparator>
                    <TimelineContent sx={{ py: '12px', px: 2 }}>
                      <Typography variant="h6" component="span">
                        {event.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {event.message}
                      </Typography>
                      <Box sx={{ mt: 1 }}>
                        <Chip 
                          label={event.source} 
                          size="small" 
                          sx={{ mr: 1 }} 
                        />
                        <Chip 
                          label={event.priority} 
                          size="small" 
                          color={getEventColor(event.priority) as any}
                        />
                      </Box>
                    </TimelineContent>
                  </TimelineItem>
                ))}
              </Timeline>
              
              {filteredEvents.length === 0 && (
                <Box sx={{ p: 2, textAlign: 'center' }}>
                  <Typography color="text.secondary">
                    No events to display
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AlphaStream; 