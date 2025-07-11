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
      content: "Hello! I'm your research graph assistant. I can help you explore the research data, find specific nodes, analyze patterns, and answer questions about the research. What would you like to know?",
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

    try {
      // Simulate AI processing - in real implementation, this would call the graph manager agent
      const response = await processUserQuery(content.trim());
      
      const agentMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: response.answer,
        timestamp: new Date(),
        highlightedNodes: response.highlightedNodes,
        suggestions: response.suggestions,
      };

      setMessages(prev => [...prev, agentMessage]);

      // Highlight nodes if specified
      if (response.highlightedNodes && response.highlightedNodes.length > 0) {
        onHighlightNodes(response.highlightedNodes);
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: "I'm sorry, I encountered an error processing your request. Please try again.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
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
      // Call the real backend graph manager API
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
      
      // Fallback to local processing if backend fails
      const lowerQuery = query.toLowerCase();
      
      if (lowerQuery.includes('active') || lowerQuery.includes('current')) {
        const activeNodes = treeData.filter(node => node.status === 'active');
        return {
          answer: `I found ${activeNodes.length} active research nodes. These are currently being processed and represent ongoing research activities.`,
          highlightedNodes: activeNodes.map(n => n.id),
          suggestions: [
            "Show me completed research",
            "What are the synthesis findings?",
            "Find high-confidence nodes",
          ],
        };
      }

      if (lowerQuery.includes('synthesis') || lowerQuery.includes('findings')) {
        const synthesisNodes = treeData.filter(node => node.type === 'synthesis');
        return {
          answer: `I found ${synthesisNodes.length} synthesis nodes. These represent key findings and insights that combine multiple research threads.`,
          highlightedNodes: synthesisNodes.map(n => n.id),
          suggestions: [
            "Show me market analysis",
            "Find technical analysis nodes",
            "What are the risk assessments?",
          ],
        };
      }

      if (lowerQuery.includes('market') || lowerQuery.includes('analysis')) {
        const marketNodes = treeData.filter(node => 
          node.research_track === 'market_analysis' || 
          node.content.toLowerCase().includes('market')
        );
        return {
          answer: `I found ${marketNodes.length} market analysis nodes. These contain insights about market trends, sentiment, and analysis.`,
          highlightedNodes: marketNodes.map(n => n.id),
          suggestions: [
            "Show me technical indicators",
            "Find sentiment analysis",
            "What are the risk factors?",
          ],
        };
      }

      if (lowerQuery.includes('confidence') || lowerQuery.includes('important')) {
        const highConfidenceNodes = treeData.filter(node => 
          node.confidence && 
          (typeof node.confidence === 'number' ? node.confidence > 0.7 : parseFloat(node.confidence) > 0.7)
        );
        return {
          answer: `I found ${highConfidenceNodes.length} nodes with high confidence (>70%). These represent the most reliable research findings.`,
          highlightedNodes: highConfidenceNodes.map(n => n.id),
          suggestions: [
            "Show me active research",
            "Find synthesis nodes",
            "What are the market trends?",
          ],
        };
      }

      if (lowerQuery.includes('technical') || lowerQuery.includes('indicator')) {
        const technicalNodes = treeData.filter(node => 
          node.research_track === 'technical_analysis' || 
          node.content.toLowerCase().includes('technical') ||
          node.content.toLowerCase().includes('indicator')
        );
        return {
          answer: `I found ${technicalNodes.length} technical analysis nodes. These contain technical indicators, patterns, and analysis.`,
          highlightedNodes: technicalNodes.map(n => n.id),
          suggestions: [
            "Show me market analysis",
            "Find fundamental research",
            "What are the synthesis findings?",
          ],
        };
      }

      // Default response
      return {
        answer: `I understand you're asking about "${query}". I can help you explore the research graph. Try asking about active research, synthesis findings, market analysis, technical indicators, or high-confidence nodes.`,
        suggestions: [
          "Show me active research nodes",
          "Find synthesis nodes",
          "What are the most important findings?",
          "Show me market analysis nodes",
          "Find nodes with high confidence",
        ],
      };


    if (lowerQuery.includes('technical') || lowerQuery.includes('indicator')) {
      const technicalNodes = treeData.filter(node => 
        node.research_track === 'technical_analysis' || 
        node.content.toLowerCase().includes('technical') ||
        node.content.toLowerCase().includes('indicator')
      );
      return {
        answer: `I found ${technicalNodes.length} technical analysis nodes. These contain technical indicators, patterns, and analysis.`,
        highlightedNodes: technicalNodes.map(n => n.id),
        suggestions: [
          "Show me market analysis",
          "Find fundamental research",
          "What are the synthesis findings?",
        ],
      };
    }

    // Default response
    return {
      answer: `I understand you're asking about "${query}". I can help you explore the research graph. Try asking about active research, synthesis findings, market analysis, technical indicators, or high-confidence nodes.`,
      suggestions: [
        "Show me active research nodes",
        "Find synthesis nodes",
        "What are the most important findings?",
        "Show me market analysis nodes",
        "Find nodes with high confidence",
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
        background: 'rgba(0,0,0,0.95)',
        color: 'white',
        border: '1px solid #333',
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
                  background: message.type === 'user' ? '#4caf50' : '#333',
                  color: 'white',
                  borderRadius: 2,
                }}
              >
                <Typography variant="body2">{message.content}</Typography>
                
                {message.highlightedNodes && message.highlightedNodes.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" sx={{ color: '#4caf50' }}>
                      Highlighted {message.highlightedNodes.length} nodes
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                      {message.highlightedNodes.slice(0, 3).map((nodeId) => (
                        <Chip
                          key={nodeId}
                          label={nodeId.substring(0, 8)}
                          size="small"
                          sx={{ fontSize: '0.6rem', background: '#555' }}
                          onClick={() => handleNodeClick(nodeId)}
                        />
                      ))}
                      {message.highlightedNodes.length > 3 && (
                        <Chip
                          label={`+${message.highlightedNodes.length - 3}`}
                          size="small"
                          sx={{ fontSize: '0.6rem', background: '#555' }}
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
                        background: '#555',
                        cursor: 'pointer',
                        '&:hover': { background: '#666' },
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
              <Typography variant="caption" sx={{ color: '#999' }}>
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