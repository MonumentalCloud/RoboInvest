# Continuous Research Architecture

## Overview

The trading system has been transformed into a **continuous autonomous research system** where AI agents work 24/7 in the background, and the frontend serves as a real-time dashboard into their research activities.

## Architecture Components

### 1. Background Research Service (`background_research_service.py`)
- **Purpose**: Continuously runs AI agents for autonomous research
- **Features**:
  - 6 research tracks running in parallel
  - Market hours awareness
  - Self-healing (restarts failed agents)
  - Results stored in JSON files
  - Dynamic research objectives

### 2. Research API Endpoints (integrated into `backend/api/fastapi_app.py`)
- **Purpose**: Provides API access to continuous research data
- **Endpoints**:
  - `/api/research/status` - Service health and stats
  - `/api/research/insights` - Consolidated insights from all tracks
  - `/api/research/tracks` - All research track data
  - `/api/research/alpha-opportunities` - High-confidence opportunities
  - `/api/research/decision-trees` - Decision tree visualizations

### 3. Frontend Dashboard (`frontend/src/pages/Insights.tsx`)
- **Purpose**: Real-time viewing interface for research results
- **Features**:
  - Live insights display with confidence levels
  - Track specialization indicators
  - Automatic refresh every 60 seconds
  - Responsive UI with status indicators

## Research Tracks

The system runs 6 specialized research tracks:

1. **Alpha Discovery** (15 min intervals)
   - Hunts for unique alpha opportunities
   - Identifies undervalued securities with catalyst potential

2. **Market Monitoring** (10 min intervals)
   - Monitors real-time market patterns
   - Tracks unusual activity and volume anomalies

3. **Sentiment Tracking** (20 min intervals)
   - Analyzes market sentiment shifts
   - Monitors news impact and social sentiment

4. **Technical Analysis** (30 min intervals)
   - Identifies technical patterns
   - Analyzes support/resistance levels

5. **Risk Assessment** (1 hour intervals)
   - Assesses market risks and tail scenarios
   - Monitors correlation structures

6. **Deep Research** (2 hour intervals)
   - Comprehensive fundamental analysis
   - Long-term thematic research

## Data Storage

Research results are stored in the `research_data/` directory:

- `{track_name}_latest.json` - Latest results for each track
- `{track_name}_{timestamp}.json` - Historical results
- `consolidated_insights.json` - All insights combined
- `system_status.json` - Service health and statistics

## Usage

### Starting the System

```bash
# Start the continuous research system
python run_continuous_research.py
```

This starts:
1. Background research service (port: background process)
2. FastAPI backend with research endpoints (port: 8000)

### Frontend Integration

The frontend automatically connects to the research API:

```typescript
// Hooks for accessing research data
const insights = useResearchInsights(50);
const opportunities = useAlphaOpportunities(0.5);
const status = useResearchStatus();
```

### API Usage Examples

```bash
# Get system status
curl http://localhost:8000/api/research/status

# Get latest insights
curl http://localhost:8000/api/research/insights?limit=20

# Get alpha opportunities (min 50% confidence)
curl http://localhost:8000/api/research/alpha-opportunities?min_confidence=0.5

# Get decision trees
curl http://localhost:8000/api/research/decision-trees
```

## Key Features

### Continuous Operation
- Agents run 24/7 with configurable intervals
- No manual triggering required
- Self-healing system restarts failed agents

### Real-Time Dashboard
- Frontend polls for updates every 60 seconds
- Live status indicators
- Confidence-based color coding

### Intelligent Scheduling
- Market hours awareness
- Dynamic research objectives
- Optimized API rate limiting

### Robust Error Handling
- Graceful degradation
- Comprehensive logging
- Fallback mechanisms

## Configuration

Research intervals can be modified in `background_research_service.py`:

```python
self.research_cycles = {
    "alpha_discovery": {
        "interval": 900,  # 15 minutes
        "enabled": True
    },
    # ... other tracks
}
```

## Monitoring

The system provides comprehensive monitoring:

- **Service Status**: Uptime, cycle counts, success rates
- **Research Activity**: Active tracks, insights generated
- **Performance**: Processing times, error rates
- **Data Quality**: Confidence levels, track coverage

## Benefits

1. **Continuous Intelligence**: AI agents work around the clock
2. **Scalable**: Easy to add new research tracks
3. **Resilient**: Self-healing and error recovery
4. **Transparent**: Full visibility into AI reasoning
5. **Efficient**: Optimized for API rate limits

## Future Enhancements

- Advanced decision tree visualizations
- Real-time notifications for high-confidence opportunities
- Historical trend analysis
- Machine learning model integration
- Advanced scheduling algorithms

This architecture transforms the system from a reactive tool into a proactive AI research platform that continuously discovers alpha opportunities. 