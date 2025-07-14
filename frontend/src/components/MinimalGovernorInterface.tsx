import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
  visualData?: any;
  responseData?: any;
  customVisualization?: {
    html: string;
    css?: string;
    js?: string;
    title: string;
  };
}

const MinimalGovernorInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showWhiteboard, setShowWhiteboard] = useState(false);
  const [currentVisualization, setCurrentVisualization] = useState<{
    html: string;
    css?: string;
    js?: string;
    title: string;
  } | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Handle custom visualization from agent
  const handleCustomVisualization = (visualization: any) => {
    if (visualization && visualization.html) {
      setCurrentVisualization(visualization);
      setShowWhiteboard(true);
      
      // Update iframe content
      setTimeout(() => {
        if (iframeRef.current && iframeRef.current.contentDocument) {
          const doc = iframeRef.current.contentDocument;
          doc.open();
          doc.write(`
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8">
              <meta name="viewport" content="width=device-width, initial-scale=1">
              <title>${visualization.title || 'Agent Visualization'}</title>
              <style>
                body { 
                  margin: 0; 
                  padding: 20px; 
                  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                  background: #f8fafc;
                }
                ${visualization.css || ''}
              </style>
            </head>
            <body>
              ${visualization.html}
              ${visualization.js ? `<script>${visualization.js}</script>` : ''}
            </body>
            </html>
          `);
          doc.close();
        }
      }, 100);
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
        // Extract the actual content from the LLM response object
        let content = '';
        if (typeof data.response === 'string') {
          content = data.response;
        } else if (data.response && typeof data.response === 'object') {
          // Handle the new LLM-based response format
          content = data.response.content || data.response.toString();
        } else {
          content = 'I received an unexpected response format.';
        }

        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'agent',
          content: content,
          timestamp: new Date(),
          responseData: data.response,
        };

        setMessages(prev => [...prev, agentMessage]);
        
        // Check if the agent wants to show a custom visualization
        if (data.response && data.response.customVisualization) {
          handleCustomVisualization(data.response.customVisualization);
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
                {message.responseData && message.responseData.type === 'markdown' && (
                  <div style={{ 
                    marginTop: '0.5rem', 
                    padding: '0.5rem', 
                    background: 'rgba(0, 0, 0, 0.05)', 
                    borderRadius: '0.5rem',
                    fontSize: '0.9rem'
                  }}>
                    <strong>Agent:</strong> {message.responseData.agent || 'Unknown'}
                  </div>
                )}
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
              placeholder="Ask anything... (try 'show me positions' or 'analyze portfolio')"
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

      {/* Right side - Agent Visualization Whiteboard */}
      {showWhiteboard && (
        <div style={{
          width: '40%',
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(8px)',
          borderLeft: '1px solid rgba(255, 255, 255, 0.2)',
          display: 'flex',
          flexDirection: 'column',
          maxHeight: '100vh'
        }}>
          {/* Header */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '1rem',
            borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <h2 style={{ margin: 0, color: '#1e3a8a', fontSize: '1.2rem' }}>
              📊 {currentVisualization?.title || 'Agent Visualization'}
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
          
          {/* Iframe for agent-generated content */}
          <div style={{ flex: 1, position: 'relative' }}>
            {currentVisualization ? (
              <iframe
                ref={iframeRef}
                style={{
                  width: '100%',
                  height: '100%',
                  border: 'none',
                  background: 'white'
                }}
                title="Agent Visualization"
                sandbox="allow-scripts allow-same-origin"
              />
            ) : (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                color: '#6b7280',
                fontSize: '0.9rem',
                textAlign: 'center',
                padding: '2rem'
              }}>
                <div>
                  <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📊</div>
                  Ask agents to create visualizations
                  <br />
                  <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>
                    Try: "show me positions", "analyze portfolio", "create chart"
                  </span>
                </div>
              </div>
            )}
          </div>
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