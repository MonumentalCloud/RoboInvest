import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress,
  Collapse,
  Divider,
} from '@mui/material';
import { Send, ExpandMore, ExpandLess, Search, Visibility } from '@mui/icons-material';

interface ChatMessage {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
  highlightedNodes?: string[];
  suggestions?: string[];
}

interface GraphChatInterfaceProps {
  onHighlightNodes: (nodeIds: string[]) => void;
  onNavigateToNode: (nodeId: string) => void;
  treeData: any[];
}

const GraphChatInterface: React.FC<GraphChatInterfaceProps> = ({
  onHighlightNodes,
  onNavigateToNode,
  treeData,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'agent',
      content: "Hello! I'm your AI-powered research graph assistant. I use advanced language models to intelligently analyze your research data, find patterns, and provide insights. I can help you explore the research data, find specific nodes, analyze patterns, and answer complex questions about the research. What would you like to know?",
      timestamp: new Date(),
      suggestions: [
        "Show me active research nodes",
        "Find synthesis nodes",
        "What are the most important findings?",
        "Show me market analysis nodes",
        "Find nodes with high confidence",
      ],
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (content: string) => {
    if (!content.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Create a streaming message
    const streamingMessageId = (Date.now() + 1).toString();
    const streamingMessage: ChatMessage = {
      id: streamingMessageId,
      type: 'agent',
      content: '',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, streamingMessage]);

    try {
      // Call the LLM-based graph manager agent for intelligent processing
      const response = await processUserQuery(content.trim());
      
      // Update the streaming message with full content
      setMessages(prev => prev.map(msg => 
        msg.id === streamingMessageId 
          ? { ...msg, content: response.answer, highlightedNodes: response.highlightedNodes, suggestions: response.suggestions }
          : msg
      ));

      // Highlight nodes if specified
      if (response.highlightedNodes && response.highlightedNodes.length > 0) {
        onHighlightNodes(response.highlightedNodes);
      }
    } catch (error) {
      // Update the streaming message with error
      setMessages(prev => prev.map(msg => 
        msg.id === streamingMessageId 
          ? { ...msg, content: "I'm sorry, I encountered an error processing your request. Please try again." }
          : msg
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const processUserQuery = async (query: string): Promise<{
    answer: string;
    highlightedNodes?: string[];
    suggestions?: string[];
  }> => {
    try {
      // Call the LLM-based backend graph manager API
      const response = await fetch('http://localhost:8081/api/graph/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error('Failed to query graph');
      }

      const data = await response.json();
      
      if (data.status === 'success') {
        return {
          answer: data.data.answer,
          highlightedNodes: data.data.highlighted_nodes || [],
          suggestions: data.data.suggestions || [],
        };
      } else {
        throw new Error('Graph query failed');
      }
    } catch (error) {
      console.error('Error querying graph:', error);
      
      // Simple fallback response if LLM backend fails
      return {
        answer: "I'm sorry, I'm having trouble connecting to my AI brain right now. Please try again in a moment, or check if the backend service is running.",
        highlightedNodes: [],
        suggestions: [
          "Try asking again",
          "Check system status",
          "Show me active research nodes",
          "Find synthesis nodes"
        ],
      };
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion);
  };

  const handleNodeClick = (nodeId: string) => {
    onNavigateToNode(nodeId);
  };

  return (
    <Paper
      sx={{
        position: 'absolute',
        bottom: 20,
        right: 20,
        width: 400,
        maxHeight: 600,
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        background: 'rgba(0,0,0,0.98)',
        color: 'white',
        border: '2px solid #333',
        boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2,
          borderBottom: '1px solid #333',
          cursor: 'pointer',
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <Typography variant="h6" sx={{ color: '#4caf50' }}>
          Research Assistant
        </Typography>
        <IconButton size="small" sx={{ color: 'white' }}>
          {isExpanded ? <ExpandMore /> : <ExpandLess />}
        </IconButton>
      </Box>

      <Collapse in={isExpanded}>
        {/* Messages */}
        <Box
          sx={{
            height: 400,
            overflowY: 'auto',
            p: 2,
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
          }}
        >
          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: message.type === 'user' ? 'flex-end' : 'flex-start',
              }}
            >
              <Paper
                sx={{
                  p: 1.5,
                  maxWidth: '80%',
                  background: message.type === 'user' ? '#4caf50' : '#1a1a1a',
                  color: 'white',
                  borderRadius: 2,
                  border: message.type === 'agent' ? '1px solid #333' : 'none',
                }}
              >
                <Typography variant="body2">{message.content}</Typography>
                
                {message.highlightedNodes && message.highlightedNodes.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" sx={{ color: '#4caf50', fontWeight: 'bold' }}>
                      Highlighted {message.highlightedNodes.length} nodes
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                      {message.highlightedNodes.slice(0, 3).map((nodeId) => (
                        <Chip
                          key={nodeId}
                          label={nodeId.substring(0, 8)}
                          size="small"
                          sx={{ 
                            fontSize: '0.6rem', 
                            background: '#2a2a2a', 
                            color: '#4caf50',
                            border: '1px solid #4caf50',
                            '&:hover': { background: '#3a3a3a' }
                          }}
                          onClick={() => handleNodeClick(nodeId)}
                        />
                      ))}
                      {message.highlightedNodes.length > 3 && (
                        <Chip
                          label={`+${message.highlightedNodes.length - 3}`}
                          size="small"
                          sx={{ 
                            fontSize: '0.6rem', 
                            background: '#2a2a2a',
                            color: '#999'
                          }}
                        />
                      )}
                    </Box>
                  </Box>
                )}
              </Paper>

              {message.suggestions && message.suggestions.length > 0 && (
                <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {message.suggestions.map((suggestion, index) => (
                    <Chip
                      key={index}
                      label={suggestion}
                      size="small"
                      sx={{
                        fontSize: '0.7rem',
                        background: '#2a2a2a',
                        color: '#e0e0e0',
                        cursor: 'pointer',
                        border: '1px solid #444',
                        '&:hover': { 
                          background: '#3a3a3a',
                          border: '1px solid #4caf50'
                        },
                      }}
                      onClick={() => handleSuggestionClick(suggestion)}
                    />
                  ))}
                </Box>
              )}
            </Box>
          ))}

          {isLoading && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 1 }}>
              <CircularProgress size={16} sx={{ color: '#4caf50' }} />
              <Typography variant="caption" sx={{ color: '#4caf50', fontWeight: 'bold' }}>
                Thinking...
              </Typography>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Box>

        <Divider sx={{ borderColor: '#333' }} />

        {/* Input */}
        <Box sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Ask about the research graph..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage(inputValue);
                }
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  color: 'white',
                  '& fieldset': {
                    borderColor: '#555',
                  },
                  '&:hover fieldset': {
                    borderColor: '#666',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#4caf50',
                  },
                },
                '& .MuiInputBase-input': {
                  color: 'white',
                  '&::placeholder': {
                    color: '#999',
                    opacity: 1,
                  },
                },
              }}
            />
            <IconButton
              onClick={() => sendMessage(inputValue)}
              disabled={!inputValue.trim() || isLoading}
              sx={{ color: '#4caf50' }}
            >
              <Send />
            </IconButton>
          </Box>
        </Box>
      </Collapse>
    </Paper>
  );
};

export default GraphChatInterface; 