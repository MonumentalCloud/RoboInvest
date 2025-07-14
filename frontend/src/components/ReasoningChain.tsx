import React, { useState, useEffect, useRef } from 'react';
import './ReasoningChain.css';

interface ReasoningStep {
  step_id: string;
  step_type: 'thought' | 'tool_use' | 'agent_call' | 'reflection' | 'decision' | 'result' | 'error';
  content: string;
  timestamp: number;
  agent_name: string;
  tool_used?: string;
  agent_called?: string;
  metadata?: any;
}

interface ReasoningChainProps {
  query: string;
  onComplete?: (finalResponse: string) => void;
}

const ReasoningChain: React.FC<ReasoningChainProps> = ({ query, onComplete }) => {
  const [steps, setSteps] = useState<ReasoningStep[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [finalResponse, setFinalResponse] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (query) {
      startReasoningStream();
    }
  }, [query]);

  useEffect(() => {
    // Auto-scroll to bottom when new steps arrive
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [steps]);

  const startReasoningStream = async () => {
    setIsStreaming(true);
    setSteps([]);
    setError(null);
    setFinalResponse(null);

    try {
      const response = await fetch('http://localhost:8000/api/reasoning/conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: query,
          session_id: 'frontend',
          stream_reasoning: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              setSteps(prev => [...prev, data]);
              
                             // Check if this is the final response
               if (data.step_type === 'result' && data.agent_name === 'governor') {
                 setFinalResponse(data.content);
                 // Let user control when to continue
               }
            } catch (e) {
              console.error('Error parsing reasoning step:', e);
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsStreaming(false);
    }
  };

  const getStepIcon = (stepType: string) => {
    switch (stepType) {
      case 'thought': return '🧠';
      case 'tool_use': return '🔧';
      case 'agent_call': return '📞';
      case 'reflection': return '🤔';
      case 'decision': return '🎯';
      case 'result': return '✅';
      case 'error': return '❌';
      default: return '📝';
    }
  };

  const getStepColor = (stepType: string) => {
    switch (stepType) {
      case 'thought': return 'var(--thought-color)';
      case 'tool_use': return 'var(--tool-color)';
      case 'agent_call': return 'var(--agent-color)';
      case 'reflection': return 'var(--reflection-color)';
      case 'decision': return 'var(--decision-color)';
      case 'result': return 'var(--result-color)';
      case 'error': return 'var(--error-color)';
      default: return 'var(--default-color)';
    }
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  return (
    <div className="reasoning-chain-container">
      <div className="reasoning-header">
        <h3>🧠 Agent Reasoning Chain</h3>
        <div className="reasoning-status">
          {isStreaming && <span className="streaming-indicator">🔄 Streaming...</span>}
          {error && <span className="error-indicator">❌ Error: {error}</span>}
          {finalResponse && <span className="complete-indicator">✅ Complete</span>}
        </div>
      </div>

      <div className="reasoning-steps" ref={containerRef}>
        {steps.length === 0 && !error && (
          <div className="no-steps">
            {isStreaming ? 'Starting reasoning process...' : 'No reasoning steps yet'}
          </div>
        )}

        {steps.map((step, index) => (
          <div
            key={step.step_id}
            className={`reasoning-step ${step.step_type}`}
            style={{ borderLeftColor: getStepColor(step.step_type) }}
          >
            <div className="step-header">
              <span className="step-icon">{getStepIcon(step.step_type)}</span>
              <span className="step-type">{step.step_type.toUpperCase()}</span>
              <span className="step-agent">{step.agent_name}</span>
              <span className="step-time">{formatTimestamp(step.timestamp)}</span>
            </div>
            
            <div className="step-content">
              {step.content}
            </div>

            {(step.tool_used || step.agent_called) && (
              <div className="step-details">
                {step.tool_used && (
                  <span className="step-tool">🔧 Tool: {step.tool_used}</span>
                )}
                {step.agent_called && (
                  <span className="step-agent-called">📞 Called: {step.agent_called}</span>
                )}
              </div>
            )}
          </div>
        ))}

        {error && (
          <div className="reasoning-error">
            <h4>❌ Error in Reasoning Chain</h4>
            <p>{error}</p>
            <button onClick={startReasoningStream} className="retry-button">
              🔄 Retry
            </button>
          </div>
        )}
      </div>

      {finalResponse && (
        <div className="final-response">
          <h4>🎯 Final Response</h4>
          <div className="response-content">
            {finalResponse}
          </div>
          <button 
            onClick={() => onComplete?.(finalResponse)}
            className="continue-button"
          >
            ✅ Continue to Chat
          </button>
        </div>
      )}
    </div>
  );
};

export default ReasoningChain; 