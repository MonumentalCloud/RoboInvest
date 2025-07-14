import React, { useState, useEffect, useRef } from 'react';

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

const SimpleGovernorInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [systemContext, setSystemContext] = useState<SystemContext | null>(null);
  const [systemPulse, setSystemPulse] = useState<SystemPulse | null>(null);
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
      case 'excellent': return '#10b981';
      case 'good': return '#3b82f6';
      case 'warning': return '#f59e0b';
      case 'critical': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const quickActions = [
    {
      label: 'System Status',
      message: 'Show me the current system status and what all agents are doing',
    },
    {
      label: 'Trade Performance',
      message: 'What trades have been executed recently and how are they performing?',
    },
    {
      label: 'Research Insights',
      message: 'What research is currently being conducted and what insights have been found?',
    },
    {
      label: 'Risk Management',
      message: 'Show me the current risk parameters and adjust them to be more conservative',
    },
  ];

  const handleQuickAction = (message: string) => {
    setInputMessage(message);
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%)',
      padding: '1rem',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(90deg, #dbeafe 0%, #e9d5ff 100%)',
          border: '1px solid #bfdbfe',
          borderRadius: '12px',
          padding: '1.5rem',
          marginBottom: '1.5rem',
          backdropFilter: 'blur(8px)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '32px',
                height: '32px',
                background: '#3b82f6',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '18px'
              }}>
                🎯
              </div>
              <div>
                <h1 style={{ fontSize: '24px', fontWeight: 'bold', color: '#1e3a8a', margin: 0 }}>
                  RoboInvest Governor
                </h1>
                <p style={{ color: '#1d4ed8', margin: '4px 0 0 0', fontSize: '14px' }}>
                  {systemContext?.mission || 'Discover the smartest and greatest upside that nobody is looking at'}
                </p>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              {/* System Pulse Indicator */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{
                  width: '12px',
                  height: '12px',
                  borderRadius: '50%',
                  backgroundColor: getHealthColor(systemPulse?.system_health || 'unknown'),
                  animation: 'pulse 2s infinite'
                }}></div>
                <span style={{ fontSize: '14px', color: '#1d4ed8' }}>
                  {systemPulse?.active_agents || 0} agents active
                </span>
              </div>
              
              {/* Streaming Indicator */}
              {isStreaming && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    backgroundColor: '#10b981',
                    borderRadius: '50%',
                    animation: 'pulse 1s infinite'
                  }}></div>
                  <span style={{ fontSize: '12px', color: '#059669' }}>Live</span>
                </div>
              )}
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '24px' }}>
          {/* Main Conversation Area */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Conversation */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.8)',
              border: '1px solid #bfdbfe',
              borderRadius: '12px',
              padding: '1.5rem',
              backdropFilter: 'blur(8px)'
            }}>
              <h2 style={{ fontSize: '18px', fontWeight: '600', margin: '0 0 16px 0', color: '#1e3a8a' }}>
                💬 Conversation with Governor Agent
              </h2>
              
              {/* Messages */}
              <div style={{
                height: '400px',
                overflowY: 'auto',
                padding: '16px',
                background: '#f9fafb',
                borderRadius: '8px',
                marginBottom: '16px',
                border: '1px solid #e5e7eb'
              }}>
                {messages.length === 0 ? (
                  <div style={{ textAlign: 'center', color: '#6b7280', padding: '32px' }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>💬</div>
                    <p>Start a conversation with the Governor Agent</p>
                    <p style={{ fontSize: '14px' }}>Ask about system status, trades, research, or make changes</p>
                  </div>
                ) : (
                  messages.map((message) => (
                    <div
                      key={message.id}
                      style={{
                        display: 'flex',
                        justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
                        marginBottom: '16px'
                      }}
                    >
                      <div
                        style={{
                          maxWidth: '400px',
                          padding: '12px 16px',
                          borderRadius: '12px',
                          background: message.type === 'user' ? '#3b82f6' : 'white',
                          color: message.type === 'user' ? 'white' : '#374151',
                          border: message.type === 'agent' ? '1px solid #e5e7eb' : 'none',
                          boxShadow: message.type === 'agent' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'
                        }}
                      >
                        <p style={{ margin: 0, fontSize: '14px' }}>{message.content}</p>
                        {message.actions && message.actions.length > 0 && (
                          <div style={{
                            marginTop: '8px',
                            paddingTop: '8px',
                            borderTop: '1px solid #e5e7eb'
                          }}>
                            <p style={{ fontSize: '12px', color: '#059669', fontWeight: '500', margin: '0 0 4px 0' }}>
                              Actions taken:
                            </p>
                            <ul style={{ fontSize: '12px', color: '#059669', margin: 0, paddingLeft: '16px' }}>
                              {message.actions.map((action, index) => (
                                <li key={index}>• {action}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        <p style={{
                          fontSize: '12px',
                          opacity: 0.7,
                          margin: '8px 0 0 0'
                        }}>
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask the Governor Agent anything..."
                  disabled={isLoading}
                  style={{
                    flex: 1,
                    padding: '12px 16px',
                    border: '1px solid #d1d5db',
                    borderRadius: '8px',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                />
                <button
                  onClick={sendMessage}
                  disabled={isLoading || !inputMessage.trim()}
                  style={{
                    padding: '12px 16px',
                    background: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: isLoading || !inputMessage.trim() ? 'not-allowed' : 'pointer',
                    opacity: isLoading || !inputMessage.trim() ? 0.5 : 1
                  }}
                >
                  {isLoading ? '⏳' : '📤'}
                </button>
              </div>
            </div>

            {/* System Pulse */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.8)',
              border: '1px solid #bfdbfe',
              borderRadius: '12px',
              padding: '1.5rem',
              backdropFilter: 'blur(8px)'
            }}>
              <h2 style={{ fontSize: '18px', fontWeight: '600', margin: '0 0 16px 0', color: '#1e3a8a' }}>
                📊 System Pulse
              </h2>
              {systemPulse ? (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
                  <div style={{ textAlign: 'center', padding: '16px', background: '#dbeafe', borderRadius: '8px' }}>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1d4ed8' }}>
                      {systemPulse.active_agents}
                    </div>
                    <div style={{ fontSize: '14px', color: '#1d4ed8' }}>Active Agents</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '16px', background: '#dcfce7', borderRadius: '8px' }}>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#15803d' }}>
                      {systemPulse.directives_processed}
                    </div>
                    <div style={{ fontSize: '14px', color: '#15803d' }}>Directives Processed</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '16px', background: '#f3e8ff', borderRadius: '8px' }}>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#7c3aed' }}>
                      {systemPulse.trades_executed}
                    </div>
                    <div style={{ fontSize: '14px', color: '#7c3aed' }}>Trades Executed</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '16px', background: '#fed7aa', borderRadius: '8px' }}>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ea580c' }}>
                      {systemPulse.research_activities}
                    </div>
                    <div style={{ fontSize: '14px', color: '#ea580c' }}>Research Activities</div>
                  </div>
                </div>
              ) : (
                <div style={{ textAlign: 'center', color: '#6b7280', padding: '32px' }}>
                  <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
                  <p>Loading system pulse...</p>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Quick Actions */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.8)',
              border: '1px solid #bfdbfe',
              borderRadius: '12px',
              padding: '1.5rem',
              backdropFilter: 'blur(8px)'
            }}>
              <h3 style={{ fontSize: '16px', fontWeight: '600', margin: '0 0 16px 0', color: '#1e3a8a' }}>
                ⚡ Quick Actions
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {quickActions.map((action, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickAction(action.message)}
                    style={{
                      padding: '8px 12px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      background: 'white',
                      cursor: 'pointer',
                      fontSize: '14px',
                      textAlign: 'left',
                      transition: 'all 0.2s'
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.background = '#f3f4f6';
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.background = 'white';
                    }}
                  >
                    {action.label}
                  </button>
                ))}
              </div>
            </div>

            {/* System Context */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.8)',
              border: '1px solid #bfdbfe',
              borderRadius: '12px',
              padding: '1.5rem',
              backdropFilter: 'blur(8px)'
            }}>
              <h3 style={{ fontSize: '16px', fontWeight: '600', margin: '0 0 16px 0', color: '#1e3a8a' }}>
                🔍 System Context
              </h3>
              {systemContext ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: '500', color: '#374151' }}>Strategy:</div>
                    <div style={{ fontSize: '14px', color: '#111827' }}>{systemContext.current_strategy}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: '500', color: '#374151' }}>Mode:</div>
                    <span style={{
                      padding: '4px 8px',
                      background: '#f3f4f6',
                      border: '1px solid #d1d5db',
                      borderRadius: '4px',
                      fontSize: '12px',
                      color: '#374151'
                    }}>
                      {systemContext.system_mode}
                    </span>
                  </div>
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: '500', color: '#374151' }}>Research Focus:</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '4px' }}>
                      {systemContext.research_priorities.map((priority, index) => (
                        <span key={index} style={{
                          padding: '2px 6px',
                          background: '#e0e7ff',
                          borderRadius: '4px',
                          fontSize: '12px',
                          color: '#3730a3'
                        }}>
                          {priority}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: '500', color: '#374151' }}>Active Directives:</div>
                    <div style={{ fontSize: '14px', color: '#111827' }}>{systemContext.active_directives}</div>
                  </div>
                </div>
              ) : (
                <div style={{ textAlign: 'center', color: '#6b7280', padding: '16px' }}>
                  <div style={{ fontSize: '32px', marginBottom: '8px' }}>👁️</div>
                  <p style={{ fontSize: '14px', margin: 0 }}>Loading system context...</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default SimpleGovernorInterface; 