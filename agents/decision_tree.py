"""
Decision Tree Framework for Autonomous Agent Reasoning
Allows agents to expand logical trees and explore multiple paths to find competitive edges.
"""

import json
import uuid
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime
from enum import Enum
import asyncio
from utils.logger import logger  # type: ignore

class NodeType(Enum):
    """Types of decision tree nodes."""
    ROOT = "root"
    HYPOTHESIS = "hypothesis" 
    RESEARCH = "research"
    ANALYSIS = "analysis"
    VALIDATION = "validation"
    DECISION = "decision"
    ACTION = "action"
    OUTCOME = "outcome"

class NodeStatus(Enum):
    """Status of tree nodes."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PRUNED = "pruned"

class DecisionNode:
    """Individual node in the decision tree."""
    
    def __init__(self, 
                 node_id: Optional[str] = None,
                 node_type: NodeType = NodeType.HYPOTHESIS,
                 content: str = "",
                 data: Optional[Dict[str, Any]] = None,
                 parent_id: Optional[str] = None):
        self.id = node_id or str(uuid.uuid4())
        self.type = node_type
        self.content = content
        self.data = data or {}
        self.parent_id = parent_id
        self.children: List[str] = []
        self.status = NodeStatus.PENDING
        self.confidence = 0.5
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.executor: Optional[Callable] = None
        self.result: Dict[str, Any] = {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "data": self.data,
            "parent_id": self.parent_id,
            "children": self.children,
            "status": self.status.value,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "result": self.result
        }

class DecisionTree:
    """Dynamic decision tree for agent reasoning."""
    
    def __init__(self, tree_id: Optional[str] = None, agent_name: str = "Agent"):
        self.id = tree_id or str(uuid.uuid4())
        self.agent_name = agent_name
        self.nodes: Dict[str, DecisionNode] = {}
        self.root_id: Optional[str] = None
        self.active_paths: List[List[str]] = []
        self.completed_paths: List[List[str]] = []
        self.best_path: Optional[List[str]] = None
        self.best_confidence = 0.0
        self.max_depth = 10
        self.max_breadth = 5
        self.pruning_threshold = 0.2
        
    def create_root(self, content: str, data: Optional[Dict[str, Any]] = None) -> str:
        """Create root node of the decision tree."""
        root = DecisionNode(
            node_type=NodeType.ROOT,
            content=content,
            data=data or {}
        )
        self.nodes[root.id] = root
        self.root_id = root.id
        logger.info(f"DecisionTree | {self.agent_name} created root: {content}")
        return root.id
        
    def add_node(self, 
                 parent_id: str,
                 node_type: NodeType,
                 content: str,
                 data: Optional[Dict[str, Any]] = None,
                 executor: Optional[Callable] = None) -> Optional[str]:
        """Add a new node to the tree."""
        
        if parent_id not in self.nodes:
            logger.error(f"DecisionTree | Parent node {parent_id} not found")
            return None
            
        parent = self.nodes[parent_id]
        
        # Check breadth limit
        if len(parent.children) >= self.max_breadth:
            logger.warning(f"DecisionTree | Max breadth {self.max_breadth} reached for node {parent_id}")
            return None
            
        # Check depth limit
        depth = self._get_depth(parent_id)
        if depth >= self.max_depth:
            logger.warning(f"DecisionTree | Max depth {self.max_depth} reached")
            return None
            
        new_node = DecisionNode(
            node_type=node_type,
            content=content,
            data=data or {},
            parent_id=parent_id
        )
        
        if executor:
            new_node.executor = executor
            
        self.nodes[new_node.id] = new_node
        parent.children.append(new_node.id)
        parent.updated_at = datetime.now()
        
        logger.info(f"DecisionTree | {self.agent_name} added {node_type.value}: {content}")
        return new_node.id
    
    def expand_hypotheses(self, parent_id: str, hypotheses: List[str]) -> List[str]:
        """Expand multiple hypotheses from a parent node."""
        node_ids = []
        
        for hypothesis in hypotheses:
            node_id = self.add_node(
                parent_id=parent_id,
                node_type=NodeType.HYPOTHESIS,
                content=hypothesis,
                data={"exploration_priority": len(hypotheses) - len(node_ids)}
            )
            if node_id:
                node_ids.append(node_id)
                
        return node_ids
    
    def expand_research_paths(self, hypothesis_id: str, research_tasks: List[Dict[str, Any]]) -> List[str]:
        """Expand research paths from a hypothesis."""
        node_ids = []
        
        for task in research_tasks:
            node_id = self.add_node(
                parent_id=hypothesis_id,
                node_type=NodeType.RESEARCH,
                content=task.get("description", "Research task"),
                data=task,
                executor=task.get("executor")
            )
            if node_id:
                node_ids.append(node_id)
                
        return node_ids
    
    async def execute_node(self, node_id: str) -> Dict[str, Any]:
        """Execute a specific node if it has an executor."""
        
        if node_id not in self.nodes:
            return {"error": "Node not found"}
            
        node = self.nodes[node_id]
        
        if not node.executor:
            return {"error": "No executor defined for node"}
            
        node.status = NodeStatus.IN_PROGRESS
        node.updated_at = datetime.now()
        
        try:
            if asyncio.iscoroutinefunction(node.executor):
                result = await node.executor(node.data)
            else:
                result = node.executor(node.data)
                
            node.result = result
            node.status = NodeStatus.COMPLETED
            
            # Update confidence based on result quality
            if isinstance(result, dict):
                node.confidence = result.get("confidence", 0.5)
                
            logger.info(f"DecisionTree | Executed node {node_id}: {node.content}")
            return result
            
        except Exception as e:
            logger.error(f"DecisionTree | Execution failed for {node_id}: {e}")
            node.status = NodeStatus.FAILED
            node.result = {"error": str(e)}
            return {"error": str(e)}
        finally:
            node.updated_at = datetime.now()
    
    async def execute_parallel_branches(self, node_ids: List[str]) -> List[Dict[str, Any]]:
        """Execute multiple nodes in parallel."""
        tasks = []
        
        for node_id in node_ids:
            if node_id in self.nodes and self.nodes[node_id].executor:
                tasks.append(self.execute_node(node_id))
        
        if not tasks:
            return []
            
        logger.info(f"DecisionTree | Executing {len(tasks)} parallel branches")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error dicts
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({"error": str(result)})
            else:
                processed_results.append(result)
                
        return processed_results
    
    def prune_low_confidence_paths(self):
        """Remove paths with confidence below threshold."""
        pruned_count = 0
        
        for node_id, node in list(self.nodes.items()):
            if (node.confidence < self.pruning_threshold and 
                node.type != NodeType.ROOT and
                node.status == NodeStatus.COMPLETED):
                
                self._prune_subtree(node_id)
                pruned_count += 1
                
        if pruned_count > 0:
            logger.info(f"DecisionTree | Pruned {pruned_count} low-confidence branches")
    
    def _prune_subtree(self, node_id: str):
        """Recursively prune a subtree."""
        if node_id not in self.nodes:
            return
            
        node = self.nodes[node_id]
        
        # Prune all children first
        for child_id in node.children.copy():
            self._prune_subtree(child_id)
            
        # Remove from parent's children list
        if node.parent_id and node.parent_id in self.nodes:
            parent = self.nodes[node.parent_id]
            if node_id in parent.children:
                parent.children.remove(node_id)
                parent.updated_at = datetime.now()
        
        # Mark as pruned and remove from active nodes
        node.status = NodeStatus.PRUNED
        logger.debug(f"DecisionTree | Pruned node: {node.content}")
    
    def find_best_path(self) -> Optional[List[str]]:
        """Find the highest confidence path from root to a decision."""
        if not self.root_id:
            return None
            
        best_path = None
        best_score = 0.0
        
        # Find all paths to decision nodes
        decision_paths = self._find_paths_to_type(NodeType.DECISION)
        
        for path in decision_paths:
            score = self._calculate_path_confidence(path)
            if score > best_score:
                best_score = score
                best_path = path
                
        self.best_path = best_path
        self.best_confidence = best_score
        
        if best_path:
            logger.info(f"DecisionTree | Best path confidence: {best_score:.3f}")
            
        return best_path
    
    def _find_paths_to_type(self, target_type: NodeType) -> List[List[str]]:
        """Find all paths from root to nodes of specific type."""
        paths = []
        
        if not self.root_id:
            return paths
            
        def dfs(node_id: str, current_path: List[str]):
            current_path.append(node_id)
            node = self.nodes[node_id]
            
            if node.type == target_type and node.status == NodeStatus.COMPLETED:
                paths.append(current_path.copy())
            
            for child_id in node.children:
                if child_id in self.nodes and self.nodes[child_id].status != NodeStatus.PRUNED:
                    dfs(child_id, current_path)
                    
            current_path.pop()
        
        dfs(self.root_id, [])
        return paths
    
    def _calculate_path_confidence(self, path: List[str]) -> float:
        """Calculate aggregate confidence for a path."""
        if not path:
            return 0.0
            
        confidences = []
        for node_id in path:
            if node_id in self.nodes:
                confidences.append(self.nodes[node_id].confidence)
                
        if not confidences:
            return 0.0
            
        # Weighted average with recent nodes having more influence
        weights = [1.0 + i * 0.1 for i in range(len(confidences))]
        weighted_sum = sum(c * w for c, w in zip(confidences, weights))
        weight_sum = sum(weights)
        
        return weighted_sum / weight_sum if weight_sum > 0 else 0.0
    
    def _get_depth(self, node_id: str) -> int:
        """Get depth of a node from root."""
        if not self.root_id or node_id not in self.nodes:
            return 0
            
        depth = 0
        current_id = node_id
        
        while current_id and current_id != self.root_id:
            node = self.nodes.get(current_id)
            if not node or not node.parent_id:
                break
            current_id = node.parent_id
            depth += 1
            
        return depth
    
    def get_active_leaves(self) -> List[str]:
        """Get all leaf nodes that are active (not completed/failed/pruned)."""
        leaves = []
        
        for node_id, node in self.nodes.items():
            if (not node.children and 
                node.status in [NodeStatus.PENDING, NodeStatus.IN_PROGRESS]):
                leaves.append(node_id)
                
        return leaves
    
    def get_summary(self) -> Dict[str, Any]:
        """Get tree summary for logging/debugging."""
        total_nodes = len(self.nodes)
        by_status = {}
        by_type = {}
        
        for node in self.nodes.values():
            by_status[node.status.value] = by_status.get(node.status.value, 0) + 1
            by_type[node.type.value] = by_type.get(node.type.value, 0) + 1
            
        return {
            "tree_id": self.id,
            "agent_name": self.agent_name,
            "total_nodes": total_nodes,
            "by_status": by_status,
            "by_type": by_type,
            "best_confidence": self.best_confidence,
            "active_leaves": len(self.get_active_leaves())
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire tree to dictionary for serialization."""
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "root_id": self.root_id,
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "best_path": self.best_path,
            "best_confidence": self.best_confidence,
            "summary": self.get_summary()
        } 