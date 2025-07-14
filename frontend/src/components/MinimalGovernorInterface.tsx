import React, { useState, useEffect, useRef } from 'react';
import './MinimalGovernorInterface.css';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'agent';
  timestamp: Date;
  responseType?: string;
  responseData?: any;
  actions?: Array<{
    label: string;
    action: string;
    icon: string;
    style: string;
  }>;
  uiHints?: string[];
}

interface SystemContext {
  mission: string;
  current_strategy: string;
  system_mode: string;
  active_directives: number;
}

interface SystemPulse {
  active_agents: number;
  directives_processed: number;
  trades_executed: number;
  research_activities: number;
  system_health: string;
}

interface AgentThought {
  step_id: string;
  step_type: string;
  content: string;
  agent_name: string;
  timestamp: number;
  tool_used?: string;
  agent_called?: string;
  metadata?: any;
}

// Rich response type definitions
interface RichResponse {
  type: 'markdown' | 'table' | 'chart' | 'code_diff' | 'interactive' | 'dashboard' | 'alert' | 'progress' | 'research_tree';
  content: any;
  agent: string;
  actions_taken?: string[];
  metadata?: any;
  timestamp: string;
  ui_config?: any;
  actions?: Array<{
    label: string;
    action: string;
    icon: string;
    style: string;
  }>;
  ui_hints?: string[];
  reasoningChain?: AgentThought[]; // Added reasoningChain to RichResponse
}

const MinimalGovernorInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [systemContext, setSystemContext] = useState<SystemContext | null>(null);
  const [systemPulse, setSystemPulse] = useState<SystemPulse | null>(null);
  const [agentThoughts, setAgentThoughts] = useState<AgentThought[]>([]);
  const [transparencyLevel, setTransparencyLevel] = useState<'full' | 'mission' | 'minimal'>('full');
  const [isStreaming, setIsStreaming] = useState(false);
  const [reasoningChain, setReasoningChain] = useState<AgentThought[]>([]);
  const [showReasoning, setShowReasoning] = useState(false);
  const [expandedReasoning, setExpandedReasoning] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  // Add a new state to track visual content for the sidebar
  const [visualContent, setVisualContent] = useState<RichResponse[]>([]);
  const [focusedVisual, setFocusedVisual] = useState<number | null>(null);

  // Initialize WebSocket connections
  useEffect(() => {
    // TODO: Add WebSocket connection when backend supports it
    // For now, just set streaming to false
    setIsStreaming(false);
    
    // TODO: Load system context and pulse when backend supports it
    // For now, use default values
    setSystemContext({
      mission: "Discover the smartest and greatest upside that nobody is looking at",
      current_strategy: "organic_alpha_hunting",
      system_mode: "normal",
      active_directives: 0
    });
    
    setSystemPulse({
      active_agents: 0,
      directives_processed: 0,
      trades_executed: 0,
      research_activities: 0,
      system_health: "offline"
    });

    return () => {
      // Cleanup when component unmounts
    };
  }, []);

  const handleWebSocketMessage = (data: any) => {
    // TODO: Handle WebSocket messages when backend supports it
    console.log('WebSocket message received:', data);
  };

  const loadSystemContext = async () => {
    // TODO: Load system context when backend supports it
    console.log('Loading system context...');
  };

  const loadSystemPulse = async () => {
    // TODO: Load system pulse when backend supports it
    console.log('Loading system pulse...');
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Find new visual content in the latest agent message
    const lastMsg = messages[messages.length - 1];
    if (lastMsg && lastMsg.sender === 'agent' && lastMsg.responseData) {
      const { type } = lastMsg.responseData;
      if (["chart", "dashboard", "research_tree"].includes(type)) {
        setVisualContent((prev) => [...prev, lastMsg.responseData]);
      }
    }
    // eslint-disable-next-line
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setReasoningChain([]);
    setShowReasoning(true);

    try {
      // Use the reasoning endpoint for streaming responses
      const response = await fetch('http://localhost:8000/api/reasoning/conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          session_id: 'default_session',
          stream_reasoning: true
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      let fullResponse = '';
      let finalResponseData: RichResponse | null = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.step_type === 'result' && data.content) {
                // Check if this is the final response
                if (data.content.includes('Final response:')) {
                  const responseMatch = data.content.match(/Final response: (.+)/);
                  if (responseMatch) {
                    fullResponse = responseMatch[1];
                    // Try to parse as rich response
                    try {
                      finalResponseData = JSON.parse(fullResponse);
                    } catch {
                      // Fallback to markdown
                      finalResponseData = {
                        type: 'markdown',
                        content: fullResponse,
                        agent: data.agent_name || 'governor',
                        timestamp: new Date().toISOString()
                      };
                    }
                  }
                } else {
                  fullResponse = data.content;
                }
              }

              // Add to reasoning chain
              console.log('Received reasoning step:', data);
              setReasoningChain(prev => [...prev, data]);
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }

      // Attach the reasoning chain to the final response data for UI display
      if (finalResponseData) {
        finalResponseData.reasoningChain = reasoningChain;
      }

      // Create the agent message with rich response data
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: fullResponse,
        sender: 'agent',
        timestamp: new Date(),
        responseType: finalResponseData?.type || 'markdown',
        responseData: finalResponseData,
        actions: finalResponseData?.actions,
        uiHints: finalResponseData?.ui_hints
      };

      setMessages(prev => [...prev, agentMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error. Please try again.',
        sender: 'agent',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderRichContent = (message: Message) => {
    if (!message.responseData) {
      return <div className="message-content">{message.content}</div>;
    }

    const { type, content, ui_config } = message.responseData;

    switch (type) {
      case 'table':
        return <TableComponent data={content} config={ui_config} />;
      
      case 'chart':
        return <ChartComponent data={content} config={ui_config} />;
      
      case 'code_diff':
        return <CodeDiffComponent data={content} config={ui_config} />;
      
      case 'interactive':
        return <InteractiveComponent data={content} actions={message.actions} uiHints={message.uiHints} />;
      
      case 'dashboard':
        return <DashboardComponent data={content} config={ui_config} />;
      
      case 'alert':
        return <AlertComponent data={content} config={ui_config} />;
      
      case 'progress':
        return <ProgressComponent data={content} config={ui_config} />;
      
      default:
        return <div className="message-content markdown-content" dangerouslySetInnerHTML={{ __html: renderMarkdown(message.content) }} />;
    }
  };

  const renderMarkdown = (content: string): string => {
    // Simple markdown to HTML conversion
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>')
      .replace(/## (.*?)\n/g, '<h2>$1</h2>')
      .replace(/# (.*?)\n/g, '<h1>$1</h1>');
  };

  const handleAction = async (action: string) => {
    console.log('Action triggered:', action);
    // Handle different actions
    switch (action) {
      case 'refresh_system_status':
        await loadSystemPulse();
        break;
      case 'start_research_agents':
        // Trigger research agent start
        break;
      case 'view_positions':
        // Show positions modal
        break;
      default:
        console.log('Unknown action:', action);
    }
  };

  return (
    <div className="minimal-governor-interface-with-sidebar">
      <div className="main-chat-area">
        {/* Mission Statement */}
        <div className="mission-statement">
          {systemContext?.mission || "Discover the smartest and greatest upside that nobody is looking at"}
        </div>

        {/* System Status */}
        <div className="system-status">
          {systemPulse && (
            <div className="status-indicator">
              <span className={`health-dot ${systemPulse.system_health}`}></span>
              {systemPulse.active_agents} agents
            </div>
          )}
        </div>

        {/* Live Reasoning Chain Display */}
        {showReasoning && reasoningChain.length > 0 && (
          <div className="reasoning-chain-live">
            <h4>🧠 Reasoning (Live)</h4>
            <div>
              {reasoningChain.map((step, i) => (
                <div key={step.step_id || i} className={`reasoning-step ${step.step_type}`}>
                  <div className="step-header">
                    <span className="step-type">{step.step_type}</span>
                    <span className="agent-name">{step.agent_name}</span>
                    {step.tool_used && <span className="tool-used">🔧 {step.tool_used}</span>}
                  </div>
                  <div className="step-content">{step.content}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="messages-container">
        {messages.map((message, idx) => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div className="message-header">
              <span className="sender">{message.sender === 'user' ? 'You' : 'Governor'}</span>
              <span className="timestamp">{message.timestamp.toLocaleTimeString()}</span>
            </div>
            {renderRichContent(message)}
            {/* Reasoning chain for this message, if available */}
            {message.sender === 'agent' && message.responseData && message.responseData.reasoningChain && (
              <div className="reasoning-chain-bubble">
                <button
                  className="toggle-reasoning-btn"
                  onClick={() => setExpandedReasoning(expandedReasoning === message.id ? null : message.id)}
                >
                  {expandedReasoning === message.id ? 'Hide Reasoning' : 'Show Reasoning'}
                </button>
                {expandedReasoning === message.id && (
                  <div className="reasoning-steps">
                    {message.responseData.reasoningChain.map((step: any, i: number) => (
                      <div key={i} className={`reasoning-step ${step.step_type}`}>
                        <div className="step-header">
                          <span className="step-type">{step.step_type}</span>
                          <span className="agent-name">{step.agent_name}</span>
                          {step.tool_used && <span className="tool-used">🔧 {step.tool_used}</span>}
                        </div>
                        <div className="step-content">{step.content}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
        
        {isLoading && (
          <div className="message agent">
            <div className="message-header">
              <span className="sender">Governor</span>
              <span className="timestamp">Thinking...</span>
            </div>
            <div className="message-content">
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask the Governor anything..."
          className="message-input"
          disabled={isLoading}
          autoFocus
        />
        <button type="submit" className="send-button" disabled={isLoading || !inputMessage.trim()}>
          Send
        </button>
      </form>

      {/* Minimal Footer */}
      <div className="minimal-footer">
        <span className="connection-status">
          {isStreaming ? '🟢 Connected' : '🔴 Disconnected'}
        </span>
      </div>
      </div>
      
      <div className="visual-sidebar">
        <h4>Visual Insights</h4>
        {visualContent.length === 0 && <div className="sidebar-empty">No visual content yet.</div>}
        {visualContent.map((visual, idx) => (
          <div key={idx} className={`visual-preview ${focusedVisual === idx ? 'focused' : ''}`}
            onClick={() => setFocusedVisual(focusedVisual === idx ? null : idx)}>
            <div className="visual-type-label">{visual.type}</div>
            <div className="visual-preview-content">
              {visual.type === 'chart' && <ChartComponent data={visual.content} config={visual.ui_config} />}
              {visual.type === 'dashboard' && <DashboardComponent data={visual.content} config={visual.ui_config} />}
              {visual.type === 'research_tree' && <ChartComponent data={visual.content} config={visual.ui_config} />}
            </div>
            {focusedVisual === idx && (
              <div className="visual-expanded">
                {/* Render full visual here, could be modal or expanded view */}
                {visual.type === 'chart' && <ChartComponent data={visual.content} config={visual.ui_config} />}
                {visual.type === 'dashboard' && <DashboardComponent data={visual.content} config={visual.ui_config} />}
                {visual.type === 'research_tree' && <ChartComponent data={visual.content} config={visual.ui_config} />}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// Rich Content Components
const TableComponent: React.FC<{ data: any; config: any }> = ({ data, config }) => {
  const { headers, rows, title } = data;
  
  return (
    <div className="table-component">
      {title && <h3>{title}</h3>}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              {headers.map((header: string, index: number) => (
                <th key={index}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row: any[], rowIndex: number) => (
              <tr key={rowIndex}>
                {row.map((cell: any, cellIndex: number) => (
                  <td key={cellIndex}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const ChartComponent: React.FC<{ data: any; config: any }> = ({ data, config }) => {
  const { chart_type, title, data: chartData } = data;
  
  return (
    <div className="chart-component">
      {title && <h3>{title}</h3>}
      <div className="chart-placeholder">
        <div className="chart-info">
          <strong>Chart Type:</strong> {chart_type}
        </div>
        <div className="chart-data">
          <pre>{JSON.stringify(chartData, null, 2)}</pre>
        </div>
      </div>
    </div>
  );
};

const CodeDiffComponent: React.FC<{ data: any; config: any }> = ({ data, config }) => {
  const { file_path, old_code, new_code, description } = data;
  
  return (
    <div className="code-diff-component">
      <h3>Code Changes: {file_path}</h3>
      {description && <p className="diff-description">{description}</p>}
      <div className="diff-container">
        <div className="diff-side">
          <h4>Old Code</h4>
          <pre className="code-block">{old_code}</pre>
        </div>
        <div className="diff-side">
          <h4>New Code</h4>
          <pre className="code-block">{new_code}</pre>
        </div>
      </div>
    </div>
  );
};

const InteractiveComponent: React.FC<{ 
  data: string; 
  actions?: Array<{ label: string; action: string; icon: string; style: string }>;
  uiHints?: string[];
}> = ({ data, actions, uiHints }) => {
  return (
    <div className="interactive-component">
      <div className="interactive-content" dangerouslySetInnerHTML={{ __html: renderMarkdown(data) }} />
      {actions && actions.length > 0 && (
        <div className="action-buttons">
          {actions.map((action, index) => (
            <button
              key={index}
              className={`action-button ${action.style}`}
              onClick={() => handleAction(action.action)}
            >
              <span className="action-icon">{action.icon}</span>
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

const DashboardComponent: React.FC<{ data: any; config: any }> = ({ data, config }) => {
  const { panels, layout, title } = data;
  
  return (
    <div className="dashboard-component">
      {title && <h3>{title}</h3>}
      <div className={`dashboard-panels ${layout}`}>
        {panels.map((panel: any, index: number) => (
          <div key={index} className={`dashboard-panel ${panel.type}`}>
            <h4>{panel.title}</h4>
            <div className="panel-content">{panel.content}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

const AlertComponent: React.FC<{ data: any; config: any }> = ({ data, config }) => {
  const { level, message, title } = data;
  
  return (
    <div className={`alert-component alert-${level}`}>
      {title && <h4>{title}</h4>}
      <p>{message}</p>
    </div>
  );
};

const ProgressComponent: React.FC<{ data: any; config: any }> = ({ data, config }) => {
  const { current, total, percentage, message } = data;
  
  return (
    <div className="progress-component">
      <div className="progress-header">
        <span className="progress-text">{message}</span>
        <span className="progress-percentage">{percentage.toFixed(1)}%</span>
      </div>
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
      <div className="progress-details">
        {current} / {total}
      </div>
    </div>
  );
};

// Helper function for markdown rendering (moved outside component)
const renderMarkdown = (content: string): string => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
    .replace(/## (.*?)\n/g, '<h2>$1</h2>')
    .replace(/# (.*?)\n/g, '<h1>$1</h1>');
};

// Helper function for action handling (moved outside component)
const handleAction = async (action: string) => {
  console.log('Action triggered:', action);
  // Implementation would go here
};

export default MinimalGovernorInterface; 