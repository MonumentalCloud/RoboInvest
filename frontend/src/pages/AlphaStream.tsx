import { useState, useEffect, useRef } from "react";
import { 
  Brain, 
  Zap, 
  TrendingUp, 
  Search, 
  Target, 
  CheckCircle, 
  Wifi,
  WifiOff,
  Activity,
  Eye,
  Clock,
  Target as TargetIcon,
  DollarSign,
  AlertTriangle,
  ArrowUp,
  ArrowDown
} from "lucide-react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  Alert,
  Fade,
  Zoom,
  Grid,
  Divider,
  Button
} from '@mui/material';
import ResearchTreeFlow from '../components/ResearchTreeFlow';
import type { TreeNode } from '../components/ResearchTreeFlow';
import { useResearchInsights, useAlphaOpportunities, useResearchStatus, useDecisionTrees } from '../hooks';

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
  const [aiThoughts, setAiThoughts] = useState<AIThought[]>([]);
  const [researchNodes, setResearchNodes] = useState<ResearchNode[]>([]);
  const [treeNodes, setTreeNodes] = useState<TreeNode[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<"connecting" | "connected" | "disconnected">("disconnected");
  
  // Research data hooks
  const { data: researchStatus } = useResearchStatus();
  const { data: insightsData } = useResearchInsights(20);
  const { data: opportunitiesData } = useAlphaOpportunities(0.6);
  const { data: decisionTreesData, refetch: refetchDecisionTrees } = useDecisionTrees();
  
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
      
      // Close existing connection if any
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      
      // Add a small delay before connecting to ensure backend is ready
      setTimeout(() => {
        wsRef.current = new WebSocket("ws://localhost:8081/ws/ai-thoughts");
        
        wsRef.current.onopen = () => {
          setConnectionStatus("connected");
          console.log("✅ WebSocket connected successfully!");
          
          // Send a ping to test connection
          if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: "ping" }));
          }
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
            } else if (message.type === "tree_update") {
              // Update tree structure
              console.log("🌳 Tree update received:", message.tree?.length, "nodes");
              // Transform backend tree format to frontend format
              const transformedTree = message.tree?.map((node: any) => ({
                ...node,
                title: node.content || node.id, // Use content as title if available
                parent: node.parent_id, // Map parent_id to parent
                timestamp: node.created_at || node.timestamp || new Date().toISOString()
              })) || [];
              setTreeNodes(transformedTree);
            }
          } catch (err) {
            console.error("Error parsing message:", err);
          }
        };
        
        wsRef.current.onclose = (event) => {
          setConnectionStatus("disconnected");
          console.log("❌ WebSocket disconnected. Code:", event.code, "Reason:", event.reason);
          
          // Handle different close codes
          let reconnectDelay = 3000;
          if (event.code === 1006) {
            console.log("🔗 Abnormal closure detected - server may be unreachable");
            reconnectDelay = 5000; // Longer delay for server issues
          }
          
          // Auto-reconnect after delay
          setTimeout(() => {
            if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
              console.log("🔄 Attempting to reconnect...");
              connectWebSocket();
            }
          }, reconnectDelay);
        };
        
        wsRef.current.onerror = (error) => {
          console.error("❌ WebSocket error:", error);
          setConnectionStatus("disconnected");
        };
      }, 500); // 500ms delay
      
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

  // Research data processing
  const insights = insightsData?.data?.insights || [];
  const opportunities = opportunitiesData?.data?.opportunities || [];
  const status = researchStatus?.data;
  
  // Use decision trees data as fallback when websocket data is not available
  useEffect(() => {
    console.log("🌳 Decision trees data check:", {
      treeNodesLength: treeNodes.length,
      decisionTreesDataLength: decisionTreesData?.length,
      decisionTreesData: decisionTreesData
    });
    
    if (treeNodes.length === 0 && decisionTreesData && decisionTreesData.length > 0) {
      console.log("🌳 Using fallback decision trees data:", decisionTreesData.length, "nodes");
      setTreeNodes(decisionTreesData);
    }
  }, [treeNodes.length, decisionTreesData]);

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
      console.error("Failed to send test message:", error);
    }
  };

  const testTreeVisualization = () => {
    // Simulate tree update for testing
    const testTree: TreeNode[] = [
      {
        id: "test_root",
        type: "decision",
        title: "Test Research",
        content: "Testing tree visualization",
        status: "active",
        timestamp: new Date().toISOString(),
        children: []
      }
    ];
    setTreeNodes(testTree);
  };

  const loadDecisionTreesFromAPI = async () => {
    try {
      console.log("🌳 Loading decision trees from API...");
      const response = await fetch("http://localhost:8081/api/research/decision-trees");
      const data = await response.json();
      
      console.log("🌳 Raw API response:", data);
      
      if (data.data) {
        const flatTrees: any[] = [];
        Object.entries(data.data).forEach(([trackName, trackData]: [string, any]) => {
          console.log(`🌳 Processing track: ${trackName}`, trackData);
          if (trackData?.tree?.nodes) {
            const nodes = Object.values(trackData.tree.nodes).map((node: any) => ({
              ...node,
              title: node.content || node.id,
              parent: node.parent_id, // Map parent_id to parent
              timestamp: node.created_at || node.timestamp || new Date().toISOString(),
              track: trackName
            }));
            flatTrees.push(...nodes);
          }
        });
        
        console.log("🌳 Loaded decision trees from API:", flatTrees.length, "nodes");
        console.log("🌳 Sample nodes:", flatTrees.slice(0, 3));
        setTreeNodes(flatTrees);
      } else {
        console.log("🌳 No data.data found in response");
      }
    } catch (error) {
      console.error("Failed to load decision trees:", error);
    }
  };

  const getThoughtStyle = (thoughtType: string) => {
    switch (thoughtType.toLowerCase()) {
      case "system_start":
        return { bgColor: "#1a332a", icon: <CheckCircle color="#4caf50" /> };
      case "opportunity_scanning":
        return { bgColor: "#332a1a", icon: <Search color="#ff9800" /> };
      case "execution_decision":
        return { bgColor: "#1a1a2a", icon: <Target color="#4a90e2" /> };
      case "fallback_decision":
        return { bgColor: "#2a1a1a", icon: <AlertTriangle color="#f44336" /> };
      default:
        return { bgColor: "#1a1a1a", icon: <Brain color="#64b5f6" /> };
    }
  };

  const getNodeStyle = (status: string) => {
    switch (status) {
      case "active":
        return { color: "warning" as const, progress: true };
      case "completed":
        return { color: "success" as const, progress: false };
      case "failed":
        return { color: "error" as const, progress: false };
      default:
        return { color: "default" as const, progress: false };
    }
  };

  return (
    <Box sx={{ p: 3, minHeight: "100vh", bgcolor: "#0a0a0a", color: "#ffffff" }}>
      {/* Header */}
      <Box sx={{ 
        display: "flex", 
        justifyContent: "space-between", 
        alignItems: "center", 
        mb: 3,
        flexWrap: "wrap",
        gap: 2
      }}>
        <Box>
          <Typography variant="h4" sx={{ 
            display: "flex", 
            alignItems: "center", 
            gap: 1,
            color: "#ff9800",
            fontWeight: "bold"
          }}>
            <Eye />
            🔍 Continuous Research Dashboard
          </Typography>
          <Typography variant="body2" sx={{ color: "#888", mt: 1 }}>
            Live AI research insights and alpha opportunities
          </Typography>
        </Box>
        
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          {/* Connection Status */}
          <Box sx={{ 
            display: "flex", 
            alignItems: "center", 
            gap: 1,
            px: 2,
            py: 1,
            borderRadius: 2,
            bgcolor: connectionStatus === "connected" ? "#1a332a" : "#332a1a",
            border: `1px solid ${connectionStatus === "connected" ? "#4caf50" : "#ff9800"}`
          }}>
            {connectionStatus === "connected" ? <Wifi color="#4caf50" /> : <WifiOff color="#ff9800" />}
            <Typography variant="body2" sx={{ 
              color: connectionStatus === "connected" ? "#4caf50" : "#ff9800",
              fontWeight: "bold"
            }}>
              {connectionStatus === "connected" ? "Live" : 
               connectionStatus === "connecting" ? "Connecting..." : "Reconnecting..."}
            </Typography>
          </Box>
          
          {/* Research Status */}
          {status && (
            <Box sx={{ 
              display: "flex", 
              alignItems: "center", 
              gap: 1,
              px: 2,
              py: 1,
              borderRadius: 2,
              bgcolor: "#1a1a2a",
              border: "1px solid #4a90e2"
            }}>
              <Activity color="#4a90e2" />
              <Typography variant="body2" sx={{ color: "#4a90e2", fontWeight: "bold" }}>
                {status.insights_generated || 0} insights
              </Typography>
            </Box>
          )}
          
          {/* Load Decision Trees Button */}
          <Button
            variant="outlined"
            onClick={loadDecisionTreesFromAPI}
            sx={{ color: "#2196f3", borderColor: "#2196f3", mr: 1 }}
          >
            Load Trees
          </Button>
          
          {/* Refetch Decision Trees Button */}
          <Button
            variant="outlined"
            onClick={() => refetchDecisionTrees()}
            sx={{ color: "#ff9800", borderColor: "#ff9800" }}
          >
            Refetch Trees
          </Button>
        </Box>
      </Box>

      {/* Continuous Research Status */}
      <Alert 
        severity="info" 
        icon={<Activity />}
        sx={{ 
          mb: 3, 
          bgcolor: "#1a1a2a", 
          color: "#4a90e2",
          border: "1px solid #4a90e2",
          "& .MuiAlert-icon": { color: "#4a90e2" }
        }}
      >
        <Typography variant="body1" fontWeight="bold">
          🤖 Continuous AI Research System Active
        </Typography>
        <Typography variant="body2" sx={{ color: "#81c784" }}>
          • 6 research tracks running 24/7 • Real-time market analysis • Alpha opportunity detection • Automated insights generation
        </Typography>
      </Alert>

      {/* Alpha Opportunities Grid */}
      <Box sx={{ display: "flex", gap: 3, mb: 3, flexDirection: { xs: "column", md: "row" } }}>
        <Box sx={{ flex: 1 }}>
          <Card sx={{ 
            bgcolor: "#1a1a1a",
            border: "1px solid #333",
            height: "100%"
          }}>
            <CardContent>
              <Typography variant="h6" sx={{ 
                display: "flex", 
                alignItems: "center", 
                gap: 1, 
                mb: 2, 
                color: "#ff9800" 
              }}>
                <TargetIcon />
                🎯 High-Confidence Alpha Opportunities
              </Typography>
              
              {opportunities.length === 0 ? (
                <Box sx={{ 
                  display: "flex", 
                  alignItems: "center", 
                  justifyContent: "center", 
                  height: "200px",
                  flexDirection: "column",
                  color: "#888"
                }}>
                  <Target size={48} />
                  <Typography variant="body1" sx={{ mt: 2, color: "#888" }}>
                    No high-confidence opportunities yet
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#666" }}>
                    AI agents are continuously scanning for alpha
                  </Typography>
                </Box>
              ) : (
                <List dense>
                  {opportunities.slice(0, 5).map((opportunity: any, index: number) => (
                    <Fade in={true} key={opportunity.id} timeout={500 + index * 100}>
                      <ListItem sx={{
                        mb: 2,
                        bgcolor: "#2a2a2a",
                        borderRadius: 2,
                        border: "1px solid #444"
                      }}>
                        <ListItemIcon>
                          <Chip
                            label={`${(opportunity.confidence * 100).toFixed(0)}%`}
                            size="small"
                            color={opportunity.confidence > 0.8 ? "success" : "warning"}
                          />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography sx={{ color: "#ffffff", fontWeight: "bold" }}>
                              {opportunity.opportunity}
                            </Typography>
                          }
                          secondary={
                            <Typography variant="body2" sx={{ color: "#888", mt: 1 }}>
                              <strong>Edge:</strong> {opportunity.competitive_edge}
                              {opportunity.action_plan && opportunity.action_plan.length > 0 && (
                                <> • <strong>Actions:</strong> {opportunity.action_plan.join(", ")}</>
                              )}
                              {opportunity.buy_conditions && opportunity.buy_conditions.length > 0 && (
                                <> • <strong style={{color: "#4caf50"}}>Buy:</strong> {opportunity.buy_conditions.join(", ")}</>
                              )}
                              {opportunity.exit_conditions && opportunity.exit_conditions.length > 0 && (
                                <> • <strong style={{color: "#ff9800"}}>Exit:</strong> {opportunity.exit_conditions.join(", ")}</>
                              )}
                              <br />
                              <span style={{color: "#666", fontSize: "0.75rem"}}>
                                {new Date(opportunity.discovered_at).toLocaleString()}
                              </span>
                            </Typography>
                          }
                        />
                        <Box sx={{ display: "flex", gap: 1, mt: 1, flexWrap: "wrap" }}>
                          <Chip 
                            label={`SL: ${opportunity.stop_loss || "5%"}`} 
                            size="small" 
                            color="error" 
                            variant="outlined"
                          />
                          <Chip 
                            label={`TP: ${opportunity.take_profit || "15%"}`} 
                            size="small" 
                            color="success" 
                            variant="outlined"
                          />
                          <Chip 
                            label={opportunity.position_sizing || "Standard"} 
                            size="small" 
                            color="primary" 
                            variant="outlined"
                          />
                        </Box>
                      </ListItem>
                    </Fade>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Box>

        <Box sx={{ flex: 1 }}>
          <Card sx={{ 
            bgcolor: "#1a1a1a",
            border: "1px solid #333",
            height: "100%"
          }}>
            <CardContent>
              <Typography variant="h6" sx={{ 
                display: "flex", 
                alignItems: "center", 
                gap: 1, 
                mb: 2, 
                color: "#64b5f6" 
              }}>
                <Brain />
                🧠 Latest Research Insights
              </Typography>
              
              {insights.length === 0 ? (
                <Box sx={{ 
                  display: "flex", 
                  alignItems: "center", 
                  justifyContent: "center", 
                  height: "200px",
                  flexDirection: "column",
                  color: "#888"
                }}>
                  <Brain size={48} />
                  <Typography variant="body1" sx={{ mt: 2, color: "#888" }}>
                    No insights available yet
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#666" }}>
                    AI agents are working in the background
                  </Typography>
                </Box>
              ) : (
                <List dense>
                  {insights.slice(0, 5).map((insight: any, index: number) => (
                    <Fade in={true} key={index} timeout={500 + index * 100}>
                      <ListItem sx={{
                        mb: 2,
                        bgcolor: "#2a2a2a",
                        borderRadius: 2,
                        border: "1px solid #444"
                      }}>
                        <ListItemIcon>
                          <Chip
                            label={insight.track}
                            size="small"
                            color="primary"
                          />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography sx={{ color: "#ffffff" }}>
                              {insight.insight}
                            </Typography>
                          }
                          secondary={
                            <Typography variant="body2" sx={{ color: "#888", mt: 1 }}>
                              <strong>Confidence:</strong> {(insight.confidence * 100).toFixed(0)}% • {new Date(insight.timestamp).toLocaleString()}
                            </Typography>
                          }
                        />
                      </ListItem>
                    </Fade>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Research Tree Visualization */}
      <Box sx={{ height: "50vh", mb: 3 }}>
        <Card sx={{ 
          height: "100%", 
          display: "flex", 
          flexDirection: "column",
          bgcolor: "#1a1a1a",
          border: "1px solid #333"
        }}>
          <CardContent sx={{ pb: 1 }}>
            <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2 }}>
              <Typography variant="h5" sx={{ display: "flex", alignItems: "center", gap: 1, color: "#ffffff" }}>
                <Search color="#ff9800" />
                🌳 Live Research Decision Trees
              </Typography>
              <Button 
                variant="outlined" 
                size="small" 
                onClick={loadDecisionTreesFromAPI}
                sx={{ color: "#ff9800", borderColor: "#ff9800" }}
              >
                Load Trees
              </Button>
            </Box>
          </CardContent>
          
          <Box sx={{ flex: 1, overflow: "hidden", px: 2, pb: 2 }}>
            {treeNodes.length === 0 ? (
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
                  Waiting for research trees...
                </Typography>
                <Typography variant="body2" sx={{ color: "#666" }}>
                  Decision trees will appear as AI agents work
                </Typography>
              </Box>
            ) : (
              <ResearchTreeFlow 
                treeData={treeNodes}
              />
            )}
          </Box>
        </Card>
      </Box>

      {/* Live AI Thoughts Stream */}
      <Card sx={{ 
        bgcolor: "#1a1a1a",
        border: "1px solid #333"
      }}>
        <CardContent>
          <Typography variant="h6" sx={{ 
            display: "flex", 
            alignItems: "center", 
            gap: 1, 
            mb: 2, 
            color: "#64b5f6" 
          }}>
            <Brain />
            🧠 Live AI Research Thoughts
          </Typography>
          
          <Box sx={{ maxHeight: "300px", overflow: "auto" }}>
            {aiThoughts.length === 0 ? (
              <Box sx={{ 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "center", 
                height: "200px",
                flexDirection: "column",
                color: "#888"
              }}>
                <Brain size={48} />
                <Typography variant="body1" sx={{ mt: 2, color: "#888" }}>
                  Waiting for AI thoughts...
                </Typography>
                <Typography variant="body2" sx={{ color: "#666" }}>
                  AI agents will share their reasoning in real-time
                </Typography>
              </Box>
            ) : (
              <List dense>
                {aiThoughts.map((thought, index) => {
                  const style = getThoughtStyle(thought.thought_type);
                  return (
                    <Fade in={true} key={index} timeout={500}>
                      <ListItem sx={{
                        mb: 1,
                        backgroundColor: style.bgColor,
                        borderRadius: 2,
                        border: "1px solid #444"
                      }}>
                        <ListItemIcon>
                          {style.icon}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography sx={{ color: "#ffffff" }}>
                              {thought.content}
                            </Typography>
                          }
                          secondary={
                            <Typography variant="caption" sx={{ color: "#888" }}>
                              {new Date(thought.timestamp).toLocaleString()}
                            </Typography>
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
        </CardContent>
      </Card>
    </Box>
  );
} 