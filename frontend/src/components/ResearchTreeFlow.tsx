import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, CircularProgress, Alert } from '@mui/material';
import OrganicResearchGraph from './OrganicResearchGraph';
import GraphChatInterface from './GraphChatInterface';
import type { TreeNode } from './OrganicResearchGraph';

// API functions for backend on port 8081
const fetchResearchTrees = async () => {
  try {
    const response = await fetch('http://localhost:8081/api/research/decision-trees');
    if (!response.ok) throw new Error('Failed to fetch research trees');
    const data = await response.json();
    console.log('Raw research trees response:', data);
    return data;
  } catch (error) {
    console.error('Error fetching research trees:', error);
    return [];
  }
};

const fetchRecentEvents = async () => {
  try {
    const response = await fetch('http://localhost:8081/api/events/recent');
    if (!response.ok) throw new Error('Failed to fetch recent events');
    const data = await response.json();
    console.log('Raw recent events response:', data);
    return data;
  } catch (error) {
    console.error('Error fetching recent events:', error);
    return [];
  }
};

interface ResearchTreeFlowProps {
  maxNodes?: number;
}

const ResearchTreeFlow: React.FC<ResearchTreeFlowProps> = ({ maxNodes = 100 }) => {
  const [treeData, setTreeData] = useState<TreeNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [highlightedNodes, setHighlightedNodes] = useState<string[]>([]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch research trees
      const treesResponse = await fetchResearchTrees();
      console.log('Research trees response:', treesResponse);

      // Fetch recent events
      const eventsResponse = await fetchRecentEvents();
      console.log('Recent events response:', eventsResponse);

      // Combine and process data
      let allNodes: TreeNode[] = [];

      // Process research trees
      if (treesResponse && treesResponse.status === 'success' && treesResponse.data) {
        // Handle the actual response structure from the backend
        const trees = Array.isArray(treesResponse.data) ? treesResponse.data : [treesResponse.data];
        
        trees.forEach((tree: any) => {
          // The backend returns different research tracks as separate objects
          // Each track has a 'tree' property containing the nodes
          Object.keys(tree).forEach((trackKey) => {
            const track = tree[trackKey];
            if (track && track.tree && Array.isArray(track.tree)) {
              const processedNodes = track.tree.map((node: any) => ({
                id: node.id || `node-${Math.random()}`,
                type: node.type || 'analysis',
                title: node.title || node.content?.substring(0, 30) || 'Untitled',
                status: node.status || 'completed',
                content: node.content || '',
                metadata: node.metadata || {},
                parent: node.parent || null,
                timestamp: node.timestamp || new Date().toISOString(),
                confidence: node.confidence || 0.5,
                progress: node.progress || 0,
                research_track: trackKey,
              }));
              allNodes = [...allNodes, ...processedNodes];
            }
          });
        });
      }

      // Process recent events
      if (eventsResponse && eventsResponse.status === 'success' && eventsResponse.data) {
        const events = Array.isArray(eventsResponse.data) ? eventsResponse.data : [eventsResponse.data];
        
        events.forEach((event: any) => {
          // Convert central events to research nodes if they contain research data
          if (event.event_type === 'research' || event.event_type === 'ai_thought') {
            const processedNode: TreeNode = {
              id: event.event_id || `event-${Math.random()}`,
              type: event.event_type === 'ai_thought' ? 'analysis' : 'websearch',
              title: event.title || event.message?.substring(0, 30) || 'Event Node',
              status: 'active',
              content: event.message || '',
              metadata: event.metadata || {},
              parent: undefined,
              timestamp: event.timestamp || new Date().toISOString(),
              confidence: 0.5,
              progress: 0,
              research_track: 'events',
            };
            allNodes.push(processedNode);
          }
        });
      }

      // Remove duplicates and limit nodes
      const uniqueNodes = allNodes.filter((node, index, self) => 
        index === self.findIndex(n => n.id === node.id)
      );

      // Sort by timestamp (newest first) and limit
      const sortedNodes = uniqueNodes
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
        .slice(0, maxNodes);

      console.log(`Processed ${sortedNodes.length} unique nodes from ${allNodes.length} total nodes`);
      setTreeData(sortedNodes);
      
      setLastUpdate(new Date());

    } catch (err) {
      console.error('Error fetching research data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch research data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    // Set up WebSocket connection for real-time updates
    const ws = new WebSocket('ws://localhost:8081/ws/central-events');
    
    ws.onopen = () => {
      console.log('WebSocket connected for research tree updates');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'research_update' || data.type === 'ai_thought') {
          console.log('Received real-time update:', data);
          // Refresh data when we receive updates
          fetchData();
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    // Cleanup WebSocket on unmount
    return () => {
      ws.close();
    };
  }, [maxNodes]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      fetchData();
    }, 30000);

    return () => clearInterval(interval);
  }, [maxNodes]);

  if (loading && treeData.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '600px' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', height: '100%' }}>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Organic Research Graph
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {treeData.length} research nodes • 
          {treeData.filter(n => n.status === 'active').length} active • 
          {treeData.filter(n => n.type === 'synthesis').length} synthesis nodes
          {lastUpdate && ` • Last updated: ${lastUpdate.toLocaleTimeString()}`}
        </Typography>
      </Paper>

      <Box sx={{ 
        width: '100%', 
        height: 'calc(100vh - 200px)', 
        minHeight: '600px',
        position: 'relative'
      }}>
        <OrganicResearchGraph 
          treeData={treeData}
          width={1200}
          height={800}
          onNodeHighlight={setHighlightedNodes}
        />

        {/* Chat Interface */}
        <GraphChatInterface
          onHighlightNodes={setHighlightedNodes}
          onNavigateToNode={(nodeId) => {
            // Find the node in the graph and highlight it
            setHighlightedNodes([nodeId]);
            // TODO: Add zoom to node functionality
            console.log('Navigate to node:', nodeId);
          }}
          treeData={treeData}
        />
      </Box>
    </Box>
  );
};

export default ResearchTreeFlow; 