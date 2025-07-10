#!/usr/bin/env python3
"""
Codebase Analyzer Agent: Cursor-like Code Analysis and Self-Editing System

This agent provides:
1. Complete codebase scanning and indexing
2. ChromaDB storage of code knowledge
3. Semantic code search and retrieval
4. Code analysis and issue detection
5. Self-editing capabilities for agents
6. Dependency mapping and impact analysis
"""

import asyncio
import json
import ast
import inspect
import os
import sys
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
import difflib
import re
import importlib.util
from dataclasses import dataclass, asdict

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from core.config import config
from core.openai_manager import openai_manager
from utils.logger import logger

@dataclass
class CodeFile:
    path: str
    content: str
    language: str
    size: int
    last_modified: datetime
    hash: str
    functions: List[Dict[str, Any]]
    classes: List[Dict[str, Any]]
    imports: List[str]
    dependencies: List[str]
    complexity_score: float
    maintainability_score: float

@dataclass
class CodeIssue:
    file_path: str
    line_number: int
    issue_type: str  # "bug", "performance", "security", "style", "maintainability"
    severity: str  # "critical", "high", "medium", "low"
    description: str
    suggestion: str
    confidence: float

@dataclass
class CodeChange:
    file_path: str
    change_type: str  # "bug_fix", "optimization", "refactoring", "new_feature"
    description: str
    diff: str
    confidence: float
    impact_analysis: Dict[str, Any]
    approved: bool = False
    applied: bool = False
    timestamp: datetime = None

class CodebaseAnalyzer:
    """
    Cursor-like codebase analyzer that can scan, index, and analyze code.
    
    Capabilities:
    - Complete codebase scanning and indexing
    - ChromaDB storage with semantic search
    - Code analysis and issue detection
    - Dependency mapping
    - Self-editing capabilities
    - Impact analysis for changes
    """
    
    def __init__(self):
        self.chroma_client = None
        self.code_collection = None
        self.issue_collection = None
        self.change_collection = None
        
        # File extensions to analyze
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
            '.txt': 'text'
        }
        
        # Directories to ignore
        self.ignore_dirs = {
            '__pycache__', '.git', 'node_modules', '.venv', 'venv',
            'env', '.env', 'dist', 'build', '.pytest_cache', '.mypy_cache',
            'chroma', '.vscode', '.idea', 'logs', '*.egg-info'
        }
        
        # Initialize ChromaDB
        self._setup_chromadb()
        
        # Cache for analysis results
        self.analysis_cache = {}
        self.file_hashes = {}
        
        logger.info("🔍 Codebase Analyzer initialized")
    
    def _setup_chromadb(self):
        """Initialize ChromaDB with collections for code, issues, and changes."""
        try:
            if not config.openai_api_key:
                logger.warning("CodebaseAnalyzer | OpenAI key missing – embeddings disabled")
                return
            
            embed_fn = OpenAIEmbeddingFunction(
                api_key=config.openai_api_key, 
                model_name="text-embedding-3-small"
            )
            
            self.chroma_client = chromadb.PersistentClient(path=config.chroma_db_path)
            
            # Create collections
            self.code_collection = self.chroma_client.get_or_create_collection(
                "codebase", embedding_function=embed_fn
            )
            self.issue_collection = self.chroma_client.get_or_create_collection(
                "code_issues", embedding_function=embed_fn
            )
            self.change_collection = self.chroma_client.get_or_create_collection(
                "code_changes", embedding_function=embed_fn
            )
            
            logger.info("✅ ChromaDB initialized successfully")
            
        except Exception as e:
            logger.error(f"ChromaDB setup failed: {e}")
            self.chroma_client = None
    
    async def scan_codebase(self, root_path: str = ".") -> Dict[str, Any]:
        """Scan the entire codebase and index all files."""
        logger.info(f"🔍 Scanning codebase at {root_path}")
        
        scan_results = {
            "total_files": 0,
            "total_lines": 0,
            "languages": {},
            "files_analyzed": [],
            "issues_found": 0,
            "scan_time": None
        }
        
        start_time = datetime.now()
        
        try:
            # Walk through all files
            for root, dirs, files in os.walk(root_path):
                # Filter out ignored directories
                dirs[:] = [d for d in dirs if d not in self.ignore_dirs and not d.startswith('.')]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, root_path)
                    
                    # Check if file should be analyzed
                    if self._should_analyze_file(file_path):
                        try:
                            file_analysis = await self._analyze_single_file(file_path, rel_path)
                            if file_analysis:
                                scan_results["files_analyzed"].append(file_analysis)
                                scan_results["total_files"] += 1
                                scan_results["total_lines"] += file_analysis.get("lines", 0)
                                
                                # Count languages
                                lang = file_analysis.get("language", "unknown")
                                scan_results["languages"][lang] = scan_results["languages"].get(lang, 0) + 1
                                
                                # Index in ChromaDB
                                await self._index_file_in_chromadb(file_analysis)
                                
                        except Exception as e:
                            logger.error(f"Failed to analyze {file_path}: {e}")
            
            scan_results["scan_time"] = (datetime.now() - start_time).total_seconds()
            
            # Find issues across the codebase
            issues = await self._find_codebase_issues(scan_results["files_analyzed"])
            scan_results["issues_found"] = len(issues)
            
            # Store issues in ChromaDB
            await self._index_issues_in_chromadb(issues)
            
            logger.info(f"✅ Codebase scan complete: {scan_results['total_files']} files, {scan_results['total_lines']} lines")
            
        except Exception as e:
            logger.error(f"Codebase scan failed: {e}")
        
        return scan_results
    
    def _should_analyze_file(self, file_path: str) -> bool:
        """Check if a file should be analyzed."""
        # Check extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.supported_extensions:
            return False
        
        # Check if file is in ignored directory
        for ignore_dir in self.ignore_dirs:
            if ignore_dir in file_path:
                return False
        
        # Check file size (skip very large files)
        try:
            if os.path.getsize(file_path) > 1024 * 1024:  # 1MB
                return False
        except:
            return False
        
        return True
    
    async def _analyze_single_file(self, file_path: str, rel_path: str) -> Optional[Dict[str, Any]]:
        """Analyze a single file and extract metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calculate file hash
            file_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Check if file has changed
            if file_hash == self.file_hashes.get(file_path):
                return None  # File hasn't changed
            
            self.file_hashes[file_path] = file_hash
            
            # Get file metadata
            stat = os.stat(file_path)
            ext = os.path.splitext(file_path)[1].lower()
            language = self.supported_extensions.get(ext, "unknown")
            
            analysis = {
                "path": rel_path,
                "full_path": file_path,
                "content": content,
                "language": language,
                "size": stat.st_size,
                "lines": len(content.splitlines()),
                "last_modified": datetime.fromtimestamp(stat.st_mtime),
                "hash": file_hash
            }
            
            # Language-specific analysis
            if language == "python":
                analysis.update(await self._analyze_python_file(content))
            elif language in ["javascript", "typescript"]:
                analysis.update(await self._analyze_js_file(content))
            elif language == "html":
                analysis.update(await self._analyze_html_file(content))
            
            # Calculate complexity and maintainability scores
            analysis["complexity_score"] = self._calculate_complexity_score(analysis)
            analysis["maintainability_score"] = self._calculate_maintainability_score(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")
            return None
    
    async def _analyze_python_file(self, content: str) -> Dict[str, Any]:
        """Analyze Python file for functions, classes, imports, etc."""
        try:
            tree = ast.parse(content)
            
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node) or ""
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        "docstring": ast.get_docstring(node) or ""
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
            
            return {
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "dependencies": list(set(imports))
            }
            
        except Exception as e:
            logger.error(f"Python analysis failed: {e}")
            return {"functions": [], "classes": [], "imports": [], "dependencies": []}
    
    async def _analyze_js_file(self, content: str) -> Dict[str, Any]:
        """Basic JavaScript/TypeScript analysis."""
        functions = []
        classes = []
        imports = []
        
        # Simple regex-based analysis
        # Function declarations
        func_pattern = r'function\s+(\w+)\s*\([^)]*\)'
        for match in re.finditer(func_pattern, content):
            functions.append({
                "name": match.group(1),
                "line": content[:match.start()].count('\n') + 1,
                "args": [],
                "docstring": ""
            })
        
        # Class declarations
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            classes.append({
                "name": match.group(1),
                "line": content[:match.start()].count('\n') + 1,
                "methods": [],
                "docstring": ""
            })
        
        # Import statements
        import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1))
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "dependencies": list(set(imports))
        }
    
    async def _analyze_html_file(self, content: str) -> Dict[str, Any]:
        """Basic HTML analysis."""
        # Extract script and style dependencies
        scripts = re.findall(r'<script[^>]*src=[\'"]([^\'"]+)[\'"]', content)
        styles = re.findall(r'<link[^>]*href=[\'"]([^\'"]+)[\'"]', content)
        
        return {
            "functions": [],
            "classes": [],
            "imports": scripts + styles,
            "dependencies": list(set(scripts + styles))
        }
    
    def _calculate_complexity_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate code complexity score."""
        score = 0.0
        
        # Base complexity from lines of code
        lines = analysis.get("lines", 0)
        score += min(lines / 100.0, 5.0)  # Cap at 5 points
        
        # Complexity from functions and classes
        functions = analysis.get("functions", [])
        classes = analysis.get("classes", [])
        score += len(functions) * 0.1
        score += len(classes) * 0.2
        
        # Complexity from dependencies
        dependencies = analysis.get("dependencies", [])
        score += len(dependencies) * 0.05
        
        return min(score, 10.0)  # Cap at 10
    
    def _calculate_maintainability_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate maintainability score (higher is better)."""
        score = 10.0
        
        # Penalize for complexity
        complexity = analysis.get("complexity_score", 0)
        score -= complexity * 0.5
        
        # Penalize for large files
        lines = analysis.get("lines", 0)
        if lines > 500:
            score -= (lines - 500) / 100
        
        # Bonus for good documentation
        functions = analysis.get("functions", [])
        documented_functions = sum(1 for f in functions if f.get("docstring"))
        if functions:
            doc_ratio = documented_functions / len(functions)
            score += doc_ratio * 2
        
        return max(score, 0.0)
    
    async def _index_file_in_chromadb(self, file_analysis: Dict[str, Any]):
        """Index a file in ChromaDB for semantic search."""
        if not self.chroma_client or not self.code_collection:
            return
        
        try:
            # Create document text for embedding
            doc_text = self._create_document_text(file_analysis)
            
            # Create metadata
            metadata = {
                "path": file_analysis["path"],
                "language": file_analysis["language"],
                "lines": file_analysis["lines"],
                "functions": len(file_analysis.get("functions", [])),
                "classes": len(file_analysis.get("classes", [])),
                "complexity_score": file_analysis.get("complexity_score", 0),
                "maintainability_score": file_analysis.get("maintainability_score", 0),
                "last_modified": file_analysis["last_modified"].isoformat()
            }
            
            # Create unique ID
            doc_id = f"file_{file_analysis['hash']}"
            
            # Add to collection
            self.code_collection.add(
                documents=[doc_text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
        except Exception as e:
            logger.error(f"Failed to index file in ChromaDB: {e}")
    
    def _create_document_text(self, file_analysis: Dict[str, Any]) -> str:
        """Create text representation of file for embedding."""
        lines = []
        
        # File header
        lines.append(f"File: {file_analysis['path']}")
        lines.append(f"Language: {file_analysis['language']}")
        lines.append(f"Lines: {file_analysis['lines']}")
        
        # Functions
        functions = file_analysis.get("functions", [])
        if functions:
            lines.append("Functions:")
            for func in functions:
                lines.append(f"  {func['name']}({', '.join(func['args'])})")
                if func.get("docstring"):
                    lines.append(f"    {func['docstring']}")
        
        # Classes
        classes = file_analysis.get("classes", [])
        if classes:
            lines.append("Classes:")
            for cls in classes:
                lines.append(f"  {cls['name']}")
                if cls.get("methods"):
                    lines.append(f"    Methods: {', '.join(cls['methods'])}")
                if cls.get("docstring"):
                    lines.append(f"    {cls['docstring']}")
        
        # Dependencies
        dependencies = file_analysis.get("dependencies", [])
        if dependencies:
            lines.append(f"Dependencies: {', '.join(dependencies)}")
        
        # Content preview (first 500 characters)
        content = file_analysis.get("content", "")
        if content:
            preview = content[:500].replace('\n', ' ')
            lines.append(f"Content preview: {preview}...")
        
        return "\n".join(lines)
    
    async def search_code(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search codebase using semantic search."""
        if not self.chroma_client or not self.code_collection:
            return []
        
        try:
            results = self.code_collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["metadatas", "documents"]
            )
            
            if not results or not results.get("ids") or not results["ids"][0]:
                return []
            
            return [
                {
                    "path": results["metadatas"][0][i]["path"],
                    "language": results["metadatas"][0][i]["language"],
                    "lines": results["metadatas"][0][i]["lines"],
                    "complexity_score": results["metadatas"][0][i]["complexity_score"],
                    "maintainability_score": results["metadatas"][0][i]["maintainability_score"],
                    "content": results["documents"][0][i]
                }
                for i in range(len(results["ids"][0]))
            ]
            
        except Exception as e:
            logger.error(f"Code search failed: {e}")
            return []
    
    async def find_similar_code(self, code_snippet: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find similar code snippets."""
        return await self.search_code(code_snippet, n_results)
    
    async def get_file_content(self, file_path: str) -> Optional[str]:
        """Get the content of a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None
    
    async def _find_codebase_issues(self, files: List[Dict[str, Any]]) -> List[CodeIssue]:
        """Find issues across the codebase."""
        issues = []
        
        for file_analysis in files:
            file_issues = await self._analyze_file_issues(file_analysis)
            issues.extend(file_issues)
        
        return issues
    
    async def _analyze_file_issues(self, file_analysis: Dict[str, Any]) -> List[CodeIssue]:
        """Analyze a single file for issues."""
        issues = []
        
        # Language-specific issue detection
        if file_analysis["language"] == "python":
            issues.extend(await self._analyze_python_issues(file_analysis))
        elif file_analysis["language"] in ["javascript", "typescript"]:
            issues.extend(await self._analyze_js_issues(file_analysis))
        
        # General issue detection
        issues.extend(await self._analyze_general_issues(file_analysis))
        
        return issues
    
    async def _analyze_python_issues(self, file_analysis: Dict[str, Any]) -> List[CodeIssue]:
        """Analyze Python file for specific issues."""
        issues = []
        content = file_analysis["content"]
        lines = content.splitlines()
        
        # Check for common Python issues
        for i, line in enumerate(lines, 1):
            # Unused imports
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                if "unused" in line.lower() or "# noqa" in line:
                    continue
                # Simple heuristic for unused imports
                import_name = line.split()[1].split('.')[0]
                if import_name not in content[i*100:]:  # Check if used later in file
                    issues.append(CodeIssue(
                        file_path=file_analysis["path"],
                        line_number=i,
                        issue_type="style",
                        severity="low",
                        description=f"Potentially unused import: {import_name}",
                        suggestion="Remove if not used",
                        confidence=0.6
                    ))
            
            # Long lines
            if len(line) > 120:
                issues.append(CodeIssue(
                    file_path=file_analysis["path"],
                    line_number=i,
                    issue_type="style",
                    severity="low",
                    description="Line too long",
                    suggestion="Break into multiple lines",
                    confidence=0.8
                ))
            
            # Hardcoded strings
            if 'password' in line.lower() or 'secret' in line.lower():
                if '"' in line or "'" in line:
                    issues.append(CodeIssue(
                        file_path=file_analysis["path"],
                        line_number=i,
                        issue_type="security",
                        severity="high",
                        description="Potential hardcoded secret",
                        suggestion="Use environment variables",
                        confidence=0.7
                    ))
        
        return issues
    
    async def _analyze_js_issues(self, file_analysis: Dict[str, Any]) -> List[CodeIssue]:
        """Analyze JavaScript/TypeScript file for issues."""
        issues = []
        content = file_analysis["content"]
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Console.log statements
            if "console.log" in line:
                issues.append(CodeIssue(
                    file_path=file_analysis["path"],
                    line_number=i,
                    issue_type="style",
                    severity="low",
                    description="Console.log statement found",
                    suggestion="Remove or replace with proper logging",
                    confidence=0.9
                ))
            
            # Long lines
            if len(line) > 120:
                issues.append(CodeIssue(
                    file_path=file_analysis["path"],
                    line_number=i,
                    issue_type="style",
                    severity="low",
                    description="Line too long",
                    suggestion="Break into multiple lines",
                    confidence=0.8
                ))
        
        return issues
    
    async def _analyze_general_issues(self, file_analysis: Dict[str, Any]) -> List[CodeIssue]:
        """Analyze file for general issues."""
        issues = []
        
        # Complexity issues
        complexity = file_analysis.get("complexity_score", 0)
        if complexity > 7.0:
            issues.append(CodeIssue(
                file_path=file_analysis["path"],
                line_number=1,
                issue_type="maintainability",
                severity="medium",
                description=f"High complexity score: {complexity:.1f}",
                suggestion="Consider refactoring into smaller functions/classes",
                confidence=0.8
            ))
        
        # Maintainability issues
        maintainability = file_analysis.get("maintainability_score", 0)
        if maintainability < 3.0:
            issues.append(CodeIssue(
                file_path=file_analysis["path"],
                line_number=1,
                issue_type="maintainability",
                severity="high",
                description=f"Low maintainability score: {maintainability:.1f}",
                suggestion="Improve documentation and reduce complexity",
                confidence=0.9
            ))
        
        # Large files
        lines = file_analysis.get("lines", 0)
        if lines > 1000:
            issues.append(CodeIssue(
                file_path=file_analysis["path"],
                line_number=1,
                issue_type="maintainability",
                severity="medium",
                description=f"Large file: {lines} lines",
                suggestion="Consider splitting into smaller modules",
                confidence=0.7
            ))
        
        return issues
    
    async def _index_issues_in_chromadb(self, issues: List[CodeIssue]):
        """Index code issues in ChromaDB."""
        if not self.chroma_client or not self.issue_collection:
            return
        
        try:
            for issue in issues:
                doc_text = f"Issue in {issue.file_path}:{issue.line_number} - {issue.description}"
                
                metadata = {
                    "file_path": issue.file_path,
                    "line_number": issue.line_number,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity,
                    "description": issue.description,
                    "suggestion": issue.suggestion,
                    "confidence": issue.confidence
                }
                
                doc_id = f"issue_{issue.file_path}_{issue.line_number}_{hash(issue.description)}"
                
                self.issue_collection.add(
                    documents=[doc_text],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
                
        except Exception as e:
            logger.error(f"Failed to index issues in ChromaDB: {e}")
    
    async def suggest_code_improvements(self, file_path: str) -> List[Dict[str, Any]]:
        """Suggest improvements for a specific file."""
        file_analysis = await self._analyze_single_file(file_path, file_path)
        if not file_analysis:
            return []
        
        issues = await self._analyze_file_issues(file_analysis)
        
        improvements = []
        for issue in issues:
            improvements.append({
                "type": issue.issue_type,
                "severity": issue.severity,
                "description": issue.description,
                "suggestion": issue.suggestion,
                "line_number": issue.line_number,
                "confidence": issue.confidence
            })
        
        return improvements
    
    async def apply_code_fix(self, file_path: str, fix_description: str) -> bool:
        """Apply a code fix to a file."""
        try:
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Generate fix using LLM
            fixed_content = await self._generate_code_fix(original_content, fix_description)
            
            if fixed_content and fixed_content != original_content:
                # Create backup
                backup_path = f"{file_path}.backup"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                # Apply fix
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                # Record change
                await self._record_code_change(file_path, "bug_fix", fix_description, 
                                             self._generate_diff(original_content, fixed_content))
                
                logger.info(f"✅ Applied code fix to {file_path}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to apply code fix to {file_path}: {e}")
        
        return False
    
    async def _generate_code_fix(self, original_content: str, fix_description: str) -> Optional[str]:
        """Generate a code fix using LLM."""
        try:
            prompt = f"""
            You are a code fixer. Given the original code and a description of what needs to be fixed,
            provide the corrected code. Only return the corrected code, no explanations.

            Original code:
            {original_content}

            Fix needed: {fix_description}

            Corrected code:
            """
            
            result = openai_manager.chat_completion([
                {"role": "user", "content": prompt}
            ])
            
            return result["content"]
            
        except Exception as e:
            logger.error(f"Failed to generate code fix: {e}")
            return None
    
    def _generate_diff(self, original: str, modified: str) -> str:
        """Generate a diff between original and modified content."""
        try:
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                modified.splitlines(keepends=True),
                fromfile='original',
                tofile='modified'
            )
            return ''.join(diff)
        except Exception as e:
            logger.error(f"Failed to generate diff: {e}")
            return ""
    
    async def _record_code_change(self, file_path: str, change_type: str, description: str, diff: str):
        """Record a code change in ChromaDB."""
        if not self.chroma_client or not self.change_collection:
            return
        
        try:
            doc_text = f"Code change in {file_path}: {description}"
            
            metadata = {
                "file_path": file_path,
                "change_type": change_type,
                "description": description,
                "diff": diff,
                "timestamp": datetime.now().isoformat(),
                "approved": False,
                "applied": True
            }
            
            doc_id = f"change_{file_path}_{datetime.now().timestamp()}"
            
            self.change_collection.add(
                documents=[doc_text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
        except Exception as e:
            logger.error(f"Failed to record code change: {e}")
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get an overview of the entire codebase."""
        if not self.chroma_client or not self.code_collection:
            return {}
        
        try:
            # Get all documents
            results = self.code_collection.get()
            
            overview = {
                "total_files": len(results["ids"]),
                "languages": {},
                "total_lines": 0,
                "avg_complexity": 0.0,
                "avg_maintainability": 0.0,
                "total_functions": 0,
                "total_classes": 0,
                "total_issues": 0
            }
            
            complexity_sum = 0
            maintainability_sum = 0
            
            for i, metadata in enumerate(results["metadatas"]):
                # Count languages
                lang = metadata.get("language", "unknown")
                overview["languages"][lang] = overview["languages"].get(lang, 0) + 1
                
                # Sum metrics
                overview["total_lines"] += metadata.get("lines", 0)
                overview["total_functions"] += metadata.get("functions", 0)
                overview["total_classes"] += metadata.get("classes", 0)
                
                complexity_sum += metadata.get("complexity_score", 0)
                maintainability_sum += metadata.get("maintainability_score", 0)
            
            # Calculate averages
            if overview["total_files"] > 0:
                overview["avg_complexity"] = complexity_sum / overview["total_files"]
                overview["avg_maintainability"] = maintainability_sum / overview["total_files"]
            
            # Get issue count
            if self.issue_collection:
                issue_results = self.issue_collection.get()
                overview["total_issues"] = len(issue_results["ids"])
            
            return overview
            
        except Exception as e:
            logger.error(f"Failed to get system overview: {e}")
            return {}

# Singleton instance
codebase_analyzer = CodebaseAnalyzer() 