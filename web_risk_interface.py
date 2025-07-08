"""
Web Interface for LLM-Based AI Risk Assessment System
Hosts the risk system as a web service accessible via browser.
"""

import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socket
from llm_risk_assessment_system import llm_risk_assessor


class RiskAssessmentHandler(BaseHTTPRequestHandler):
    """HTTP handler for the risk assessment web interface."""
    
    def do_GET(self):
        """Handle GET requests for the web interface."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_main_page()
        elif parsed_path.path == '/assess':
            self.send_error(404, "Use POST to /api/assess for risk assessment")
        elif parsed_path.path == '/memory':
            self.serve_memory_page()
        elif parsed_path.path == '/api/memory':
            self.handle_memory_query(parsed_path.query)
        elif parsed_path.path == '/live-demo':
            self.serve_live_demo()
        else:
            self.send_error(404, "Page not found")
    
    def do_POST(self):
        """Handle POST requests for risk assessment."""
        if self.path == '/api/assess':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                context = json.loads(post_data.decode('utf-8'))
                result = llm_risk_assessor.assess_trading_decision(context)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # Convert datetime objects to strings for JSON serialization
                serializable_result = self._make_serializable(result)
                self.wfile.write(json.dumps(serializable_result, indent=2).encode())
                
            except Exception as e:
                self.send_error(500, f"Error processing request: {str(e)}")
        else:
            self.send_error(404, "Endpoint not found")
    
    def _make_serializable(self, obj):
        """Convert objects to JSON serializable format."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj
    
    def serve_main_page(self):
        """Serve the main risk assessment interface."""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 LLM AI Risk Assessment System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        .card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
            overflow: hidden;
        }
        .card-header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 20px;
            font-size: 1.3em;
            font-weight: bold;
        }
        .card-body {
            padding: 25px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }
        .form-control {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        .form-control:focus {
            outline: none;
            border-color: #4facfe;
            box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.1);
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s ease;
            width: 100%;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .result-container {
            display: none;
            margin-top: 20px;
        }
        .risk-level {
            font-size: 2em;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .risk-critical { background: #ffebee; color: #c62828; }
        .risk-high { background: #fff3e0; color: #f57c00; }
        .risk-medium { background: #fff8e1; color: #f9a825; }
        .risk-low { background: #f3e5f5; color: #8e24aa; }
        .risk-minimal { background: #e8f5e8; color: #2e7d32; }
        .reasoning {
            background: #f8f9fa;
            border-left: 4px solid #4facfe;
            padding: 15px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }
        .nav-links {
            text-align: center;
            margin-bottom: 20px;
        }
        .nav-links a {
            color: white;
            text-decoration: none;
            margin: 0 15px;
            padding: 10px 20px;
            border-radius: 25px;
            background: rgba(255,255,255,0.2);
            transition: background 0.3s ease;
        }
        .nav-links a:hover {
            background: rgba(255,255,255,0.3);
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #4facfe;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 LLM AI Risk Assessment System</h1>
            <p>Real-time AI-powered trading risk analysis with memory and learning</p>
        </div>
        
        <div class="nav-links">
            <a href="/">🏠 Risk Assessment</a>
            <a href="/memory">🧠 Memory System</a>
            <a href="/live-demo">🎬 Live Demo</a>
        </div>

        <div class="card">
            <div class="card-header">
                📊 Trading Decision Risk Assessment
            </div>
            <div class="card-body">
                <form id="riskForm">
                    <div class="grid">
                        <div>
                            <div class="form-group">
                                <label for="ticker">Stock Ticker</label>
                                <input type="text" id="ticker" class="form-control" placeholder="e.g., TSLA, AAPL, NVDA" required>
                            </div>
                            <div class="form-group">
                                <label for="action">Action</label>
                                <select id="action" class="form-control" required>
                                    <option value="">Select Action</option>
                                    <option value="BUY">BUY</option>
                                    <option value="SELL">SELL</option>
                                    <option value="HOLD">HOLD</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="confidence">Confidence Level (0.0 - 1.0)</label>
                                <input type="number" id="confidence" class="form-control" step="0.01" min="0" max="1" placeholder="e.g., 0.75" required>
                            </div>
                        </div>
                        <div>
                            <div class="form-group">
                                <label for="position_size">Position Size (0.0 - 1.0)</label>
                                <input type="number" id="position_size" class="form-control" step="0.01" min="0" max="1" placeholder="e.g., 0.15 (15%)" required>
                            </div>
                            <div class="form-group">
                                <label for="sector">Sector</label>
                                <input type="text" id="sector" class="form-control" placeholder="e.g., technology, automotive">
                            </div>
                            <div class="form-group">
                                <label for="market_volatility">Market Volatility</label>
                                <select id="market_volatility" class="form-control">
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high" selected>High</option>
                                    <option value="extreme">Extreme</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <button type="submit" class="btn" id="assessBtn">
                        🔍 Assess Trading Risk
                    </button>
                </form>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>🧠 AI is analyzing your trading decision...</p>
                </div>
                
                <div class="result-container" id="results">
                    <div id="riskLevel" class="risk-level"></div>
                    <div id="decision"></div>
                    <div id="reasoning" class="reasoning"></div>
                    <div id="recommendations"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('riskForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const assessBtn = document.getElementById('assessBtn');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            
            // Show loading state
            assessBtn.disabled = true;
            loading.style.display = 'block';
            results.style.display = 'none';
            
            // Collect form data
            const context = {
                primary_ticker: document.getElementById('ticker').value.toUpperCase(),
                action: document.getElementById('action').value,
                confidence: parseFloat(document.getElementById('confidence').value),
                position_size: parseFloat(document.getElementById('position_size').value),
                sector: document.getElementById('sector').value,
                market_volatility: document.getElementById('market_volatility').value
            };
            
            try {
                const response = await fetch('/api/assess', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(context)
                });
                
                const result = await response.json();
                displayResults(result);
                
            } catch (error) {
                console.error('Error:', error);
                alert('Error assessing risk: ' + error.message);
            } finally {
                assessBtn.disabled = false;
                loading.style.display = 'none';
            }
        });
        
        function displayResults(result) {
            const results = document.getElementById('results');
            const riskLevel = document.getElementById('riskLevel');
            const decision = document.getElementById('decision');
            const reasoning = document.getElementById('reasoning');
            const recommendations = document.getElementById('recommendations');
            
            // Risk level display
            const level = result.risk_level.toLowerCase();
            riskLevel.className = `risk-level risk-${level}`;
            riskLevel.innerHTML = `${getRiskEmoji(level)} ${result.risk_level} RISK<br>Score: ${result.risk_score.toFixed(3)}`;
            
            // Decision
            const proceed = result.should_proceed ? '✅ PROCEED' : '❌ BLOCKED';
            decision.innerHTML = `<h3>Decision: ${proceed}</h3>`;
            
            // Reasoning
            reasoning.textContent = result.reasoning.join('\\n');
            
            // Recommendations
            if (result.recommendations && result.recommendations.length > 0) {
                recommendations.innerHTML = `
                    <h3>🎯 Recommendations:</h3>
                    <ul>
                        ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                `;
            }
            
            results.style.display = 'block';
        }
        
        function getRiskEmoji(level) {
            const emojis = {
                'critical': '🚨',
                'high': '🔴',
                'medium': '🟠',
                'low': '🟡',
                'minimal': '🟢'
            };
            return emojis[level] || '⚪';
        }
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_memory_page(self):
        """Serve the memory system interface."""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Risk Memory System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .card { background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin-bottom: 20px; overflow: hidden; }
        .card-header { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; font-size: 1.3em; font-weight: bold; }
        .card-body { padding: 25px; }
        .nav-links { text-align: center; margin-bottom: 20px; }
        .nav-links a { color: white; text-decoration: none; margin: 0 15px; padding: 10px 20px; border-radius: 25px; background: rgba(255,255,255,0.2); transition: background 0.3s ease; }
        .nav-links a:hover { background: rgba(255,255,255,0.3); }
        .memory-item { background: #f8f9fa; border-left: 4px solid #4facfe; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .risk-critical { border-left-color: #c62828; }
        .risk-high { border-left-color: #f57c00; }
        .risk-medium { border-left-color: #f9a825; }
        .risk-low { border-left-color: #8e24aa; }
        .risk-minimal { border-left-color: #2e7d32; }
        .tag { background: #e3f2fd; color: #1976d2; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; margin: 2px; display: inline-block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Risk Memory System</h1>
            <p>AI learning database with pattern recognition</p>
        </div>
        
        <div class="nav-links">
            <a href="/">🏠 Risk Assessment</a>
            <a href="/memory">🧠 Memory System</a>
            <a href="/live-demo">🎬 Live Demo</a>
        </div>

        <div class="card">
            <div class="card-header">📚 Memory Insights</div>
            <div class="card-body" id="insights">Loading memory insights...</div>
        </div>

        <div class="card">
            <div class="card-header">📋 Recent Risk Assessments</div>
            <div class="card-body" id="memories">Loading recent memories...</div>
        </div>
    </div>

    <script>
        async function loadMemoryData() {
            try {
                const response = await fetch('/api/memory');
                const data = await response.json();
                
                // Display insights
                const insights = document.getElementById('insights');
                insights.innerHTML = `
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                        <div><h3>📊 Total Assessments</h3><p style="font-size: 2em; color: #4facfe;">${data.insights.total_assessments}</p></div>
                        <div><h3>🔴 High-Risk Events</h3><p style="font-size: 2em; color: #f57c00;">${data.insights.recent_high_risk_count}</p></div>
                        <div><h3>🏷️ Top Risk Tags</h3><p>${data.insights.most_common_tags.map(([tag, count]) => `<span class="tag">${tag} (${count})</span>`).join('')}</p></div>
                    </div>
                `;
                
                // Display recent memories
                const memories = document.getElementById('memories');
                if (data.recent_memories.length === 0) {
                    memories.innerHTML = '<p>No recent risk assessments found. Try running some assessments first!</p>';
                } else {
                    memories.innerHTML = data.recent_memories.map(memory => `
                        <div class="memory-item risk-${memory.risk_level.toLowerCase()}">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <h3>${memory.ticker} - ${memory.scenario}</h3>
                                <span style="font-weight: bold; color: ${getRiskColor(memory.risk_level)};">${memory.risk_level}</span>
                            </div>
                            <p><strong>Time:</strong> ${new Date(memory.timestamp).toLocaleString()}</p>
                            <p><strong>Key Factors:</strong> ${memory.key_factors.join(', ')}</p>
                            <p><strong>Outcome:</strong> ${memory.outcome || 'Pending'}</p>
                            <div style="margin-top: 10px;">
                                ${memory.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                            </div>
                        </div>
                    `).join('');
                }
                
            } catch (error) {
                console.error('Error loading memory data:', error);
                document.getElementById('insights').innerHTML = 'Error loading memory data';
                document.getElementById('memories').innerHTML = 'Error loading memories';
            }
        }
        
        function getRiskColor(level) {
            const colors = {
                'CRITICAL': '#c62828',
                'HIGH': '#f57c00',
                'MEDIUM': '#f9a825',
                'LOW': '#8e24aa',
                'MINIMAL': '#2e7d32'
            };
            return colors[level] || '#666';
        }
        
        // Load data when page loads
        loadMemoryData();
        
        // Refresh every 30 seconds
        setInterval(loadMemoryData, 30000);
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_memory_query(self, query_string):
        """Handle memory API requests."""
        try:
            insights = llm_risk_assessor.get_memory_insights()
            recent_memories = llm_risk_assessor.query_memory("recent", days=7)
            
            # Convert memories to serializable format
            serializable_memories = []
            for memory in recent_memories:
                serializable_memories.append({
                    'timestamp': memory.timestamp.isoformat(),
                    'ticker': memory.ticker,
                    'scenario': memory.scenario,
                    'risk_level': memory.risk_level,
                    'key_factors': memory.key_factors,
                    'outcome': memory.outcome,
                    'tags': memory.tags or []
                })
            
            response_data = {
                'insights': insights,
                'recent_memories': serializable_memories
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, indent=2).encode())
            
        except Exception as e:
            self.send_error(500, f"Error querying memory: {str(e)}")
    
    def serve_live_demo(self):
        """Serve the live demo page."""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎬 Live Demo - AI Risk System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .card { background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin-bottom: 20px; overflow: hidden; }
        .card-header { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; font-size: 1.3em; font-weight: bold; }
        .card-body { padding: 25px; }
        .nav-links { text-align: center; margin-bottom: 20px; }
        .nav-links a { color: white; text-decoration: none; margin: 0 15px; padding: 10px 20px; border-radius: 25px; background: rgba(255,255,255,0.2); transition: background 0.3s ease; }
        .nav-links a:hover { background: rgba(255,255,255,0.3); }
        .demo-scenario { background: #f8f9fa; border-radius: 10px; padding: 20px; margin: 15px 0; border-left: 4px solid #4facfe; }
        .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; margin: 5px; }
        .btn:hover { transform: translateY(-1px); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 Live Demo</h1>
            <p>See the AI risk system in action with real market scenarios</p>
        </div>
        
        <div class="nav-links">
            <a href="/">🏠 Risk Assessment</a>
            <a href="/memory">🧠 Memory System</a>
            <a href="/live-demo">🎬 Live Demo</a>
        </div>

        <div class="card">
            <div class="card-header">🎭 Pre-configured Demo Scenarios</div>
            <div class="card-body">
                <div class="demo-scenario">
                    <h3>🚨 Tesla High-Risk Scenario</h3>
                    <p>Current governance crisis with Musk political involvement</p>
                    <button class="btn" onclick="runDemo('tesla')">Run Tesla Demo</button>
                </div>
                
                <div class="demo-scenario">
                    <h3>🔴 NVIDIA Position Risk</h3>
                    <p>High confidence but oversized position in volatile market</p>
                    <button class="btn" onclick="runDemo('nvidia')">Run NVIDIA Demo</button>
                </div>
                
                <div class="demo-scenario">
                    <h3>🟢 Safe SPY Trade</h3>
                    <p>Conservative ETF approach during market uncertainty</p>
                    <button class="btn" onclick="runDemo('spy')">Run SPY Demo</button>
                </div>
                
                <div class="demo-scenario">
                    <h3>🎲 Random Meme Stock</h3>
                    <p>High-risk speculative trade with poor fundamentals</p>
                    <button class="btn" onclick="runDemo('meme')">Run Meme Stock Demo</button>
                </div>
            </div>
        </div>

        <div class="card" id="demo-results" style="display: none;">
            <div class="card-header">📊 Demo Results</div>
            <div class="card-body" id="demo-content"></div>
        </div>
    </div>

    <script>
        const demoScenarios = {
            tesla: {
                primary_ticker: 'TSLA',
                action: 'BUY',
                confidence: 0.7,
                position_size: 0.18,
                sector: 'automotive technology',
                market_volatility: 'high'
            },
            nvidia: {
                primary_ticker: 'NVDA',
                action: 'BUY',
                confidence: 0.85,
                position_size: 0.22,
                sector: 'semiconductors',
                market_volatility: 'high'
            },
            spy: {
                primary_ticker: 'SPY',
                action: 'BUY',
                confidence: 0.72,
                position_size: 0.08,
                sector: 'broad_market',
                market_volatility: 'high'
            },
            meme: {
                primary_ticker: 'MEME',
                action: 'BUY',
                confidence: 0.35,
                position_size: 0.25,
                sector: 'speculative',
                market_volatility: 'extreme'
            }
        };
        
        async function runDemo(scenario) {
            const context = demoScenarios[scenario];
            const resultsCard = document.getElementById('demo-results');
            const content = document.getElementById('demo-content');
            
            content.innerHTML = '<div style="text-align: center;"><div style="border: 4px solid #f3f3f3; border-top: 4px solid #4facfe; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto;"></div><p>🧠 AI is analyzing the scenario...</p></div>';
            resultsCard.style.display = 'block';
            
            try {
                const response = await fetch('/api/assess', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(context)
                });
                
                const result = await response.json();
                displayDemoResults(result, context);
                
            } catch (error) {
                content.innerHTML = `<p style="color: red;">Error running demo: ${error.message}</p>`;
            }
        }
        
        function displayDemoResults(result, context) {
            const content = document.getElementById('demo-content');
            const riskColor = getRiskColor(result.risk_level);
            
            content.innerHTML = `
                <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 20px;">
                    <div>
                        <h3>📋 Scenario Input</h3>
                        <p><strong>Ticker:</strong> ${context.primary_ticker}</p>
                        <p><strong>Action:</strong> ${context.action}</p>
                        <p><strong>Confidence:</strong> ${(context.confidence * 100).toFixed(0)}%</p>
                        <p><strong>Position:</strong> ${(context.position_size * 100).toFixed(0)}%</p>
                        <p><strong>Sector:</strong> ${context.sector}</p>
                        
                        <div style="margin-top: 20px; padding: 15px; background: ${riskColor}; color: white; border-radius: 10px; text-align: center;">
                            <h2>${getRiskEmoji(result.risk_level)} ${result.risk_level}</h2>
                            <p>Score: ${result.risk_score.toFixed(3)}</p>
                            <p style="font-size: 1.2em; margin-top: 10px;">
                                ${result.should_proceed ? '✅ APPROVED' : '❌ BLOCKED'}
                            </p>
                        </div>
                    </div>
                    
                    <div>
                        <h3>🧠 AI Reasoning Process</h3>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; max-height: 300px; overflow-y: auto; font-family: monospace; white-space: pre-wrap; font-size: 0.9em;">
${result.reasoning.join('\\n')}
                        </div>
                        
                        ${result.recommendations.length > 0 ? `
                        <h3 style="margin-top: 20px;">💡 Recommendations</h3>
                        <ul>
                            ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                        ` : ''}
                    </div>
                </div>
            `;
        }
        
        function getRiskColor(level) {
            const colors = {
                'CRITICAL': '#c62828',
                'HIGH': '#f57c00', 
                'MEDIUM': '#f9a825',
                'LOW': '#8e24aa',
                'MINIMAL': '#2e7d32'
            };
            return colors[level] || '#666';
        }
        
        function getRiskEmoji(level) {
            const emojis = {
                'CRITICAL': '🚨',
                'HIGH': '🔴',
                'MEDIUM': '🟠', 
                'LOW': '🟡',
                'MINIMAL': '🟢'
            };
            return emojis[level] || '⚪';
        }
    </script>
    <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        print(f"🌐 Web Request: {format % args}")


def find_free_port():
    """Find a free port to run the server on."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def start_web_server():
    """Start the web server for the risk assessment system."""
    
    # Find available port
    port = find_free_port()
    
    print("🚀 STARTING LLM AI RISK ASSESSMENT WEB SERVER")
    print("=" * 80)
    print(f"🌐 Server starting on port {port}")
    print(f"📱 Access from your browser at:")
    print(f"   🔗 http://localhost:{port}")
    print(f"   🔗 http://127.0.0.1:{port}")
    print("=" * 80)
    print("🧠 LLM Risk System Features Available:")
    print("   📊 Interactive Risk Assessment Interface")
    print("   🧠 Memory System Browser") 
    print("   🎬 Live Demo Scenarios")
    print("   📡 REST API Endpoints")
    print("=" * 80)
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    # Create and start server
    server_address = ('', port)
    httpd = HTTPServer(server_address, RiskAssessmentHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down web server...")
        httpd.shutdown()
        print("✅ Server stopped successfully")


if __name__ == "__main__":
    start_web_server()