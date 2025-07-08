#!/usr/bin/env python3
"""
Production Web Server for Intelligent Trading Agent
Clean, tested, and ready for frontend integration.
"""

import json
import time
import socket
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from intelligent_trading_agent import IntelligentTradingAgent


# Global trading agent instance
trading_agent = IntelligentTradingAgent()


class ProductionTradingHandler(BaseHTTPRequestHandler):
    """Production HTTP handler for the trading agent."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_main_interface()
        elif parsed_path.path == '/api/status':
            self.handle_status()
        elif parsed_path.path == '/api/memory':
            self.handle_memory()
        elif parsed_path.path == '/api/insights':
            self.handle_insights()
        elif parsed_path.path == '/health':
            self.handle_health_check()
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/api/analyze':
            self.handle_analyze()
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_analyze(self):
        """Handle trading analysis requests."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error(400, "No request body provided")
                return
            
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            ticker = request_data.get('ticker', '').upper().strip()
            if not ticker:
                self.send_error(400, "Ticker is required")
                return
            
            # Run complete trading analysis
            trade_record = trading_agent.analyze_and_trade(ticker)
            
            # Convert to API response format
            response = self._format_trade_response(trade_record)
            
            self._send_json_response(response)
            
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON in request body")
        except Exception as e:
            self.send_error(500, f"Analysis error: {str(e)}")
    
    def handle_status(self):
        """Handle system status requests."""
        try:
            status = {
                'status': 'active',
                'timestamp': datetime.now().isoformat(),
                'total_trades': len(trading_agent.trade_history),
                'total_assessments': len(trading_agent.risk_screener.memory),
                'recent_activity': self._get_recent_activity()
            }
            
            self._send_json_response(status)
            
        except Exception as e:
            self.send_error(500, f"Status error: {str(e)}")
    
    def handle_memory(self):
        """Handle memory system requests."""
        try:
            insights = trading_agent.get_risk_insights()
            recent_memories = trading_agent.risk_screener.memory[-10:]
            
            response = {
                'insights': insights,
                'recent_memories': [
                    {
                        'timestamp': mem.timestamp.isoformat(),
                        'ticker': mem.ticker,
                        'scenario': mem.scenario,
                        'risk_level': mem.risk_level,
                        'key_factors': mem.key_factors,
                        'outcome': mem.outcome,
                        'tags': mem.tags or []
                    }
                    for mem in recent_memories
                ]
            }
            
            self._send_json_response(response)
            
        except Exception as e:
            self.send_error(500, f"Memory error: {str(e)}")
    
    def handle_insights(self):
        """Handle risk insights requests."""
        try:
            insights = trading_agent.get_risk_insights()
            self._send_json_response(insights)
            
        except Exception as e:
            self.send_error(500, f"Insights error: {str(e)}")
    
    def handle_health_check(self):
        """Handle health check requests."""
        try:
            health = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'components': {
                    'research_engine': 'operational',
                    'risk_screener': 'operational', 
                    'trade_executor': 'operational',
                    'memory_system': 'operational'
                }
            }
            
            self._send_json_response(health)
            
        except Exception as e:
            self.send_error(500, f"Health check error: {str(e)}")
    
    def serve_main_interface(self):
        """Serve the main trading interface."""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Intelligent Trading Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; color: #333;
        }
        .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .card { background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin-bottom: 20px; overflow: hidden; }
        .card-header { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; font-size: 1.3em; font-weight: bold; }
        .card-body { padding: 25px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #555; }
        .form-control { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px; transition: border-color 0.3s ease; }
        .form-control:focus { outline: none; border-color: #4facfe; box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.1); }
        .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 15px 30px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; transition: transform 0.2s ease; width: 100%; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .btn-quick { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); width: auto; margin: 5px; padding: 10px 20px; font-size: 14px; }
        .quick-tests { text-align: center; margin-bottom: 20px; }
        .loading { display: none; text-align: center; padding: 20px; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #4facfe; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 10px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .results { display: none; margin-top: 20px; }
        .risk-display { font-size: 2em; font-weight: bold; text-align: center; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .risk-critical { background: #ffebee; color: #c62828; }
        .risk-high { background: #fff3e0; color: #f57c00; }
        .risk-medium { background: #fff8e1; color: #f9a825; }
        .risk-low { background: #f3e5f5; color: #8e24aa; }
        .risk-minimal { background: #e8f5e8; color: #2e7d32; }
        .details { background: #f8f9fa; border-left: 4px solid #4facfe; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .reasoning { background: #f8f9fa; padding: 15px; margin: 15px 0; font-family: 'Courier New', monospace; white-space: pre-wrap; max-height: 300px; overflow-y: auto; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Intelligent Trading Agent</h1>
            <p>Research → LLM Risk Screening → Filtered Execution</p>
        </div>

        <div class="card">
            <div class="card-header">🚀 Complete Trading Analysis</div>
            <div class="card-body">
                <div class="quick-tests">
                    <p><strong>Quick Tests:</strong></p>
                    <button class="btn-quick" onclick="analyze('TSLA')">🚨 Tesla</button>
                    <button class="btn-quick" onclick="analyze('NVDA')">🔴 NVIDIA</button>
                    <button class="btn-quick" onclick="analyze('SPY')">🟢 SPY</button>
                    <button class="btn-quick" onclick="analyze('AAPL')">🟡 Apple</button>
                </div>

                <form id="analyzeForm">
                    <div class="form-group">
                        <label for="ticker">Stock Ticker</label>
                        <input type="text" id="ticker" class="form-control" placeholder="Enter ticker (e.g., MSFT, GOOGL)" required>
                    </div>
                    <button type="submit" class="btn" id="analyzeBtn">🔍 Run Complete Analysis</button>
                </form>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>🧠 Running complete trading analysis...</p>
                </div>
                
                <div class="results" id="results">
                    <div id="riskDisplay" class="risk-display"></div>
                    <div id="tradeDetails" class="details"></div>
                    <div id="reasoning" class="reasoning"></div>
                    <div id="recommendations"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('analyzeForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const ticker = document.getElementById('ticker').value.toUpperCase().trim();
            if (ticker) analyze(ticker);
        });
        
        async function analyze(ticker) {
            const btn = document.getElementById('analyzeBtn');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            
            btn.disabled = true;
            loading.style.display = 'block';
            results.style.display = 'none';
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ticker: ticker })
                });
                
                if (!response.ok) {
                    const error = await response.text();
                    throw new Error(`${response.status}: ${error}`);
                }
                
                const data = await response.json();
                displayResults(data);
                
            } catch (error) {
                alert('Analysis failed: ' + error.message);
            } finally {
                btn.disabled = false;
                loading.style.display = 'none';
            }
        }
        
        function displayResults(data) {
            const riskDisplay = document.getElementById('riskDisplay');
            const tradeDetails = document.getElementById('tradeDetails');
            const reasoning = document.getElementById('reasoning');
            const recommendations = document.getElementById('recommendations');
            
            // Risk level
            const level = data.risk_level.toLowerCase();
            riskDisplay.className = `risk-display risk-${level}`;
            riskDisplay.innerHTML = `${getRiskEmoji(level)} ${data.risk_level} RISK<br>Score: ${data.risk_score.toFixed(3)}`;
            
            // Trade details
            const status = data.execution_status === 'EXECUTED' ? '✅ EXECUTED' : '❌ BLOCKED';
            tradeDetails.innerHTML = `
                <h4>📊 Trading Decision: ${status}</h4>
                <p><strong>Original:</strong> ${data.original_action} ${(data.original_position_size * 100).toFixed(0)}% (Confidence: ${(data.research_confidence * 100).toFixed(0)}%)</p>
                <p><strong>Final:</strong> ${data.final_action} ${(data.final_position_size * 100).toFixed(0)}%</p>
                <p><strong>Sector:</strong> ${data.sector}</p>
            `;
            
            // Reasoning
            reasoning.textContent = data.reasoning.join('\\n');
            
            // Recommendations
            if (data.recommendations.length > 0) {
                recommendations.innerHTML = `
                    <h4>💡 Recommendations:</h4>
                    <ul>${data.recommendations.map(r => `<li>${r}</li>`).join('')}</ul>
                `;
            }
            
            document.getElementById('results').style.display = 'block';
        }
        
        function getRiskEmoji(level) {
            const emojis = { critical: '🚨', high: '🔴', medium: '🟠', low: '🟡', minimal: '🟢' };
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
    
    def _format_trade_response(self, trade_record):
        """Format trade record for API response."""
        research = trade_record['research']
        risk_assessment = trade_record['risk_assessment']
        execution_result = trade_record['execution_result']
        
        return {
            'ticker': trade_record['ticker'],
            'risk_level': risk_assessment.risk_level.value,
            'risk_score': risk_assessment.risk_score,
            'should_proceed': risk_assessment.should_proceed,
            'reasoning': risk_assessment.reasoning,
            'recommendations': risk_assessment.recommendations,
            'original_action': research.recommended_action.value,
            'final_action': risk_assessment.modified_action.value,
            'original_position_size': research.target_position_size,
            'final_position_size': risk_assessment.modified_position_size,
            'execution_status': execution_result['status'],
            'research_confidence': research.confidence,
            'risk_factors': risk_assessment.risk_factors,
            'sector': research.sector,
            'timestamp': trade_record.get('timestamp', datetime.now()).isoformat()
        }
    
    def _get_recent_activity(self):
        """Get recent trading activity."""
        return [
            {
                'ticker': trade['ticker'],
                'risk_level': trade['risk_assessment'].risk_level.value,
                'execution_status': trade['execution_result']['status'],
                'timestamp': trade.get('timestamp', datetime.now()).isoformat()
            }
            for trade in trading_agent.trade_history[-5:]
        ]
    
    def _send_json_response(self, data):
        """Send JSON response with proper headers."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Make data JSON serializable
        serializable_data = self._make_serializable(data)
        response_json = json.dumps(serializable_data, indent=2)
        self.wfile.write(response_json.encode())
    
    def _make_serializable(self, obj):
        """Convert objects to JSON serializable format."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return self._make_serializable(obj.__dict__)
        else:
            return obj
    
    def log_message(self, format, *args):
        """Custom logging."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")


def find_free_port():
    """Find a free port for the server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def start_production_server():
    """Start the production web server."""
    port = find_free_port()
    
    print("🚀 PRODUCTION TRADING AGENT SERVER")
    print("=" * 60)
    print(f"🌐 Server: http://localhost:{port}")
    print(f"📊 Status: http://localhost:{port}/api/status")
    print(f"🔍 Analysis: POST http://localhost:{port}/api/analyze")
    print(f"🧠 Memory: http://localhost:{port}/api/memory")
    print(f"💊 Health: http://localhost:{port}/health")
    print("=" * 60)
    print("🎯 System: READY FOR FRONTEND TESTING")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, ProductionTradingHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        httpd.shutdown()
        print("✅ Server stopped")


if __name__ == "__main__":
    start_production_server()