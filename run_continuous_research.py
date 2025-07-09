#!/usr/bin/env python3
"""
Continuous Research System Launcher
Launch both the background research service and the API server.
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path
from typing import List, Optional

class ContinuousResearchLauncher:
    """Launcher for the continuous research system."""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.running = False
        
    def start_system(self):
        """Start the continuous research system."""
        
        print("🚀 Starting Continuous Research System")
        print("=" * 50)
        
        try:
            # Set up signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            self.running = True
            
            # Start background research service
            print("🔍 Starting background research service...")
            research_process = subprocess.Popen([
                sys.executable, "background_research_service.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.processes.append(research_process)
            
            # Give research service time to start
            time.sleep(2)
            
            # Start FastAPI backend (which includes research endpoints)
            print("🌐 Starting FastAPI backend...")
            api_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "backend.api.fastapi_app:app", "--reload", "--port", "8081"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.processes.append(api_process)
            
            print("✅ System started successfully!")
            print("🔗 API available at: http://localhost:8081/api")
            print("📊 Frontend should connect to the API automatically")
            print("🛑 Press Ctrl+C to stop the system")
            print("=" * 50)
            
            # Monitor processes
            self._monitor_processes()
            
        except Exception as e:
            print(f"❌ Failed to start system: {e}")
            self.stop_system()
            return False
            
        return True
    
    def _monitor_processes(self):
        """Monitor running processes and restart if needed."""
        
        while self.running:
            try:
                # Check if any process has died
                for i, process in enumerate(self.processes):
                    if process.poll() is not None:
                        print(f"⚠️  Process {i} has stopped, restarting...")
                        
                        # Restart the process
                        if i == 0:  # Research service
                            new_process = subprocess.Popen([
                                sys.executable, "background_research_service.py"
                            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        else:  # FastAPI backend
                            new_process = subprocess.Popen([
                                sys.executable, "-m", "uvicorn", "backend.api.fastapi_app:app", "--reload", "--port", "8081"
                            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        
                        self.processes[i] = new_process
                        print(f"✅ Process {i} restarted")
                
                time.sleep(60)  # Check every 60 seconds instead of 10
                
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(5)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.stop_system()
    
    def stop_system(self):
        """Stop all processes."""
        
        self.running = False
        
        print("🔄 Stopping processes...")
        
        for i, process in enumerate(self.processes):
            try:
                if process.poll() is None:  # Process is still running
                    print(f"⏹️  Stopping process {i}...")
                    process.terminate()
                    
                    # Wait up to 5 seconds for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        print(f"💀 Force killing process {i}...")
                        process.kill()
                        process.wait()
                    
                    print(f"✅ Process {i} stopped")
                    
            except Exception as e:
                print(f"❌ Error stopping process {i}: {e}")
        
        self.processes.clear()
        print("🏁 System stopped")
    
    def get_status(self) -> dict:
        """Get current system status."""
        
        status = {
            "running": self.running,
            "processes": len(self.processes),
            "process_status": []
        }
        
        for i, process in enumerate(self.processes):
            status["process_status"].append({
                "index": i,
                "name": "research_service" if i == 0 else "fastapi_backend",
                "running": process.poll() is None,
                "pid": process.pid
            })
        
        return status

def main():
    """Main entry point."""
    
    # Check if required files exist
    required_files = [
        "background_research_service.py",
        "backend/api/fastapi_app.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    # Create launcher and start system
    launcher = ContinuousResearchLauncher()
    
    try:
        success = launcher.start_system()
        return success
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        return True
    except Exception as e:
        print(f"❌ System error: {e}")
        return False
    finally:
        launcher.stop_system()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 