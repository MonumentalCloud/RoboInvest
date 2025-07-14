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
        
        # Monte Carlo search state tracking
        self.search_state: str = "idle"  # idle, exploring, evaluating, selected, pruned
        self.search_score: Optional[float] = None
        self.search_path: bool = False
        self.monte_carlo_visits: int = 0
        self.monte_carlo_wins: int = 0
        
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
            "result": self.result,
            # Monte Carlo search state
            "searchState": self.search_state,
            "searchScore": self.search_score,
            "searchPath": self.search_path
        }
    
    def set_search_state(self, state: str, score: Optional[float] = None, in_path: bool = False):
        """Update Monte Carlo search state."""
        self.search_state = state
        if score is not None:
            self.search_score = score
        self.search_path = in_path
        self.updated_at = datetime.now()
    
    def update_monte_carlo_stats(self, visit: bool = False, win: bool = False):
        """Update Monte Carlo visit/win statistics."""
        if visit:
            self.monte_carlo_visits += 1
        if win:
            self.monte_carlo_wins += 1
        
        # Update search score based on win rate
        if self.monte_carlo_visits > 0:
            self.search_score = self.monte_carlo_wins / self.monte_carlo_visits
        self.updated_at = datetime.now()

class DecisionTree:
    """Dynamic decision tree for agent reasoning."""
    
    def __init__(self, tree_id: Optional[str] = None, agent_name: str = "Agent", track_name: str = "general"):
        self.id = tree_id or str(uuid.uuid4())
        self.agent_name = agent_name
        self.track_name = track_name
        self.nodes: Dict[str, DecisionNode] = {}
        self.root_id: Optional[str] = None
        self.active_paths: List[List[str]] = []
        self.completed_paths: List[List[str]] = []
        self.best_path: Optional[List[str]] = None
        self.best_confidence = 0.0
        self.max_depth = 10
        self.max_breadth = 5
        self.pruning_threshold = 0.2
        self.research_agent = None
        
        # Try to load existing tree from database
        self._load_from_database()
    
    def _load_from_database(self):
        """Load existing tree from database if it exists."""
        try:
            from core.central_event_bus import central_event_bus
            
            # Check if tree exists in database
            existing_trees = central_event_bus.get_research_trees(agent_name=self.agent_name, track_name=self.track_name)
            
            if existing_trees:
                # Load the most recent tree
                latest_tree = existing_trees[0]
                tree_data = latest_tree["tree_data"]
                
                # Reconstruct tree from saved data
                self.id = latest_tree["tree_id"]
                self.root_id = latest_tree["root_id"]
                
                # Load nodes
                for node_id, node_dict in tree_data.get("nodes", {}).items():
                    node = DecisionNode(
                        node_id=node_id,
                        node_type=NodeType(node_dict.get("type", "hypothesis")),
                        content=node_dict.get("content", ""),
                        data=node_dict.get("data", {}),
                        parent_id=node_dict.get("parent_id")
                    )
                    node.children = node_dict.get("children", [])
                    node.status = NodeStatus(node_dict.get("status", "pending"))
                    node.confidence = node_dict.get("confidence", 0.5)
                    node.result = node_dict.get("result", {})
                    
                    # Load Monte Carlo search state
                    node.search_state = node_dict.get("searchState", "idle")
                    node.search_score = node_dict.get("searchScore")
                    node.search_path = node_dict.get("searchPath", False)
                    node.monte_carlo_visits = node_dict.get("monte_carlo_visits", 0)
                    node.monte_carlo_wins = node_dict.get("monte_carlo_wins", 0)
                    
                    self.nodes[node_id] = node
                
                self.best_path = tree_data.get("best_path")
                self.best_confidence = tree_data.get("best_confidence", 0.0)
                
                logger.info(f"DecisionTree | Loaded existing tree {self.id} with {len(self.nodes)} nodes")
            else:
                logger.info(f"DecisionTree | Creating new tree {self.id} for {self.agent_name}")
                
        except Exception as e:
            logger.error(f"DecisionTree | Failed to load from database: {e}")
            logger.info(f"DecisionTree | Creating new tree {self.id} for {self.agent_name}")
    
    def save_to_database(self):
        """Save current tree state to database."""
        try:
            from core.central_event_bus import central_event_bus
            
            tree_data = self.to_dict()
            central_event_bus.save_research_tree(
                tree_id=self.id,
                agent_name=self.agent_name,
                track_name=self.track_name,
                root_id=self.root_id or "",
                tree_data=tree_data
            )
            
            logger.info(f"DecisionTree | Saved tree {self.id} to database")
            
        except Exception as e:
            logger.error(f"DecisionTree | Failed to save to database: {e}")
    
    def continue_research(self) -> bool:
        """Check if there's ongoing research to continue."""
        if not self.nodes:
            return False
        
        # Check if there are active nodes that need completion
        active_nodes = [node for node in self.nodes.values() 
                       if node.status in [NodeStatus.PENDING, NodeStatus.IN_PROGRESS]]
        
        if active_nodes:
            logger.info(f"DecisionTree | Continuing research with {len(active_nodes)} active nodes")
            return True
        
        # Check if Monte Carlo search was in progress
        mcts_nodes = [node for node in self.nodes.values() 
                     if node.monte_carlo_visits > 0]
        
        if mcts_nodes:
            logger.info(f"DecisionTree | Continuing Monte Carlo search with {len(mcts_nodes)} visited nodes")
            return True
        
        return False
        
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
        
        # Save to database
        self.save_to_database()
        
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
        
        # Save to database periodically (not on every node to avoid excessive writes)
        if len(self.nodes) % 5 == 0:  # Save every 5 nodes
            self.save_to_database()
        
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
    
    async def run_monte_carlo_search(self, iterations: int = 100, exploration_constant: float = 1.414, research_agent=None):
        """Run Monte Carlo Tree Search on the decision tree with research agent integration."""
        logger.info(f"DecisionTree | Starting Monte Carlo search with {iterations} iterations")
        
        if not self.root_id:
            logger.error("DecisionTree | No root node found for MCTS")
            return
        
        # Store research agent for use in simulations
        self.research_agent = research_agent
        
        # Reset all search states
        for node in self.nodes.values():
            node.set_search_state("idle", 0.0, False)
        
        # Set root as exploring
        self.nodes[self.root_id].set_search_state("exploring", 0.0, True)
        
        for i in range(iterations):
            # Selection: Find the best node to expand
            selected_node_id = self._mcts_select(self.root_id, exploration_constant)
            
            if selected_node_id:
                # Expansion: Add new child if possible
                expanded_node_id = self._mcts_expand(selected_node_id)
                
                if expanded_node_id:
                    # Simulation: Run research-based simulation from expanded node
                    simulation_result = await self._mcts_simulate_with_research(expanded_node_id)
                    
                    # Backpropagation: Update statistics along the path
                    self._mcts_backpropagate(expanded_node_id, simulation_result)
                    
                    # Update search states for visualization
                    self._update_search_visualization(selected_node_id, expanded_node_id, simulation_result)
                
                # Broadcast tree update every few iterations
                if i % 10 == 0:
                    await self._broadcast_tree_update()
                    # Save to database every 10 iterations
                    self.save_to_database()
                
                # Small delay to make the search visible
                await asyncio.sleep(0.1)
        
        # Mark best path as selected
        best_path = self.find_best_path()
        if best_path:
            for node_id in best_path:
                if node_id in self.nodes:
                    self.nodes[node_id].set_search_state("selected", self.nodes[node_id].search_score, True)
        
        logger.info(f"DecisionTree | Monte Carlo search completed")
        await self._broadcast_tree_update()
        self.save_to_database()
    
    def _mcts_select(self, node_id: str, exploration_constant: float) -> Optional[str]:
        """Select the best node to expand using UCB1 formula."""
        if node_id not in self.nodes:
            return None
        
        node = self.nodes[node_id]
        
        # If node has unexpanded children, return it
        if node.children:
            unexpanded = [child_id for child_id in node.children 
                         if child_id in self.nodes and self.nodes[child_id].monte_carlo_visits == 0]
            if unexpanded:
                return node_id
        
        # If no unexpanded children, select best child using UCB1
        if node.children:
            best_child = None
            best_score = float('-inf')
            
            for child_id in node.children:
                if child_id in self.nodes:
                    child = self.nodes[child_id]
                    if child.monte_carlo_visits > 0:
                        # UCB1 formula: exploitation + exploration
                        exploitation = child.search_score or 0.0
                        exploration = exploration_constant * (node.monte_carlo_visits ** 0.5) / (child.monte_carlo_visits ** 0.5)
                        ucb_score = exploitation + exploration
                        
                        if ucb_score > best_score:
                            best_score = ucb_score
                            best_child = child_id
            
            if best_child:
                return self._mcts_select(best_child, exploration_constant)
        
        return node_id
    
    def _mcts_expand(self, node_id: str) -> Optional[str]:
        """Expand a new child node for the selected node."""
        if node_id not in self.nodes:
            return None
        
        node = self.nodes[node_id]
        
        # Create a new hypothesis node as child
        new_node_id = self.add_node(
            parent_id=node_id,
            node_type=NodeType.HYPOTHESIS,
            content=f"Hypothesis {len(node.children) + 1}",
            data={"mcts_expanded": True}
        )
        
        if new_node_id:
            # Set initial search state
            self.nodes[new_node_id].set_search_state("exploring", 0.0, True)
            logger.debug(f"DecisionTree | MCTS expanded node: {new_node_id}")
        
        return new_node_id
    
    async def _mcts_simulate(self, node_id: str) -> float:
        """Simulate a random playout from the given node."""
        if node_id not in self.nodes:
            return 0.0
        
        # Simple simulation: random walk with confidence scoring
        current_id = node_id
        simulation_depth = 0
        max_simulation_depth = 5
        
        while simulation_depth < max_simulation_depth:
            node = self.nodes[current_id]
            
            # Update simulation state
            node.set_search_state("evaluating", node.confidence, True)
            
            # Simulate some processing time
            await asyncio.sleep(0.05)
            
            # Random outcome based on confidence
            import random
            if random.random() < node.confidence:
                # Success - continue to children
                if node.children:
                    current_id = random.choice(node.children)
                    simulation_depth += 1
                else:
                    # Leaf node reached
                    return node.confidence
            else:
                # Failure - return current confidence
                return node.confidence * 0.5
        
        # Max depth reached
        return 0.3
    
    async def _mcts_simulate_with_research(self, node_id: str) -> float:
        """Simulate a research-based playout from the given node."""
        if node_id not in self.nodes:
            return 0.0
        
        node = self.nodes[node_id]
        
        # Update simulation state
        node.set_search_state("evaluating", node.confidence, True)
        
        # Execute the research task
        if self.research_agent:
            try:
                result = await self.research_agent.execute_task(node.data)
                node.result = result
                node.status = NodeStatus.COMPLETED
                node.confidence = result.get("confidence", 0.5)
                logger.info(f"DecisionTree | MCTS simulated research for {node_id}: {node.content}")
                return node.confidence
            except Exception as e:
                logger.error(f"DecisionTree | MCTS research simulation failed for {node_id}: {e}")
                node.status = NodeStatus.FAILED
                node.result = {"error": str(e)}
                return 0.0 # Indicate failure
        else:
            logger.warning(f"DecisionTree | No research_agent defined for MCTS simulation of {node_id}")
            return 0.5 # Default confidence if no agent
    
    def _mcts_backpropagate(self, node_id: str, simulation_result: float):
        """Backpropagate simulation results up the tree."""
        current_id = node_id
        
        while current_id and current_id in self.nodes:
            node = self.nodes[current_id]
            
            # Update Monte Carlo statistics
            node.update_monte_carlo_stats(visit=True, win=(simulation_result > 0.5))
            
            # Move to parent
            current_id = node.parent_id
    
    def _update_search_visualization(self, selected_id: str, expanded_id: str, simulation_result: float):
        """Update search states for real-time visualization."""
        # Mark selected node as exploring
        if selected_id in self.nodes:
            self.nodes[selected_id].set_search_state("exploring", self.nodes[selected_id].search_score, True)
        
        # Mark expanded node as evaluating
        if expanded_id in self.nodes:
            self.nodes[expanded_id].set_search_state("evaluating", simulation_result, True)
    
    async def _broadcast_tree_update(self):
        """Broadcast tree update to frontend via WebSocket."""
        try:
            from backend.api.fastapi_app import manager
            tree_data = self.to_dict()
            
            # Convert to frontend format
            tree_nodes = []
            for node_id, node_dict in tree_data["nodes"].items():
                tree_nodes.append({
                    "id": node_dict["id"],
                    "type": node_dict["type"],
                    "title": node_dict["content"],
                    "content": node_dict["content"],
                    "status": node_dict["status"],
                    "parent": node_dict["parent_id"],
                    "timestamp": node_dict["created_at"],
                    "metadata": node_dict["data"],
                    "searchState": node_dict.get("searchState", "idle"),
                    "searchScore": node_dict.get("searchScore"),
                    "searchPath": node_dict.get("searchPath", False)
                })
            
            await manager.broadcast({
                "type": "tree_update",
                "action": "monte_carlo_update",
                "tree": tree_nodes,
                "iteration": len([n for n in self.nodes.values() if n.monte_carlo_visits > 0])
            })
            
        except Exception as e:
            logger.error(f"DecisionTree | Failed to broadcast tree update: {e}") 