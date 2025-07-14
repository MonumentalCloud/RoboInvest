"""
Intelligent Memory Manager

LLM-based memory management system that:
- Analyzes and scores experience importance
- Clusters similar experiences and removes duplicates
- Optimizes memory retention based on system usage patterns
- Provides intelligent pruning recommendations
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
import re

from core.config import config
from core.openai_manager import openai_manager
from core.central_experience_db import CentralExperienceDB, Experience, ExperienceType, MemoryTier
from utils.logger import logger


class PruningStrategy(Enum):
    """Pruning strategies for different types of content"""
    AGGRESSIVE = "aggressive"    # Remove quickly, keep only high-value
    MODERATE = "moderate"        # Balanced retention
    CONSERVATIVE = "conservative"  # Keep longer, minimal pruning


@dataclass
class MemoryCluster:
    """Represents a cluster of similar experiences"""
    cluster_id: str
    experiences: List[Experience]
    centroid_content: str
    representative_experience: Experience
    cluster_score: float
    should_consolidate: bool


@dataclass
class PruningRecommendation:
    """LLM-based pruning recommendation"""
    experience_id: str
    action: str  # "keep", "downgrade", "prune", "consolidate"
    reasoning: str
    confidence: float
    suggested_retention_days: int


class IntelligentMemoryManager:
    """Intelligent memory management with LLM-based analysis"""
    
    def __init__(self, experience_db: CentralExperienceDB):
        self.experience_db = experience_db
        self.pruning_strategies = self._setup_pruning_strategies()
        self.clustering_threshold = 0.7
        self.min_cluster_size = 2
        
        logger.info("🧠 Intelligent Memory Manager initialized")
    
    def _setup_pruning_strategies(self) -> Dict[ExperienceType, PruningStrategy]:
        """Setup pruning strategies for different experience types"""
        return {
            ExperienceType.TRADE_EXECUTION: PruningStrategy.CONSERVATIVE,
            ExperienceType.MARKET_INSIGHT: PruningStrategy.MODERATE,
            ExperienceType.AGENT_LEARNING: PruningStrategy.CONSERVATIVE,
            ExperienceType.VISUALIZATION: PruningStrategy.MODERATE,
            ExperienceType.USER_QUERY: PruningStrategy.AGGRESSIVE,
            ExperienceType.AGENT_RESPONSE: PruningStrategy.AGGRESSIVE,
            ExperienceType.SYSTEM_ERROR: PruningStrategy.MODERATE,
            ExperienceType.SESSION_CONTEXT: PruningStrategy.AGGRESSIVE,
            ExperienceType.REFERENCE_RESOLUTION: PruningStrategy.AGGRESSIVE
        }
    
    async def analyze_experience_importance(self, experience: Experience) -> float:
        """Analyze experience importance using LLM"""
        try:
            prompt = f"""
            Analyze the importance of this experience for an autonomous trading system:
            
            Type: {experience.experience_type.value}
            Content: {experience.content[:500]}...
            Metadata: {json.dumps(experience.metadata, indent=2)}
            
            Consider these factors:
            1. **User Value**: How directly does this help the user?
            2. **Learning Potential**: Does this provide insights for system improvement?
            3. **Trading Relevance**: Is this related to trading decisions or market analysis?
            4. **Uniqueness**: Is this new information or a unique insight?
            5. **Long-term Utility**: Will this be useful in the future?
            6. **Actionability**: Can this lead to concrete actions or decisions?
            
            Score from 1-10:
            - 10: Critical insight, unique learning, high user value, actionable
            - 8-9: Important information, good learning potential, relevant
            - 6-7: Useful information, moderate value
            - 4-5: Some value, but not critical
            - 2-3: Low value, routine, or redundant
            - 1: Trivial, noise, or irrelevant
            
            Provide your score and brief reasoning:
            Score: """
            
            response = await openai_manager.get_completion(prompt, max_tokens=100)
            
            # Extract score from response
            score_match = re.search(r'(\d+(?:\.\d+)?)', response)
            if score_match:
                score = float(score_match.group(1))
                return max(1.0, min(10.0, score))
            
            # Fallback to existing score
            return experience.importance_score
            
        except Exception as e:
            logger.error(f"Error analyzing experience importance: {e}")
            return experience.importance_score
    
    async def cluster_similar_experiences(self, experiences: List[Experience]) -> List[MemoryCluster]:
        """Cluster similar experiences using semantic similarity"""
        if len(experiences) < self.min_cluster_size:
            return []
        
        try:
            # Extract text content for clustering
            texts = [exp.content for exp in experiences]
            
            # Use TF-IDF for text vectorization
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            vectors = vectorizer.fit_transform(texts)
            
            # Use DBSCAN for clustering
            clustering = DBSCAN(
                eps=0.3,
                min_samples=self.min_cluster_size,
                metric='cosine'
            ).fit(vectors)
            
            # Group experiences by cluster
            clusters = {}
            for i, label in enumerate(clustering.labels_):
                if label == -1:  # Noise points (no cluster)
                    continue
                
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(experiences[i])
            
            # Create MemoryCluster objects
            memory_clusters = []
            for cluster_id, cluster_experiences in clusters.items():
                if len(cluster_experiences) >= self.min_cluster_size:
                    cluster = await self._create_memory_cluster(
                        f"cluster_{cluster_id}",
                        cluster_experiences
                    )
                    memory_clusters.append(cluster)
            
            return memory_clusters
            
        except Exception as e:
            logger.error(f"Error clustering experiences: {e}")
            return []
    
    async def _create_memory_cluster(self, cluster_id: str, experiences: List[Experience]) -> MemoryCluster:
        """Create a MemoryCluster from a group of experiences"""
        # Find the most representative experience (highest importance score)
        representative = max(experiences, key=lambda x: x.importance_score)
        
        # Create centroid content (average of all contents)
        contents = [exp.content for exp in experiences]
        centroid_content = self._create_centroid_content(contents)
        
        # Calculate cluster score (average importance)
        cluster_score = sum(exp.importance_score for exp in experiences) / len(experiences)
        
        # Determine if cluster should be consolidated
        should_consolidate = len(experiences) > 3 or cluster_score < 5.0
        
        return MemoryCluster(
            cluster_id=cluster_id,
            experiences=experiences,
            centroid_content=centroid_content,
            representative_experience=representative,
            cluster_score=cluster_score,
            should_consolidate=should_consolidate
        )
    
    def _create_centroid_content(self, contents: List[str]) -> str:
        """Create a representative content for a cluster"""
        if not contents:
            return ""
        
        # Simple approach: use the longest content as centroid
        return max(contents, key=len)
    
    async def get_pruning_recommendations(self, experiences: List[Experience]) -> List[PruningRecommendation]:
        """Get LLM-based pruning recommendations for experiences"""
        recommendations = []
        
        for experience in experiences:
            try:
                recommendation = await self._analyze_experience_for_pruning(experience)
                recommendations.append(recommendation)
            except Exception as e:
                logger.error(f"Error analyzing experience {experience.id} for pruning: {e}")
        
        return recommendations
    
    async def _analyze_experience_for_pruning(self, experience: Experience) -> PruningRecommendation:
        """Analyze a single experience for pruning"""
        try:
            prompt = f"""
            Analyze this experience for memory management:
            
            Experience ID: {experience.id}
            Type: {experience.experience_type.value}
            Content: {experience.content[:300]}...
            Current Importance Score: {experience.importance_score}
            Age: {(datetime.now() - experience.timestamp).total_seconds() / 3600:.1f} hours
            Memory Tier: {experience.memory_tier.value}
            
            Consider:
            1. **Relevance**: Is this information still relevant and useful?
            2. **Redundancy**: Is this redundant with other experiences?
            3. **Supersession**: Has this been superseded by newer information?
            4. **Routine**: Is this routine or trivial information?
            5. **Learning Value**: Does this contribute to system learning?
            
            Recommend one of these actions:
            - KEEP: Important, unique, still relevant (retain indefinitely)
            - DOWNGRADE: Less important than initially scored (move to lower tier)
            - PRUNE: Redundant, outdated, or trivial (mark for deletion)
            - CONSOLIDATE: Similar to other experiences (merge with cluster)
            
            Provide your recommendation and reasoning:
            Action: """
            
            response = await openai_manager.get_completion(prompt, max_tokens=150)
            
            # Parse response
            action_match = re.search(r'(KEEP|DOWNGRADE|PRUNE|CONSOLIDATE)', response.upper())
            action = action_match.group(1) if action_match else "KEEP"
            
            # Extract reasoning
            reasoning = response.replace(action, "").strip()
            
            # Calculate confidence based on importance score and age
            confidence = min(1.0, experience.importance_score / 10.0)
            
            # Determine retention days based on action
            retention_days = self._get_retention_days(action, experience)
            
            return PruningRecommendation(
                experience_id=experience.id,
                action=action.lower(),
                reasoning=reasoning,
                confidence=confidence,
                suggested_retention_days=retention_days
            )
            
        except Exception as e:
            logger.error(f"Error in pruning analysis: {e}")
            return PruningRecommendation(
                experience_id=experience.id,
                action="keep",
                reasoning="Error in analysis, defaulting to keep",
                confidence=0.5,
                suggested_retention_days=30
            )
    
    def _get_retention_days(self, action: str, experience: Experience) -> int:
        """Get suggested retention days based on action and experience"""
        base_retention = {
            "keep": 365,  # 1 year
            "downgrade": 90,  # 3 months
            "prune": 7,  # 1 week
            "consolidate": 30  # 1 month
        }
        
        base_days = base_retention.get(action.lower(), 30)
        
        # Adjust based on importance score
        importance_multiplier = experience.importance_score / 5.0
        
        # Adjust based on experience type
        type_multiplier = {
            ExperienceType.TRADE_EXECUTION: 2.0,
            ExperienceType.MARKET_INSIGHT: 1.5,
            ExperienceType.AGENT_LEARNING: 1.5,
            ExperienceType.VISUALIZATION: 1.0,
            ExperienceType.USER_QUERY: 0.5,
            ExperienceType.AGENT_RESPONSE: 0.5,
            ExperienceType.SYSTEM_ERROR: 1.0,
            ExperienceType.SESSION_CONTEXT: 0.3,
            ExperienceType.REFERENCE_RESOLUTION: 0.3
        }.get(experience.experience_type, 1.0)
        
        return int(base_days * importance_multiplier * type_multiplier)
    
    async def optimize_memory_usage(self) -> Dict[str, Any]:
        """Run comprehensive memory optimization"""
        try:
            logger.info("🔄 Starting memory optimization...")
            
            # Get all experiences
            cursor = self.experience_db.sqlite_conn.cursor()
            cursor.execute("SELECT * FROM experiences WHERE memory_tier != 'pruned' ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            
            experiences = [self.experience_db._row_to_experience(row) for row in rows]
            
            if not experiences:
                return {"status": "no_experiences", "optimizations": 0}
            
            optimizations = 0
            
            # 1. Re-analyze importance scores
            logger.info("📊 Re-analyzing importance scores...")
            for experience in experiences[:100]:  # Limit to recent 100
                new_score = await self.analyze_experience_importance(experience)
                if abs(new_score - experience.importance_score) > 1.0:
                    await self._update_experience_score(experience.id, new_score)
                    optimizations += 1
            
            # 2. Cluster similar experiences
            logger.info("🔗 Clustering similar experiences...")
            clusters = await self.cluster_similar_experiences(experiences)
            
            for cluster in clusters:
                if cluster.should_consolidate:
                    await self._consolidate_cluster(cluster)
                    optimizations += 1
            
            # 3. Get pruning recommendations
            logger.info("✂️ Getting pruning recommendations...")
            recommendations = await self.get_pruning_recommendations(experiences[:50])  # Limit to recent 50
            
            for rec in recommendations:
                if rec.confidence > 0.7:  # Only apply high-confidence recommendations
                    await self._apply_pruning_recommendation(rec)
                    optimizations += 1
            
            # 4. Update memory stats
            await self.experience_db._update_memory_stats()
            
            logger.info(f"✅ Memory optimization completed: {optimizations} optimizations applied")
            
            return {
                "status": "completed",
                "optimizations": optimizations,
                "clusters_found": len(clusters),
                "recommendations_processed": len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error in memory optimization: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _update_experience_score(self, experience_id: str, new_score: float):
        """Update experience importance score"""
        cursor = self.experience_db.sqlite_conn.cursor()
        cursor.execute("""
            UPDATE experiences 
            SET importance_score = ? 
            WHERE id = ?
        """, (new_score, experience_id))
        self.experience_db.sqlite_conn.commit()
    
    async def _consolidate_cluster(self, cluster: MemoryCluster):
        """Consolidate a cluster by keeping representative and pruning others"""
        # Keep the representative experience
        representative_id = cluster.representative_experience.id
        
        # Mark others for pruning
        for experience in cluster.experiences:
            if experience.id != representative_id:
                await self.experience_db._prune_experience(experience.id)
        
        logger.info(f"Consolidated cluster {cluster.cluster_id}: kept {representative_id}, pruned {len(cluster.experiences) - 1} others")
    
    async def _apply_pruning_recommendation(self, recommendation: PruningRecommendation):
        """Apply a pruning recommendation"""
        if recommendation.action == "prune":
            await self.experience_db._prune_experience(recommendation.experience_id)
        elif recommendation.action == "downgrade":
            await self.experience_db._downgrade_experience(recommendation.experience_id)
        elif recommendation.action == "consolidate":
            # Mark for consolidation (will be handled in clustering)
            pass
        # "keep" action requires no change
    
    async def get_memory_insights(self) -> Dict[str, Any]:
        """Get insights about memory usage and optimization opportunities"""
        try:
            stats = await self.experience_db.get_memory_stats()
            
            # Analyze memory distribution
            total = stats["total_experiences"]
            if total == 0:
                return {"status": "no_data"}
            
            hot_ratio = stats["hot_memory_count"] / total
            warm_ratio = stats["warm_memory_count"] / total
            cold_ratio = stats["cold_memory_count"] / total
            
            # Generate insights
            insights = []
            
            if hot_ratio > 0.3:
                insights.append("High hot memory ratio - consider promoting important warm memories")
            
            if cold_ratio > 0.5:
                insights.append("High cold memory ratio - consider aggressive pruning")
            
            if stats["pruned_count"] > total * 0.1:
                insights.append("Significant pruned data - consider cleanup")
            
            # Get recent activity
            cursor = self.experience_db.sqlite_conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM experiences 
                WHERE timestamp > datetime('now', '-1 day')
            """)
            recent_count = cursor.fetchone()[0]
            
            return {
                "status": "success",
                "stats": stats,
                "ratios": {
                    "hot": hot_ratio,
                    "warm": warm_ratio,
                    "cold": cold_ratio
                },
                "insights": insights,
                "recent_activity": recent_count,
                "optimization_needed": len(insights) > 0
            }
            
        except Exception as e:
            logger.error(f"Error getting memory insights: {e}")
            return {"status": "error", "error": str(e)}


# Global instance - will be initialized after central_experience_db is available
intelligent_memory_manager = None

def initialize_intelligent_memory_manager():
    """Initialize the intelligent memory manager after central_experience_db is ready"""
    global intelligent_memory_manager
    from core.central_experience_db import central_experience_db
    intelligent_memory_manager = IntelligentMemoryManager(central_experience_db)
    return intelligent_memory_manager 