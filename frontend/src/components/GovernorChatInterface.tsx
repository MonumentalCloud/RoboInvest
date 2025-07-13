import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Chip,
  CircularProgress,
  Collapse,
  Divider,
} from '@mui/material';
import { Send, ExpandMore, ExpandLess } from '@mui/icons-material';

interface ChatMessage {
  id: string;
  type: 'user' | 'governor' | 'thought';
  content: string;
  timestamp: Date;
  actions?: string[];
  context?: any;
}

const SUGGESTIONS = [
  'Show system status',
  'Pause trading',
  'Update mission',
  'Show risk parameters',
  'Emergency stop',
  'Resume trading',
];

const GovernorChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      type: 'governor',
      content:
        "Hello! I'm the Governor Agent. I can answer questions about the system, execute commands, and provide real-time insights. How can I help you today?",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // WebSocket for live thoughts
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/api/governor/ws/thoughts');
    wsRef.current = ws;
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'agent_thought' && data.thought?.content) {
          setMessages((prev) => [
            ...prev,
            {
              id: `thought-${Date.now()}`,
              type: 'thought',
              content: data.thought.content,
              timestamp: new Date(),
            },
          ]);
        }
      } catch (e) {
        // Ignore parse errors
      }
    };
    ws.onerror = () => {};
    ws.onclose = () => {};
    return () => {
      ws.close();
    };
  }, []);

  const sendMessage = async (content: string) => {
    if (!content.trim()) return;
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/governor/conversation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: content.trim() }),
      });
      if (!response.ok) throw new Error('Failed to get response');
      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString() + '-gov',
          type: 'governor',
          content: data.response,
          timestamp: new Date(),
          actions: data.metadata?.actions_taken,
          context: data.metadata?.context_used ? data.metadata : undefined,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString() + '-err',
          type: 'governor',
          content: "I'm sorry, I encountered an error processing your request. Please try again.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion);
  };

  return (
    <Paper
      sx={{
        position: 'fixed',
        bottom: 20,
        right: 20,
        width: 400,
        maxHeight: 600,
        zIndex: 2000,
        display: 'flex',
        flexDirection: 'column',
        background: 'rgba(20,20,0,0.98)',
        color: 'white',
        border: '2px solid #FFD700',
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
          borderBottom: '1px solid #FFD700',
          cursor: 'pointer',
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <Typography variant="h6" sx={{ color: '#FFD700' }}>
          Governor
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
                  background:
                    message.type === 'user'
                      ? '#FFD700'
                      : message.type === 'thought'
                      ? '#222'
                      : '#1a1a1a',
                  color:
                    message.type === 'user'
                      ? '#222'
                      : message.type === 'thought'
                      ? '#FFD700'
                      : 'white',
                  borderRadius: 2,
                  border:
                    message.type === 'governor'
                      ? '1px solid #FFD700'
                      : message.type === 'thought'
                      ? '1px dashed #FFD700'
                      : 'none',
                  fontStyle: message.type === 'thought' ? 'italic' : 'normal',
                }}
              >
                <Typography variant="body2">{message.content}</Typography>
                {message.actions && message.actions.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" sx={{ color: '#FFD700', fontWeight: 'bold' }}>
                      Actions taken: {message.actions.join(', ')}
                    </Typography>
                  </Box>
                )}
              </Paper>
            </Box>
          ))}

          {isLoading && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 1 }}>
              <CircularProgress size={16} sx={{ color: '#FFD700' }} />
              <Typography variant="caption" sx={{ color: '#FFD700', fontWeight: 'bold' }}>
                Thinking...
              </Typography>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Box>

        <Divider sx={{ borderColor: '#FFD700' }} />

        {/* Suggestions */}
        <Box sx={{ p: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
          {SUGGESTIONS.map((suggestion, idx) => (
            <Chip
              key={idx}
              label={suggestion}
              size="small"
              sx={{
                fontSize: '0.7rem',
                background: '#222',
                color: '#FFD700',
                cursor: 'pointer',
                border: '1px solid #FFD700',
                '&:hover': {
                  background: '#333',
                  border: '1px solid #FFD700',
                },
              }}
              onClick={() => handleSuggestionClick(suggestion)}
            />
          ))}
        </Box>

        {/* Input */}
        <Box sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Ask the Governor..."
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
                    borderColor: '#FFD700',
                  },
                  '&:hover fieldset': {
                    borderColor: '#FFD700',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#FFD700',
                  },
                },
                '& .MuiInputBase-input': {
                  color: 'white',
                  '&::placeholder': {
                    color: '#FFD700',
                    opacity: 1,
                  },
                },
              }}
            />
            <IconButton
              onClick={() => sendMessage(inputValue)}
              disabled={!inputValue.trim() || isLoading}
              sx={{ color: '#FFD700' }}
            >
              <Send />
            </IconButton>
          </Box>
        </Box>
      </Collapse>
    </Paper>
  );
};

export default GovernorChatInterface; 