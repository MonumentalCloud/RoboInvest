from fastapi import APIRouter, HTTPException
import logging
from typing import Dict, Any, List, Optional
import json

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            logger.error(f"Error getting Alpaca data: {e}")
            # Fallback to LLM response
            system_prompt = """You are a sophisticated trading agent for an autonomous trading system.
            The user is asking about positions or portfolio data, but I couldn't connect to the trading platform.
            Provide helpful guidance on how to check positions and manage portfolios.
            """
            response = get_llm_response(message, system_prompt)
            return {
                "type": "markdown",
                "content": response,
                "agent": "trading",
                "actions_taken": ["fallback_response"]
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
    
    # Default LLM response for other research queries
    system_prompt = """You are a market research and alpha discovery agent.
    You can:
    - Analyze market trends and patterns
    - Identify alpha opportunities
    - Conduct sentiment analysis
    - Generate research insights
    - Provide data-driven recommendations
    
    Use markdown formatting for tables, lists, and structured information.
    """
    
    response = get_llm_response(message, system_prompt)
    
    return {
        "type": "markdown",
        "content": response,
        "agent": "research",
        "actions_taken": []
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
    system_prompt = """You are the Governor Agent, the central coordinator of an autonomous trading system.
    You oversee:
    - System status and health
    - Agent coordination
    - Mission and strategy alignment
    - Performance monitoring
    - Risk management
    
    You can coordinate with other agents and provide high-level insights and decisions.
    Be conversational, professional, and helpful.
    """
    
    response = get_llm_response(message, system_prompt)
    
    return {
        "type": "markdown",
        "content": response,
        "agent": "governor",
        "actions_taken": []
    }

# Agent handler mapping
AGENT_HANDLERS = {
    "trading": trading_agent_llm,
    "research": research_agent_llm,
    "self_editing": self_editing_agent_llm,
    "governor": governor_agent_llm
}

# --- Main Conversational Endpoint ---
@router.post("/conversation")
async def governor_conversation(request: Dict[str, Any]):
    """Unified conversational endpoint for all LLM-based agent requests"""
    try:
        message = request.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Use LLM for intent detection
        intent_result = llm_intent_detection(message)
        agent_name = intent_result.get("agent", "governor")
        action = intent_result.get("action", "general inquiry")
        
        # Get the appropriate agent handler
        agent_handler = AGENT_HANDLERS.get(agent_name, governor_agent_llm)
        
        # Create context with intent information
        context = {
            "intent": intent_result,
            "user_message": message,
            "timestamp": "2025-07-14T13:36:11.888896"
        }
        
        # Get LLM response from the selected agent
        response = agent_handler(message, context)
        
        # Add metadata about the routing decision
        response["metadata"] = {
            "agent": agent_name,
            "intent": intent_result,
            "llm_based": True
        }
        
        return {
            "status": "success",
            "response": response,
            "metadata": {
                "agent": agent_name,
                "intent": intent_result,
                "llm_based": True
            }
        }
    except Exception as e:
        logger.error(f"Error in governor conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))