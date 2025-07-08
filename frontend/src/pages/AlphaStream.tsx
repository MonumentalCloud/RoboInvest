import React, { useState, useEffect, useRef } from "react";
import { 
  Brain, 
  Zap, 
  TrendingUp, 
  Search, 
  Target, 
  CheckCircle, 
  Play, 
  Pause, 
  Wifi,
  WifiOff,
  Activity
} from "lucide-react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  IconButton,
  Paper,
  Alert,
  Fade,
  Zoom
} from '@mui/material';

interface AIThought {
  type: string;
  thought_type: string;
  content: string;
  metadata: any;
  timestamp: string;
}

interface ResearchNode {
  type: string;
  node_type: string;
  node_data: {
    title: string;
    status: string;
    data: any;
  };
  timestamp: string;
}

export default function AlphaStream() {
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [aiThoughts, setAiThoughts] = useState<AIThought[]>([]);
  const [researchNodes, setResearchNodes] = useState<ResearchNode[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<"connecting" | "connected" | "disconnected">("disconnected");
  
  const wsRef = useRef<WebSocket | null>(null);
  const thoughtsEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest thoughts
  const scrollToBottom = () => {
    thoughtsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [aiThoughts]);

  // Auto-connect websocket on component mount
  useEffect(() => {
    connectWebSocket();
    
    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // WebSocket connection management with auto-reconnect
  const connectWebSocket = () => {
    try {
      console.log("🔄 Attempting to connect to WebSocket...");
      setConnectionStatus("connecting");
      wsRef.current = new WebSocket("ws://localhost:8081/ws/ai-thoughts");
      
      wsRef.current.onopen = () => {
        setIsConnected(true);
        setConnectionStatus("connected");
        console.log("✅ WebSocket connected successfully!");
      };
      
      wsRef.current.onmessage = (event) => {
        console.log("📥 Received message:", event.data);
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === "ai_thought") {
            setAiThoughts(prev => [...prev, message].slice(-20)); // Keep last 20 thoughts
          } else if (message.type === "research_update") {
            setResearchNodes(prev => {
              const updated = [...prev];
              const existingIndex = updated.findIndex(node => 
                node.node_data.title === message.node_data.title
              );
              
              if (existingIndex >= 0) {
                updated[existingIndex] = message;
              } else {
                updated.push(message);
              }
              
              return updated.slice(-6); // Keep last 6 research nodes
            });
          }
        } catch (err) {
          console.error("Error parsing message:", err);
        }
      };
      
      wsRef.current.onclose = (event) => {
        setIsConnected(false);
        setConnectionStatus("disconnected");
        console.log("❌ WebSocket disconnected. Code:", event.code, "Reason:", event.reason);
        
        // Auto-reconnect after 3 seconds
        setTimeout(() => {
          if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
            console.log("🔄 Attempting to reconnect...");
            connectWebSocket();
          }
        }, 3000);
      };
      
      wsRef.current.onerror = (error) => {
        console.error("❌ WebSocket error:", error);
        setConnectionStatus("disconnected");
      };
      
    } catch (error) {
      console.error("❌ Failed to create WebSocket:", error);
      setConnectionStatus("disconnected");
      
      // Retry connection after 5 seconds
      setTimeout(() => {
        console.log("🔄 Retrying connection...");
        connectWebSocket();
      }, 5000);
    }
  };



  // Start autonomous trading with streaming
  const startAutonomousTrading = async () => {
    try {
      const response = await fetch("http://localhost:8081/api/autonomous/start", {
        method: "POST",
      });
      
      if (response.ok) {
        setIsStreaming(true);
      }
    } catch (error) {
      console.error("Failed to start autonomous trading:", error);
    }
  };

  const stopStreaming = () => {
    setIsStreaming(false);
    setAiThoughts([]);
    setResearchNodes([]);
  };

  // Test websocket connection
  const testWebSocket = async () => {
    try {
      const response = await fetch("http://localhost:8081/api/test/websocket", {
        method: "POST",
      });
      
      if (response.ok) {
        console.log("✅ Test message sent successfully");
      }
    } catch (error) {
      console.error("❌ Failed to send test message:", error);
    }
  };

  // Get thought type styling
  const getThoughtStyle = (thoughtType: string) => {
    switch (thoughtType) {
      case "system_start":
        return { icon: <Zap />, color: "primary" as const, bgColor: "#1a2332" };
      case "analysis":
        return { icon: <Brain />, color: "info" as const, bgColor: "#2a1a32" };
      case "discovery":
        return { icon: <Target />, color: "success" as const, bgColor: "#1a321a" };
      case "strategy":
        return { icon: <TrendingUp />, color: "warning" as const, bgColor: "#323228" };
      case "completion":
        return { icon: <CheckCircle />, color: "success" as const, bgColor: "#1a321a" };
      case "error":
        return { icon: <Activity />, color: "error" as const, bgColor: "#321a1a" };
      default:
        return { icon: <Brain />, color: "default" as const, bgColor: "#2a2a2a" };
    }
  };

  // Get research node status styling
  const getNodeStyle = (status: string) => {
    switch (status) {
      case "analyzing":
      case "scanning":
      case "researching":
        return { color: "primary" as const, progress: true };
      case "complete":
        return { color: "success" as const, progress: false };
      default:
        return { color: "default" as const, progress: false };
    }
  };

  return (
    <Box sx={{ p: 2, minHeight: "100vh", bgcolor: "#0a0a0a" }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Typography variant="h4" sx={{ display: "flex", alignItems: "center", gap: 1, color: "#ffffff" }}>
          <Brain color="#64b5f6" />
          🚀 Autonomous Alpha Stream
        </Typography>
        
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          {/* Connection Status */}
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            {connectionStatus === "connected" ? <Wifi color="#4caf50" /> : <WifiOff color="#757575" />}
            <Typography variant="body2" sx={{ color: connectionStatus === "connected" ? "#4caf50" : "#ffffff" }}>
              {connectionStatus === "connected" ? "Live" : 
               connectionStatus === "connecting" ? "Connecting..." : "Reconnecting..."}
            </Typography>
          </Box>
          
          {/* Control Buttons */}
          <Button
            variant="outlined"
            onClick={testWebSocket}
            disabled={connectionStatus !== "connected"}
            startIcon={<Zap />}
            sx={{ mr: 1 }}
          >
            Test Connection
          </Button>
          
          <Button
            variant="contained"
            color={isStreaming ? "secondary" : "primary"}
            onClick={isStreaming ? stopStreaming : startAutonomousTrading}
            disabled={connectionStatus !== "connected"}
            startIcon={isStreaming ? <Pause /> : <Play />}
          >
            {isStreaming ? "Stop Alpha Hunt" : "Start Alpha Hunt"}
          </Button>
        </Box>
      </Box>



      {/* Real AI System Indicator */}
      <Alert 
        severity="success" 
        icon={<Activity />}
        sx={{ 
          mb: 3, 
          bgcolor: "#1a332a", 
          color: "#4caf50",
          border: "1px solid #4caf50",
          "& .MuiAlert-icon": { color: "#4caf50" }
        }}
      >
        <Typography variant="body1" fontWeight="bold">
          🤖 Real AI Research System Active
        </Typography>
        <Typography variant="body2" sx={{ color: "#81c784" }}>
          • Live market data via yfinance • OpenAI LLM analysis • Real web research • Dynamic strategies
          {aiThoughts.some(t => t.metadata?.real_system || t.metadata?.real_ai || t.metadata?.real_data) && 
            " • Currently processing real data"}
        </Typography>
      </Alert>

      <Box sx={{ display: "flex", gap: 3, flexDirection: { xs: "column", md: "row" } }}>
        {/* Left Panel - Real-time AI Thoughts */}
        <Box sx={{ flex: 2 }}>
          <Card sx={{ 
            height: "70vh", 
            display: "flex", 
            flexDirection: "column",
            bgcolor: "#1a1a1a",
            border: "1px solid #333"
          }}>
            <CardContent sx={{ pb: 1 }}>
              <Typography variant="h5" sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2, color: "#ffffff" }}>
                <Brain color="#64b5f6" />
                🧠 AI Thought Stream
                {isStreaming && <Activity size={20} className="animate-pulse" />}
                {aiThoughts.some(t => t.metadata?.real_system || t.metadata?.real_ai || t.metadata?.real_data) && (
                  <Chip
                    label="REAL AI ACTIVE"
                    size="small"
                    sx={{
                      bgcolor: "#1a332a",
                      color: "#4caf50",
                      border: "1px solid #4caf50",
                      fontSize: "0.75rem"
                    }}
                  />
                )}
              </Typography>
            </CardContent>
            
            <Box sx={{ flex: 1, overflow: "auto", px: 2, pb: 2 }}>
              {aiThoughts.length === 0 ? (
                <Box sx={{ 
                  display: "flex", 
                  alignItems: "center", 
                  justifyContent: "center", 
                  height: "100%",
                  flexDirection: "column",
                  color: "#888"
                }}>
                  <Brain size={48} />
                  <Typography variant="h6" sx={{ mt: 2, color: "#888" }}>
                    Waiting for AI thoughts...
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#666" }}>
                    Start the alpha hunt to see live reasoning
                  </Typography>
                </Box>
              ) : (
                <List dense>
                  {aiThoughts.map((thought, index) => {
                    const style = getThoughtStyle(thought.thought_type);
                    return (
                      <Fade in={true} key={index} timeout={500}>
                        <ListItem
                                                     sx={{
                             mb: 1,
                             backgroundColor: style.bgColor,
                             borderRadius: 2,
                             border: "1px solid #444"
                           }}
                        >
                          <ListItemIcon>
                            <Chip
                              icon={style.icon}
                              label={thought.thought_type}
                              color={style.color}
                              size="small"
                            />
                          </ListItemIcon>
                                                     <ListItemText
                             primary={
                               <Box>
                                 <Typography sx={{ color: "#ffffff" }}>
                                   {thought.content}
                                 </Typography>
                                 {(thought.metadata?.real_system || thought.metadata?.real_ai || thought.metadata?.real_data) && (
                                   <Chip
                                     label="REAL AI"
                                     size="small"
                                     sx={{
                                       mt: 1,
                                       bgcolor: "#1a332a",
                                       color: "#4caf50",
                                       border: "1px solid #4caf50",
                                       fontSize: "0.75rem"
                                     }}
                                   />
                                 )}
                               </Box>
                             }
                             secondary={
                               <Box sx={{ display: "flex", justifyContent: "space-between", mt: 1, flexWrap: "wrap", gap: 1 }}>
                                 <Typography variant="caption" sx={{ color: "#aaa" }}>
                                   {new Date(thought.timestamp).toLocaleTimeString()}
                                 </Typography>
                                 <Box sx={{ display: "flex", gap: 1 }}>
                                   {thought.metadata?.confidence && (
                                     <Typography variant="caption" sx={{ color: "#64b5f6" }}>
                                       Confidence: {(thought.metadata.confidence * 100).toFixed(0)}%
                                     </Typography>
                                   )}
                                   {thought.metadata?.vix && (
                                     <Typography variant="caption" sx={{ color: "#ff9800" }}>
                                       VIX: {thought.metadata.vix.toFixed(1)}
                                     </Typography>
                                   )}
                                   {thought.metadata?.action && (
                                     <Typography variant="caption" sx={{ color: "#4caf50" }}>
                                       {thought.metadata.action} {thought.metadata.symbol}
                                     </Typography>
                                   )}
                                 </Box>
                               </Box>
                             }
                           />
                        </ListItem>
                      </Fade>
                    );
                  })}
                  <div ref={thoughtsEndRef} />
                </List>
              )}
            </Box>
          </Card>
        </Box>

        {/* Right Panel - Alpha Research Tree */}
        <Box sx={{ flex: 1 }}>
          <Card sx={{ 
            height: "70vh", 
            display: "flex", 
            flexDirection: "column",
            bgcolor: "#1a1a1a",
            border: "1px solid #333"
          }}>
            <CardContent sx={{ pb: 1 }}>
              <Typography variant="h5" sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2, color: "#ffffff" }}>
                <Search color="#ff9800" />
                🔍 Research Pipeline
                {researchNodes.some(n => n.node_data?.data?.real_ai || n.node_data?.data?.using_llm) && (
                  <Chip
                    label="REAL AI ACTIVE"
                    size="small"
                    sx={{
                      bgcolor: "#1a332a",
                      color: "#4caf50",
                      border: "1px solid #4caf50",
                      fontSize: "0.75rem"
                    }}
                  />
                )}
              </Typography>
            </CardContent>
            
            <Box sx={{ flex: 1, overflow: "auto", px: 2, pb: 2 }}>
              {researchNodes.length === 0 ? (
                <Box sx={{ 
                  display: "flex", 
                  alignItems: "center", 
                  justifyContent: "center", 
                  height: "100%",
                  flexDirection: "column",
                  color: "#888"
                }}>
                  <Search size={48} />
                  <Typography variant="h6" sx={{ mt: 2, color: "#888" }}>
                    Research Tree Empty
                  </Typography>
                  <Typography variant="body2" textAlign="center" sx={{ color: "#666" }}>
                    Alpha research pipeline will appear here during analysis
                  </Typography>
                </Box>
              ) : (
                <List>
                  {researchNodes.map((node, index) => {
                    const style = getNodeStyle(node.node_data.status);
                    return (
                                             <Zoom in={true} key={index} timeout={300}>
                         <Paper
                           elevation={2}
                           sx={{
                             p: 2,
                             mb: 2,
                             bgcolor: "#2a2a2a",
                             borderLeft: `4px solid ${
                               style.color === "success" ? "#4caf50" :
                               style.color === "primary" ? "#2196f3" : "#757575"
                             }`
                           }}
                        >
                                                     <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 1 }}>
                             <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
                               <Typography variant="subtitle1" fontWeight="bold" sx={{ color: "#ffffff" }}>
                                 {node.node_data.title}
                               </Typography>
                               {(node.node_data.data?.real_ai || node.node_data.data?.using_llm) && (
                                 <Chip
                                   label="REAL AI RESEARCH"
                                   size="small"
                                   sx={{
                                     bgcolor: "#1a332a",
                                     color: "#4caf50",
                                     border: "1px solid #4caf50",
                                     fontSize: "0.7rem",
                                     alignSelf: "flex-start"
                                   }}
                                 />
                               )}
                             </Box>
                             <Chip
                               label={node.node_data.status}
                               color={style.color}
                               size="small"
                             />
                           </Box>
                          
                          {style.progress && node.node_data.data?.progress !== undefined && (
                            <LinearProgress
                              variant="determinate"
                              value={node.node_data.data.progress}
                              sx={{ mb: 1 }}
                            />
                          )}
                          
                                                     {/* Research Data */}
                           {node.node_data.data && (
                             <Box sx={{ mt: 1 }}>
                               {node.node_data.data.opportunities_found && (
                                 <Typography variant="body2" sx={{ color: "#aaa" }}>
                                   Found {node.node_data.data.opportunities_found} opportunities
                                 </Typography>
                               )}
                               {node.node_data.data.sources_analyzed && (
                                 <Typography variant="body2" sx={{ color: "#aaa" }}>
                                   Analyzed {node.node_data.data.sources_analyzed} sources
                                 </Typography>
                               )}
                               {node.node_data.data.final_strategy && (
                                 <Box sx={{ mt: 1 }}>
                                   <Typography variant="body2" fontWeight="bold" sx={{ color: "#ffffff" }}>
                                     Strategy: {node.node_data.data.final_strategy.action} {node.node_data.data.final_strategy.symbol}
                                   </Typography>
                                   <Typography variant="body2" sx={{ color: "#aaa" }}>
                                     Confidence: {(node.node_data.data.final_strategy.confidence * 100).toFixed(0)}%
                                   </Typography>
                                 </Box>
                               )}
                             </Box>
                           )}
                        </Paper>
                      </Zoom>
                    );
                  })}
                </List>
              )}
            </Box>
          </Card>
        </Box>
      </Box>
    </Box>
  );
} 