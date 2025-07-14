# Hybrid Memory System Overview

## 🧠 System Architecture

The RoboInvest system now features a sophisticated hybrid memory architecture that combines:

- **ChromaDB** for semantic (vector) search and recall
- **SQLite** for structured events, session context, and cross-agent memory
- **LLM-based intelligent pruning** for adaptive memory management

## 🏗️ Core Components

### 1. Central Experience Database (`core/central_experience_db.py`)

**Purpose**: Centralized storage for all agent experiences and interactions

**Key Features**:
- **Hybrid Storage**: ChromaDB for semantic search + SQLite for structured data
- **Experience Types**: User queries, agent responses, visualizations, trade executions, market insights, system errors, agent learning, session context, reference resolution
- **Memory Tiers**: Hot (recent/frequent), Warm (important), Cold (archived), Pruned (marked for deletion)
- **Session Management**: Maintains conversation context across interactions
- **Cross-References**: Links related experiences for context awareness

**Experience Structure**:
```python
@dataclass
class Experience:
    id: str
    timestamp: datetime
    experience_type: ExperienceType
    source_agent: str
    content: str
    metadata: Dict[str, Any]
    importance_score: float
    memory_tier: MemoryTier
    session_id: Optional[str]
    user_message: Optional[str]
    references: List[str]  # IDs of related experiences
```

### 2. Intelligent Memory Manager (`core/intelligent_memory_manager.py`)

**Purpose**: LLM-based memory optimization and pruning

**Key Features**:
- **Importance Scoring**: LLM analyzes each experience for user value, learning potential, trading relevance, uniqueness, and long-term utility
- **Semantic Clustering**: Groups similar experiences using TF-IDF and DBSCAN
- **Intelligent Pruning**: LLM-based recommendations for keep/downgrade/prune/consolidate
- **Memory Optimization**: Comprehensive analysis and cleanup of memory usage
- **Adaptive Retention**: Different retention strategies for different experience types

**Pruning Strategies**:
- **Conservative**: Trade executions, agent learning (long retention)
- **Moderate**: Market insights, visualizations, system errors (balanced retention)
- **Aggressive**: User queries, agent responses, session context (short retention)

### 3. Governor Integration (`backend/api/governor_endpoints.py`)

**Purpose**: Seamless integration with the governor agent system

**Key Features**:
- **Memory-Aware Conversations**: Every user query and agent response is stored
- **Context Retrieval**: Relevant past experiences are retrieved for each conversation
- **Session Continuity**: Maintains conversation context across interactions
- **Memory Management Endpoints**: APIs for stats, optimization, cleanup, and experience queries

**New Endpoints**:
- `GET /api/governor/memory/stats` - Memory statistics and insights
- `POST /api/governor/memory/optimize` - Run memory optimization
- `POST /api/governor/memory/cleanup` - Clean up pruned data
- `GET /api/governor/memory/experiences` - Query experiences from memory

## 🔄 Memory Flow

### 1. Experience Storage
```
User Query → Store in Memory → Intent Detection → Agent Response → Store Response → Update Session Context
```

### 2. Context Retrieval
```
New Query → Semantic Search → Retrieve Relevant Experiences → Enhance Context → Generate Response
```

### 3. Memory Optimization
```
Background Thread → Analyze Experiences → LLM Scoring → Clustering → Pruning Recommendations → Apply Changes
```

## 🎯 Key Benefits

### 1. **Persistent Memory**
- All conversations, decisions, and insights are preserved
- Cross-session continuity and learning
- Historical context for better decision-making

### 2. **Intelligent Retention**
- LLM-based importance scoring (1-10 scale)
- Automatic pruning of redundant or outdated information
- Adaptive retention based on experience type and value

### 3. **Semantic Search**
- Find relevant past experiences using natural language
- Context-aware responses based on historical interactions
- Cross-reference related experiences

### 4. **Session Management**
- Maintain conversation context across interactions
- Track recent experiences and user preferences
- Enable personalized responses

### 5. **Scalable Architecture**
- Hybrid storage for optimal performance
- Background optimization and pruning
- Efficient memory usage with intelligent cleanup

## 🧪 Testing

The system includes comprehensive testing (`scripts/test_hybrid_memory_system.py`):

- ✅ Basic functionality (storage/retrieval)
- ✅ Memory optimization
- ✅ Agent integration
- ✅ Error handling
- ✅ Session management

## 🚀 Usage Examples

### 1. Basic Memory Operations
```python
# Store user query
await central_experience_db.add_experience(
    experience_type=ExperienceType.USER_QUERY,
    source_agent="user",
    content="What are my current positions?",
    metadata={"session_id": "user_123"},
    session_id="user_123"
)

# Query relevant experiences
experiences = await central_experience_db.query_experiences(
    query="positions portfolio",
    limit=10
)
```

### 2. Memory Optimization
```python
# Get memory insights
insights = await intelligent_memory_manager.get_memory_insights()

# Run optimization
result = await intelligent_memory_manager.optimize_memory_usage()
```

### 3. Governor Integration
```python
# Memory-aware conversation
response = await governor_conversation({
    "message": "Show me my trading history",
    "session_id": "user_123"
})
```

## 📊 Memory Statistics

The system tracks comprehensive memory statistics:

- **Total Experiences**: Overall memory size
- **Memory Tiers**: Distribution across hot/warm/cold/pruned
- **Recent Activity**: Experiences added in last 24 hours
- **Optimization Insights**: Recommendations for memory management

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for LLM-based features
- `CHROMA_DB_PATH`: ChromaDB storage location (default: `./chroma_db`)

### Database Files
- `data/central_experience.db`: SQLite database for structured data
- `chroma_db/`: ChromaDB directory for vector embeddings

## 🎯 Future Enhancements

1. **Advanced Clustering**: More sophisticated similarity detection
2. **Memory Compression**: Efficient storage of large experiences
3. **Predictive Pruning**: Proactive memory management
4. **Memory Analytics**: Detailed insights into memory usage patterns
5. **Cross-Agent Learning**: Shared knowledge between different agent types

## 🏆 Success Metrics

The hybrid memory system successfully provides:

- **Persistent Context**: Conversations maintain context across sessions
- **Intelligent Retention**: Important information is preserved, irrelevant data is pruned
- **Semantic Search**: Natural language queries find relevant past experiences
- **Scalable Performance**: Efficient storage and retrieval of large amounts of data
- **LLM Integration**: AI-powered memory management and optimization

This architecture enables RoboInvest to learn from every interaction, maintain context across sessions, and provide increasingly intelligent and personalized responses over time. 