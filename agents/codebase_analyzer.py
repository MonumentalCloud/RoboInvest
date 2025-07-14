"""
Codebase Analyzer - Comprehensive analysis of system structure and dependencies

Features:
- File structure analysis
- Import dependency mapping
- Code pattern recognition
- API endpoint discovery
- Agent system analysis
- Change impact assessment
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import json

from utils.logger import logger


@dataclass
class FileInfo:
    """Information about a file in the codebase"""
    path: str
    file_type: str  # 'python', 'typescript', 'javascript', 'json', etc.
    size: int
    lines: int
    imports: List[str]
    exports: List[str]
    classes: List[str]
    functions: List[str]
    dependencies: List[str]
    last_modified: str


@dataclass
class DependencyInfo:
    """Information about dependencies between files"""
    source_file: str
    target_file: str
    dependency_type: str  # 'import', 'function_call', 'class_inheritance'
    line_number: int
    description: str


@dataclass
class APIIntrospection:
    """Information about API endpoints"""
    endpoint_path: str
    method: str
    handler_function: str
    parameters: List[str]
    return_type: str
    description: str
    file_location: str


@dataclass
class AgentInfo:
    """Information about agents in the system"""
    agent_name: str
    agent_file: str
    agent_class: str
    capabilities: List[str]
    dependencies: List[str]
    status: str  # 'active', 'inactive', 'error'
    last_activity: str


class CodebaseAnalyzer:
    """Comprehensive codebase analysis system"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.file_cache: Dict[str, FileInfo] = {}
        self.dependency_graph: Dict[str, List[DependencyInfo]] = defaultdict(list)
        self.api_endpoints: List[APIIntrospection] = []
        self.agents: List[AgentInfo] = []
        
        # File patterns to analyze
        self.python_patterns = ["*.py"]
        self.typescript_patterns = ["*.ts", "*.tsx"]
        self.javascript_patterns = ["*.js", "*.jsx"]
        self.config_patterns = ["*.json", "*.yaml", "*.yml", "*.toml"]
        
        logger.info(f"CodebaseAnalyzer initialized for {self.root_path}")
    
    def analyze_codebase(self) -> Dict[str, Any]:
        """Perform comprehensive codebase analysis"""
        try:
            logger.info("Starting comprehensive codebase analysis...")
            
            # Clear previous analysis
            self.file_cache.clear()
            self.dependency_graph.clear()
            self.api_endpoints.clear()
            self.agents.clear()
            
            # Analyze file structure
            file_structure = self._analyze_file_structure()
            
            # Analyze Python files
            python_files = self._find_files(self.python_patterns)
            for file_path in python_files:
                self._analyze_python_file(file_path)
            
            # Analyze TypeScript/JavaScript files
            ts_js_files = self._find_files(self.typescript_patterns + self.javascript_patterns)
            for file_path in ts_js_files:
                self._analyze_typescript_file(file_path)
            
            # Discover API endpoints
            self._discover_api_endpoints()
            
            # Discover agents
            self._discover_agents()
            
            # Build dependency graph
            self._build_dependency_graph()
            
            # Generate analysis summary
            analysis_summary = {
                "total_files": len(self.file_cache),
                "python_files": len([f for f in self.file_cache.values() if f.file_type == "python"]),
                "typescript_files": len([f for f in self.file_cache.values() if f.file_type == "typescript"]),
                "javascript_files": len([f for f in self.file_cache.values() if f.file_type == "javascript"]),
                "api_endpoints": len(self.api_endpoints),
                "agents": len(self.agents),
                "total_dependencies": sum(len(deps) for deps in self.dependency_graph.values()),
                "file_structure": file_structure,
                "analysis_timestamp": str(Path().stat().st_mtime)
            }
            
            logger.info(f"Codebase analysis completed: {analysis_summary['total_files']} files analyzed")
            return analysis_summary
            
        except Exception as e:
            logger.error(f"Codebase analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_file_structure(self) -> Dict[str, Any]:
        """Analyze the overall file structure"""
        structure = {
            "directories": [],
            "file_types": defaultdict(int),
            "largest_files": [],
            "recent_files": []
        }
        
        for root, dirs, files in os.walk(self.root_path):
            # Skip hidden directories and common exclusions
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.git']]
            
            rel_root = os.path.relpath(root, self.root_path)
            if rel_root != '.':
                structure["directories"].append(rel_root)
            
            for file in files:
                if file.startswith('.'):
                    continue
                
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.root_path)
                
                # Determine file type
                file_type = self._get_file_type(file)
                structure["file_types"][file_type] += 1
                
                # Get file stats
                try:
                    stat = os.stat(file_path)
                    file_size = stat.st_size
                    file_info = {
                        "path": rel_path,
                        "size": file_size,
                        "modified": stat.st_mtime
                    }
                    
                    if file_size > 10000:  # Files larger than 10KB
                        structure["largest_files"].append(file_info)
                    
                    if stat.st_mtime > (Path().stat().st_mtime - 86400):  # Modified in last 24h
                        structure["recent_files"].append(file_info)
                        
                except OSError:
                    continue
        
        # Sort by size and time
        structure["largest_files"].sort(key=lambda x: x["size"], reverse=True)
        structure["recent_files"].sort(key=lambda x: x["modified"], reverse=True)
        
        return structure
    
    def _get_file_type(self, filename: str) -> str:
        """Determine file type based on extension"""
        ext = Path(filename).suffix.lower()
        
        if ext in ['.py']:
            return 'python'
        elif ext in ['.ts', '.tsx']:
            return 'typescript'
        elif ext in ['.js', '.jsx']:
            return 'javascript'
        elif ext in ['.json', '.yaml', '.yml', '.toml']:
            return 'config'
        elif ext in ['.md', '.txt']:
            return 'documentation'
        elif ext in ['.html', '.css']:
            return 'web'
        else:
            return 'other'
    
    def _find_files(self, patterns: List[str]) -> List[str]:
        """Find files matching patterns"""
        files = []
        for pattern in patterns:
            files.extend(self.root_path.glob(pattern))
        return [str(f.relative_to(self.root_path)) for f in files]
    
    def _analyze_python_file(self, file_path: str):
        """Analyze a Python file for imports, classes, functions, etc."""
        try:
            full_path = self.root_path / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            imports = []
            classes = []
            functions = []
            dependencies = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                        dependencies.append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
                        dependencies.append(module)
                
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
            
            # Create file info
            file_info = FileInfo(
                path=file_path,
                file_type="python",
                size=len(content),
                lines=len(content.splitlines()),
                imports=imports,
                exports=classes + functions,  # Python doesn't have explicit exports
                classes=classes,
                functions=functions,
                dependencies=dependencies,
                last_modified=str(full_path.stat().st_mtime)
            )
            
            self.file_cache[file_path] = file_info
            
        except Exception as e:
            logger.warning(f"Failed to analyze Python file {file_path}: {e}")
    
    def _analyze_typescript_file(self, file_path: str):
        """Analyze a TypeScript/JavaScript file"""
        try:
            full_path = self.root_path / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple regex-based analysis for TS/JS
            imports = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', content)
            exports = re.findall(r'export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)', content)
            classes = re.findall(r'(?:export\s+)?class\s+(\w+)', content)
            functions = re.findall(r'(?:export\s+)?(?:function\s+)?(\w+)\s*\(', content)
            
            file_info = FileInfo(
                path=file_path,
                file_type="typescript" if file_path.endswith(('.ts', '.tsx')) else "javascript",
                size=len(content),
                lines=len(content.splitlines()),
                imports=imports,
                exports=exports,
                classes=classes,
                functions=functions,
                dependencies=imports,
                last_modified=str(full_path.stat().st_mtime)
            )
            
            self.file_cache[file_path] = file_info
            
        except Exception as e:
            logger.warning(f"Failed to analyze TypeScript file {file_path}: {e}")
    
    def _discover_api_endpoints(self):
        """Discover API endpoints in the codebase"""
        try:
            # Look for FastAPI endpoints
            for file_path, file_info in self.file_cache.items():
                if file_info.file_type == "python" and "api" in file_path.lower():
                    self._extract_fastapi_endpoints(file_path, file_info)
            
            # Look for Express/Node.js endpoints
            for file_path, file_info in self.file_cache.items():
                if file_info.file_type in ["javascript", "typescript"] and "api" in file_path.lower():
                    self._extract_express_endpoints(file_path, file_info)
                    
        except Exception as e:
            logger.error(f"API endpoint discovery failed: {e}")
    
    def _extract_fastapi_endpoints(self, file_path: str, file_info: FileInfo):
        """Extract FastAPI endpoints from a Python file"""
        try:
            full_path = self.root_path / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find FastAPI route decorators
            route_patterns = [
                r'@app\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]',
                r'@router\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]',
            ]
            
            for pattern in route_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    method = match.group(1).upper()
                    path = match.group(2)
                    
                    # Try to find the function name
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if match.group(0) in line:
                            # Look for function definition in next few lines
                            for j in range(i + 1, min(i + 5, len(lines))):
                                func_match = re.search(r'def\s+(\w+)', lines[j])
                                if func_match:
                                    func_name = func_match.group(1)
                                    break
                            else:
                                func_name = "unknown"
                            break
                    else:
                        func_name = "unknown"
                    
                    endpoint = APIIntrospection(
                        endpoint_path=path,
                        method=method,
                        handler_function=func_name,
                        parameters=[],  # Could be enhanced to extract parameters
                        return_type="dict",  # Could be enhanced
                        description=f"FastAPI endpoint in {file_path}",
                        file_location=file_path
                    )
                    
                    self.api_endpoints.append(endpoint)
                    
        except Exception as e:
            logger.warning(f"Failed to extract FastAPI endpoints from {file_path}: {e}")
    
    def _extract_express_endpoints(self, file_path: str, file_info: FileInfo):
        """Extract Express.js endpoints from a JavaScript/TypeScript file"""
        try:
            full_path = self.root_path / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find Express route patterns
            route_patterns = [
                r'\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]',
                r'router\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]',
            ]
            
            for pattern in route_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    method = match.group(1).upper()
                    path = match.group(2)
                    
                    endpoint = APIIntrospection(
                        endpoint_path=path,
                        method=method,
                        handler_function="anonymous",  # Could be enhanced
                        parameters=[],
                        return_type="object",
                        description=f"Express endpoint in {file_path}",
                        file_location=file_path
                    )
                    
                    self.api_endpoints.append(endpoint)
                    
        except Exception as e:
            logger.warning(f"Failed to extract Express endpoints from {file_path}: {e}")
    
    def _discover_agents(self):
        """Discover agents in the codebase"""
        try:
            # Look for agent files
            agent_patterns = ["*agent*.py", "*Agent*.py"]
            agent_files = []
            
            for pattern in agent_patterns:
                agent_files.extend(self.root_path.glob(pattern))
            
            for agent_file in agent_files:
                rel_path = str(agent_file.relative_to(self.root_path))
                self._analyze_agent_file(rel_path)
                
        except Exception as e:
            logger.error(f"Agent discovery failed: {e}")
    
    def _analyze_agent_file(self, file_path: str):
        """Analyze an agent file"""
        try:
            if file_path not in self.file_cache:
                return
            
            file_info = self.file_cache[file_path]
            
            # Extract agent class names
            agent_classes = []
            for class_name in file_info.classes:
                if "agent" in class_name.lower() or "Agent" in class_name:
                    agent_classes.append(class_name)
            
            # Analyze capabilities based on methods
            capabilities = []
            for func_name in file_info.functions:
                if any(keyword in func_name.lower() for keyword in ['analyze', 'process', 'execute', 'run', 'handle']):
                    capabilities.append(func_name)
            
            # Determine agent status (simplified)
            status = "active"  # Could be enhanced to check actual status
            
            for agent_class in agent_classes:
                agent_info = AgentInfo(
                    agent_name=agent_class,
                    agent_file=file_path,
                    agent_class=agent_class,
                    capabilities=capabilities,
                    dependencies=file_info.dependencies,
                    status=status,
                    last_activity="unknown"  # Could be enhanced
                )
                
                self.agents.append(agent_info)
                
        except Exception as e:
            logger.warning(f"Failed to analyze agent file {file_path}: {e}")
    
    def _build_dependency_graph(self):
        """Build dependency graph between files"""
        try:
            for file_path, file_info in self.file_cache.items():
                for dep in file_info.dependencies:
                    # Try to resolve dependency to actual file
                    resolved_file = self._resolve_dependency(dep, file_path)
                    if resolved_file:
                        dependency_info = DependencyInfo(
                            source_file=file_path,
                            target_file=resolved_file,
                            dependency_type="import",
                            line_number=0,  # Could be enhanced
                            description=f"Import of {dep}"
                        )
                        self.dependency_graph[file_path].append(dependency_info)
                        
        except Exception as e:
            logger.error(f"Dependency graph building failed: {e}")
    
    def _resolve_dependency(self, dep: str, source_file: str) -> Optional[str]:
        """Try to resolve a dependency to an actual file"""
        try:
            # Handle relative imports
            if dep.startswith('.'):
                source_dir = Path(source_file).parent
                rel_path = dep.replace('.', '/').lstrip('/')
                if rel_path.endswith('/'):
                    rel_path += '__init__.py'
                elif not rel_path.endswith('.py'):
                    rel_path += '.py'
                
                resolved_path = source_dir / rel_path
                if resolved_path.exists():
                    return str(resolved_path.relative_to(self.root_path))
            
            # Handle absolute imports
            else:
                # Try common patterns
                possible_paths = [
                    f"{dep.replace('.', '/')}.py",
                    f"{dep.replace('.', '/')}/__init__.py",
                    f"agents/{dep}.py",
                    f"core/{dep}.py",
                    f"utils/{dep}.py"
                ]
                
                for path in possible_paths:
                    if (self.root_path / path).exists():
                        return path
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to resolve dependency {dep}: {e}")
            return None
    
    def get_file_info(self, file_path: str) -> Optional[FileInfo]:
        """Get information about a specific file"""
        return self.file_cache.get(file_path)
    
    def get_dependencies(self, file_path: str) -> List[DependencyInfo]:
        """Get dependencies for a specific file"""
        return self.dependency_graph.get(file_path, [])
    
    def get_api_endpoints(self) -> List[APIIntrospection]:
        """Get all discovered API endpoints"""
        return self.api_endpoints
    
    def get_agents(self) -> List[AgentInfo]:
        """Get all discovered agents"""
        return self.agents
    
    def find_files_by_pattern(self, pattern: str) -> List[str]:
        """Find files matching a pattern"""
        import fnmatch
        matching_files = []
        
        for file_path in self.file_cache.keys():
            if fnmatch.fnmatch(file_path, pattern):
                matching_files.append(file_path)
        
        return matching_files
    
    def search_code(self, query: str) -> List[Dict[str, Any]]:
        """Search for code patterns"""
        results = []
        
        for file_path, file_info in self.file_cache.items():
            try:
                full_path = self.root_path / file_path
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if query.lower() in content.lower():
                    # Find line numbers
                    lines = content.split('\n')
                    matching_lines = []
                    
                    for i, line in enumerate(lines, 1):
                        if query.lower() in line.lower():
                            matching_lines.append({
                                "line_number": i,
                                "content": line.strip()
                            })
                    
                    if matching_lines:
                        results.append({
                            "file_path": file_path,
                            "file_type": file_info.file_type,
                            "matching_lines": matching_lines
                        })
                        
            except Exception as e:
                logger.warning(f"Failed to search file {file_path}: {e}")
        
        return results
    
    def get_impact_analysis(self, file_path: str) -> Dict[str, Any]:
        """Analyze the impact of changing a file"""
        try:
            if file_path not in self.file_cache:
                return {"error": "File not found"}
            
            # Find files that depend on this file
            dependents = []
            for dep_file, deps in self.dependency_graph.items():
                for dep in deps:
                    if dep.target_file == file_path:
                        dependents.append(dep_file)
            
            # Find files this file depends on
            dependencies = self.dependency_graph.get(file_path, [])
            
            # Calculate impact score
            impact_score = len(dependents) * 2 + len(dependencies)
            
            return {
                "file_path": file_path,
                "dependents": dependents,
                "dependencies": [d.target_file for d in dependencies],
                "impact_score": impact_score,
                "risk_level": "high" if impact_score > 10 else "medium" if impact_score > 5 else "low"
            }
            
        except Exception as e:
            logger.error(f"Impact analysis failed for {file_path}: {e}")
            return {"error": str(e)}


# Global instance
codebase_analyzer = CodebaseAnalyzer() 