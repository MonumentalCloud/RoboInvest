"""
Research Graph Manager Agent

This agent analyzes the research graph to:
1. Identify similar/relevant research nodes
2. Detect patterns across different research areas
3. Suggest synthesis opportunities
4. Create synthesis nodes that combine insights
5. Identify converging research threads
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid

from core.openai_manager import openai_manager
from core.central_event_bus import central_event_bus, EventType, EventPriority, create_event

logger = logging.getLogger(__name__)

class SynthesisType(Enum):
    """Types of synthesis that can be created"""
    PATTERN_CONVERGENCE = "pattern_convergence"
    EVIDENCE_AGGREGATION = "evidence_aggregation"
    HYPOTHESIS_REFINEMENT = "hypothesis_refinement"
    PLAY_OPPORTUNITY = "play_opportunity"
    RISK_ASSESSMENT = "risk_assessment"

@dataclass
class ResearchNode:
    """Represents a research node in the graph"""
    id: str
    type: str
    title: str
    content: str
    status: str
    confidence: Optional[float]
    parent: Optional[str]
    children: List[str]
    metadata: Dict[str, Any]
    timestamp: str
    research_track: Optional[str] = None

@dataclass
class SynthesisOpportunity:
    """Represents a potential synthesis opportunity"""
    id: str
    type: SynthesisType
    title: str
    description: str
    source_nodes: List[str]
    confidence: float
    reasoning: str
    suggested_actions: List[str]
    created_at: str

@dataclass
class PatternMatch:
    """Represents a pattern match across research nodes"""
    pattern_type: str
    matched_nodes: List[str]
    confidence: float
    description: str
    implications: List[str]

class ResearchGraphManager:
    """Manages and analyzes the research graph for patterns and synthesis opportunities"""
    
    def __init__(self):
        self.synthesis_opportunities: List[SynthesisOpportunity] = []
        self.pattern_matches: List[PatternMatch] = []
        self.analyzed_nodes: Set[str] = set()
        
    def analyze_research_graph(self, research_nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the entire research graph for patterns and synthesis opportunities"""
        try:
            logger.info(f"🔍 Analyzing research graph with {len(research_nodes)} nodes")
            
            # Convert to ResearchNode objects
            nodes = [self._dict_to_research_node(node) for node in research_nodes]
            
            # Find similar nodes
            similar_groups = self._find_similar_nodes(nodes)
            
            # Detect patterns
            patterns = self._detect_patterns(nodes)
            
            # Find synthesis opportunities
            synthesis_ops = self._find_synthesis_opportunities(nodes, similar_groups, patterns)
            
            # Create synthesis nodes
            synthesis_nodes = self._create_synthesis_nodes(synthesis_ops, nodes)
            
            # Update central event bus
            self._emit_analysis_results(similar_groups, patterns, synthesis_ops)
            
            return {
                "similar_groups": similar_groups,
                "patterns": patterns,
                "synthesis_opportunities": synthesis_ops,
                "synthesis_nodes": synthesis_nodes,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze research graph: {e}")
            return {"error": str(e)}
    
    def _dict_to_research_node(self, node_dict: Dict[str, Any]) -> ResearchNode:
        """Convert dictionary to ResearchNode object"""
        return ResearchNode(
            id=node_dict.get("id", ""),
            type=node_dict.get("type", "unknown"),
            title=node_dict.get("title", ""),
            content=node_dict.get("content", ""),
            status=node_dict.get("status", "pending"),
            confidence=node_dict.get("confidence"),
            parent=node_dict.get("parent"),
            children=node_dict.get("children", []),
            metadata=node_dict.get("metadata", {}),
            timestamp=node_dict.get("timestamp", ""),
            research_track=node_dict.get("research_track")
        )
    
    def _find_similar_nodes(self, nodes: List[ResearchNode]) -> List[List[ResearchNode]]:
        """Find groups of similar research nodes"""
        similar_groups = []
        processed = set()
        
        for i, node1 in enumerate(nodes):
            if node1.id in processed:
                continue
                
            similar_group = [node1]
            processed.add(node1.id)
            
            for j, node2 in enumerate(nodes[i+1:], i+1):
                if node2.id in processed:
                    continue
                    
                if self._are_nodes_similar(node1, node2):
                    similar_group.append(node2)
                    processed.add(node2.id)
            
            if len(similar_group) > 1:
                similar_groups.append(similar_group)
        
        logger.info(f"Found {len(similar_groups)} groups of similar nodes")
        return similar_groups
    
    def _are_nodes_similar(self, node1: ResearchNode, node2: ResearchNode) -> bool:
        """Check if two nodes are similar based on content and type"""
        # Check type similarity
        if node1.type == node2.type:
            return True
        
        # Check content similarity using keywords
        content1 = (node1.title + " " + node1.content).lower()
        content2 = (node2.title + " " + node2.content).lower()
        
        # Extract key terms
        key_terms1 = set(content1.split())
        key_terms2 = set(content2.split())
        
        # Calculate Jaccard similarity
        intersection = len(key_terms1.intersection(key_terms2))
        union = len(key_terms1.union(key_terms2))
        
        if union == 0:
            return False
            
        similarity = intersection / union
        return similarity > 0.3  # 30% similarity threshold
    
    def _detect_patterns(self, nodes: List[ResearchNode]) -> List[PatternMatch]:
        """Detect patterns across research nodes"""
        patterns = []
        
        # Pattern 1: High confidence nodes with similar themes
        high_conf_nodes = [n for n in nodes if n.confidence and isinstance(n.confidence, (int, float)) and n.confidence > 0.7]
        if len(high_conf_nodes) >= 2:
            pattern = self._detect_high_confidence_pattern(high_conf_nodes)
            if pattern:
                patterns.append(pattern)
        
        # Pattern 2: Active research paths
        active_nodes = [n for n in nodes if n.status == "active"]
        if len(active_nodes) >= 2:
            pattern = self._detect_active_research_pattern(active_nodes)
            if pattern:
                patterns.append(pattern)
        
        # Pattern 3: Cross-track connections
        cross_track_pattern = self._detect_cross_track_pattern(nodes)
        if cross_track_pattern:
            patterns.append(cross_track_pattern)
        
        logger.info(f"Detected {len(patterns)} patterns")
        return patterns
    
    def _detect_high_confidence_pattern(self, nodes: List[ResearchNode]) -> Optional[PatternMatch]:
        """Detect pattern among high confidence nodes"""
        if len(nodes) < 2:
            return None
            
        # Group by research track
        track_groups = {}
        for node in nodes:
            track = node.research_track or "unknown"
            if track not in track_groups:
                track_groups[track] = []
            track_groups[track].append(node)
        
        # Find tracks with multiple high confidence nodes
        converging_tracks = {track: nodes for track, nodes in track_groups.items() if len(nodes) >= 2}
        
        if converging_tracks:
            track_names = list(converging_tracks.keys())
            return PatternMatch(
                pattern_type="high_confidence_convergence",
                matched_nodes=[n.id for nodes in converging_tracks.values() for n in nodes],
                confidence=0.8,
                description=f"High confidence research converging in tracks: {', '.join(track_names)}",
                implications=[
                    "Strong evidence building in multiple areas",
                    "Potential for cross-validation",
                    "Ready for synthesis and play generation"
                ]
            )
        
        return None
    
    def _detect_active_research_pattern(self, nodes: List[ResearchNode]) -> Optional[PatternMatch]:
        """Detect pattern among active research nodes"""
        if len(nodes) < 2:
            return None
            
        # Check if active nodes are connected
        connected_groups = self._find_connected_groups(nodes)
        
        if len(connected_groups) > 0:
            largest_group = max(connected_groups, key=len)
            return PatternMatch(
                pattern_type="active_research_cluster",
                matched_nodes=[n.id for n in largest_group],
                confidence=0.7,
                description=f"Active research cluster with {len(largest_group)} connected nodes",
                implications=[
                    "Research momentum building",
                    "Focus area for continued investigation",
                    "Potential breakthrough opportunity"
                ]
            )
        
        return None
    
    def _detect_cross_track_pattern(self, nodes: List[ResearchNode]) -> Optional[PatternMatch]:
        """Detect patterns that cross research tracks"""
        # Find nodes that reference multiple tracks or have cross-track connections
        cross_track_nodes = []
        
        for node in nodes:
            content = (node.title + " " + node.content).lower()
            track_mentions = []
            
            tracks = ["alpha", "market", "sentiment", "technical", "fundamental", "risk"]
            for track in tracks:
                if track in content:
                    track_mentions.append(track)
            
            if len(track_mentions) >= 2:
                cross_track_nodes.append(node)
        
        if len(cross_track_nodes) >= 2:
            return PatternMatch(
                pattern_type="cross_track_synthesis",
                matched_nodes=[n.id for n in cross_track_nodes],
                confidence=0.6,
                description=f"Cross-track synthesis opportunities with {len(cross_track_nodes)} nodes",
                implications=[
                    "Multi-disciplinary insights emerging",
                    "Potential for comprehensive analysis",
                    "Synthesis nodes needed to connect insights"
                ]
            )
        
        return None
    
    def _find_connected_groups(self, nodes: List[ResearchNode]) -> List[List[ResearchNode]]:
        """Find groups of connected nodes"""
        node_map = {node.id: node for node in nodes}
        visited = set()
        groups = []
        
        for node in nodes:
            if node.id in visited:
                continue
                
            group = []
            self._dfs_connected(node, node_map, visited, group)
            if len(group) > 1:
                groups.append(group)
        
        return groups
    
    def _dfs_connected(self, node: ResearchNode, node_map: Dict[str, ResearchNode], 
                      visited: Set[str], group: List[ResearchNode]):
        """Depth-first search to find connected nodes"""
        if node.id in visited:
            return
            
        visited.add(node.id)
        group.append(node)
        
        # Check children
        for child_id in node.children:
            if child_id in node_map:
                self._dfs_connected(node_map[child_id], node_map, visited, group)
        
        # Check parent
        if node.parent and node.parent in node_map:
            self._dfs_connected(node_map[node.parent], node_map, visited, group)
    
    def _find_synthesis_opportunities(self, nodes: List[ResearchNode], 
                                    similar_groups: List[List[ResearchNode]], 
                                    patterns: List[PatternMatch]) -> List[SynthesisOpportunity]:
        """Find opportunities to create synthesis nodes"""
        opportunities = []
        
        # Opportunity 1: Synthesize similar nodes
        for group in similar_groups:
            if len(group) >= 2:
                opp = self._create_similarity_synthesis(group)
                opportunities.append(opp)
        
        # Opportunity 2: Synthesize pattern matches
        for pattern in patterns:
            if pattern.pattern_type == "high_confidence_convergence":
                opp = self._create_convergence_synthesis(pattern, nodes)
                opportunities.append(opp)
        
        # Opportunity 3: Synthesize cross-track insights
        cross_track_pattern = next((p for p in patterns if p.pattern_type == "cross_track_synthesis"), None)
        if cross_track_pattern:
            opp = self._create_cross_track_synthesis(cross_track_pattern, nodes)
            opportunities.append(opp)
        
        logger.info(f"Found {len(opportunities)} synthesis opportunities")
        return opportunities
    
    def _create_similarity_synthesis(self, group: List[ResearchNode]) -> SynthesisOpportunity:
        """Create synthesis opportunity from similar nodes"""
        return SynthesisOpportunity(
            id=str(uuid.uuid4()),
            type=SynthesisType.EVIDENCE_AGGREGATION,
            title=f"Synthesize {len(group)} Similar {group[0].type.title()} Nodes",
            description=f"Combine insights from {len(group)} similar research nodes",
            source_nodes=[n.id for n in group],
            confidence=0.7,
            reasoning="Multiple similar findings suggest strong evidence",
            suggested_actions=[
                "Create synthesis node combining key insights",
                "Validate findings across multiple sources",
                "Generate hypothesis based on aggregated evidence"
            ],
            created_at=datetime.now().isoformat()
        )
    
    def _create_convergence_synthesis(self, pattern: PatternMatch, nodes: List[ResearchNode]) -> SynthesisOpportunity:
        """Create synthesis opportunity from converging high-confidence nodes"""
        pattern_nodes = [n for n in nodes if n.id in pattern.matched_nodes]
        
        return SynthesisOpportunity(
            id=str(uuid.uuid4()),
            type=SynthesisType.PLAY_OPPORTUNITY,
            title="High Confidence Research Convergence",
            description="Multiple high-confidence findings converging on opportunity",
            source_nodes=pattern.matched_nodes,
            confidence=pattern.confidence,
            reasoning="High confidence across multiple research areas suggests strong play opportunity",
            suggested_actions=[
                "Generate play hypothesis",
                "Assess risk-reward profile",
                "Plan execution strategy"
            ],
            created_at=datetime.now().isoformat()
        )
    
    def _create_cross_track_synthesis(self, pattern: PatternMatch, nodes: List[ResearchNode]) -> SynthesisOpportunity:
        """Create synthesis opportunity from cross-track insights"""
        return SynthesisOpportunity(
            id=str(uuid.uuid4()),
            type=SynthesisType.PATTERN_CONVERGENCE,
            title="Cross-Track Insight Synthesis",
            description="Multi-disciplinary insights ready for synthesis",
            source_nodes=pattern.matched_nodes,
            confidence=pattern.confidence,
            reasoning="Cross-track insights provide comprehensive view",
            suggested_actions=[
                "Create comprehensive synthesis node",
                "Identify key themes across tracks",
                "Generate unified hypothesis"
            ],
            created_at=datetime.now().isoformat()
        )
    
    def _create_synthesis_nodes(self, opportunities: List[SynthesisOpportunity], 
                              nodes: List[ResearchNode]) -> List[Dict[str, Any]]:
        """Create actual synthesis nodes from opportunities"""
        synthesis_nodes = []
        
        for opp in opportunities:
            if opp.confidence > 0.6:  # Only create high-confidence synthesis
                synthesis_node = self._generate_synthesis_node(opp, nodes)
                synthesis_nodes.append(synthesis_node)
        
        logger.info(f"Created {len(synthesis_nodes)} synthesis nodes")
        return synthesis_nodes
    
    def _generate_synthesis_node(self, opportunity: SynthesisOpportunity, 
                               nodes: List[ResearchNode]) -> Dict[str, Any]:
        """Generate a synthesis node using AI"""
        try:
            # Get source node details
            source_nodes = [n for n in nodes if n.id in opportunity.source_nodes]
            source_summaries = [f"{n.type}: {n.title}" for n in source_nodes]
            
            prompt = f"""
            Create a synthesis node that combines insights from the following research nodes:
            
            Source Nodes:
            {chr(10).join(f"- {summary}" for summary in source_summaries)}
            
            Synthesis Type: {opportunity.type.value}
            Description: {opportunity.description}
            Reasoning: {opportunity.reasoning}
            
            Generate a synthesis node with:
            1. A clear title that captures the synthesized insight
            2. Detailed content explaining the synthesis
            3. Confidence level based on source evidence
            4. Suggested next actions
            
            Return as JSON with fields: title, content, confidence, suggested_actions
            """
            
            response = openai_manager.chat_completion([{ 'role': 'user', 'content': prompt }], temperature=0.3)
            
            try:
                synthesis_data = json.loads(response["content"])
                return {
                    "id": opportunity.id,
                    "type": "synthesis",
                    "title": synthesis_data.get("title", opportunity.title),
                    "content": synthesis_data.get("content", opportunity.description),
                    "status": "pending",
                    "confidence": synthesis_data.get("confidence", opportunity.confidence),
                    "parent": None,
                    "children": [],
                    "metadata": {
                        "synthesis_type": opportunity.type.value,
                        "source_nodes": opportunity.source_nodes,
                        "suggested_actions": synthesis_data.get("suggested_actions", opportunity.suggested_actions)
                    },
                    "timestamp": datetime.now().isoformat(),
                    "research_track": "synthesis"
                }
            except json.JSONDecodeError:
                # Fallback if AI response isn't valid JSON
                return {
                    "id": opportunity.id,
                    "type": "synthesis",
                    "title": opportunity.title,
                    "content": opportunity.description,
                    "status": "pending",
                    "confidence": opportunity.confidence,
                    "parent": None,
                    "children": [],
                    "metadata": {
                        "synthesis_type": opportunity.type.value,
                        "source_nodes": opportunity.source_nodes,
                        "suggested_actions": opportunity.suggested_actions
                    },
                    "timestamp": datetime.now().isoformat(),
                    "research_track": "synthesis"
                }
                
        except Exception as e:
            logger.error(f"Failed to generate synthesis node: {e}")
            return {"error": str(e)}
    
    def _emit_analysis_results(self, similar_groups: List[List[ResearchNode]], 
                             patterns: List[PatternMatch], 
                             opportunities: List[SynthesisOpportunity]):
        """Emit analysis results to the central event bus"""
        try:
            # Emit pattern detection events
            for pattern in patterns:
                event = create_event(
                    event_type=EventType.RESEARCH,
                    source="research_graph_manager",
                    title=f"Pattern Detected: {pattern.pattern_type}",
                    message=pattern.description,
                    priority=EventPriority.MEDIUM,
                    metadata={
                        "pattern_type": pattern.pattern_type,
                        "matched_nodes": pattern.matched_nodes,
                        "confidence": pattern.confidence,
                        "implications": pattern.implications
                    },
                    tags=["pattern", "research", "synthesis"]
                )
                central_event_bus.emit_event(event)
            
            # Emit synthesis opportunities
            for opp in opportunities:
                event = create_event(
                    event_type=EventType.RESEARCH,
                    source="research_graph_manager",
                    title=f"Synthesis Opportunity: {opp.title}",
                    message=opp.description,
                    priority=EventPriority.HIGH,
                    metadata={
                        "synthesis_type": opp.type.value,
                        "source_nodes": opp.source_nodes,
                        "confidence": opp.confidence,
                        "suggested_actions": opp.suggested_actions
                    },
                    tags=["synthesis", "opportunity", "research"]
                )
                central_event_bus.emit_event(event)
                
        except Exception as e:
            logger.error(f"Failed to emit analysis results: {e}")

# Global instance
research_graph_manager = ResearchGraphManager() 