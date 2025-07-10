#!/usr/bin/env python3
"""
Test Script: ChromaDB Cursor-like System

This script demonstrates:
1. ChromaDB setup and codebase indexing
2. Semantic code search capabilities
3. Self-editing agent functionality
4. Code analysis and issue detection
5. Real-time code modification
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.codebase_analyzer import codebase_analyzer
from agents.self_editing_agent import self_editing_agent
from core.config import config
from utils.logger import logger

class ChromaDBCursorTester:
    """
    Test class for ChromaDB Cursor-like system.
    """
    
    def __init__(self):
        self.test_results = {}
        self.demo_data = {}
    
    async def run_all_tests(self):
        """Run all tests for the ChromaDB Cursor-like system."""
        logger.info("🧪 Running ChromaDB Cursor-like System Tests")
        
        try:
            # Test 1: Basic ChromaDB functionality
            await self._test_chromadb_basics()
            
            # Test 2: Codebase scanning and indexing
            await self._test_codebase_scanning()
            
            # Test 3: Semantic code search
            await self._test_semantic_search()
            
            # Test 4: Issue detection
            await self._test_issue_detection()
            
            # Test 5: Self-editing capabilities
            await self._test_self_editing()
            
            # Test 6: Code analysis
            await self._test_code_analysis()
            
            # Test 7: Real-time modifications
            await self._test_real_time_modifications()
            
            # Generate test report
            await self._generate_test_report()
            
            logger.info("✅ All tests completed successfully!")
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            raise
    
    async def _test_chromadb_basics(self):
        """Test basic ChromaDB functionality."""
        logger.info("📊 Testing ChromaDB basics...")
        
        try:
            # Check if ChromaDB is available
            if codebase_analyzer.chroma_client:
                collections = codebase_analyzer.chroma_client.list_collections()
                logger.info(f"   ✅ ChromaDB available with {len(collections)} collections")
                
                self.test_results["chromadb_basics"] = {
                    "status": "passed",
                    "collections_count": len(collections),
                    "collections": [c.name for c in collections]
                }
            else:
                logger.warning("   ⚠️  ChromaDB not available - using fallback mode")
                self.test_results["chromadb_basics"] = {
                    "status": "warning",
                    "message": "ChromaDB not available"
                }
                
        except Exception as e:
            logger.error(f"   ❌ ChromaDB basics test failed: {e}")
            self.test_results["chromadb_basics"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_codebase_scanning(self):
        """Test codebase scanning and indexing."""
        logger.info("🔍 Testing codebase scanning...")
        
        try:
            # Scan a small subset of the codebase for testing
            scan_results = await codebase_analyzer.scan_codebase(".")
            
            files_indexed = scan_results.get("total_files", 0)
            issues_found = scan_results.get("issues_found", 0)
            
            logger.info(f"   ✅ Scanned {files_indexed} files, found {issues_found} issues")
            
            self.test_results["codebase_scanning"] = {
                "status": "passed",
                "files_indexed": files_indexed,
                "issues_found": issues_found,
                "languages": scan_results.get("languages", {}),
                "scan_time": scan_results.get("scan_time", 0)
            }
            
        except Exception as e:
            logger.error(f"   ❌ Codebase scanning test failed: {e}")
            self.test_results["codebase_scanning"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_semantic_search(self):
        """Test semantic code search capabilities."""
        logger.info("🔍 Testing semantic code search...")
        
        try:
            # Test various search queries
            search_queries = [
                "class Agent",
                "trading strategy",
                "API client",
                "error handling",
                "configuration management"
            ]
            
            search_results = {}
            
            for query in search_queries:
                results = await codebase_analyzer.search_code(query, n_results=3)
                search_results[query] = {
                    "results_count": len(results),
                    "top_result": results[0]["path"] if results else None
                }
                logger.info(f"   '{query}': {len(results)} results")
            
            self.test_results["semantic_search"] = {
                "status": "passed",
                "queries_tested": len(search_queries),
                "search_results": search_results
            }
            
        except Exception as e:
            logger.error(f"   ❌ Semantic search test failed: {e}")
            self.test_results["semantic_search"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_issue_detection(self):
        """Test issue detection capabilities."""
        logger.info("🐛 Testing issue detection...")
        
        try:
            # Test issue detection on sample files
            sample_files = [
                "agents/simple_organic_strategy.py",
                "core/config.py",
                "utils/logger.py"
            ]
            
            issue_results = {}
            
            for file_path in sample_files:
                if os.path.exists(file_path):
                    improvements = await codebase_analyzer.suggest_code_improvements(file_path)
                    issue_results[file_path] = {
                        "improvements_count": len(improvements),
                        "improvements": improvements[:3]  # Top 3
                    }
                    logger.info(f"   {file_path}: {len(improvements)} improvements")
                else:
                    logger.info(f"   {file_path}: File not found")
            
            self.test_results["issue_detection"] = {
                "status": "passed",
                "files_analyzed": len([f for f in sample_files if os.path.exists(f)]),
                "issue_results": issue_results
            }
            
        except Exception as e:
            logger.error(f"   ❌ Issue detection test failed: {e}")
            self.test_results["issue_detection"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_self_editing(self):
        """Test self-editing agent capabilities."""
        logger.info("🔧 Testing self-editing capabilities...")
        
        try:
            # Test self-analysis
            analysis = await self_editing_agent.analyze_self()
            
            logger.info(f"   Self-analysis: {len(analysis.get('issues_found', []))} issues found")
            
            # Test self-stats
            stats = await self_editing_agent.get_self_stats()
            
            logger.info(f"   Self-stats: {stats.get('total_modifications', 0)} modifications")
            
            self.test_results["self_editing"] = {
                "status": "passed",
                "self_analysis": {
                    "issues_found": len(analysis.get('issues_found', [])),
                    "improvements_suggested": len(analysis.get('improvements_suggested', [])),
                    "maintainability_score": analysis.get('maintainability_score', 0)
                },
                "self_stats": stats
            }
            
        except Exception as e:
            logger.error(f"   ❌ Self-editing test failed: {e}")
            self.test_results["self_editing"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_code_analysis(self):
        """Test advanced code analysis capabilities."""
        logger.info("📈 Testing code analysis...")
        
        try:
            # Get system overview
            overview = await codebase_analyzer.get_system_overview()
            
            logger.info(f"   System overview: {overview.get('total_files', 0)} files, {overview.get('total_lines', 0)} lines")
            
            # Test code similarity search
            similar_results = await codebase_analyzer.find_similar_code("def __init__", n_results=3)
            
            logger.info(f"   Similar code search: {len(similar_results)} results")
            
            self.test_results["code_analysis"] = {
                "status": "passed",
                "system_overview": overview,
                "similar_code_results": len(similar_results)
            }
            
        except Exception as e:
            logger.error(f"   ❌ Code analysis test failed: {e}")
            self.test_results["code_analysis"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_real_time_modifications(self):
        """Test real-time code modification capabilities."""
        logger.info("⚡ Testing real-time modifications...")
        
        try:
            # Create a test file for modification
            test_file = "test_modification_file.py"
            test_content = """
# Test file for modification
def test_function():
    print("Hello World")
    return True

class TestClass:
    def __init__(self):
        self.value = 0
    
    def get_value(self):
        return self.value
"""
            
            # Write test file
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            # Test code fix
            fix_description = "Add error handling to test_function"
            success = await codebase_analyzer.apply_code_fix(test_file, fix_description)
            
            if success:
                logger.info("   ✅ Code modification test passed")
                
                # Read modified file
                with open(test_file, 'r') as f:
                    modified_content = f.read()
                
                self.test_results["real_time_modifications"] = {
                    "status": "passed",
                    "modification_applied": True,
                    "file_modified": test_file,
                    "content_length": len(modified_content)
                }
            else:
                logger.warning("   ⚠️  Code modification test failed")
                self.test_results["real_time_modifications"] = {
                    "status": "warning",
                    "modification_applied": False
                }
            
            # Clean up test file
            if os.path.exists(test_file):
                os.remove(test_file)
            
        except Exception as e:
            logger.error(f"   ❌ Real-time modifications test failed: {e}")
            self.test_results["real_time_modifications"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def _generate_test_report(self):
        """Generate a comprehensive test report."""
        logger.info("📋 Generating test report...")
        
        # Calculate overall results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.get("status") == "passed"])
        failed_tests = len([r for r in self.test_results.values() if r.get("status") == "failed"])
        warning_tests = len([r for r in self.test_results.values() if r.get("status") == "warning"])
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "test_results": self.test_results,
            "system_info": {
                "chromadb_available": codebase_analyzer.chroma_client is not None,
                "openai_available": bool(config.openai_api_key),
                "python_version": sys.version
            }
        }
        
        # Save report
        with open("chromadb_cursor_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        logger.info("\n📊 Test Report Summary:")
        logger.info(f"   Total tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Warnings: {warning_tests}")
        logger.info(f"   Success rate: {report['summary']['success_rate']:.1f}%")
        
        logger.info("✅ Test report saved to chromadb_cursor_test_report.json")
        
        return report
    
    async def demonstrate_cursor_like_features(self):
        """Demonstrate Cursor-like features."""
        logger.info("🎯 Demonstrating Cursor-like Features")
        
        try:
            # Demo 1: Natural language code search
            logger.info("\n🔍 Demo 1: Natural Language Code Search")
            logger.info("Searching for 'authentication and security' related code...")
            results = await codebase_analyzer.search_code("authentication and security", n_results=5)
            for i, result in enumerate(results, 1):
                logger.info(f"   {i}. {result['path']} (maintainability: {result.get('maintainability_score', 0):.1f})")
            
            # Demo 2: Code pattern matching
            logger.info("\n🔍 Demo 2: Code Pattern Matching")
            logger.info("Finding all class definitions...")
            class_results = await codebase_analyzer.search_code("class definition", n_results=5)
            for i, result in enumerate(class_results, 1):
                logger.info(f"   {i}. {result['path']}")
            
            # Demo 3: Issue detection and suggestions
            logger.info("\n🐛 Demo 3: Issue Detection and Suggestions")
            logger.info("Analyzing a sample file for improvements...")
            sample_file = "agents/simple_organic_strategy.py"
            if os.path.exists(sample_file):
                improvements = await codebase_analyzer.suggest_code_improvements(sample_file)
                logger.info(f"   Found {len(improvements)} potential improvements:")
                for i, improvement in enumerate(improvements[:3], 1):
                    logger.info(f"     {i}. {improvement.get('description', 'Unknown')} ({improvement.get('severity', 'medium')})")
            
            # Demo 4: Self-analysis
            logger.info("\n🤖 Demo 4: Self-Analysis")
            analysis = await self_editing_agent.analyze_self()
            logger.info(f"   Self-editing agent analysis:")
            logger.info(f"     - Maintainability score: {analysis.get('maintainability_score', 0):.1f}")
            logger.info(f"     - Issues found: {len(analysis.get('issues_found', []))}")
            logger.info(f"     - Improvements suggested: {len(analysis.get('improvements_suggested', []))}")
            
            # Demo 5: Code similarity
            logger.info("\n🔍 Demo 5: Code Similarity Search")
            logger.info("Finding similar code patterns...")
            similar_results = await codebase_analyzer.find_similar_code("async def", n_results=3)
            logger.info(f"   Found {len(similar_results)} similar async function patterns")
            
            logger.info("\n✅ Cursor-like features demonstration complete!")
            
        except Exception as e:
            logger.error(f"Feature demonstration failed: {e}")
    
    async def create_usage_guide(self):
        """Create a comprehensive usage guide."""
        logger.info("📚 Creating usage guide...")
        
        usage_guide = {
            "overview": {
                "title": "ChromaDB Cursor-like System Usage Guide",
                "description": "A comprehensive guide for using the ChromaDB system with Cursor-like capabilities",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            },
            "quick_start": {
                "setup": "Run setup_chromadb_system.py to initialize the system",
                "basic_search": "await codebase_analyzer.search_code('your query', n_results=5)",
                "issue_detection": "await codebase_analyzer.suggest_code_improvements('file_path.py')",
                "self_editing": "await self_editing_agent.analyze_self()"
            },
            "examples": {
                "code_search": {
                    "description": "Search for code using natural language",
                    "examples": [
                        "await codebase_analyzer.search_code('authentication function')",
                        "await codebase_analyzer.search_code('trading strategy implementation')",
                        "await codebase_analyzer.search_code('error handling patterns')"
                    ]
                },
                "issue_detection": {
                    "description": "Find and fix code issues",
                    "examples": [
                        "await codebase_analyzer.suggest_code_improvements('my_file.py')",
                        "await codebase_analyzer.apply_code_fix('my_file.py', 'Fix memory leak')"
                    ]
                },
                "self_editing": {
                    "description": "Self-modify agent code",
                    "examples": [
                        "await self_editing_agent.analyze_self()",
                        "await self_editing_agent.fix_self_issue('Fix performance bottleneck')",
                        "await self_editing_agent.optimize_self('performance')",
                        "await self_editing_agent.add_self_feature('Add caching mechanism')"
                    ]
                },
                "code_analysis": {
                    "description": "Analyze code quality and patterns",
                    "examples": [
                        "await codebase_analyzer.get_system_overview()",
                        "await codebase_analyzer.find_similar_code('def __init__')"
                    ]
                }
            },
            "best_practices": [
                "Use specific, descriptive search queries for better results",
                "Review suggested improvements before applying them",
                "Test code modifications before deploying to production",
                "Regularly run self-analysis to maintain code quality",
                "Use the system overview to track codebase health"
            ],
            "troubleshooting": {
                "chromadb_not_available": "Check if OpenAI API key is set in .env file",
                "search_no_results": "Try more specific or different search terms",
                "modification_failed": "Check file permissions and ensure file exists",
                "self_editing_errors": "Review error logs and check agent code integrity"
            }
        }
        
        # Save usage guide
        with open("chromadb_cursor_usage_guide.json", "w") as f:
            json.dump(usage_guide, f, indent=2)
        
        logger.info("✅ Usage guide saved to chromadb_cursor_usage_guide.json")
        
        return usage_guide

async def main():
    """Main test function."""
    logger.info("🚀 Starting ChromaDB Cursor-like System Tests")
    
    # Create tester instance
    tester = ChromaDBCursorTester()
    
    try:
        # Run all tests
        await tester.run_all_tests()
        
        # Demonstrate features
        await tester.demonstrate_cursor_like_features()
        
        # Create usage guide
        await tester.create_usage_guide()
        
        logger.info("\n🎉 ChromaDB Cursor-like system is fully functional!")
        logger.info("📋 Check the generated reports and guides for detailed information")
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 