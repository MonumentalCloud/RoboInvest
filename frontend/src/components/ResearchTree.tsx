import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Box, Typography, Chip, Paper } from '@mui/material';
import { 
  Search, 
  TrendingUp, 
  Assessment, 
  Web,
  BarChart,
  Psychology,
  PlayArrow,
  CheckCircle,
  Schedule,
  Error,
  Lightbulb,
  Target,
  Analytics,
  DataUsage
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
  width?: number;
  height?: number;
}

const ResearchTree: React.FC<ResearchTreeProps> = ({ 
  treeData, 
  width = 800, 
  height = 600 
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null);

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'root': return <Psychology />;
      case 'decision': return <Target />;
      case 'analysis': return <Analytics />;
      case 'websearch': return <Web />;
      case 'fundamental': return <TrendingUp />;
      case 'pandas': return <DataUsage />;
      case 'strategy': return <Lightbulb />;
      case 'execution': return <CheckCircle />;
      default: return <Psychology />;
    }
  };

  const getNodeColor = (type: string, status: string) => {
    // Status-based colors (priority over type)
    if (status === 'active') {
      return { bg: '#2e7d32', border: '#4caf50', opacity: 1 }; // Green for active
    } else if (status === 'failed') {
      return { bg: '#d32f2f', border: '#f44336', opacity: 0.8 }; // Red for failed
    } else if (status === 'completed') {
      return { bg: '#424242', border: '#9e9e9e', opacity: 0.9 }; // White/gray for completed
    } else if (status === 'pending') {
      return { bg: '#1976d2', border: '#2196f3', opacity: 0.7 }; // Blue for pending
    }

    // Type-based colors (fallback)
    const colors = {
      root: { bg: '#1a332a', border: '#4caf50' },
      decision: { bg: '#2a1a32', border: '#9c27b0' },
      analysis: { bg: '#1a2332', border: '#2196f3' },
      websearch: { bg: '#32281a', border: '#ff9800' },
      fundamental: { bg: '#1a321a', border: '#4caf50' },
      pandas: { bg: '#321a1a', border: '#f44336' },
      strategy: { bg: '#32321a', border: '#ffeb3b' },
      execution: { bg: '#1a3232', border: '#00bcd4' }
    };

    const baseColor = colors[type as keyof typeof colors] || colors.root;
    return {
      bg: baseColor.bg,
      border: baseColor.border,
      opacity: 0.8
    };
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Schedule sx={{ fontSize: 16 }} />;
      case 'active': return <PlayArrow sx={{ fontSize: 16 }} />;
      case 'completed': return <CheckCircle sx={{ fontSize: 16 }} />;
      case 'failed': return <Error sx={{ fontSize: 16 }} />;
      default: return <Schedule sx={{ fontSize: 16 }} />;
    }
  };

  const getDetailedContent = (node: TreeNode): string => {
    // Try to extract detailed content from metadata
    const metadata = node.metadata || {};
    
    // Check for specific research content
    if (metadata.opportunity) {
      return `Researching: ${metadata.opportunity}`;
    }
    
    if (metadata.research_type) {
      return `${node.content} - Type: ${metadata.research_type}`;
    }
    
    if (metadata.confidence) {
      return `${node.content} - Confidence: ${(metadata.confidence * 100).toFixed(0)}%`;
    }
    
    if (metadata.primary_ticker) {
      return `${node.content} - Ticker: ${metadata.primary_ticker}`;
    }
    
    if (metadata.decision_type) {
      return `${node.content} - Decision: ${metadata.decision_type}`;
    }
    
    if (metadata.strategy_type) {
      return `${node.content} - Strategy: ${metadata.strategy_type}`;
    }
    
    if (metadata.synthesis_type) {
      return `${node.content} - Synthesis: ${metadata.synthesis_type}`;
    }
    
    if (metadata.phase) {
      return `${node.content} - Phase: ${metadata.phase}`;
    }
    
    // Fallback to original content
    return node.content;
  };

  // Convert flat array to hierarchical structure
  const buildTree = (nodes: TreeNode[]): TreeNode => {
    const rootNode: TreeNode = {
      id: 'root',
      type: 'root',
      title: 'AI Research Engine',
      status: 'active',
      content: 'Autonomous Alpha Hunter',
      timestamp: new Date().toISOString(),
      children: []
    };

    // Create a map for quick lookup
    const nodeMap = new Map<string, TreeNode>();
    nodeMap.set('root', rootNode);

    // Add all nodes to the map
    nodes.forEach(node => {
      nodeMap.set(node.id, { ...node, children: [] });
    });

    // Build hierarchy
    nodes.forEach(node => {
      const parentId = node.parent || 'root';
      const parent = nodeMap.get(parentId);
      const child = nodeMap.get(node.id);
      
      if (parent && child) {
        parent.children = parent.children || [];
        parent.children.push(child);
      }
    });

    return rootNode;
  };

  useEffect(() => {
    if (!svgRef.current || treeData.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 20, right: 120, bottom: 20, left: 120 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Build tree hierarchy
    const root = buildTree(treeData);
    
    // Create tree layout
    const treeLayout = d3.tree<TreeNode>()
      .size([innerHeight, innerWidth])
      .separation((a, b) => (a.parent === b.parent ? 1 : 1.5));

    const hierarchy = d3.hierarchy(root);
    const treeData_d3 = treeLayout(hierarchy);

    // Create links with status-based colors
    g.selectAll('.link')
      .data(treeData_d3.links())
      .enter().append('path')
      .attr('class', 'link')
      .attr('d', d3.linkHorizontal<any, any>()
        .x((d: any) => d.y)
        .y((d: any) => d.x)
      )
      .style('fill', 'none')
      .style('stroke', (d: any) => {
        // Color links based on child node status
        const childStatus = d.target.data.status;
        if (childStatus === 'active') return '#4caf50';
        if (childStatus === 'failed') return '#f44336';
        if (childStatus === 'completed') return '#9e9e9e';
        return '#555';
      })
      .style('stroke-width', 2)
      .style('stroke-opacity', 0.8);

    // Create nodes
    const node = g.selectAll('.node')
      .data(treeData_d3.descendants())
      .enter().append('g')
      .attr('class', 'node')
      .attr('transform', (d: any) => `translate(${d.y},${d.x})`)
      .style('cursor', 'pointer')
      .on('click', (_, d: any) => {
        setSelectedNode(d.data);
      });

    // Add circles for nodes with improved styling
    node.append('circle')
      .attr('r', (d: any) => d.data.type === 'root' ? 10 : 8)
      .style('fill', (d: any) => {
        const color = getNodeColor(d.data.type, d.data.status);
        return color.bg;
      })
      .style('stroke', (d: any) => {
        const color = getNodeColor(d.data.type, d.data.status);
        return color.border;
      })
      .style('stroke-width', 3)
      .style('opacity', (d: any) => {
        const color = getNodeColor(d.data.type, d.data.status);
        return color.opacity;
      })
      .style('filter', (d: any) => {
        // Add glow effect for active nodes
        if (d.data.status === 'active') {
          return 'drop-shadow(0 0 8px #4caf50)';
        }
        return 'none';
      });

    // Add labels with better positioning and content
    node.append('text')
      .attr('dy', '.35em')
      .attr('x', (d: any) => d.children ? -15 : 15)
      .style('text-anchor', (d: any) => d.children ? 'end' : 'start')
      .style('fill', '#ffffff')
      .style('font-size', '11px')
      .style('font-weight', (d: any) => d.data.type === 'root' ? 'bold' : 'normal')
      .text((d: any) => {
        // Show detailed content for better understanding
        return getDetailedContent(d.data);
      });

    // Add progress indicators for active nodes
    node.filter((d: any) => d.data.status === 'active' && d.data.progress !== undefined)
      .append('circle')
      .attr('r', 12)
      .style('fill', 'none')
      .style('stroke', '#4caf50')
      .style('stroke-width', 2)
      .style('stroke-dasharray', '20')
      .style('stroke-dashoffset', (d: any) => 20 - (d.data.progress || 0) * 0.2)
      .style('opacity', 0.8);

    // Add status indicators
    node.filter((d: any) => d.data.status === 'failed')
      .append('text')
      .attr('dy', '-1.5em')
      .attr('x', 0)
      .style('text-anchor', 'middle')
      .style('fill', '#f44336')
      .style('font-size', '14px')
      .text('✗');

  }, [treeData, width, height]);

  return (
    <Box sx={{ display: 'flex', height: '100%' }}>
      {/* Tree visualization */}
      <Box sx={{ flex: 1 }}>
        <svg
          ref={svgRef}
          width={width}
          height={height}
          style={{ 
            background: '#0a0a0a',
            border: '1px solid #333',
            borderRadius: 8
          }}
        />
      </Box>

      {/* Node details panel */}
      {selectedNode && (
        <Box sx={{ width: 350, ml: 2 }}>
          <Paper sx={{ 
            p: 2, 
            bgcolor: '#1a1a1a', 
            border: '1px solid #333',
            height: '100%'
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
              {getDetailedContent(selectedNode)}
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
              </Box>
            )}

            <Typography variant="caption" sx={{ color: '#666' }}>
              {new Date(selectedNode.timestamp).toLocaleString()}
            </Typography>

            {selectedNode.metadata && Object.keys(selectedNode.metadata).length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" sx={{ color: '#888', display: 'block', mb: 1 }}>
                  Research Details:
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

export default ResearchTree; 