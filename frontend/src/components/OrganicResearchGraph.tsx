import React, { useRef, useEffect, useState, useMemo } from 'react';
import * as d3 from 'd3';
import { Box, Typography, Chip, LinearProgress } from '@mui/material';

export interface TreeNode {
  id: string;
  type: 'root' | 'decision' | 'analysis' | 'websearch' | 'fundamental' | 'pandas' | 'strategy' | 'execution' | 'synthesis';
  title: string;
  status: 'pending' | 'active' | 'completed' | 'failed';
  content: string;
  metadata?: Record<string, any>;
  parent?: string;
  timestamp: string;
  confidence?: number | string;
  progress?: number;
  research_track?: string;
}

interface OrganicResearchGraphProps {
  treeData: TreeNode[];
  width?: number;
  height?: number;
  onNodeHighlight?: (nodeIds: string[]) => void;
}

const OrganicResearchGraph: React.FC<OrganicResearchGraphProps> = ({ 
  treeData, 
  width = 1200, 
  height = 800,
  onNodeHighlight
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [highlightedNodes, setHighlightedNodes] = useState<Set<string>>(new Set());

  // Process data to create nodes and links
  const { nodes, links } = useMemo(() => {
    const nodeMap = new Map<string, TreeNode>();
    const processedNodes: any[] = [];
    const processedLinks: any[] = [];

    // Create nodes with enhanced data
    treeData.forEach((node, index) => {
      const isImportant = node.status === 'active' || 
        (node.confidence && typeof node.confidence === 'number' && node.confidence > 0.7);
      const isSynthesis = node.type === 'synthesis';
      const isDeadend = node.status === 'failed' || node.status === 'completed';
      
      // Dynamic sizing based on importance
      let nodeSize = 20;
      if (isSynthesis) nodeSize = 35;
      else if (isImportant) nodeSize = 28;
      else if (isDeadend) nodeSize = 15;
      else nodeSize = 22;

      const processedNode = {
        ...node,
        size: nodeSize,
        isImportant,
        isSynthesis,
        isDeadend,
        isActive: node.status === 'active',
        originalIndex: index,
      };
      
      processedNodes.push(processedNode);
      nodeMap.set(node.id, node);
    });

    // Create links between nodes
    treeData.forEach(node => {
      if (node.parent && nodeMap.has(node.parent)) {
        processedLinks.push({
          source: node.parent,
          target: node.id,
          strength: 0.3,
        });
      }
    });

    return { nodes: processedNodes, links: processedLinks };
  }, [treeData]);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Add zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.1, 5])
      .on('zoom', (event) => {
        const { transform } = event;
        setZoomLevel(transform.k);
        svg.select('g.zoom-container').attr('transform', transform);
      });

    svg.call(zoom as any);

    // Create container for zoomable content
    const container = svg.append('g').attr('class', 'zoom-container');

    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id((d: any) => d.id).distance(150))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius((d: any) => d.size + 10));

    // Add organic clustering forces
    const nodeTypes = new Set(nodes.map(n => n.type));
    nodeTypes.forEach(type => {
      const typeNodes = nodes.filter(n => n.type === type);
      if (typeNodes.length > 1) {
        const clusterCenter = d3.forceCenter(
          d3.mean(typeNodes, (d: any) => d.x) || width / 2,
          d3.mean(typeNodes, (d: any) => d.y) || height / 2
        ).strength(0.2);
        simulation.force(`cluster-${type}`, clusterCenter);
      }
    });

    // Add importance-based clustering
    const importantNodes = nodes.filter(n => n.isImportant);
    if (importantNodes.length > 1) {
      const importantCenter = d3.forceCenter(
        d3.mean(importantNodes, (d: any) => d.x) || width / 2,
        d3.mean(importantNodes, (d: any) => d.y) || height / 2
      ).strength(0.4);
      simulation.force("important-cluster", importantCenter);
    }

    // Add active research clustering
    const activeNodes = nodes.filter(n => n.isActive);
    if (activeNodes.length > 1) {
      const activeCenter = d3.forceCenter(
        d3.mean(activeNodes, (d: any) => d.x) || width / 2,
        d3.mean(activeNodes, (d: any) => d.y) || height / 2
      ).strength(0.6);
      simulation.force("active-cluster", activeCenter);
    }

    // Create links
    const link = container.append("g")
      .selectAll("line")
      .data(links)
      .enter().append("line")
      .attr("stroke", "#666")
      .attr("stroke-width", 2)
      .attr("stroke-opacity", 0.3)
      .attr("stroke-dasharray", "5,5");

    // Create nodes
    const node = container.append("g")
      .selectAll("g")
      .data(nodes)
      .enter().append("g")
      .attr("class", "node")
      .attr("data-id", (d: any) => d.id)
      .call(d3.drag<any, any>()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // Add node circles with dynamic styling
    node.append("circle")
      .attr("r", (d: any) => d.size)
      .attr("fill", (d: any) => {
        if (highlightedNodes.has(d.id)) return "#ff9800";
        if (d.isSynthesis) return "#e91e63";
        if (d.isActive) return "#4caf50";
        if (d.isImportant) return "#2196f3";
        if (d.isDeadend) return "#9e9e9e";
        return "#666";
      })
      .attr("stroke", (d: any) => {
        if (highlightedNodes.has(d.id)) return "#ff9800";
        if (d.isSynthesis) return "#e91e63";
        if (d.isActive) return "#4caf50";
        if (d.isImportant) return "#2196f3";
        return "#333";
      })
      .attr("stroke-width", (d: any) => d.isImportant ? 3 : 2)
      .attr("opacity", (d: any) => d.isDeadend ? 0.5 : 1)
      .style("filter", (d: any) => {
        if (highlightedNodes.has(d.id)) return "drop-shadow(0 0 20px rgba(255, 152, 0, 0.8))";
        if (d.isActive) return "drop-shadow(0 0 10px rgba(76, 175, 80, 0.6))";
        if (d.isSynthesis) return "drop-shadow(0 0 15px rgba(233, 30, 99, 0.6))";
        if (d.isImportant) return "drop-shadow(0 0 8px rgba(33, 150, 243, 0.4))";
        return "none";
      })
      .on("mouseover", function(_, d: any) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr("r", d.size * 1.3)
          .style("filter", "drop-shadow(0 0 20px rgba(255, 255, 255, 0.8))");
      })
      .on("mouseout", function(_, d: any) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr("r", d.size)
          .style("filter", (d: any) => {
            if (d.isActive) return "drop-shadow(0 0 10px rgba(76, 175, 80, 0.6))";
            if (d.isSynthesis) return "drop-shadow(0 0 15px rgba(233, 30, 99, 0.6))";
            if (d.isImportant) return "drop-shadow(0 0 8px rgba(33, 150, 243, 0.4))";
            return "none";
          });
      })
      .on("click", function(_, d: any) {
        setSelectedNode(d);
      });

    // Add pulsing animation for active nodes
    node.filter((d: any) => d.isActive)
      .select("circle")
      .style("animation", "pulse 2s infinite")
      .style("animation-timing-function", "ease-in-out");

    // Add node labels
    node.append("text")
      .text((d: any) => d.title.length > 20 ? d.title.substring(0, 20) + "..." : d.title)
      .attr("text-anchor", "middle")
      .attr("dy", (d: any) => d.size + 15)
      .attr("font-size", (d: any) => {
        if (d.isSynthesis) return "12px";
        if (d.isImportant) return "11px";
        return "10px";
      })
      .attr("font-weight", (d: any) => d.isImportant ? "bold" : "normal")
      .attr("fill", (d: any) => {
        if (d.isActive) return "#4caf50";
        if (d.isSynthesis) return "#e91e63";
        if (d.isImportant) return "#2196f3";
        return "#fff";
      })
      .style("pointer-events", "none");

    // Add status indicators
    node.filter((d: any) => d.isActive)
      .append("circle")
      .attr("r", 4)
      .attr("fill", "#4caf50")
      .attr("cx", (d: any) => d.size - 5)
      .attr("cy", (d: any) => -d.size + 5)
      .style("animation", "pulse 1s infinite");

    // Add synthesis indicators
    node.filter((d: any) => d.isSynthesis)
      .append("circle")
      .attr("r", 6)
      .attr("fill", "#e91e63")
      .attr("cx", (d: any) => d.size - 8)
      .attr("cy", (d: any) => -d.size + 8)
      .style("animation", "pulse 1.5s infinite");

    // Update positions on simulation tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node
        .attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    // Cleanup
    return () => {
      simulation.stop();
    };
  }, [nodes, links, width, height]);

  // Function to highlight nodes
  const highlightNodes = (nodeIds: string[]) => {
    setHighlightedNodes(new Set(nodeIds));
    if (onNodeHighlight) {
      onNodeHighlight(nodeIds);
    }
  };

  // Function to reset zoom
  const resetZoom = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg.transition().duration(750).call(
        d3.zoom().transform as any,
        d3.zoomIdentity
      );
    }
  };

  // Function to fit to view
  const fitToView = () => {
    if (svgRef.current && nodes.length > 0) {
      const svg = d3.select(svgRef.current);
      const container = svg.select('g.zoom-container');
      
      // Calculate bounds of all nodes
      const containerNode = container.node() as SVGGElement;
      const bounds = containerNode?.getBBox();
      if (bounds) {
        const fullWidth = width;
        const fullHeight = height;
        const width_ratio = fullWidth / bounds.width;
        const height_ratio = fullHeight / bounds.height;
        const scale = Math.min(width_ratio, height_ratio) * 0.8;
        
        const transform = d3.zoomIdentity
          .translate(fullWidth / 2 - bounds.x * scale - bounds.width * scale / 2, 
                    fullHeight / 2 - bounds.y * scale - bounds.height * scale / 2)
          .scale(scale);
        
        svg.transition().duration(750).call(
          d3.zoom().transform as any,
          transform
        );
      }
    }
  };

  // Function to navigate to specific node
  const navigateToNode = (nodeId: string) => {
    const targetNode = nodes.find(n => n.id === nodeId);
    if (targetNode && svgRef.current) {
      const svg = d3.select(svgRef.current);
      const container = svg.select('g.zoom-container');
      
      // Calculate the node's position in the container
      const nodeElement = container.select(`[data-id="${nodeId}"]`);
      if (nodeElement.node()) {
        const bbox = (nodeElement.node() as SVGGElement).getBBox();
        const centerX = bbox.x + bbox.width / 2;
        const centerY = bbox.y + bbox.height / 2;
        
        // Zoom to the node
        const transform = d3.zoomIdentity
          .translate(width / 2 - centerX * 2, height / 2 - centerY * 2)
          .scale(2);
        
        svg.transition().duration(1000).call(
          d3.zoom().transform as any,
          transform
        );
      }
    }
  };

  return (
    <Box sx={{ width: '100%', height: '100%', position: 'relative' }}>
      {/* Zoom Controls */}
      <Box sx={{
        position: 'absolute',
        top: 10,
        left: 10,
        zIndex: 10,
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
      }}>
        <Box sx={{
          background: 'rgba(0,0,0,0.8)',
          borderRadius: 1,
          padding: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: 0.5,
        }}>
          <button
            onClick={() => {
              if (svgRef.current) {
                const svg = d3.select(svgRef.current);
                svg.transition().duration(300).call(
                  d3.zoom().scaleBy as any,
                  1.2
                );
              }
            }}
            style={{
              background: '#333',
              border: '1px solid #555',
              color: 'white',
              borderRadius: '4px',
              padding: '4px 8px',
              cursor: 'pointer',
              fontSize: '12px',
            }}
          >
            +
          </button>
          <button
            onClick={() => {
              if (svgRef.current) {
                const svg = d3.select(svgRef.current);
                svg.transition().duration(300).call(
                  d3.zoom().scaleBy as any,
                  0.8
                );
              }
            }}
            style={{
              background: '#333',
              border: '1px solid #555',
              color: 'white',
              borderRadius: '4px',
              padding: '4px 8px',
              cursor: 'pointer',
              fontSize: '12px',
            }}
          >
            -
          </button>
          <button
            onClick={resetZoom}
            style={{
              background: '#333',
              border: '1px solid #555',
              color: 'white',
              borderRadius: '4px',
              padding: '4px 8px',
              cursor: 'pointer',
              fontSize: '10px',
            }}
            title="Reset Zoom"
          >
            Reset
          </button>
          <button
            onClick={fitToView}
            style={{
              background: '#333',
              border: '1px solid #555',
              color: 'white',
              borderRadius: '4px',
              padding: '4px 8px',
              cursor: 'pointer',
              fontSize: '10px',
            }}
            title="Fit to View"
          >
            Fit
          </button>
        </Box>
      </Box>

      {/* Zoom Level Indicator */}
      <Box sx={{
        position: 'absolute',
        bottom: 10,
        left: 10,
        background: 'rgba(0,0,0,0.8)',
        color: 'white',
        padding: '4px 8px',
        borderRadius: '4px',
        fontSize: '12px',
      }}>
        {Math.round(zoomLevel * 100)}%
      </Box>

      <svg
        ref={svgRef}
        width={width}
        height={height}
        style={{
          background: 'radial-gradient(circle at center, #1a1a1a 0%, #0a0a0a 100%)',
          borderRadius: '8px',
        }}
      />
      
      {/* Node Details Panel */}
      {selectedNode && (
        <Box
          sx={{
            position: 'absolute',
            top: 20,
            right: 20,
            background: 'rgba(0,0,0,0.9)',
            borderRadius: 2,
            padding: 2,
            maxWidth: 300,
            color: 'white',
            border: '1px solid #333',
          }}
        >
          <Typography variant="h6" sx={{ mb: 1, color: '#4caf50' }}>
            {selectedNode.title}
          </Typography>
          <Typography variant="body2" sx={{ mb: 1, opacity: 0.8 }}>
            {selectedNode.content}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
            <Chip
              label={selectedNode.type.toUpperCase()}
              size="small"
              sx={{ fontSize: '0.7rem' }}
            />
            <Chip
              label={selectedNode.status.toUpperCase()}
              size="small"
              color={selectedNode.status === 'active' ? 'success' : 'default'}
              sx={{ fontSize: '0.7rem' }}
            />
            {selectedNode.confidence && (
              <Chip
                label={`${(typeof selectedNode.confidence === 'number' ? selectedNode.confidence : 0.5) * 100}%`}
                size="small"
                sx={{ fontSize: '0.7rem' }}
              />
            )}
          </Box>
          {selectedNode.status === 'active' && selectedNode.progress !== undefined && (
            <Box sx={{ mb: 1 }}>
              <Typography variant="caption" sx={{ color: '#4caf50' }}>
                Progress: {selectedNode.progress}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={selectedNode.progress}
                sx={{ mt: 0.5, height: 4 }}
              />
            </Box>
          )}
        </Box>
      )}

      {/* CSS for animations */}
      <style>{`
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.7; }
          100% { opacity: 1; }
        }
      `}</style>
    </Box>
  );
};

export default OrganicResearchGraph; 