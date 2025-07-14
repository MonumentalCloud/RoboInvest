import React, { useState, useEffect, useRef } from 'react';

interface Message {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
  visualData?: any;
}

interface VisualElement {
  id: string;
  type: 'chart' | 'graph' | 'metric' | 'diagram';
  title: string;
  data: any;
  timestamp: Date;
}

const MinimalGovernorInterface: React.FC = () => {
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [systemStatus, setSystemStatus] = useState<string>('');
  const [visualElements, setVisualElements] = useState<VisualElement[]>([]);
  const [showWhiteboard, setShowWhiteboard] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const generateVisualData = (request: string): VisualElement | null => {
    const lowerRequest = request.toLowerCase();
    
    // Performance metrics chart
    if (lowerRequest.includes('performance') || lowerRequest.includes('pnl') || lowerRequest.includes('profit')) {
      return {
        id: Date.now().toString(),
        type: 'chart',
        title: 'Trading Performance',
        data: {
          type: 'line',
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          datasets: [{
            label: 'Portfolio Value',
            data: [10000, 10500, 11200, 10800, 12000, 12500],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4
          }]
        },
        timestamp: new Date()
      };
    }
    
    // Risk metrics
    if (lowerRequest.includes('risk') || lowerRequest.includes('volatility') || lowerRequest.includes('drawdown')) {
      return {
        id: Date.now().toString(),
        type: 'chart',
        title: 'Risk Metrics',
        data: {
          type: 'bar',
          labels: ['Max Drawdown', 'Volatility', 'Sharpe Ratio', 'Beta'],
          datasets: [{
            label: 'Current Values',
            data: [0.08, 0.15, 1.2, 0.9],
            backgroundColor: ['#ef4444', '#f59e0b', '#10b981', '#3b82f6']
          }]
        },
        timestamp: new Date()
      };
    }
    
    // Agent activity
    if (lowerRequest.includes('agent') || lowerRequest.includes('activity') || lowerRequest.includes('workload')) {
      return {
        id: Date.now().toString(),
        type: 'chart',
        title: 'Agent Activity',
        data: {
          type: 'doughnut',
          labels: ['Research', 'Analysis', 'Execution', 'Monitoring'],
          datasets: [{
            data: [35, 25, 20, 20],
            backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
          }]
        },
        timestamp: new Date()
      };
    }
    
    // Market sentiment
    if (lowerRequest.includes('sentiment') || lowerRequest.includes('market') || lowerRequest.includes('mood')) {
      return {
        id: Date.now().toString(),
        type: 'chart',
        title: 'Market Sentiment',
        data: {
          type: 'radar',
          labels: ['Fear', 'Greed', 'Optimism', 'Pessimism', 'Neutrality'],
          datasets: [{
            label: 'Current Sentiment',
            data: [0.3, 0.7, 0.6, 0.2, 0.4],
            borderColor: '#8b5cf6',
            backgroundColor: 'rgba(139, 92, 246, 0.2)'
          }]
        },
        timestamp: new Date()
      };
    }
    
    // System health
    if (lowerRequest.includes('health') || lowerRequest.includes('status') || lowerRequest.includes('system')) {
      return {
        id: Date.now().toString(),
        type: 'metric',
        title: 'System Health',
        data: {
          metrics: [
            { label: 'CPU Usage', value: '45%', color: '#10b981' },
            { label: 'Memory', value: '2.1GB', color: '#3b82f6' },
            { label: 'Active Agents', value: '5', color: '#f59e0b' },
            { label: 'Uptime', value: '99.8%', color: '#10b981' }
          ]
        },
        timestamp: new Date()
      };
    }
    
    return null;
  };

  const renderVisualElement = (element: VisualElement) => {
    switch (element.type) {
      case 'chart':
        return (
          <div key={element.id} style={{
            background: 'rgba(255, 255, 255, 0.9)',
            borderRadius: '12px',
            padding: '1rem',
            marginBottom: '1rem',
            backdropFilter: 'blur(8px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)'
          }}>
            <h3 style={{ margin: '0 0 1rem 0', color: '#1e3a8a', fontSize: '1rem' }}>
              {element.title}
            </h3>
            <div style={{
              height: '200px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: 'linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%)',
              borderRadius: '8px',
              color: '#6b7280',
              fontSize: '0.9rem'
            }}>
              📊 {element.data.type} Chart
              <br />
              <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>
                {element.data.labels?.length || 0} data points
              </span>
            </div>
          </div>
        );
      
      case 'metric':
        return (
          <div key={element.id} style={{
            background: 'rgba(255, 255, 255, 0.9)',
            borderRadius: '12px',
            padding: '1rem',
            marginBottom: '1rem',
            backdropFilter: 'blur(8px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)'
          }}>
            <h3 style={{ margin: '0 0 1rem 0', color: '#1e3a8a', fontSize: '1rem' }}>
              {element.title}
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem' }}>
              {element.data.metrics.map((metric: any, index: number) => (
                <div key={index} style={{
                  padding: '0.5rem',
                  background: 'rgba(248, 250, 252, 0.8)',
                  borderRadius: '6px',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>{metric.label}</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: '600', color: metric.color }}>
                    {metric.value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Check if user wants a visual
    const visualData = generateVisualData(inputValue);
    if (visualData) {
      setVisualElements(prev => [...prev, visualData]);
      setShowWhiteboard(true);
    }

    try {
      const response = await fetch('http://localhost:8000/api/governor/conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage.content }),
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'agent',
          content: data.response,
          timestamp: new Date(),
        };

        setMessages(prev => [...prev, agentMessage]);
        
        // Check if the governor agent wants to show any visuals
        if (data.metadata && data.metadata.visual_request) {
          const visualData = generateVisualData(data.metadata.visual_request);
          if (visualData) {
            setVisualElements(prev => [...prev, visualData]);
            setShowWhiteboard(true);
          }
        }
      }
    } catch (error) {
      console.error('Error connecting to governor agent:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: 'I encountered an error connecting to the governor agent system. Please check if the backend is running.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }, 100);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%)',
      display: 'flex',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      position: 'relative'
    }}>
      {/* Left side - Conversation */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        maxWidth: showWhiteboard ? '60%' : '100%',
        transition: 'max-width 0.3s ease'
      }}>
        {/* Mission header */}
        <div style={{
          padding: '2rem',
          textAlign: 'center',
          color: '#1e3a8a',
          fontSize: '1.1rem',
          fontWeight: '300',
          opacity: 0.8
        }}>
          Discover the smartest and greatest upside that nobody is looking at
        </div>

        {/* Messages area */}
        <div style={{
          flex: 1,
          padding: '0 2rem',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'flex-end',
          gap: '1rem',
          marginBottom: '2rem'
        }}>
          {messages.map((message) => (
            <div
              key={message.id}
              style={{
                display: 'flex',
                justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
                opacity: 0.9
              }}
            >
              <div style={{
                maxWidth: '70%',
                padding: '0.5rem 1rem',
                borderRadius: '1rem',
                background: message.type === 'user' ? '#3b82f6' : 'rgba(255, 255, 255, 0.8)',
                color: message.type === 'user' ? 'white' : '#374151',
                fontSize: '0.95rem',
                lineHeight: '1.4',
                backdropFilter: 'blur(8px)',
                border: message.type === 'agent' ? '1px solid rgba(255, 255, 255, 0.2)' : 'none',
                boxShadow: message.type === 'agent' ? '0 2px 8px rgba(0, 0, 0, 0.1)' : 'none'
              }}>
                {message.content}
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div style={{
              display: 'flex',
              justifyContent: 'flex-start',
              opacity: 0.7
            }}>
              <div style={{
                padding: '0.5rem 1rem',
                borderRadius: '1rem',
                background: 'rgba(255, 255, 255, 0.8)',
                color: '#6b7280',
                fontSize: '0.9rem',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(255, 255, 255, 0.2)'
              }}>
                Thinking...
              </div>
            </div>
          )}
        </div>

        {/* Input area */}
        <div style={{
          padding: '0 2rem 2rem 2rem',
          display: 'flex',
          justifyContent: 'center'
        }}>
          <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: '600px' }}>
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask anything... (try 'show me performance' or 'display risk metrics')"
              disabled={isTyping}
              style={{
                width: '100%',
                padding: '1rem 1.5rem',
                border: 'none',
                borderRadius: '2rem',
                background: 'rgba(255, 255, 255, 0.9)',
                fontSize: '1rem',
                outline: 'none',
                backdropFilter: 'blur(12px)',
                boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
                transition: 'all 0.2s ease',
                color: '#374151'
              }}
            />
          </form>
        </div>
      </div>

      {/* Right side - Visual Whiteboard */}
      {showWhiteboard && (
        <div style={{
          width: '40%',
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(8px)',
          borderLeft: '1px solid rgba(255, 255, 255, 0.2)',
          padding: '1rem',
          overflowY: 'auto',
          maxHeight: '100vh'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '1rem',
            paddingBottom: '0.5rem',
            borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <h2 style={{ margin: 0, color: '#1e3a8a', fontSize: '1.2rem' }}>
              📊 Visual Whiteboard
            </h2>
            <button
              onClick={() => setShowWhiteboard(false)}
              style={{
                background: 'none',
                border: 'none',
                color: '#6b7280',
                cursor: 'pointer',
                fontSize: '1.2rem',
                padding: '0.25rem'
              }}
            >
              ✕
            </button>
          </div>
          
          {visualElements.length === 0 ? (
            <div style={{
              textAlign: 'center',
              color: '#6b7280',
              padding: '2rem',
              fontSize: '0.9rem'
            }}>
              Ask for charts, graphs, or metrics to see them here
              <br />
              <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>
                Try: "show me performance", "display risk metrics", "agent activity"
              </span>
            </div>
          ) : (
            visualElements.map(renderVisualElement)
          )}
        </div>
      )}

      {/* Footer */}
      <div style={{
        position: 'absolute',
        bottom: '0.5rem',
        left: '50%',
        transform: 'translateX(-50%)',
        fontSize: '0.7rem',
        color: '#9ca3af',
        opacity: 0.5
      }}>
        RoboInvest Governor
      </div>
    </div>
  );
};

export default MinimalGovernorInterface; 