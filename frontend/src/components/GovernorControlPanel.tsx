import React, { useState, useEffect, useRef } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Alert } from './ui/alert';
import { Tabs } from './ui/tabs';
import GovernorChatInterface from './GovernorChatInterface';

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
  const [activeTab, setActiveTab] = useState('conversation');
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
    const contextWs = new WebSocket(`ws://localhost:8000/api/governor/ws/context`);
    contextWs.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'context_update') {
        setSystemContext(data.context);
      }
    };
    connections.context = contextWs;

    // Agent thoughts WebSocket
    const thoughtsWs = new WebSocket(`ws://localhost:8000/api/governor/ws/thoughts`);
    thoughtsWs.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'agent_thought') {
        setAgentThoughts(prev => [...prev.slice(-9), data.thought]);
      }
    };
    connections.thoughts = thoughtsWs;

    // System pulse WebSocket
    const pulseWs = new WebSocket(`ws://localhost:8000/api/governor/ws/pulse`);
    pulseWs.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'system_pulse') {
        setSystemPulse(data.pulse);
      }
    };
    connections.pulse = pulseWs;

    setWsConnections(connections);
  };

  const fetchInitialData = async () => {
    try {
      const [contextRes, pulseRes] = await Promise.all([
        fetch('http://localhost:8000/api/governor/context'),
        fetch('http://localhost:8000/api/governor/pulse')
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
      const response = await fetch('http://localhost:8000/api/governor/conversation', {
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

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getSystemHealthColor = (health: string) => {
    switch (health) {
      case 'excellent': return 'text-green-500';
      case 'good': return 'text-blue-500';
      case 'operational': return 'text-yellow-500';
      case 'warning': return 'text-orange-500';
      case 'critical': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            👑 Governor Control Panel
          </h1>
          <p className="text-purple-200 text-lg">
            Natural conversation interface with your AI administrative agent
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Conversation Area */}
          <div className="lg:col-span-3">
            <Card className="h-[600px] flex flex-col bg-black/20 backdrop-blur-sm border-purple-500/30">
              <div className="p-6 border-b border-purple-500/30">
                <h2 className="text-xl font-semibold text-white mb-2">
                  💬 Conversation with Governor Agent
                </h2>
                <p className="text-purple-200 text-sm">
                  Speak naturally with your AI administrator about any system aspect
                </p>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                        message.type === 'user'
                          ? 'bg-purple-600 text-white'
                          : message.type === 'governor'
                          ? 'bg-blue-600 text-white'
                          : 'bg-red-600 text-white'
                      }`}
                    >
                      <div className="text-sm font-medium mb-1">
                        {message.type === 'user' ? 'You' : 
                         message.type === 'governor' ? 'Governor Agent' : 'System'}
                      </div>
                      <div className="text-sm leading-relaxed">{message.content}</div>
                      <div className="text-xs opacity-70 mt-2">
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
                
                {isTyping && (
                  <div className="flex justify-start">
                    <div className="bg-blue-600 text-white rounded-2xl px-4 py-3">
                      <div className="text-sm font-medium mb-1">Governor Agent</div>
                      <div className="text-sm">Typing...</div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="p-6 border-t border-purple-500/30">
                <div className="flex space-x-3">
                  <Textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask me anything about the system, agents, trades, or strategies..."
                    className="flex-1 bg-black/30 border-purple-500/50 text-white placeholder-purple-300"
                    rows={2}
                  />
                  <Button
                    onClick={sendMessage}
                    disabled={!inputMessage.trim() || isTyping}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-6"
                  >
                    Send
                  </Button>
                </div>
              </div>
            </Card>
          </div>

          {/* Sidebar - System Status */}
          <div className="space-y-6">
            {/* System Pulse */}
            <Card className="bg-black/20 backdrop-blur-sm border-purple-500/30">
              <div className="p-4">
                <h3 className="text-lg font-semibold text-white mb-3">📊 System Pulse</h3>
                {systemPulse ? (
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-purple-200">Active Agents:</span>
                      <span className="text-white font-semibold">{systemPulse.active_agents}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-200">Trades Executed:</span>
                      <span className="text-white font-semibold">{systemPulse.trades_executed}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-200">Research Activities:</span>
                      <span className="text-white font-semibold">{systemPulse.research_activities}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-200">Health:</span>
                      <span className={`font-semibold ${getSystemHealthColor(systemPulse.system_health)}`}>
                        {systemPulse.system_health}
                      </span>
                    </div>
                    <div className="text-xs text-purple-300 mt-2">
                      Last updated: {formatTimestamp(systemPulse.timestamp)}
                    </div>
                  </div>
                ) : (
                  <div className="text-purple-300 text-sm">Loading...</div>
                )}
              </div>
            </Card>

            {/* Quick Actions */}
            <Card className="bg-black/20 backdrop-blur-sm border-purple-500/30">
              <div className="p-4">
                <h3 className="text-lg font-semibold text-white mb-3">⚡ Quick Actions</h3>
                <div className="space-y-2">
                  <Button
                    onClick={() => setInputMessage("Show me the current system status and what all agents are doing")}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm"
                  >
                    📊 System Status
                  </Button>
                  <Button
                    onClick={() => setInputMessage("What trades have been executed recently and how are they performing?")}
                    className="w-full bg-green-600 hover:bg-green-700 text-white text-sm"
                  >
                    💰 Trade Performance
                  </Button>
                  <Button
                    onClick={() => setInputMessage("What research is currently being conducted and what insights have been found?")}
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white text-sm"
                  >
                    🔍 Research Insights
                  </Button>
                  <Button
                    onClick={() => setInputMessage("Adjust the risk parameters to be more conservative")}
                    className="w-full bg-orange-600 hover:bg-orange-700 text-white text-sm"
                  >
                    🛡️ Risk Management
                  </Button>
                </div>
              </div>
            </Card>

            {/* Agent Thoughts */}
            <Card className="bg-black/20 backdrop-blur-sm border-purple-500/30">
              <div className="p-4">
                <h3 className="text-lg font-semibold text-white mb-3">🧠 Live Agent Thoughts</h3>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {agentThoughts.length > 0 ? (
                    agentThoughts.map((thought, index) => (
                      <div key={index} className="bg-black/30 rounded-lg p-3">
                        <div className="text-xs text-purple-300 mb-1">
                          {thought.agent_id} • {formatTimestamp(thought.timestamp)}
                        </div>
                        <div className="text-sm text-white mb-1">{thought.thought}</div>
                        <div className="text-xs text-purple-200">
                          Confidence: {(thought.confidence * 100).toFixed(0)}%
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-purple-300 text-sm">Waiting for agent thoughts...</div>
                  )}
                </div>
              </div>
            </Card>
          </div>
        </div>

        {/* System Context Display */}
        {systemContext && (
          <Card className="mt-6 bg-black/20 backdrop-blur-sm border-purple-500/30">
            <div className="p-6">
              <h3 className="text-xl font-semibold text-white mb-4">🎯 Current System Context</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div>
                  <h4 className="text-purple-300 font-medium mb-2">Mission</h4>
                  <p className="text-white text-sm">{systemContext.mission}</p>
                </div>
                <div>
                  <h4 className="text-purple-300 font-medium mb-2">Strategy</h4>
                  <p className="text-white text-sm">{systemContext.current_strategy}</p>
                </div>
                <div>
                  <h4 className="text-purple-300 font-medium mb-2">System Mode</h4>
                  <Badge className={`${
                    systemContext.system_mode === 'normal' ? 'bg-green-600' :
                    systemContext.system_mode === 'conservative' ? 'bg-yellow-600' :
                    systemContext.system_mode === 'aggressive' ? 'bg-blue-600' :
                    'bg-red-600'
                  }`}>
                    {systemContext.system_mode}
                  </Badge>
                </div>
                <div>
                  <h4 className="text-purple-300 font-medium mb-2">Research Priorities</h4>
                  <div className="flex flex-wrap gap-1">
                    {systemContext.research_priorities.map((priority, index) => (
                      <Badge key={index} className="bg-purple-600 text-xs">
                        {priority}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="text-purple-300 font-medium mb-2">Active Directives</h4>
                  <p className="text-white text-sm">{systemContext.active_directives.length} active</p>
                </div>
                <div>
                  <h4 className="text-purple-300 font-medium mb-2">Last Updated</h4>
                  <p className="text-white text-sm">{formatTimestamp(systemContext.last_updated)}</p>
                </div>
              </div>
            </div>
          </Card>
        )}
      </div>
      {/* Floating Governor Chatbot */}
      <GovernorChatInterface />
    </div>
  );
};

export default GovernorControlPanel; 