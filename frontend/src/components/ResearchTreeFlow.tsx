import React, { useCallback, useMemo, useState } from 'react';
import {
  ReactFlow,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  BackgroundVariant,
  Handle,
  Position,
} from 'reactflow';
import type { Node, Edge, Connection, NodeTypes } from 'reactflow';
import 'reactflow/dist/style.css';
import { Box, Typography, Chip, Paper, LinearProgress } from '@mui/material';
import {
  Psychology,
  PlayArrow,
  Assessment,
  Web,
  BarChart,
  TrendingUp,
  Search,
  CheckCircle,
  Schedule,
  Error,
} from '@mui/icons-material';

export interface TreeNode {
  id: string;
  type: 'root' | 'decision' | 'analysis' | 'websearch' | 'fundamental' | 'pandas' | 'strategy' | 'execution';
  title: string;
  status: 'pending' | 'active' | 'completed' | 'failed';
  content: string;
  metadata?: Record<string, any>;
  children?: TreeNode[];
  parent?: string;
  timestamp: string;
  confidence?: number;
  progress?: number;
}

interface ResearchTreeProps {
  treeData: TreeNode[];
}

const getNodeColor = (nodeType: string, status: string) => {
  const colors = {
    root: { bg: '#1a332a', border: '#4caf50', text: '#ffffff' },
    decision: { bg: '#2a1a32', border: '#9c27b0', text: '#ffffff' },
    analysis: { bg: '#1a2332', border: '#2196f3', text: '#ffffff' },
    websearch: { bg: '#32281a', border: '#ff9800', text: '#ffffff' },
    fundamental: { bg: '#1a321a', border: '#4caf50', text: '#ffffff' },
    pandas: { bg: '#321a1a', border: '#f44336', text: '#ffffff' },
    strategy: { bg: '#32321a', border: '#ffeb3b', text: '#000000' },
    execution: { bg: '#1a3232', border: '#00bcd4', text: '#ffffff' },
  };

  const statusOpacity = {
    pending: 0.6,
    active: 1,
    completed: 0.8,
    failed: 0.4,
  };

  const baseColor = colors[nodeType as keyof typeof colors] || colors.root;
  const opacity = statusOpacity[status as keyof typeof statusOpacity] || 0.6;

  return {
    ...baseColor,
    opacity,
  };
};

const getNodeIcon = (nodeType: string) => {
  const iconProps = { style: { fontSize: 16 } };
  switch (nodeType) {
    case 'root': return <Psychology {...iconProps} />;
    case 'decision': return <PlayArrow {...iconProps} />;
    case 'analysis': return <Assessment {...iconProps} />;
    case 'websearch': return <Web {...iconProps} />;
    case 'fundamental': return <TrendingUp {...iconProps} />;
    case 'pandas': return <BarChart {...iconProps} />;
    case 'strategy': return <Search {...iconProps} />;
    case 'execution': return <CheckCircle {...iconProps} />;
    default: return <Psychology {...iconProps} />;
  }
};

const getStatusIcon = (status: string) => {
  const iconProps = { style: { fontSize: 14 } };
  switch (status) {
    case 'pending': return <Schedule {...iconProps} />;
    case 'active': return <PlayArrow {...iconProps} />;
    case 'completed': return <CheckCircle {...iconProps} />;
    case 'failed': return <Error {...iconProps} />;
    default: return <Schedule {...iconProps} />;
  }
};

// Custom Node Component
const CustomNode = React.memo(({ data }: { data: any }) => {
  const { nodeType, status, title, content, progress, confidence, metadata } = data;
  const colors = getNodeColor(nodeType, status);

  return (
    <Box
      sx={{
        background: colors.bg,
        border: `2px solid ${colors.border}`,
        borderRadius: 2,
        padding: 2,
        minWidth: 200,
        maxWidth: 300,
        opacity: colors.opacity,
        color: colors.text,
        position: 'relative',
      }}
    >
      <Handle type="target" position={Position.Top} />
      
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        {getNodeIcon(nodeType)}
        <Typography variant="subtitle2" sx={{ fontWeight: 'bold', fontSize: '0.85rem' }}>
          {title}
        </Typography>
        {getStatusIcon(status)}
      </Box>

      {/* Content */}
      <Typography variant="body2" sx={{ fontSize: '0.75rem', mb: 1, lineHeight: 1.3 }}>
        {content}
      </Typography>

      {/* Progress Bar */}
      {status === 'active' && progress !== undefined && (
        <LinearProgress
          variant="determinate"
          value={progress}
          sx={{
            mb: 1,
            height: 4,
            borderRadius: 2,
            backgroundColor: 'rgba(255,255,255,0.2)',
            '& .MuiLinearProgress-bar': {
              backgroundColor: colors.border,
            },
          }}
        />
      )}

      {/* Metadata */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
        {confidence !== undefined && (
          <Chip
            label={`${(confidence * 100).toFixed(0)}%`}
            size="small"
            sx={{
              fontSize: '0.65rem',
              height: 18,
              backgroundColor: 'rgba(100, 181, 246, 0.2)',
              color: '#64b5f6',
            }}
          />
        )}
        {metadata?.real_ai && (
          <Chip
            label="REAL AI"
            size="small"
            sx={{
              fontSize: '0.65rem',
              height: 18,
              backgroundColor: 'rgba(76, 175, 80, 0.2)',
              color: '#4caf50',
            }}
          />
        )}
        {nodeType && (
          <Chip
            label={nodeType.toUpperCase()}
            size="small"
            variant="outlined"
            sx={{
              fontSize: '0.6rem',
              height: 16,
              borderColor: colors.border,
              color: colors.text,
            }}
          />
        )}
      </Box>

      <Handle type="source" position={Position.Bottom} />
    </Box>
  );
});

// Node types
const nodeTypes: NodeTypes = {
  custom: CustomNode,
};

const ResearchTreeFlow: React.FC<ResearchTreeProps> = ({ treeData }) => {
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null);

  // Convert tree data to React Flow format
  const { nodes, edges } = useMemo(() => {
    console.log("🌳 Building tree with", treeData.length, "nodes");
    console.log("🌳 RAW treeData:", treeData);
    console.log("🌳 Sample nodes:", treeData.slice(0, 3).map(n => ({ id: n.id, parent: n.parent, type: n.type })));
    
    const flowNodes: Node[] = [];
    const flowEdges: Edge[] = [];
    const nodeMap = new Map<string, TreeNode>();

    // Create node map
    treeData.forEach(node => {
      nodeMap.set(node.id, node);
    });
    
    console.log("🌳 Original treeData:", treeData.map(n => ({ id: n.id, parent: n.parent, type: n.type })));
    console.log("🌳 nodeMap after construction:", Array.from(nodeMap.values()).map(n => ({ id: n.id, parent: n.parent, type: n.type })));

    // Add root node if not present
    let rootExists = treeData.some(node => !node.parent);
    if (!rootExists && treeData.length > 0) {
      const rootNode: TreeNode = {
        id: 'root',
        type: 'root',
        title: 'AI Research Engine',
        status: 'active',
        content: 'Autonomous Alpha Hunter',
        timestamp: new Date().toISOString(),
      };
      nodeMap.set('root', rootNode);
    }

    // Calculate positions using a simple tree layout
    const positions = new Map<string, { x: number; y: number }>();
    const levelWidth = new Map<number, number>();
    const nodeLevel = new Map<string, number>();

    // Assign levels - completely rewritten to handle the hierarchy properly
    const assignLevels = (nodeId: string, level: number) => {
      if (nodeLevel.has(nodeId)) {
        console.log(`🌳 Node ${nodeId} already has level ${nodeLevel.get(nodeId)}`);
        return;
      }
      
      console.log(`🌳 Assigning level ${level} to node ${nodeId}`);
      nodeLevel.set(nodeId, level);
      levelWidth.set(level, (levelWidth.get(level) || 0) + 1);

      // Find all children of this node
      const children = Array.from(nodeMap.values()).filter(n => n.parent === nodeId);
      console.log(`🌳 Node ${nodeId} has ${children.length} children:`, children.map(c => ({ id: c.id, parent: c.parent })));
      
      // Process children recursively
      children.forEach(child => {
        console.log(`🌳 Processing child ${child.id} of ${nodeId} at level ${level + 1}`);
        assignLevels(child.id, level + 1);
      });
    };

    // Find all root nodes (nodes without parents)
    const rootNodes = treeData.filter(n => !n.parent);
    console.log("🌳 Found", rootNodes.length, "root nodes:", rootNodes.map(n => ({ id: n.id, type: n.type, title: n.title })));
    
    // If we have multiple root nodes, create a virtual root
    if (rootNodes.length > 1) {
      console.log("🌳 Creating virtual root for", rootNodes.length, "research tracks");
      const virtualRoot: TreeNode = {
        id: 'virtual_root',
        type: 'root',
        title: 'Research Tracks',
        status: 'active',
        content: 'Multiple Research Tracks',
        timestamp: new Date().toISOString(),
        parent: undefined
      };
      nodeMap.set('virtual_root', virtualRoot);
      
      // Assign all root nodes as children of virtual root
      rootNodes.forEach(root => {
        const nodeInMap = nodeMap.get(root.id);
        if (nodeInMap) {
          nodeInMap.parent = 'virtual_root';
          console.log("🌳 Connected root", root.id, "to virtual root");
        } else {
          console.log("🌳 WARNING: Root node", root.id, "not found in nodeMap");
        }
      });
      
      // Debug: Check what's in nodeMap after connecting
      console.log("🌳 nodeMap after connecting roots:", Array.from(nodeMap.values()).map(n => ({ id: n.id, parent: n.parent })));
      
      // Start level assignment from virtual root - this will traverse the entire tree
      assignLevels('virtual_root', 0);
    } else if (rootNodes.length === 1) {
      // Single root node
      assignLevels(rootNodes[0].id, 0);
    } else {
      // No root nodes found, use first node
      const firstNode = treeData[0];
      if (firstNode) {
        assignLevels(firstNode.id, 0);
      }
    }
    
    // Ensure all nodes have levels assigned (fallback for disconnected nodes)
    Array.from(nodeMap.values()).forEach(node => {
      if (!nodeLevel.has(node.id)) {
        console.log(`🌳 Assigning fallback level 0 to disconnected node ${node.id}`);
        nodeLevel.set(node.id, 0);
        levelWidth.set(0, (levelWidth.get(0) || 0) + 1);
      }
    });

    // Calculate positions with better spacing
    const levelCounters = new Map<number, number>();
    const calculatePosition = (nodeId: string): { x: number; y: number } => {
      const level = nodeLevel.get(nodeId) || 0;
      const nodesInLevel = levelWidth.get(level) || 1;
      const currentIndex = levelCounters.get(level) || 0;
      levelCounters.set(level, currentIndex + 1);

      // Increase horizontal spacing for better distribution
      // Use adaptive spacing: more nodes = less spacing, but with minimum and maximum bounds
      const baseSpacing = 500;
      const maxSpacing = 800;
      const minSpacing = 300;
      const horizontalSpacing = Math.max(minSpacing, Math.min(maxSpacing, baseSpacing / Math.max(nodesInLevel, 1)));
      const verticalSpacing = 200; // Increase vertical spacing
      
      const x = (currentIndex - (nodesInLevel - 1) / 2) * horizontalSpacing;
      const y = level * verticalSpacing;

      return { x, y };
    };

    // Create flow nodes
    Array.from(nodeMap.values()).forEach(node => {
      const position = calculatePosition(node.id);
      positions.set(node.id, position);
      
      const level = nodeLevel.get(node.id) || 0;
      console.log(`🌳 Node ${node.id} (${node.title?.substring(0, 30)}...) at level ${level}, position (${position.x}, ${position.y})`);

      flowNodes.push({
        id: node.id,
        type: 'custom',
        position,
        data: {
          ...node,
          nodeType: node.type,
          onClick: () => setSelectedNode(node),
        },
      });
    });

    // Create edges
    let edgeCount = 0;
    Array.from(nodeMap.values()).forEach(node => {
      if (node.parent && nodeMap.has(node.parent)) {
        flowEdges.push({
          id: `${node.parent}-${node.id}`,
          source: node.parent,
          target: node.id,
          type: 'smoothstep',
          style: {
            stroke: '#555',
            strokeWidth: 2,
          },
          animated: node.status === 'active',
        });
        edgeCount++;
      }
    });
    console.log("🌳 Created", edgeCount, "edges from nodeMap");
    
    // Log level distribution
    const levelDistribution = new Map<number, number>();
    Array.from(nodeLevel.values()).forEach(level => {
      levelDistribution.set(level, (levelDistribution.get(level) || 0) + 1);
    });
    console.log("🌳 Level distribution:", Object.fromEntries(levelDistribution));
    
    // Also create edges for virtual root if it exists
    if (nodeMap.has('virtual_root')) {
      console.log("🌳 Creating virtual root edges for", rootNodes.length, "root nodes");
      rootNodes.forEach(root => {
        flowEdges.push({
          id: `virtual_root-${root.id}`,
          source: 'virtual_root',
          target: root.id,
          type: 'smoothstep',
          style: {
            stroke: '#4caf50',
            strokeWidth: 3,
          },
          animated: false,
        });
      });
      console.log("🌳 Created", rootNodes.length, "virtual root edges");
    }

    return { nodes: flowNodes, edges: flowEdges };
  }, [treeData]);

  const [flowNodes, setNodes, onNodesChange] = useNodesState(nodes);
  const [flowEdges, setEdges, onEdgesChange] = useEdgesState(edges);

  // Update nodes when treeData changes
  React.useEffect(() => {
    setNodes(nodes);
    setEdges(edges);
  }, [nodes, edges, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNode(node.data as TreeNode);
  }, []);

  return (
    <Box sx={{ display: 'flex', height: '100%', width: '100%' }}>
      {/* Main Flow */}
      <Box sx={{ 
        flex: 1, 
        height: '100%', 
        overflow: 'hidden',
        position: 'relative'
      }}>
        <ReactFlow
          nodes={flowNodes}
          edges={flowEdges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.1, includeHiddenNodes: false }}
          minZoom={0.1}
          maxZoom={2}
          attributionPosition="bottom-left"
          style={{
            backgroundColor: '#0a0a0a',
          }}
        >
          <Controls
            style={{
              backgroundColor: '#1a1a1a',
              border: '1px solid #333',
            }}
          />
          <Background 
            variant={BackgroundVariant.Dots} 
            gap={20} 
            size={1} 
            color="#333"
          />
        </ReactFlow>
      </Box>

      {/* Node Details Panel */}
      {selectedNode && (
        <Box sx={{ width: 300, ml: 2, height: '100%' }}>
          <Paper sx={{
            p: 2,
            bgcolor: '#1a1a1a',
            border: '1px solid #333',
            height: '100%',
            overflow: 'auto',
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              {getNodeIcon(selectedNode.type)}
              <Typography variant="h6" sx={{ color: '#ffffff' }}>
                {selectedNode.title}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              {getStatusIcon(selectedNode.status)}
              <Chip
                label={selectedNode.status.toUpperCase()}
                color={
                  selectedNode.status === 'completed' ? 'success' :
                  selectedNode.status === 'active' ? 'primary' :
                  selectedNode.status === 'failed' ? 'error' : 'default'
                }
                size="small"
              />
              <Chip
                label={selectedNode.type.toUpperCase()}
                variant="outlined"
                size="small"
              />
            </Box>

            <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
              {selectedNode.content}
            </Typography>

            {selectedNode.confidence !== undefined && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" sx={{ color: '#64b5f6' }}>
                  Confidence: {(selectedNode.confidence * 100).toFixed(0)}%
                </Typography>
              </Box>
            )}

            {selectedNode.progress !== undefined && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" sx={{ color: '#ff9800' }}>
                  Progress: {selectedNode.progress}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={selectedNode.progress}
                  sx={{ mt: 0.5 }}
                />
              </Box>
            )}

            <Typography variant="caption" sx={{ color: '#666' }}>
              {new Date(selectedNode.timestamp).toLocaleString()}
            </Typography>

            {selectedNode.metadata && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" sx={{ color: '#888', display: 'block', mb: 1 }}>
                  Metadata:
                </Typography>
                <pre style={{
                  fontSize: '10px',
                  color: '#666',
                  background: '#0a0a0a',
                  padding: '8px',
                  borderRadius: 4,
                  overflow: 'auto',
                  maxHeight: '200px'
                }}>
                  {JSON.stringify(selectedNode.metadata, null, 2)}
                </pre>
              </Box>
            )}
          </Paper>
        </Box>
      )}
    </Box>
  );
};

export default ResearchTreeFlow; 