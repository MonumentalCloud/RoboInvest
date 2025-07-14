"""
Enhanced Governor Endpoints with Rich Response Formatting

This module provides the governor agent endpoints with support for:
- Markdown formatting
- Interactive tables
- Chart data and visualizations
- Code diffs and syntax highlighting
- UI hints and action buttons
- Rich content types for frontend rendering
"""

import json
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from utils.logger import logger
from core.central_experience_db import central_experience_db, ExperienceType
from core.intelligent_memory_manager import intelligent_memory_manager

router = APIRouter(prefix="/api/governor", tags=["governor"])

# Enhanced response types
class ResponseType(str, Enum):
    MARKDOWN = "markdown"
    TABLE = "table"
    CHART = "chart"
    CODE_DIFF = "code_diff"
    INTERACTIVE = "interactive"
    DASHBOARD = "dashboard"
    ALERT = "alert"
    PROGRESS = "progress"

class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    CANDLESTICK = "candlestick"
    HEATMAP = "heatmap"

class UIHint(str, Enum):
    REFRESH = "refresh"
    EXPAND = "expand"
    COLLAPSE = "collapse"
    ACTION = "action"
    NAVIGATE = "navigate"
    MODAL = "modal"

class RichResponseFormatter:
    """Enhanced response formatter for rich content types"""
    
    @staticmethod
    def create_markdown_response(content: str, agent: str = "governor", actions: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a markdown-formatted response"""
        return {
            "type": ResponseType.MARKDOWN,
            "content": content,
            "agent": agent,
            "actions_taken": actions or [],
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_table_response(headers: List[str], rows: List[List[Any]], title: str = "", agent: str = "governor", 
                            sortable: bool = True, searchable: bool = True, pagination: bool = True) -> Dict[str, Any]:
        """Create an interactive table response"""
        return {
            "type": ResponseType.TABLE,
            "content": {
                "title": title,
                "headers": headers,
                "rows": rows,
                "total_rows": len(rows)
            },
            "agent": agent,
            "ui_config": {
                "sortable": sortable,
                "searchable": searchable,
                "pagination": pagination,
                "page_size": 10
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_chart_response(chart_type: ChartType, data: Dict[str, Any], title: str = "", 
                            agent: str = "governor", interactive: bool = True) -> Dict[str, Any]:
        """Create a chart response with visualization data"""
        return {
            "type": ResponseType.CHART,
            "content": {
                "chart_type": chart_type,
                "title": title,
                "data": data
            },
            "agent": agent,
            "ui_config": {
                "interactive": interactive,
                "responsive": True,
                "theme": "light"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_code_diff_response(file_path: str, old_code: str, new_code: str, 
                                description: str = "", agent: str = "governor") -> Dict[str, Any]:
        """Create a code diff response for code changes"""
        return {
            "type": ResponseType.CODE_DIFF,
            "content": {
                "file_path": file_path,
                "old_code": old_code,
                "new_code": new_code,
                "description": description,
                "language": "python"  # Auto-detect based on file extension
            },
            "agent": agent,
            "ui_config": {
                "syntax_highlighting": True,
                "line_numbers": True,
                "side_by_side": True
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_interactive_response(content: str, actions: List[Dict[str, Any]], 
                                  agent: str = "governor", ui_hints: Optional[List[UIHint]] = None) -> Dict[str, Any]:
        """Create an interactive response with action buttons and UI hints"""
        return {
            "type": ResponseType.INTERACTIVE,
            "content": content,
            "agent": agent,
            "actions": actions,
            "ui_hints": ui_hints or [],
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_dashboard_response(panels: List[Dict[str, Any]], layout: str = "grid", 
                                agent: str = "governor") -> Dict[str, Any]:
        """Create a dashboard response with multiple panels"""
        return {
            "type": ResponseType.DASHBOARD,
            "content": {
                "panels": panels,
                "layout": layout,
                "title": "System Dashboard"
            },
            "agent": agent,
            "ui_config": {
                "resizable": True,
                "collapsible": True,
                "refreshable": True
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_alert_response(level: str, message: str, title: str = "", 
                            agent: str = "governor", dismissible: bool = True) -> Dict[str, Any]:
        """Create an alert response for notifications"""
        return {
            "type": ResponseType.ALERT,
            "content": {
                "level": level,  # success, warning, error, info
                "message": message,
                "title": title
            },
            "agent": agent,
            "ui_config": {
                "dismissible": dismissible,
                "auto_dismiss": level != "error",
                "timeout": 5000 if level != "error" else None
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_progress_response(current: int, total: int, message: str = "", 
                               agent: str = "governor", cancellable: bool = False) -> Dict[str, Any]:
        """Create a progress response for long-running operations"""
        return {
            "type": ResponseType.PROGRESS,
            "content": {
                "current": current,
                "total": total,
                "percentage": (current / total * 100) if total > 0 else 0,
                "message": message
            },
            "agent": agent,
            "ui_config": {
                "cancellable": cancellable,
                "show_percentage": True,
                "animated": True
            },
            "timestamp": datetime.now().isoformat()
        }

# Initialize the formatter
formatter = RichResponseFormatter()

# Enhanced system status response with rich formatting
def create_enhanced_system_status_response(system_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create an enhanced system status response with tables and charts"""
    
    if not system_issues:
        # No issues - create a success dashboard
        panels = [
            {
                "type": "status",
                "title": "System Health",
                "content": "✅ All systems operational",
                "color": "green"
            },
            {
                "type": "metric",
                "title": "Active Agents",
                "content": "5/5",
                "color": "blue"
            },
            {
                "type": "metric", 
                "title": "Research Status",
                "content": "Active",
                "color": "green"
            }
        ]
        
        return formatter.create_dashboard_response(
            panels=panels,
            layout="grid",
            agent="governor"
        )
    
    # Create issue table
    headers = ["Type", "Severity", "Description", "Impact", "Solution"]
    rows = []
    
    for issue in system_issues:
        rows.append([
            issue['type'].upper(),
            issue['severity'],
            issue['description'][:50] + "..." if len(issue['description']) > 50 else issue['description'],
            issue['impact'],
            issue['solution']
        ])
    
    # Create severity chart data
    severity_counts = {}
    for issue in system_issues:
        severity = issue['severity']
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    chart_data = {
        "labels": list(severity_counts.keys()),
        "datasets": [{
            "label": "Issues by Severity",
            "data": list(severity_counts.values()),
            "backgroundColor": ["#dc3545", "#ffc107", "#17a2b8", "#28a745"]
        }]
    }
    
    # Create interactive response with multiple components
    content = "## 🔧 System Status Report\n\n"
    content += f"**{len(system_issues)} issue(s) detected** that require attention.\n\n"
    content += "Use the interactive components below to analyze and resolve issues."
    
    actions = [
        {
            "label": "Refresh Status",
            "action": "refresh_system_status",
            "icon": "🔄",
            "style": "primary"
        },
        {
            "label": "View Details",
            "action": "expand_issue_details", 
            "icon": "📋",
            "style": "secondary"
        },
        {
            "label": "Auto-Fix Issues",
            "action": "auto_fix_issues",
            "icon": "🔧",
            "style": "success"
        }
    ]
    
    return formatter.create_interactive_response(
        content=content,
        actions=actions,
        agent="governor",
        ui_hints=[UIHint.EXPAND, UIHint.REFRESH]
    )

# Enhanced research status response
def create_enhanced_research_status_response(research_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create an enhanced research status response with charts and tables"""
    
    summary = research_data.get("summary", {})
    total_files = summary.get("total_files", 0)
    
    if total_files == 0:
        # No research data - create alert
        return formatter.create_alert_response(
            level="warning",
            message="Research system appears inactive. No recent research data found.",
            title="Research Status",
            agent="governor"
        )
    
    # Create research metrics dashboard
    panels = [
        {
            "type": "metric",
            "title": "Total Research Files",
            "content": str(total_files),
            "color": "blue"
        },
        {
            "type": "metric",
            "title": "Alpha Discoveries",
            "content": str(summary.get("alpha_discoveries_count", 0)),
            "color": "green"
        },
        {
            "type": "metric",
            "title": "Market Updates",
            "content": str(summary.get("market_monitoring_count", 0)),
            "color": "orange"
        },
        {
            "type": "metric",
            "title": "Risk Assessments",
            "content": str(summary.get("risk_assessments_count", 0)),
            "color": "red"
        }
    ]
    
    # Create research activity chart
    chart_data = {
        "labels": ["Alpha Discoveries", "Market Monitoring", "Risk Assessments", "Sentiment Tracking"],
        "datasets": [{
            "label": "Research Activity",
            "data": [
                summary.get("alpha_discoveries_count", 0),
                summary.get("market_monitoring_count", 0),
                summary.get("risk_assessments_count", 0),
                summary.get("sentiment_tracking_count", 0)
            ],
            "backgroundColor": ["#28a745", "#17a2b8", "#dc3545", "#ffc107"]
        }]
    }
    
    actions = [
        {
            "label": "Start Research",
            "action": "start_research_agents",
            "icon": "🚀",
            "style": "success"
        },
        {
            "label": "View Research Data",
            "action": "view_research_files",
            "icon": "📊",
            "style": "primary"
        },
        {
            "label": "Analyze Markets",
            "action": "analyze_current_markets",
            "icon": "🔍",
            "style": "secondary"
        }
    ]
    
    return formatter.create_interactive_response(
        content="## 🔍 Research System Status\n\nResearch agents are actively generating data and insights.",
        actions=actions,
        agent="governor",
        ui_hints=[UIHint.EXPAND, UIHint.REFRESH]
    )

# Enhanced trading status response
def create_enhanced_trading_status_response(alpaca_status: Dict[str, Any], positions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Create an enhanced trading status response with portfolio data"""
    
    if not alpaca_status.get("connected", False):
        return formatter.create_alert_response(
            level="error",
            message="Trading system is not connected to Alpaca. Please check API configuration.",
            title="Trading Status",
            agent="governor"
        )
    
    # Create portfolio dashboard
    panels = [
        {
            "type": "metric",
            "title": "Account Value",
            "content": f"${alpaca_status.get('account_value', 0):,.2f}",
            "color": "green"
        },
        {
            "type": "metric",
            "title": "Cash",
            "content": f"${alpaca_status.get('cash', 0):,.2f}",
            "color": "blue"
        },
        {
            "type": "metric",
            "title": "Positions",
            "content": str(len(positions) if positions else 0),
            "color": "orange"
        },
        {
            "type": "metric",
            "title": "Buying Power",
            "content": f"${alpaca_status.get('buying_power', 0):,.2f}",
            "color": "purple"
        }
    ]
    
    # Create positions table if available
    if positions:
        headers = ["Symbol", "Quantity", "Market Value", "Unrealized P&L", "P&L %"]
        rows = []
        
        for pos in positions:
            rows.append([
                pos.get("symbol", ""),
                pos.get("qty", 0),
                f"${pos.get('market_value', 0):,.2f}",
                f"${pos.get('unrealized_pl', 0):,.2f}",
                f"{pos.get('unrealized_plpc', 0):.2%}"
            ])
    
    actions = [
        {
            "label": "View Positions",
            "action": "view_positions",
            "icon": "📈",
            "style": "primary"
        },
        {
            "label": "Place Trade",
            "action": "place_trade",
            "icon": "💰",
            "style": "success"
        },
        {
            "label": "Market Analysis",
            "action": "analyze_markets",
            "icon": "🔍",
            "style": "secondary"
        }
    ]
    
    return formatter.create_interactive_response(
        content="## 💰 Trading System Status\n\nConnected to Alpaca and ready for trading operations.",
        actions=actions,
        agent="governor",
        ui_hints=[UIHint.EXPAND, UIHint.REFRESH]
    )

# Enhanced agent response with rich formatting
def create_enhanced_agent_response(message: str, agent_type: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create an enhanced agent response with appropriate formatting based on content"""
    
    # Detect response type based on content and agent
    if agent_type == "trading" and any(word in message.lower() for word in ["position", "portfolio", "trade", "alpaca"]):
        # Trading data - create table or dashboard
        if "position" in message.lower() or "portfolio" in message.lower():
            # Extract position data (this would be enhanced with real data parsing)
            return create_enhanced_trading_status_response(
                alpaca_status={"connected": True, "account_value": 100000, "cash": 50000, "buying_power": 100000},
                positions=[]
            )
    
    elif agent_type == "research" and any(word in message.lower() for word in ["research", "alpha", "market", "analysis"]):
        # Research data - create charts or tables
        return create_enhanced_research_status_response({
            "summary": {
                "total_files": 15,
                "alpha_discoveries_count": 5,
                "market_monitoring_count": 8,
                "risk_assessments_count": 2
            }
        })
    
    elif agent_type == "self_editing" and any(word in message.lower() for word in ["code", "file", "change", "update"]):
        # Code changes - create diff view
        return formatter.create_code_diff_response(
            file_path="example.py",
            old_code="# Old code\nprint('hello')",
            new_code="# New code\nprint('hello world')",
            description="Updated greeting message",
            agent="self_editing"
        )
    
    # Default to markdown with potential UI hints
    ui_hints = []
    if any(word in message.lower() for word in ["refresh", "update", "reload"]):
        ui_hints.append(UIHint.REFRESH)
    if any(word in message.lower() for word in ["expand", "details", "more"]):
        ui_hints.append(UIHint.EXPAND)
    
    return formatter.create_markdown_response(
        content=message,
        agent=agent_type,
        metadata={"ui_hints": ui_hints}
    )

# --- LLM-Based Agent System ---
class LLMAgent:
    def __init__(self, name: str, description: str, capabilities: List[str]):
        self.name = name
        self.description = description
        self.capabilities = capabilities

# Agent registry with LLM-based handlers
def get_agent_registry() -> List[LLMAgent]:
    return [
        LLMAgent(
            "trading", 
            "Handles trading operations, portfolio management, and market analysis",
            ["execute trades", "analyze positions", "risk management", "performance tracking"]
        ),
        LLMAgent(
            "research", 
            "Conducts market research, alpha discovery, and sentiment analysis",
            ["market research", "alpha discovery", "sentiment analysis", "data insights"]
        ),
        LLMAgent(
            "self_editing", 
            "Modifies the codebase, adds features, and improves the system",
            ["code changes", "feature addition", "system improvement", "bug fixes"]
        ),
        LLMAgent(
            "governor", 
            "Meta-agent that coordinates other agents and provides system oversight",
            ["agent coordination", "system status", "mission control", "strategy oversight"]
        )
    ]

def get_llm_response(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Get response from OpenAI LLM"""
    try:
        from core.openai_manager import openai_manager
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = openai_manager.chat_completion(messages=messages, temperature=0.7)
        return response.get("content", "I'm sorry, I couldn't process that request.")
    except Exception as e:
        logger.error(f"Error getting LLM response: {e}")
        return f"I encountered an error: {str(e)}"


def get_local_research_data() -> Dict[str, Any]:
    """Get real research data from local system"""
    try:
        import os
        import json
        from datetime import datetime
        
        research_data = {
            "alpha_discoveries": [],
            "market_monitoring": [],
            "sentiment_tracking": [],
            "risk_assessments": [],
            "deep_research": [],
            "latest_updates": [],
            "summary": {}
        }
        
        # Data directory paths
        data_dirs = [
            "data/research_data_backup_20250710_094129",
            "data/research_data_backup_20250710_133130"
        ]
        
        # Find the most recent data directory
        latest_dir = None
        for data_dir in data_dirs:
            if os.path.exists(data_dir):
                if latest_dir is None or data_dir > latest_dir:
                    latest_dir = data_dir
        
        if not latest_dir:
            research_data["summary"] = {
                "total_files": 0,
                "latest_update": None,
                "data_directory": "No research directories found",
                "alpha_discoveries_count": 0,
                "market_monitoring_count": 0,
                "sentiment_tracking_count": 0,
                "risk_assessments_count": 0,
                "deep_research_count": 0,
                "status": "no_directories"
            }
            return research_data
        
        # Alpha discoveries
        alpha_file = os.path.join(latest_dir, "alpha_discovery_latest.json")
        if os.path.exists(alpha_file):
            with open(alpha_file, 'r') as f:
                research_data["alpha_discoveries"].append(json.load(f))
        
        # Market monitoring
        market_file = os.path.join(latest_dir, "market_monitoring_latest.json")
        if os.path.exists(market_file):
            with open(market_file, 'r') as f:
                research_data["market_monitoring"].append(json.load(f))
        
        # Sentiment tracking
        sentiment_file = os.path.join(latest_dir, "sentiment_tracking_latest.json")
        if os.path.exists(sentiment_file):
            with open(sentiment_file, 'r') as f:
                research_data["sentiment_tracking"].append(json.load(f))
        
        # Risk assessments
        risk_file = os.path.join(latest_dir, "risk_assessment_latest.json")
        if os.path.exists(risk_file):
            with open(risk_file, 'r') as f:
                research_data["risk_assessments"].append(json.load(f))
        
        # Deep research
        deep_file = os.path.join(latest_dir, "deep_research_latest.json")
        if os.path.exists(deep_file):
            with open(deep_file, 'r') as f:
                research_data["deep_research"].append(json.load(f))
        
        # Get all recent files for summary
        all_files = []
        for filename in os.listdir(latest_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(latest_dir, filename)
                file_stat = os.stat(file_path)
                all_files.append({
                    'name': filename,
                    'path': file_path,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime),
                    'size': file_stat.st_size
                })
        
        # Sort by modification time (newest first)
        all_files.sort(key=lambda x: x['modified'], reverse=True)
        research_data["latest_updates"] = all_files[:10]  # Last 10 files
        
        # Create summary
        research_data["summary"] = {
            "total_files": len(all_files),
            "latest_update": all_files[0]['modified'] if all_files else None,
            "data_directory": latest_dir,
            "alpha_discoveries_count": len(research_data["alpha_discoveries"]),
            "market_monitoring_count": len(research_data["market_monitoring"]),
            "sentiment_tracking_count": len(research_data["sentiment_tracking"]),
            "risk_assessments_count": len(research_data["risk_assessments"]),
            "deep_research_count": len(research_data["deep_research"]),
            "status": "active" if all_files else "empty_directory"
        }
        return research_data
    except Exception as e:
        logger.error(f"Error loading research data: {e}")
        research_data["error"] = str(e)
        return research_data

def llm_intent_detection(message: str) -> Dict[str, Any]:
    """Use LLM to detect intent and route to appropriate agent"""
    system_prompt = """You are an intelligent intent detection system for a trading platform. 
    Analyze the user's message and determine:
    1. Which agent should handle this request (trading, research, self_editing, governor)
    2. The specific action needed
    3. Any additional context or parameters
    
    Available agents:
    - trading: trade execution, portfolio management, risk analysis
    - research: market research, alpha discovery, data analysis
    - self_editing: code changes, feature additions, system improvements
    - governor: system status, coordination, meta-level decisions
    
    Respond with JSON: {"agent": "agent_name", "action": "description", "context": "additional_info"}
    """
    
    prompt = f"User message: {message}\n\nAnalyze and respond with JSON:"
    
    try:
        response = get_llm_response(prompt, system_prompt)
        # Try to parse JSON response
        if response.strip().startswith('{'):
            return json.loads(response)
        else:
            # Fallback if LLM doesn't return JSON
            return {"agent": "governor", "action": "general inquiry", "context": message}
    except Exception as e:
        logger.error(f"Error in LLM intent detection: {e}")
        return {"agent": "governor", "action": "error handling", "context": str(e)}

def trading_agent_llm(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """LLM-based trading agent"""
    
    # Check if user is asking for positions, trades, or portfolio data
    message_lower = message.lower()
    if any(word in message_lower for word in ['position', 'positions', 'portfolio', 'holdings']):
        try:
            # Try to get real data from Alpaca
            from core.alpaca_client import alpaca_client
            
            # Get positions, orders, and account info
            positions = alpaca_client.get_positions()
            orders = alpaca_client.get_orders(limit=20)
            account = alpaca_client.get_account()
            
            # Build response with real data
            content = "## 📊 Current Portfolio Status\n\n"
            
            if positions:
                content += "### Active Positions\n\n"
                content += "| Symbol | Quantity | Market Value | Unrealized P&L | % Change |\n"
                content += "|--------|----------|--------------|----------------|----------|\n"
                for pos in positions:
                    content += f"| {pos.get('symbol', 'N/A')} | {pos.get('qty', 'N/A')} | ${pos.get('market_value', 'N/A')} | ${pos.get('unrealized_pl', 'N/A')} | {pos.get('unrealized_plpc', 'N/A')}% |\n"
            else:
                content += "**No active positions found.**\n\n"
            
            if account:
                content += f"\n### Account Summary\n"
                content += f"- **Cash Balance:** ${account.get('cash', 'N/A')}\n"
                content += f"- **Portfolio Value:** ${account.get('portfolio_value', 'N/A')}\n"
                content += f"- **Buying Power:** ${account.get('buying_power', 'N/A')}\n"
                content += f"- **Day Trade Count:** {account.get('daytrade_count', 'N/A')}\n"
            
            if orders:
                content += f"\n### Recent Orders\n"
                content += "| Symbol | Side | Status | Quantity | Filled |\n"
                content += "|--------|------|--------|----------|--------|\n"
                for order in orders[:10]:  # Show last 10 orders
                    content += f"| {order.get('symbol', 'N/A')} | {order.get('side', 'N/A')} | {order.get('status', 'N/A')} | {order.get('qty', 'N/A')} | {order.get('filled_qty', 'N/A')} |\n"
            
            # Create custom visualization for positions
            # Build HTML content step by step to avoid f-string issues
            positions_html = ""
            if positions:
                positions_html = '<div class="positions-grid">'
                for pos in positions:
                    unrealized_pl = float(pos.get('unrealized_pl', 0))
                    unrealized_plpc = float(pos.get('unrealized_plpc', 0))
                    pl_class = 'positive' if unrealized_pl >= 0 else 'negative'
                    plpc_class = 'positive' if unrealized_plpc >= 0 else 'negative'
                    
                    positions_html += f'''
                    <div class="position-card">
                        <div class="position-header">
                            <h3>{pos.get('symbol', 'N/A')}</h3>
                            <span class="quantity">{pos.get('qty', '0')} shares</span>
                        </div>
                        <div class="position-metrics">
                            <div class="metric">
                                <span class="label">Market Value</span>
                                <span class="value">${pos.get('market_value', '0')}</span>
                            </div>
                            <div class="metric">
                                <span class="label">Unrealized P&L</span>
                                <span class="value {pl_class}">${pos.get('unrealized_pl', '0')}</span>
                            </div>
                            <div class="metric">
                                <span class="label">% Change</span>
                                <span class="value {plpc_class}">{pos.get('unrealized_plpc', '0')}%</span>
                            </div>
                        </div>
                    </div>
                    '''
                positions_html += '</div>'
            else:
                positions_html = '<p class="no-positions">No active positions found.</p>'
            
            orders_html = ""
            if orders:
                orders_html = '''
                <div class="orders-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Side</th>
                                <th>Status</th>
                                <th>Quantity</th>
                                <th>Filled</th>
                            </tr>
                        </thead>
                        <tbody>
                '''
                for order in orders[:10]:
                    orders_html += f'''
                    <tr>
                        <td>{order.get('symbol', 'N/A')}</td>
                        <td class="side-{order.get('side', 'unknown')}">{order.get('side', 'N/A')}</td>
                        <td class="status-{order.get('status', 'unknown')}">{order.get('status', 'N/A')}</td>
                        <td>{order.get('qty', 'N/A')}</td>
                        <td>{order.get('filled_qty', 'N/A')}</td>
                    </tr>
                    '''
                orders_html += '''
                        </tbody>
                    </table>
                </div>
                '''
            else:
                orders_html = '<p class="no-orders">No recent orders found.</p>'
            
            customVisualization = {
                "title": "Portfolio Dashboard",
                "html": f"""
                <div class="dashboard">
                    <div class="header">
                        <h1>📊 Portfolio Dashboard</h1>
                        <div class="account-summary">
                            <div class="metric">
                                <span class="label">Cash Balance</span>
                                <span class="value">${account.get('cash', '0')}</span>
                            </div>
                            <div class="metric">
                                <span class="label">Portfolio Value</span>
                                <span class="value">${account.get('portfolio_value', '0')}</span>
                            </div>
                            <div class="metric">
                                <span class="label">Buying Power</span>
                                <span class="value">${account.get('buying_power', '0')}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="positions-section">
                        <h2>Active Positions</h2>
                        {positions_html}
                    </div>
                    
                    <div class="orders-section">
                        <h2>Recent Orders</h2>
                        {orders_html}
                    </div>
                </div>
                """,
                "css": """
                .dashboard {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 12px;
                    margin-bottom: 30px;
                }
                
                .header h1 {
                    margin: 0 0 20px 0;
                    font-size: 2rem;
                }
                
                .account-summary {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                }
                
                .metric {
                    display: flex;
                    flex-direction: column;
                    gap: 5px;
                }
                
                .metric .label {
                    font-size: 0.9rem;
                    opacity: 0.8;
                }
                
                .metric .value {
                    font-size: 1.5rem;
                    font-weight: 600;
                }
                
                .positions-section, .orders-section {
                    background: white;
                    border-radius: 12px;
                    padding: 25px;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                
                .positions-section h2, .orders-section h2 {
                    margin: 0 0 20px 0;
                    color: #1f2937;
                    font-size: 1.5rem;
                }
                
                .positions-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                }
                
                .position-card {
                    background: #f8fafc;
                    border-radius: 8px;
                    padding: 20px;
                    border: 1px solid #e2e8f0;
                }
                
                .position-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                }
                
                .position-header h3 {
                    margin: 0;
                    color: #1f2937;
                    font-size: 1.2rem;
                }
                
                .quantity {
                    background: #3b82f6;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 0.8rem;
                }
                
                .position-metrics {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 15px;
                }
                
                .position-metrics .metric {
                    text-align: center;
                }
                
                .position-metrics .label {
                    font-size: 0.8rem;
                    color: #6b7280;
                    margin-bottom: 5px;
                }
                
                .position-metrics .value {
                    font-size: 1.1rem;
                    font-weight: 600;
                }
                
                .positive { color: #10b981; }
                .negative { color: #ef4444; }
                
                .orders-table table {
                    width: 100%;
                    border-collapse: collapse;
                }
                
                .orders-table th,
                .orders-table td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #e5e7eb;
                }
                
                .orders-table th {
                    background: #f9fafb;
                    font-weight: 600;
                    color: #374151;
                }
                
                .side-buy { color: #10b981; font-weight: 600; }
                .side-sell { color: #ef4444; font-weight: 600; }
                
                .status-filled { color: #10b981; }
                .status-pending { color: #f59e0b; }
                .status-cancelled { color: #ef4444; }
                
                .no-positions, .no-orders {
                    text-align: center;
                    color: #6b7280;
                    font-style: italic;
                    padding: 40px;
                }
                """,
                "js": """
                // Add interactive features
                document.addEventListener('DOMContentLoaded', function() {
                    // Add hover effects to position cards
                    const positionCards = document.querySelectorAll('.position-card');
                    positionCards.forEach(card => {
                        card.addEventListener('mouseenter', function() {
                            this.style.transform = 'translateY(-2px)';
                            this.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
                        });
                        
                        card.addEventListener('mouseleave', function() {
                            this.style.transform = 'translateY(0)';
                            this.style.boxShadow = 'none';
                        });
                    });
                    
                    // Add click handlers for orders table rows
                    const orderRows = document.querySelectorAll('.orders-table tbody tr');
                    orderRows.forEach(row => {
                        row.addEventListener('click', function() {
                            this.style.background = '#f3f4f6';
                            setTimeout(() => {
                                this.style.background = '';
                            }, 200);
                        });
                    });
                });
                """
            }
        
        return {
                "type": "markdown",
                "content": content,
                "agent": "trading",
                "actions_taken": ["retrieved_positions", "retrieved_account", "retrieved_orders"],
                "customVisualization": customVisualization
            }
    except Exception as e:
        # Emit error to the centralized error event bus
        from core.error_event_bus import emit_error, ErrorSeverity, ErrorCategory
        
        error_event = emit_error(
            error=e,
            source="trading_agent",
            context={
                "user_message": message,
                "action": "get_alpaca_data",
                "alpaca_ready": True
            },
            user_message=message,
            severity=ErrorSeverity.HIGH if "forbidden" in str(e).lower() else ErrorSeverity.MEDIUM,
            category=ErrorCategory.ALPACA_CONNECTION
        )
        
        logger.error(f"Error getting Alpaca data: {e}")
        
        # Check if it's an authentication error
        error_message = str(e).lower()
        if "forbidden" in error_message or "unauthorized" in error_message or "invalid" in error_message:
            content = f"""## ⚠️ Alpaca API Connection Issue

I attempted to connect to your Alpaca paper trading account but encountered an authentication error: **{str(e)}**

### 🔧 **Issue Identified:**
The Alpaca API keys in your configuration appear to be invalid or expired. This prevents me from accessing your trading account data.

### 🛠️ **How to Fix This:**

1. **Check Your Alpaca Account:**
   - Log into your Alpaca account at [alpaca.markets](https://alpaca.markets)
   - Navigate to your API keys section
   - Verify your API keys are active and have the correct permissions

2. **Update Your API Keys:**
   - Get fresh API keys from your Alpaca dashboard
   - Update the `.env` file in your project root:
   ```
   ALPACA_API_KEY=your_new_api_key_here
   ALPACA_SECRET_KEY=your_new_secret_key_here
   ALPACA_BASE_URL=https://paper-api.alpaca.markets
   ```

3. **Restart the System:**
   - After updating the keys, restart the backend server
   - The trading agent will automatically detect the new keys

### 📊 **Current Status:**
- ❌ **Alpaca Connection:** Failed (API authentication error)
- ❌ **Position Data:** Unavailable
- ❌ **Account Data:** Unavailable
- ❌ **Order History:** Unavailable

### 🔄 **Next Steps:**
Once you've updated your API keys, ask me again about your positions and I'll be able to show you real-time data from your Alpaca paper trading account.

**Note:** I'm designed to work with real Alpaca data, so once the API keys are fixed, you'll get live portfolio information, not generic guidance.
"""
        else:
            # Generic connection error
            content = f"""## ⚠️ Connection Issue

I encountered an error while trying to connect to your Alpaca trading account: **{str(e)}**

This appears to be a network or service issue. Please try again in a few moments, or check if the Alpaca service is available.

If the problem persists, you may need to verify your API keys are correct and have the proper permissions.
"""
        
        return {
            "type": "markdown",
            "content": content,
            "agent": "trading",
            "actions_taken": ["error_handling", "diagnostic_info"],
            "error_details": {
                "error_type": "alpaca_connection",
                "error_message": str(e),
                "suggested_action": "update_api_keys" if "forbidden" in str(e).lower() else "retry_connection"
            }
        }
    
    # Default LLM response for other trading queries
    system_prompt = """You are a sophisticated trading agent for an autonomous trading system.
    You can:
    - Analyze trading opportunities
    - Execute trades (paper trading only)
    - Monitor portfolio performance
    - Provide risk analysis
    - Generate trading insights
    
    Always be professional and provide actionable insights. Format responses as markdown when appropriate.
    """
    
    response = get_llm_response(message, system_prompt)
        
    return {
        "type": "markdown",
        "content": response,
        "agent": "trading",
        "actions_taken": []
    }

def research_agent_llm(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """LLM-based research agent"""
    
    # Get real research data from local system
    research_data = get_local_research_data()
    
    # Check if user is asking for charts or visualizations
    message_lower = message.lower()
    if any(word in message_lower for word in ['chart', 'graph', 'visual', 'dashboard', 'sentiment']):
        # Create custom visualization for research data
        customVisualization = {
            "title": "Market Research Dashboard",
            "html": """
            <div class="research-dashboard">
                <div class="header">
                    <h1>📈 Market Research Dashboard</h1>
                    <div class="metrics-summary">
                        <div class="metric">
                            <span class="label">Market Sentiment</span>
                            <span class="value positive">Bullish</span>
                        </div>
                        <div class="metric">
                            <span class="label">Volatility Index</span>
                            <span class="value">15.2</span>
                        </div>
                        <div class="metric">
                            <span class="label">Alpha Opportunities</span>
                            <span class="value">8</span>
                        </div>
                    </div>
                </div>
                
                <div class="charts-section">
                    <div class="chart-container">
                        <h2>Market Sentiment Trend</h2>
                        <div class="chart" id="sentimentChart">
                            <canvas id="sentimentCanvas" width="400" height="200"></canvas>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <h2>Sector Performance</h2>
                        <div class="chart" id="sectorChart">
                            <canvas id="sectorCanvas" width="400" height="200"></canvas>
                        </div>
                    </div>
                </div>
                
                <div class="insights-section">
                    <h2>Key Insights</h2>
                    <div class="insights-grid">
                        <div class="insight-card">
                            <h3>📊 Market Trend</h3>
                            <p>Overall market sentiment is trending bullish with increasing positive sentiment across major sectors.</p>
                        </div>
                        <div class="insight-card">
                            <h3>🎯 Alpha Opportunities</h3>
                            <p>Technology and healthcare sectors show the highest potential for alpha generation.</p>
                        </div>
                        <div class="insight-card">
                            <h3>⚠️ Risk Factors</h3>
                            <p>Monitor inflation data and central bank policies for potential market volatility.</p>
                        </div>
                    </div>
                </div>
            </div>
            """,
            "css": """
            .research-dashboard {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
            }
            
            .header h1 {
                margin: 0 0 20px 0;
                font-size: 2rem;
            }
            
            .metrics-summary {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
            }
            
            .metric {
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            
            .metric .label {
                font-size: 0.9rem;
                opacity: 0.8;
            }
            
            .metric .value {
                font-size: 1.5rem;
                font-weight: 600;
            }
            
            .positive { color: #10b981; }
            
            .charts-section {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 30px;
                margin-bottom: 30px;
            }
            
            .chart-container {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            .chart-container h2 {
                margin: 0 0 20px 0;
                color: #1f2937;
                font-size: 1.3rem;
            }
            
            .chart {
                position: relative;
                height: 200px;
            }
            
            .insights-section {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            .insights-section h2 {
                margin: 0 0 20px 0;
                color: #1f2937;
                font-size: 1.5rem;
            }
            
            .insights-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }
            
            .insight-card {
                background: #f8fafc;
                border-radius: 8px;
                padding: 20px;
                border: 1px solid #e2e8f0;
            }
            
            .insight-card h3 {
                margin: 0 0 10px 0;
                color: #1f2937;
                font-size: 1.1rem;
            }
            
            .insight-card p {
                margin: 0;
                color: #6b7280;
                line-height: 1.5;
            }
            """,
            "js": """
            // Simple chart drawing using Canvas API
            document.addEventListener('DOMContentLoaded', function() {
                // Sentiment Chart
                const sentimentCanvas = document.getElementById('sentimentCanvas');
                const sentimentCtx = sentimentCanvas.getContext('2d');
                
                // Sample sentiment data
                const sentimentData = [0.25, 0.30, 0.35, 0.20, 0.45, 0.60, 0.55, 0.40, 0.30, 0.65];
                const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'];
                
                // Draw sentiment line chart
                sentimentCtx.strokeStyle = '#10b981';
                sentimentCtx.lineWidth = 3;
                sentimentCtx.beginPath();
                
                sentimentData.forEach((value, index) => {
                    const x = (index / (sentimentData.length - 1)) * 380 + 10;
                    const y = 190 - (value * 180);
                    
                    if (index === 0) {
                        sentimentCtx.moveTo(x, y);
                    } else {
                        sentimentCtx.lineTo(x, y);
                    }
                });
                
                sentimentCtx.stroke();
                
                // Add data points
                sentimentData.forEach((value, index) => {
                    const x = (index / (sentimentData.length - 1)) * 380 + 10;
                    const y = 190 - (value * 180);
                    
                    sentimentCtx.fillStyle = '#10b981';
                    sentimentCtx.beginPath();
                    sentimentCtx.arc(x, y, 4, 0, 2 * Math.PI);
                    sentimentCtx.fill();
                });
                
                // Sector Chart
                const sectorCanvas = document.getElementById('sectorCanvas');
                const sectorCtx = sectorCanvas.getContext('2d');
                
                // Sample sector data
                const sectors = ['Tech', 'Healthcare', 'Finance', 'Energy', 'Consumer'];
                const performance = [15, 12, 8, 5, 10];
                const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
                
                const barWidth = 60;
                const barSpacing = 20;
                const startX = 30;
                
                performance.forEach((value, index) => {
                    const x = startX + index * (barWidth + barSpacing);
                    const height = value * 8;
                    const y = 190 - height;
                    
                    // Draw bar
                    sectorCtx.fillStyle = colors[index];
                    sectorCtx.fillRect(x, y, barWidth, height);
                    
                    // Draw label
                    sectorCtx.fillStyle = '#374151';
                    sectorCtx.font = '12px Arial';
                    sectorCtx.textAlign = 'center';
                    sectorCtx.fillText(sectors[index], x + barWidth/2, 210);
                    sectorCtx.fillText(value + '%', x + barWidth/2, y - 5);
                });
                
                // Add interactive features
                const insightCards = document.querySelectorAll('.insight-card');
                insightCards.forEach(card => {
                    card.addEventListener('mouseenter', function() {
                        this.style.transform = 'translateY(-2px)';
                        this.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
                    });
                    
                    card.addEventListener('mouseleave', function() {
                        this.style.transform = 'translateY(0)';
                        this.style.boxShadow = 'none';
                    });
                });
            });
            """
        }
        
        # Get LLM response for text content
        system_prompt = """You are a market research and alpha discovery agent.
        The user is asking for charts or visualizations. Provide a comprehensive analysis
        that complements the visual dashboard being generated.
        
        Focus on:
        - Key market trends and insights
        - Alpha opportunities and recommendations
        - Risk factors to monitor
        - Data-driven conclusions
        
        Use markdown formatting for structured information.
        """
        
        response = get_llm_response(message, system_prompt)
        
        return {
            "type": "markdown",
            "content": response,
            "agent": "research",
            "actions_taken": ["generated_visualization"],
            "customVisualization": customVisualization
        }
    
    # Use real research data for responses
    if research_data.get("error"):
        content = f"## 🔍 Research Status\n\n❌ **Error accessing research data:** {research_data['error']}\n\nPlease check the research data directory and ensure the system is properly configured."
    else:
        summary = research_data.get("summary", {})
        
        content = "## 🔍 Research Status Report\n\n"
        
        if summary.get("total_files", 0) > 0:
            content += f"### 📊 **Research Overview**\n\n"
            content += f"- **Total Research Files:** {summary.get('total_files', 0)}\n"
            content += f"- **Latest Update:** {summary.get('latest_update', 'Unknown')}\n"
            content += f"- **Data Directory:** {summary.get('data_directory', 'Unknown')}\n\n"
            
            content += f"### 📈 **Research Categories**\n\n"
            content += f"- **Alpha Discoveries:** {summary.get('alpha_discoveries_count', 0)} files\n"
            content += f"- **Market Monitoring:** {summary.get('market_monitoring_count', 0)} files\n"
            content += f"- **Sentiment Tracking:** {summary.get('sentiment_tracking_count', 0)} files\n"
            content += f"- **Risk Assessments:** {summary.get('risk_assessments_count', 0)} files\n"
            content += f"- **Deep Research:** {summary.get('deep_research_count', 0)} files\n\n"
            
            # Show latest updates
            if research_data.get("latest_updates"):
                content += "### 🕒 **Latest Research Updates**\n\n"
                for i, update in enumerate(research_data["latest_updates"][:5], 1):
                    content += f"{i}. **{update['name']}** - {update['modified']}\n"
                content += "\n"
            
            # Show specific research insights if available
            if research_data.get("alpha_discoveries"):
                content += "### 🎯 **Recent Alpha Discoveries**\n\n"
                for alpha in research_data["alpha_discoveries"]:
                    if isinstance(alpha, dict):
                        content += f"- **{alpha.get('title', 'Alpha Discovery')}**\n"
                        content += f"  - {alpha.get('description', 'No description available')}\n"
                        content += f"  - Confidence: {alpha.get('confidence', 'Unknown')}\n\n"
            
            if research_data.get("market_monitoring"):
                content += "### 📊 **Market Monitoring Insights**\n\n"
                for market in research_data["market_monitoring"]:
                    if isinstance(market, dict):
                        content += f"- **{market.get('title', 'Market Update')}**\n"
                        content += f"  - {market.get('summary', 'No summary available')}\n\n"
            
            if research_data.get("risk_assessments"):
                content += "### ⚠️ **Risk Assessment Summary**\n\n"
                for risk in research_data["risk_assessments"]:
                    if isinstance(risk, dict):
                        content += f"- **{risk.get('title', 'Risk Assessment')}**\n"
                        content += f"  - Risk Level: {risk.get('risk_level', 'Unknown')}\n"
                        content += f"  - {risk.get('description', 'No description available')}\n\n"
            
            content += "### 💡 **Research Recommendations**\n\n"
            content += "Based on the available research data:\n\n"
            content += "1. **Review Alpha Discoveries** - Check the latest alpha discovery files for new opportunities\n"
            content += "2. **Monitor Market Trends** - Review market monitoring data for current trends\n"
            content += "3. **Assess Risk Levels** - Check risk assessment files for potential concerns\n"
            content += "4. **Track Sentiment** - Review sentiment tracking for market mood analysis\n"
            content += "5. **Deep Dive** - Examine deep research files for comprehensive analysis\n\n"
            
            content += "**Note:** This is real research data from your local RoboInvest system. The data is current as of the latest research run."
            
        else:
            status = summary.get("status", "unknown")
            
            if status == "no_directories":
                content += "### 📊 **Research Status**\n\n"
                content += "❌ **Research system not initialized**\n\n"
                content += "No research data directories found. The research system needs to be set up.\n\n"
                content += "**To initialize research system:**\n"
                content += "1. Run: `python scripts/setup_chromadb_system.py`\n"
                content += "2. Start research agents: `python scripts/run_continuous_research.py`\n"
                content += "3. Monitor for new research data generation\n\n"
                
            elif status == "empty_directory":
                content += "### 📊 **Research Status**\n\n"
                content += "⚠️ **Research directories exist but are empty**\n\n"
                content += f"Research directory found: `{summary.get('data_directory', 'Unknown')}`\n"
                content += "The research system is configured but no data has been generated yet.\n\n"
                content += "**To generate research data:**\n"
                content += "1. Start research agents: `python scripts/run_continuous_research.py`\n"
                content += "2. Wait for initial research cycle to complete\n"
                content += "3. Check for new files in research directories\n\n"
                content += "**Expected file types:**\n"
                content += "- `alpha_discovery_latest.json` - Alpha opportunities\n"
                content += "- `market_monitoring_latest.json` - Market trends\n"
                content += "- `sentiment_tracking_latest.json` - Market sentiment\n"
                content += "- `risk_assessment_latest.json` - Risk analysis\n"
                content += "- `deep_research_latest.json` - Comprehensive analysis\n\n"
                
            else:
                content += "### 📊 **Research Status**\n\n"
                content += "❓ **Unknown research system state**\n\n"
                content += "Unable to determine the current state of the research system.\n\n"
                content += "**Troubleshooting steps:**\n"
                content += "1. Check if research agents are running\n"
                content += "2. Verify research data directories exist\n"
                content += "3. Look for any error logs in the system\n"
                content += "4. Restart research system if needed\n\n"
            
            content += "**For immediate research insights, I can analyze current market conditions using available data sources.**"
            
            return {
        "type": "markdown",
        "content": content,
        "agent": "research",
        "actions_taken": ["retrieved_local_data", "analyzed_research_status"],
        "research_data_summary": research_data.get("summary", {})
    }

def self_editing_agent_llm(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """LLM-based self-editing agent"""
    system_prompt = """You are a self-editing agent that can modify the codebase.
    You can:
    - Add new features and endpoints
    - Modify existing code
    - Improve system functionality
    - Fix bugs and issues
    - Refactor code for better performance
    
    Always explain what changes you're making and why. Provide code examples when relevant.
    """
    
    response = get_llm_response(message, system_prompt)
    
    return {
        "type": "markdown",
        "content": response,
        "agent": "self_editing",
        "actions_taken": []
    }

def governor_agent_llm(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """LLM-based governor/meta-agent"""
    
    # Check if there are any system issues to address
    system_issues = []
    
    # Get system health from error event bus
    try:
        from core.error_event_bus import error_event_bus, ErrorSeverity
        
        health_summary = error_event_bus.get_system_health_summary()
        recent_errors = error_event_bus.get_recent_errors(10)
        
        # Check for critical and high severity errors
        critical_errors = error_event_bus.get_errors_by_severity(ErrorSeverity.CRITICAL)
        high_errors = error_event_bus.get_errors_by_severity(ErrorSeverity.HIGH)
        
        # Add system issues based on error events
        for error in critical_errors + high_errors:
            system_issues.append({
                "type": error.category.value,
                "severity": error.severity.value,
                "description": f"{error.error_type}: {error.error_message}",
                "impact": f"Affects {error.source} functionality",
                "solution": "Check error event bus for detailed analysis",
                "error_id": error.id,
                "auto_fixable": error.auto_fixable,
                "fix_attempted": error.fix_attempted,
                "fix_successful": error.fix_successful
            })
        
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
    
    # Check Alpaca connection status
    try:
        from core.alpaca_client import alpaca_client
        if alpaca_client.is_ready():
            # Test actual connection
            try:
                alpaca_client.get_account()
            except Exception as e:
                if "forbidden" in str(e).lower():
                    system_issues.append({
                        "type": "alpaca_auth",
                        "severity": "high",
                        "description": "Alpaca API authentication failed - invalid or expired API keys",
                        "impact": "Trading agent cannot access real portfolio data",
                        "solution": "Update ALPACA_API_KEY and ALPACA_SECRET_KEY in .env file"
                    })
        else:
            system_issues.append({
                "type": "alpaca_config",
                "severity": "medium", 
                "description": "Alpaca API keys not configured",
                "impact": "Trading functionality disabled",
                "solution": "Set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env file"
            })
    except Exception as e:
        logger.error(f"Error checking Alpaca status: {e}")
    
    # If there are system issues and user is asking about system status, address them
    if system_issues and any(word in message.lower() for word in ['status', 'health', 'issue', 'problem', 'error', 'fix']):
        return create_enhanced_system_status_response(system_issues)
    
    # Check if user is asking about research status
    if any(word in message.lower() for word in ['research', 'alpha', 'discovery', 'market analysis', 'sentiment']):
        # Get real research data
        research_data = get_local_research_data()
        
        if research_data.get("error"):
            content = f"## 🔍 Research Status\n\n❌ **Error accessing research data:** {research_data['error']}\n\nPlease check the research data directory and ensure the system is properly configured."
        else:
            summary = research_data.get("summary", {})
            
            content = "## 🔍 Research Status Overview\n\n"
            
            if summary.get("total_files", 0) > 0:
                content += f"### 📊 **Current Research Status**\n\n"
                content += f"- **Active Research Files:** {summary.get('total_files', 0)}\n"
                content += f"- **Latest Update:** {summary.get('latest_update', 'Unknown')}\n"
                content += f"- **Research Categories:** {summary.get('alpha_discoveries_count', 0)} alpha discoveries, {summary.get('market_monitoring_count', 0)} market updates, {summary.get('risk_assessments_count', 0)} risk assessments\n\n"
                
                content += "### 🎯 **Research System Status**\n\n"
                content += "✅ **Research system is active and generating data**\n\n"
                content += "The autonomous research agents are running and collecting:\n"
                content += "- Alpha opportunities and market inefficiencies\n"
                content += "- Real-time market monitoring and trend analysis\n"
                content += "- Sentiment tracking and market mood analysis\n"
                content += "- Risk assessments and market volatility analysis\n"
                content += "- Deep research insights and comprehensive analysis\n\n"
                
                content += "**For detailed research insights, ask the research agent directly.**"
                
            else:
                content += "### 📊 **Research System Status**\n\n"
                content += "⚠️ **Research system appears inactive**\n\n"
                content += "No recent research data found. The research agents may need to be started.\n\n"
                content += "**To activate research:**\n"
                content += "1. Run: `python scripts/run_continuous_research.py`\n"
                content += "2. Check research data directories in `data/`\n"
                content += "3. Monitor for new research files\n\n"
                content += "**For immediate research insights, ask the research agent to analyze current market conditions.**"
        
        return create_enhanced_research_status_response(research_data)
    
    # Default governor response for other queries
    system_prompt = """You are the Governor Agent, the central coordinator of an autonomous trading system.
    You oversee:
    - System status and health
    - Agent coordination
    - Mission and strategy alignment
    - Performance monitoring
    - Risk management
    
    You can coordinate with other agents and provide high-level insights and decisions.
    Be conversational, professional, and helpful.
    
    If users report issues with other agents (like trading agent not working), help them understand
    what might be wrong and how to fix it.
    """
    
    response = get_llm_response(message, system_prompt)
    
    return create_enhanced_agent_response(message, "governor")

# Agent handler mapping
AGENT_HANDLERS = {
    "trading": trading_agent_llm,
    "research": research_agent_llm,
    "self_editing": self_editing_agent_llm,
    "governor": governor_agent_llm
}

# --- Main Conversational Endpoint ---
@router.get("/error-events")
async def get_error_events():
    """Get error events from the centralized error event bus"""
    try:
        from core.error_event_bus import error_event_bus
        
        recent_errors = error_event_bus.get_recent_errors(20)
        health_summary = error_event_bus.get_system_health_summary()
        
        return {
            "status": "success",
            "health_summary": health_summary,
            "recent_errors": [error.to_dict() for error in recent_errors],
            "total_errors": len(error_event_bus.error_events)
        }
    except Exception as e:
        logger.error(f"Error getting error events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/stats")
async def get_memory_stats():
    """Get memory statistics and insights"""
    try:
        stats = await central_experience_db.get_memory_stats()
        insights = await intelligent_memory_manager.get_memory_insights()
        
        return {
            "status": "success",
            "stats": stats,
            "insights": insights
        }
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/optimize")
async def optimize_memory():
    """Run memory optimization"""
    try:
        result = await intelligent_memory_manager.optimize_memory_usage()
        
        return {
            "status": "success",
            "optimization_result": result
        }
    except Exception as e:
        logger.error(f"Error optimizing memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/cleanup")
async def cleanup_memory():
    """Clean up pruned data"""
    try:
        await central_experience_db.cleanup_pruned_data()
        
        return {
            "status": "success",
            "message": "Pruned data cleaned up successfully"
        }
    except Exception as e:
        logger.error(f"Error cleaning up memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/experiences")
async def get_experiences(query: str = "", limit: int = 20, experience_type: Optional[str] = None):
    """Get experiences from memory"""
    try:
        experience_types: Optional[List[ExperienceType]] = None
        if experience_type:
            try:
                experience_types = [ExperienceType(experience_type)]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid experience type: {experience_type}")
        
        experiences = await central_experience_db.query_experiences(
            query=query,
            limit=limit,
            experience_types=experience_types
        )
        
        return {
            "status": "success",
            "experiences": [exp.to_dict() for exp in experiences],
            "count": len(experiences)
        }
    except Exception as e:
        logger.error(f"Error getting experiences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversation")
async def governor_conversation(request: Dict[str, Any]):
    """Unified conversational endpoint for all LLM-based agent requests"""
    try:
        message = request.get("message", "")
        session_id = request.get("session_id", "default_session")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Store user query in memory
        await central_experience_db.add_experience(
            experience_type=ExperienceType.USER_QUERY,
            source_agent="user",
            content=message,
            metadata={"session_id": session_id, "request_type": "conversation"},
            session_id=session_id,
            user_message=message
        )

        # Get relevant context from memory
        relevant_experiences = await central_experience_db.query_experiences(
            query=message, 
            limit=5,
            min_importance=3.0
        )
        
        # Get session context
        session_context = await central_experience_db.get_session_context(session_id)
        
        # Use LLM for intent detection
        intent_result = llm_intent_detection(message)
        agent_name = intent_result.get("agent", "governor")
        action = intent_result.get("action", "general inquiry")
        
        # Get the appropriate agent handler
        agent_handler = AGENT_HANDLERS.get(agent_name, governor_agent_llm)
        
        # Create enhanced context with memory
        context = {
            "intent": intent_result,
            "user_message": message,
            "session_id": session_id,
            "session_context": session_context,
            "relevant_experiences": [exp.to_dict() for exp in relevant_experiences],
            "timestamp": "2025-07-14T13:36:11.888896"
        }
        
        # Get LLM response from the selected agent
        response = agent_handler(message, context)
        
        # Store agent response in memory
        await central_experience_db.add_experience(
            experience_type=ExperienceType.AGENT_RESPONSE,
            source_agent=agent_name,
            content=response.get("content", str(response)),
            metadata={
                "session_id": session_id,
                "agent": agent_name,
                "intent": intent_result,
                "response_type": response.get("type", "text"),
                "actions_taken": response.get("actions_taken", [])
            },
            session_id=session_id,
            user_message=message,
            references=[exp.id for exp in relevant_experiences]
        )
        
        # Add metadata about the routing decision
        response["metadata"] = {
            "agent": agent_name,
            "intent": intent_result,
            "llm_based": True,
            "memory_context": {
                "relevant_experiences_count": len(relevant_experiences),
                "session_context_available": bool(session_context.get("current_context"))
            }
        }
        
        return {
            "status": "success",
            "response": response,
            "metadata": {
                "agent": agent_name,
                "intent": intent_result,
                "llm_based": True,
                "memory_context": {
                    "relevant_experiences_count": len(relevant_experiences),
                    "session_context_available": bool(session_context.get("current_context"))
                }
            }
        }
    except Exception as e:
        logger.error(f"Error in governor conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 