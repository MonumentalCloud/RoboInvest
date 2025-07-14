import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Chip,
  Avatar,
  Divider,
  LinearProgress,
  IconButton,
  Tooltip,
  Alert,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Badge,
  Tabs,
  Tab,
  CircularProgress
} from '@mui/material';
import { Grid } from '@mui/material';
import {
  Send,
  Psychology,
  TrendingUp,
  Security,
  Settings,
  Refresh,
  PlayArrow,
  Pause,
  Stop,
  Warning,
  CheckCircle,
  Error,
  Info,
  AutoGraph,
  Timeline,
  Assessment
} from '@mui/icons-material';
import { customColors } from '../theme';

interface Message {
  id: string;
  type: 'user' | 'governor' | 'system';
  content: string;
  timestamp: Date;
  metadata?: any;
}

interface SystemContext {
  mission: string;
  current_strategy: string;
  risk_parameters: any;
  performance_targets: any;
  active_directives: string[];
  system_mode: string;
  governance_rules: any;
  research_priorities: string[];
  trading_rules: any;
  last_updated: string;
}

interface AgentThought {
  agent_id: string;
  timestamp: string;
  thought: string;
  reasoning: string;
  confidence: number;
  action_taken: string;
}

interface SystemPulse {
  timestamp: string;
  active_agents: number;
  directives_processed: number;
  trades_executed: number;
  research_activities: number;
  system_health: string;
}

const GovernorControlPanel: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'governor',
      content: "Greetings, Human Governor. I am your AI administrative agent, ready to assist with any aspect of the autonomous trading system. I can monitor agents, adjust strategies, manage risk, and execute any system changes you require. How may I serve you today?",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [systemContext, setSystemContext] = useState<SystemContext | null>(null);
  const [agentThoughts, setAgentThoughts] = useState<AgentThought[]>([]);
  const [systemPulse, setSystemPulse] = useState<SystemPulse | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [wsConnections, setWsConnections] = useState<{ [key: string]: WebSocket }>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    initializeWebSocketConnections();
    fetchInitialData();
    return () => {
      Object.values(wsConnections).forEach(ws => ws.close());
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeWebSocketConnections = () => {
    const connections: { [key: string]: WebSocket } = {};

    // System context WebSocket
    try {
      const contextWs = new WebSocket(`ws://localhost:8081/api/governor/ws/context`);
      contextWs.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'context_update') {
          setSystemContext(data.context);
        }
      };
      contextWs.onerror = (error) => {
        console.log('WebSocket context connection error:', error);
      };
      connections.context = contextWs;
    } catch (error) {
      console.log('Failed to connect to context WebSocket');
    }

    // Agent thoughts WebSocket
    try {
      const thoughtsWs = new WebSocket(`ws://localhost:8081/api/governor/ws/thoughts`);
      thoughtsWs.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'agent_thought') {
          setAgentThoughts(prev => [...prev.slice(-9), data.thought]);
        }
      };
      thoughtsWs.onerror = (error) => {
        console.log('WebSocket thoughts connection error:', error);
      };
      connections.thoughts = thoughtsWs;
    } catch (error) {
      console.log('Failed to connect to thoughts WebSocket');
    }

    // System pulse WebSocket
    try {
      const pulseWs = new WebSocket(`ws://localhost:8081/api/governor/ws/pulse`);
      pulseWs.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'system_pulse') {
          setSystemPulse(data.pulse);
        }
      };
      pulseWs.onerror = (error) => {
        console.log('WebSocket pulse connection error:', error);
      };
      connections.pulse = pulseWs;
    } catch (error) {
      console.log('Failed to connect to pulse WebSocket');
    }

    setWsConnections(connections);
  };

  const fetchInitialData = async () => {
    try {
      const [contextRes, pulseRes] = await Promise.all([
        fetch('http://localhost:8081/api/governor/context'),
        fetch('http://localhost:8081/api/governor/pulse')
      ]);
      
      if (contextRes.ok) {
        const contextData = await contextRes.json();
        setSystemContext(contextData.context);
      }
      
      if (pulseRes.ok) {
        const pulseData = await pulseRes.json();
        setSystemPulse(pulseData);
      }
    } catch (error) {
      console.error('Error fetching initial data:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:8081/api/governor/conversation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputMessage })
      });

      if (response.ok) {
        const data = await response.json();
        const governorMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'governor',
          content: data.response,
          timestamp: new Date(),
          metadata: data.metadata
        };
        setMessages(prev => [...prev, governorMessage]);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: "I apologize, but I'm having trouble processing your request right now. Please try again.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getSystemHealthColor = (health: string) => {
    switch (health) {
      case 'excellent': return customColors.success;
      case 'good': return customColors.info;
      case 'operational': return customColors.warning;
      case 'warning': return customColors.error;
      default: return customColors.neutral;
    }
  };

  const getSystemHealthIcon = (health: string) => {
    switch (health) {
      case 'excellent': return <CheckCircle />;
      case 'good': return <CheckCircle />;
      case 'operational': return <Warning />;
      case 'warning': return <Error />;
      default: return <Info />;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const renderMessage = (message: Message) => {
    const isUser = message.type === 'user';
    const isSystem = message.type === 'system';

    return (
      <Box
        key={message.id}
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
        }}
      >
        <Paper
          sx={{
            maxWidth: '70%',
            p: 2,
            backgroundColor: isUser 
              ? 'rgba(0, 212, 170, 0.1)' 
              : isSystem 
                ? 'rgba(239, 68, 68, 0.1)'
                : 'rgba(255, 255, 255, 0.05)',
            border: `1px solid ${
              isUser 
                ? 'rgba(0, 212, 170, 0.3)' 
                : isSystem 
                  ? 'rgba(239, 68, 68, 0.3)'
                  : 'rgba(255, 255, 255, 0.1)'
            }`,
            borderRadius: 2,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Avatar
              sx={{
                width: 24,
                height: 24,
                mr: 1,
                backgroundColor: isUser 
                  ? customColors.primary 
                  : isSystem 
                    ? customColors.error
                    : customColors.secondary,
              }}
            >
              {isUser ? 'U' : isSystem ? 'S' : 'G'}
            </Avatar>
            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
              {isUser ? 'You' : isSystem ? 'System' : 'Governor'} • {message.timestamp.toLocaleTimeString()}
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ lineHeight: 1.5 }}>
            {message.content}
          </Typography>
        </Paper>
      </Box>
    );
  };

  return (
    <Box sx={{ height: 'calc(100vh - 140px)' }}>
      <Grid container spacing={3} sx={{ height: '100%' }}>
        {/* Main Chat Interface */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 0 }}>
              {/* Header */}
              <Box sx={{ p: 3, borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Avatar sx={{ mr: 2, backgroundColor: customColors.primary }}>
                      <Psychology />
                    </Avatar>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        AI Governor Interface
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        Autonomous Trading System Control
                      </Typography>
                    </Box>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Tooltip title="Refresh">
                      <IconButton size="small" onClick={fetchInitialData}>
                        <Refresh />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Settings">
                      <IconButton size="small">
                        <Settings />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
              </Box>

              {/* Messages */}
              <Box sx={{ flexGrow: 1, overflow: 'auto', p: 3 }}>
                {messages.map(renderMessage)}
                {isTyping && (
                  <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                    <Paper sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <CircularProgress size={16} sx={{ mr: 1 }} />
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          Governor is typing...
                        </Typography>
                      </Box>
                    </Paper>
                  </Box>
                )}
                <div ref={messagesEndRef} />
              </Box>

              {/* Input */}
              <Box sx={{ p: 3, borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <TextField
                    fullWidth
                    variant="outlined"
                    placeholder="Ask the Governor anything about the trading system..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={isTyping}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 2,
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        '&:hover': {
                          backgroundColor: 'rgba(255, 255, 255, 0.08)',
                        },
                      },
                    }}
                  />
                  <Button
                    variant="contained"
                    onClick={sendMessage}
                    disabled={!inputMessage.trim() || isTyping}
                    sx={{ minWidth: 'auto', px: 2 }}
                  >
                    <Send />
                  </Button>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* System Status Panel */}
        <Grid item xs={12} md={4}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, height: '100%' }}>
            {/* System Pulse */}
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Timeline sx={{ mr: 1, color: customColors.primary }} />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    System Pulse
                  </Typography>
                </Box>
                {systemPulse ? (
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Box sx={{ color: getSystemHealthColor(systemPulse.system_health), mr: 1 }}>
                        {getSystemHealthIcon(systemPulse.system_health)}
                      </Box>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {systemPulse.system_health.charAt(0).toUpperCase() + systemPulse.system_health.slice(1)}
                      </Typography>
                    </Box>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                          Active Agents
                        </Typography>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {systemPulse.active_agents}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                          Trades Today
                        </Typography>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {systemPulse.trades_executed}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                          Directives
                        </Typography>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {systemPulse.directives_processed}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                          Research
                        </Typography>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {systemPulse.research_activities}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>
                ) : (
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', py: 2 }}>
                    <CircularProgress size={24} />
                  </Box>
                )}
              </CardContent>
            </Card>

            {/* System Context */}
            {systemContext && (
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Assessment sx={{ mr: 1, color: customColors.secondary }} />
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      System Context
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      Current Strategy
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {systemContext.current_strategy}
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      System Mode
                    </Typography>
                    <Chip
                      label={systemContext.system_mode}
                      size="small"
                      sx={{
                        backgroundColor: 'rgba(0, 212, 170, 0.2)',
                        color: customColors.primary,
                        fontWeight: 600,
                      }}
                    />
                  </Box>
                  <Box>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      Active Directives
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      {systemContext.active_directives.map((directive, index) => (
                        <Chip
                          key={index}
                          label={directive}
                          size="small"
                          variant="outlined"
                          sx={{ mr: 0.5, mb: 0.5 }}
                        />
                      ))}
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            )}

            {/* Agent Thoughts */}
            <Card sx={{ flexGrow: 1 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <AutoGraph sx={{ mr: 1, color: customColors.accent }} />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Agent Thoughts
                  </Typography>
                </Box>
                <List sx={{ p: 0 }}>
                  {agentThoughts.slice(-5).map((thought, index) => (
                    <ListItem key={index} sx={{ px: 0, py: 1 }}>
                      <ListItemAvatar>
                        <Avatar sx={{ width: 32, height: 32, fontSize: '0.75rem' }}>
                          {thought.agent_id.split('_')[1]}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={thought.thought}
                        secondary={`${thought.action_taken} • ${formatTimestamp(thought.timestamp)}`}
                        primaryTypographyProps={{ variant: 'body2', sx: { fontWeight: 500 } }}
                        secondaryTypographyProps={{ variant: 'caption' }}
                      />
                      <Chip
                        label={`${Math.round(thought.confidence * 100)}%`}
                        size="small"
                        sx={{
                          backgroundColor: thought.confidence > 0.8 
                            ? 'rgba(16, 185, 129, 0.2)' 
                            : 'rgba(245, 158, 11, 0.2)',
                          color: thought.confidence > 0.8 
                            ? customColors.success 
                            : customColors.warning,
                          fontWeight: 600,
                        }}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default GovernorControlPanel; 