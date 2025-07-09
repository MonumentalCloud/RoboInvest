"""
Research API Endpoints
API endpoints for the frontend to access continuous research data.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

class ResearchAPI:
    """API for accessing continuous research data."""
    
    def __init__(self, app: Flask = None):
        self.research_data_dir = Path("research_data")
        self.research_data_dir.mkdir(exist_ok=True)
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the API with a Flask app."""
        
        # Enable CORS for frontend access
        CORS(app)
        
        # Register API endpoints
        @app.route('/api/research/status', methods=['GET'])
        def get_research_status():
            """Get current research service status."""
            return jsonify(self.get_system_status())
        
        @app.route('/api/research/insights', methods=['GET'])
        def get_consolidated_insights():
            """Get consolidated insights from all research tracks."""
            limit = request.args.get('limit', 50, type=int)
            return jsonify(self.get_insights(limit))
        
        @app.route('/api/research/track/<track_name>', methods=['GET'])
        def get_track_data(track_name: str):
            """Get latest data for a specific research track."""
            return jsonify(self.get_track_data(track_name))
        
        @app.route('/api/research/tracks', methods=['GET'])
        def get_all_tracks():
            """Get latest data for all research tracks."""
            return jsonify(self.get_all_tracks())
        
        @app.route('/api/research/history/<track_name>', methods=['GET'])
        def get_track_history(track_name: str):
            """Get historical data for a research track."""
            hours = request.args.get('hours', 24, type=int)
            return jsonify(self.get_track_history(track_name, hours))
        
        @app.route('/api/research/decision-trees', methods=['GET'])
        def get_decision_trees():
            """Get current decision trees from active research."""
            return jsonify(self.get_decision_trees())
        
        @app.route('/api/research/alpha-opportunities', methods=['GET'])
        def get_alpha_opportunities():
            """Get current alpha opportunities."""
            min_confidence = request.args.get('min_confidence', 0.0, type=float)
            return jsonify(self.get_alpha_opportunities(min_confidence))
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        try:
            status_file = self.research_data_dir / "system_status.json"
            if status_file.exists():
                with open(status_file, 'r') as f:
                    status = json.load(f)
                return {"status": "success", "data": status}
            else:
                return {
                    "status": "error", 
                    "message": "Research service not running",
                    "data": {"running": False}
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_insights(self, limit: int = 50) -> Dict[str, Any]:
        """Get consolidated insights."""
        try:
            insights_file = self.research_data_dir / "consolidated_insights.json"
            if insights_file.exists():
                with open(insights_file, 'r') as f:
                    data = json.load(f)
                
                # Limit results
                insights = data.get("insights", [])[-limit:]
                
                return {
                    "status": "success",
                    "data": {
                        "insights": insights,
                        "total_available": data.get("total_insights", 0),
                        "last_updated": data.get("last_updated"),
                        "returned": len(insights)
                    }
                }
            else:
                return {
                    "status": "success",
                    "data": {
                        "insights": [],
                        "total_available": 0,
                        "last_updated": None,
                        "returned": 0
                    }
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_track_data(self, track_name: str) -> Dict[str, Any]:
        """Get latest data for a specific research track."""
        try:
            track_file = self.research_data_dir / f"{track_name}_latest.json"
            if track_file.exists():
                with open(track_file, 'r') as f:
                    data = json.load(f)
                return {"status": "success", "data": data}
            else:
                return {"status": "error", "message": f"No data found for track: {track_name}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_all_tracks(self) -> Dict[str, Any]:
        """Get latest data for all research tracks."""
        try:
            tracks = {}
            track_names = [
                "alpha_discovery", "market_monitoring", "sentiment_tracking",
                "technical_analysis", "risk_assessment", "deep_research"
            ]
            
            for track_name in track_names:
                track_file = self.research_data_dir / f"{track_name}_latest.json"
                if track_file.exists():
                    with open(track_file, 'r') as f:
                        tracks[track_name] = json.load(f)
            
            return {"status": "success", "data": tracks}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_track_history(self, track_name: str, hours: int = 24) -> Dict[str, Any]:
        """Get historical data for a research track."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            history_files = []
            
            # Find all history files for the track
            for file_path in self.research_data_dir.glob(f"{track_name}_*.json"):
                if file_path.name.endswith("_latest.json"):
                    continue
                
                # Extract timestamp from filename
                try:
                    timestamp_str = file_path.stem.split('_', 1)[1]
                    file_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    
                    if file_time >= cutoff_time:
                        history_files.append((file_time, file_path))
                except ValueError:
                    continue
            
            # Sort by timestamp
            history_files.sort(key=lambda x: x[0])
            
            # Load the data
            history_data = []
            for file_time, file_path in history_files:
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        data["file_timestamp"] = file_time.isoformat()
                        history_data.append(data)
                except Exception:
                    continue
            
            return {
                "status": "success",
                "data": {
                    "track_name": track_name,
                    "hours_requested": hours,
                    "entries_found": len(history_data),
                    "history": history_data
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_decision_trees(self) -> Dict[str, Any]:
        """Get current decision trees from active research."""
        try:
            trees = {}
            
            # Get decision trees from latest track data
            track_names = [
                "alpha_discovery", "market_monitoring", "sentiment_tracking",
                "technical_analysis", "risk_assessment", "deep_research"
            ]
            
            for track_name in track_names:
                track_file = self.research_data_dir / f"{track_name}_latest.json"
                if track_file.exists():
                    with open(track_file, 'r') as f:
                        data = json.load(f)
                        
                        # Extract decision tree data
                        decision_tree = data.get("decision_tree")
                        if decision_tree:
                            trees[track_name] = {
                                "tree": decision_tree,
                                "completed_at": data.get("completed_at"),
                                "specialization": data.get("specialization"),
                                "research_track": data.get("research_track")
                            }
            
            return {"status": "success", "data": trees}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_alpha_opportunities(self, min_confidence: float = 0.0) -> Dict[str, Any]:
        """Get current alpha opportunities."""
        try:
            opportunities = []
            
            # Get opportunities from all tracks
            track_names = [
                "alpha_discovery", "market_monitoring", "sentiment_tracking",
                "technical_analysis", "risk_assessment", "deep_research"
            ]
            
            for track_name in track_names:
                track_file = self.research_data_dir / f"{track_name}_latest.json"
                if track_file.exists():
                    with open(track_file, 'r') as f:
                        data = json.load(f)
                        
                        # Extract opportunities from insights
                        insights = data.get("insights", [])
                        for insight in insights:
                            confidence = insight.get("confidence", 0.0)
                            if confidence >= min_confidence:
                                opportunity = {
                                    "id": f"{track_name}_{hash(str(insight))}",
                                    "track": track_name,
                                    "specialization": data.get("specialization", "unknown"),
                                    "opportunity": insight.get("insight", str(insight)),
                                    "confidence": confidence,
                                    "competitive_edge": insight.get("competitive_edge", ""),
                                    "action_plan": insight.get("actionable_steps", []),
                                    "discovered_at": data.get("completed_at"),
                                    "market_session": data.get("market_context", {}).get("market_session", "unknown")
                                }
                                opportunities.append(opportunity)
            
            # Sort by confidence
            opportunities.sort(key=lambda x: x["confidence"], reverse=True)
            
            return {
                "status": "success",
                "data": {
                    "opportunities": opportunities,
                    "total_found": len(opportunities),
                    "min_confidence": min_confidence,
                    "last_updated": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Create Flask app for the research API
def create_research_api_app():
    """Create Flask app with research API endpoints."""
    app = Flask(__name__)
    
    # Initialize research API
    research_api = ResearchAPI(app)
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "service": "research_api",
            "timestamp": datetime.now().isoformat()
        })
    
    @app.route('/api', methods=['GET'])
    def api_info():
        """API information endpoint."""
        return jsonify({
            "service": "Autonomous Research API",
            "version": "1.0.0",
            "endpoints": [
                "/api/research/status",
                "/api/research/insights",
                "/api/research/track/<track_name>",
                "/api/research/tracks",
                "/api/research/history/<track_name>",
                "/api/research/decision-trees",
                "/api/research/alpha-opportunities"
            ],
            "timestamp": datetime.now().isoformat()
        })
    
    return app

if __name__ == "__main__":
    # Run the API server
    app = create_research_api_app()
    app.run(host="0.0.0.0", port=5000, debug=True) 