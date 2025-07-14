import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  MessageSquare, 
  Send, 
  Activity, 
  Target, 
  Brain, 
  TrendingUp,
  Shield,
  Play,
  Pause,
  Settings,
  Zap,
  Eye
} from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
  actions?: string[];
}

interface SystemContext {
  mission: string;
  current_strategy: string;
  system_mode: string;
  research_priorities: string[];
  risk_parameters: Record<string, any>;
  trading_rules: Record<string, any>;
  active_directives: number;
  last_updated: string;
}

interface SystemPulse {
  timestamp: string;
  active_agents: number;
  directives_processed: number;
  trades_executed: number;
  research_activities: number;
  system_health: string;
  mission: string;
}

interface AgentThought {
  agent_id: string;
  agent_type: string;
  thought: string;
  reasoning: string;
  confidence: number;
  action_taken?: string;
  timestamp: string;
  metadata: Record<string, any>;
}

const SimplifiedGovernorInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [systemContext, setSystemContext] = useState<SystemContext | null>(null);
  const [systemPulse, setSystemPulse] = useState<SystemPulse | null>(null);
  const [agentThoughts, setAgentThoughts] = useState<AgentThought[]>([]);
  const [transparencyLevel, setTransparencyLevel] = useState<'full' | 'mission' | 'minimal'>('full');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Initialize WebSocket connections
  useEffect(() => {
    // Connect to governor WebSocket for real-time updates
    const ws = new WebSocket('ws://localhost:8000/ws/governor');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('Connected to Governor WebSocket');
      setIsStreaming(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    ws.onclose = () => {
      console.log('Disconnected from Governor WebSocket');
      setIsStreaming(false);
    };

    // Load initial data
    loadSystemContext();
    loadSystemPulse();

    return () => {
      ws.close();
    };
  }, []);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'initial_context':
        setSystemContext(data.context);
        break;
      case 'context_update':
        setSystemContext(data.context);
        break;
      case 'system_pulse':
        setSystemPulse(data.pulse);
        break;
      case 'agent_thought':
        setAgentThoughts(prev => [...prev, data.thought].slice(-50));
        break;
    }
  };

  const loadSystemContext = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/governor/context');
      const data = await response.json();
      if (data.status === 'success') {
        setSystemContext(data.context);
      }
    } catch (error) {
      console.error('Error loading system context:', error);
    }
  };

  const loadSystemPulse = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/governor/pulse');
      const data = await response.json();
      if (data.status === 'success') {
        setSystemPulse(data.pulse);
      }
    } catch (error) {
      console.error('Error loading system pulse:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/governor/conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage }),
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'agent',
          content: data.response,
          timestamp: new Date(),
          actions: data.metadata?.actions_taken || [],
        };

        setMessages(prev => [...prev, agentMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'excellent': return 'bg-green-500';
      case 'good': return 'bg-blue-500';
      case 'warning': return 'bg-yellow-500';
      case 'critical': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const quickActions = [
    {
      label: 'System Status',
      icon: Activity,
      message: 'Show me the current system status and what all agents are doing',
    },
    {
      label: 'Trade Performance',
      icon: TrendingUp,
      message: 'What trades have been executed recently and how are they performing?',
    },
    {
      label: 'Research Insights',
      icon: Brain,
      message: 'What research is currently being conducted and what insights have been found?',
    },
    {
      label: 'Risk Management',
      icon: Shield,
      message: 'Show me the current risk parameters and adjust them to be more conservative',
    },
  ];

  const handleQuickAction = (message: string) => {
    setInputMessage(message);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header with Mission Banner */}
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200 backdrop-blur-sm">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Target className="h-8 w-8 text-blue-600" />
                <div>
                  <CardTitle className="text-2xl font-bold text-blue-900">
                    RoboInvest Governor
                  </CardTitle>
                  <p className="text-blue-700 mt-1">
                    {systemContext?.mission || 'Discover the smartest and greatest upside that nobody is looking at'}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                {/* Transparency Level Selector */}
                <select
                  value={transparencyLevel}
                  onChange={(e) => setTransparencyLevel(e.target.value as any)}
                  className="px-3 py-1 border border-blue-200 rounded-md bg-white/80 backdrop-blur-sm"
                >
                  <option value="full">Full Transparency</option>
                  <option value="mission">Mission Focus</option>
                  <option value="minimal">Minimal</option>
                </select>
                
                {/* System Pulse Indicator */}
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${getHealthColor(systemPulse?.system_health || 'unknown')} animate-pulse`}></div>
                  <span className="text-sm text-blue-700">
                    {systemPulse?.active_agents || 0} agents active
                  </span>
                </div>
                
                {/* Streaming Indicator */}
                {isStreaming && (
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-xs text-green-600">Live</span>
                  </div>
                )}
              </div>
            </div>
          </CardHeader>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Conversation Area */}
          <div className="lg:col-span-3 space-y-6">
            <Tabs defaultValue="conversation" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="conversation" className="flex items-center space-x-2">
                  <MessageSquare className="h-4 w-4" />
                  <span>Conversation</span>
                </TabsTrigger>
                <TabsTrigger value="thoughts" className="flex items-center space-x-2">
                  <Brain className="h-4 w-4" />
                  <span>Agent Thoughts</span>
                </TabsTrigger>
                <TabsTrigger value="pulse" className="flex items-center space-x-2">
                  <Activity className="h-4 w-4" />
                  <span>System Pulse</span>
                </TabsTrigger>
                <TabsTrigger value="controls" className="flex items-center space-x-2">
                  <Settings className="h-4 w-4" />
                  <span>Controls</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value="conversation" className="space-y-4">
                <Card className="bg-white/80 backdrop-blur-sm border-blue-200">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <MessageSquare className="h-5 w-5" />
                      <span>Conversation with Governor Agent</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {/* Messages */}
                    <div className="h-96 overflow-y-auto space-y-4 mb-4 p-4 bg-gray-50 rounded-lg">
                      {messages.length === 0 ? (
                        <div className="text-center text-gray-500 py-8">
                          <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                          <p>Start a conversation with the Governor Agent</p>
                          <p className="text-sm">Ask about system status, trades, research, or make changes</p>
                        </div>
                      ) : (
                        messages.map((message) => (
                          <div
                            key={message.id}
                            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                          >
                            <div
                              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                                message.type === 'user'
                                  ? 'bg-blue-600 text-white'
                                  : 'bg-white border border-gray-200'
                              }`}
                            >
                              <p className="text-sm">{message.content}</p>
                              {message.actions && message.actions.length > 0 && (
                                <div className="mt-2 pt-2 border-t border-gray-200">
                                  <p className="text-xs text-green-600 font-medium">Actions taken:</p>
                                  <ul className="text-xs text-green-600">
                                    {message.actions.map((action, index) => (
                                      <li key={index}>• {action}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              <p className="text-xs opacity-70 mt-1">
                                {message.timestamp.toLocaleTimeString()}
                              </p>
                            </div>
                          </div>
                        ))
                      )}
                      <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="flex space-x-2">
                      <Input
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask the Governor Agent anything..."
                        disabled={isLoading}
                        className="flex-1"
                      />
                      <Button
                        onClick={sendMessage}
                        disabled={isLoading || !inputMessage.trim()}
                        className="bg-blue-600 hover:bg-blue-700"
                      >
                        {isLoading ? (
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <Send className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="thoughts" className="space-y-4">
                <Card className="bg-white/80 backdrop-blur-sm border-blue-200">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Brain className="h-5 w-5" />
                      <span>Real-Time Agent Thoughts</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-96 overflow-y-auto space-y-4">
                      {agentThoughts.length === 0 ? (
                        <div className="text-center text-gray-500 py-8">
                          <Brain className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                          <p>No agent thoughts yet</p>
                          <p className="text-sm">Start the autonomous system to see live agent reasoning</p>
                        </div>
                      ) : (
                        agentThoughts.map((thought, index) => (
                          <div key={index} className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-center space-x-2">
                                <Brain className="h-4 w-4 text-blue-600" />
                                <span className="font-medium">{thought.agent_id}</span>
                                <Badge>{Math.round(thought.confidence * 100)}% confidence</Badge>
                              </div>
                              <span className="text-xs text-gray-500">
                                {new Date(thought.timestamp).toLocaleTimeString()}
                              </span>
                            </div>
                            <div className="space-y-2">
                              <div>
                                <div className="text-sm font-medium text-gray-700">Thought:</div>
                                <div className="text-sm text-gray-900">{thought.thought}</div>
                              </div>
                              <div>
                                <div className="text-sm font-medium text-gray-700">Reasoning:</div>
                                <div className="text-sm text-gray-900">{thought.reasoning}</div>
                              </div>
                              {thought.action_taken && (
                                <div>
                                  <div className="text-sm font-medium text-gray-700">Action:</div>
                                  <div className="text-sm text-green-700">{thought.action_taken}</div>
                                </div>
                              )}
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="pulse" className="space-y-4">
                <Card className="bg-white/80 backdrop-blur-sm border-blue-200">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Activity className="h-5 w-5" />
                      <span>System Pulse</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {systemPulse ? (
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center p-4 bg-blue-50 rounded-lg">
                          <div className="text-2xl font-bold text-blue-600">{systemPulse.active_agents}</div>
                          <div className="text-sm text-blue-700">Active Agents</div>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-lg">
                          <div className="text-2xl font-bold text-green-600">{systemPulse.directives_processed}</div>
                          <div className="text-sm text-green-700">Directives Processed</div>
                        </div>
                        <div className="text-center p-4 bg-purple-50 rounded-lg">
                          <div className="text-2xl font-bold text-purple-600">{systemPulse.trades_executed}</div>
                          <div className="text-sm text-purple-700">Trades Executed</div>
                        </div>
                        <div className="text-center p-4 bg-orange-50 rounded-lg">
                          <div className="text-2xl font-bold text-orange-600">{systemPulse.research_activities}</div>
                          <div className="text-sm text-orange-700">Research Activities</div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center text-gray-500 py-8">
                        <Activity className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                        <p>Loading system pulse...</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="controls" className="space-y-4">
                <Card className="bg-white/80 backdrop-blur-sm border-blue-200">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Settings className="h-5 w-5" />
                      <span>System Controls</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Button className="w-full bg-green-600 hover:bg-green-700">
                        <Play className="h-4 w-4 mr-2" />
                        Start Autonomous System
                      </Button>
                      <Button className="w-full bg-red-600 hover:bg-red-700">
                        <Pause className="h-4 w-4 mr-2" />
                        Stop Autonomous System
                      </Button>
                      <Button className="w-full bg-yellow-600 hover:bg-yellow-700">
                        <Shield className="h-4 w-4 mr-2" />
                        Emergency Stop
                      </Button>
                      <Button className="w-full bg-blue-600 hover:bg-blue-700">
                        <Zap className="h-4 w-4 mr-2" />
                        Paper Trading Only
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card className="bg-white/80 backdrop-blur-sm border-blue-200">
              <CardHeader>
                <CardTitle className="text-lg">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {quickActions.map((action, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      className="w-full justify-start"
                      onClick={() => handleQuickAction(action.message)}
                    >
                      <action.icon className="h-4 w-4 mr-2" />
                      {action.label}
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* System Context */}
            <Card className="bg-white/80 backdrop-blur-sm border-blue-200">
              <CardHeader>
                <CardTitle className="text-lg">System Context</CardTitle>
              </CardHeader>
              <CardContent>
                {systemContext ? (
                  <div className="space-y-3">
                    <div>
                      <div className="text-sm font-medium text-gray-700">Strategy:</div>
                      <div className="text-sm text-gray-900">{systemContext.current_strategy}</div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-700">Mode:</div>
                      <Badge variant="outline">{systemContext.system_mode}</Badge>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-700">Research Focus:</div>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {systemContext.research_priorities.map((priority, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {priority}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-700">Active Directives:</div>
                      <div className="text-sm text-gray-900">{systemContext.active_directives}</div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-gray-500 py-4">
                    <Eye className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                    <p className="text-sm">Loading system context...</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimplifiedGovernorInterface; 