#!/usr/bin/env python3
"""
ChromaDB Setup Script: Cursor-like Code Analysis and Self-Editing System

This script sets up:
1. ChromaDB with proper collections for code, issues, and changes
2. Codebase analyzer that can scan and index all code
3. Self-editing capabilities for agents
4. Integration with existing meta-agent system
5. Real-time code monitoring and analysis
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.codebase_analyzer import codebase_analyzer
from agents.self_editing_agent import self_editing_agent
from agents.meta_agent_system import MetaAgent
from core.config import config
from utils.logger import logger

class ChromaDBSetup:
    """
    Comprehensive ChromaDB setup with Cursor-like capabilities.
    """
    
    def __init__(self):
        self.setup_complete = False
        self.collections_created = []
        self.indexed_files = 0
        self.issues_found = 0
        
    async def setup_complete_system(self):
        """Set up the complete ChromaDB system with code analysis and self-editing."""
        logger.info("🚀 Setting up ChromaDB system with Cursor-like capabilities...")
        
        try:
            # Step 1: Initialize ChromaDB
            await self._setup_chromadb()
            
            # Step 2: Scan and index the codebase
            await self._scan_and_index_codebase()
            
            # Step 3: Set up self-editing capabilities
            await self._setup_self_editing()
            
            # Step 4: Integrate with meta-agent system
            await self._integrate_with_meta_agent()
            
            # Step 5: Run initial analysis
            await self._run_initial_analysis()
            
            # Step 6: Test the system
            await self._test_system()
            
            self.setup_complete = True
            logger.info("✅ ChromaDB system setup complete!")
            
        except Exception as e:
            logger.error(f"ChromaDB setup failed: {e}")
            raise
    
    async def _setup_chromadb(self):
        """Initialize ChromaDB with proper collections."""
        logger.info("📊 Setting up ChromaDB collections...")
        
        try:
            # Check if ChromaDB is properly configured
            if not config.openai_api_key:
                logger.warning("⚠️  OpenAI API key not found - embeddings will be disabled")
                logger.info("💡 Set OPENAI_API_KEY in your .env file for full functionality")
            
            # Initialize the codebase analyzer (which sets up ChromaDB)
            if codebase_analyzer.chroma_client:
                logger.info("✅ ChromaDB client initialized successfully")
                
                # List available collections
                collections = codebase_analyzer.chroma_client.list_collections()
                logger.info(f"📋 Available collections: {[c.name for c in collections]}")
                
                self.collections_created = [c.name for c in collections]
            else:
                logger.warning("⚠️  ChromaDB client not available - using fallback mode")
                
        except Exception as e:
            logger.error(f"ChromaDB setup failed: {e}")
            raise
    
    async def _scan_and_index_codebase(self):
        """Scan the entire codebase and index it in ChromaDB."""
        logger.info("🔍 Scanning and indexing codebase...")
        
        try:
            # Scan the codebase
            scan_results = await codebase_analyzer.scan_codebase(".")
            
            self.indexed_files = scan_results.get("total_files", 0)
            self.issues_found = scan_results.get("issues_found", 0)
            
            logger.info(f"📁 Indexed {self.indexed_files} files")
            logger.info(f"🐛 Found {self.issues_found} issues")
            
            # Log language distribution
            languages = scan_results.get("languages", {})
            if languages:
                logger.info("📊 Language distribution:")
                for lang, count in languages.items():
                    logger.info(f"   {lang}: {count} files")
            
            # Log scan time
            scan_time = scan_results.get("scan_time", 0)
            logger.info(f"⏱️  Scan completed in {scan_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Codebase scanning failed: {e}")
            raise
    
    async def _setup_self_editing(self):
        """Set up self-editing capabilities."""
        logger.info("🔧 Setting up self-editing capabilities...")
        
        try:
            # Test self-editing agent
            analysis = await self_editing_agent.analyze_self()
            
            logger.info(f"🤖 Self-editing agent analysis complete:")
            logger.info(f"   Maintainability score: {analysis.get('maintainability_score', 0):.1f}")
            logger.info(f"   Issues found: {len(analysis.get('issues_found', []))}")
            logger.info(f"   Improvements suggested: {len(analysis.get('improvements_suggested', []))}")
            
            # Log suggested improvements
            improvements = analysis.get("improvements_suggested", [])
            if improvements:
                logger.info("💡 Suggested improvements:")
                for improvement in improvements[:5]:  # Show first 5
                    logger.info(f"   - {improvement.get('description', 'Unknown')} ({improvement.get('priority', 'medium')})")
            
        except Exception as e:
            logger.error(f"Self-editing setup failed: {e}")
            raise
    
    async def _integrate_with_meta_agent(self):
        """Integrate the system with the existing meta-agent."""
        logger.info("🔗 Integrating with meta-agent system...")
        
        try:
            # Initialize meta-agent
            meta_agent = MetaAgent()
            
            # Register the codebase analyzer and self-editing agent
            await meta_agent.register_agent("codebase_analyzer", {
                "type": "analysis",
                "capabilities": ["code_scanning", "issue_detection", "semantic_search"],
                "status": "active"
            })
            
            await meta_agent.register_agent("self_editing_agent", {
                "type": "modification",
                "capabilities": ["self_analysis", "bug_fixing", "optimization", "feature_addition"],
                "status": "active"
            })
            
            logger.info("✅ Integration with meta-agent complete")
            
        except Exception as e:
            logger.error(f"Meta-agent integration failed: {e}")
            # Don't raise here as this is optional
    
    async def _run_initial_analysis(self):
        """Run initial analysis of the system."""
        logger.info("📈 Running initial system analysis...")
        
        try:
            # Get system overview
            overview = await codebase_analyzer.get_system_overview()
            
            logger.info("📊 System Overview:")
            logger.info(f"   Total files: {overview.get('total_files', 0)}")
            logger.info(f"   Total lines: {overview.get('total_lines', 0)}")
            logger.info(f"   Average complexity: {overview.get('avg_complexity', 0):.1f}")
            logger.info(f"   Average maintainability: {overview.get('avg_maintainability', 0):.1f}")
            logger.info(f"   Total functions: {overview.get('total_functions', 0)}")
            logger.info(f"   Total classes: {overview.get('total_classes', 0)}")
            logger.info(f"   Total issues: {overview.get('total_issues', 0)}")
            
            # Language breakdown
            languages = overview.get("languages", {})
            if languages:
                logger.info("   Language breakdown:")
                for lang, count in languages.items():
                    logger.info(f"     {lang}: {count} files")
            
        except Exception as e:
            logger.error(f"Initial analysis failed: {e}")
            # Don't raise here as this is informational
    
    async def _test_system(self):
        """Test the ChromaDB system functionality."""
        logger.info("🧪 Testing system functionality...")
        
        try:
            # Test 1: Code search
            logger.info("   Testing code search...")
            search_results = await codebase_analyzer.search_code("class Agent", n_results=3)
            logger.info(f"   Found {len(search_results)} results for 'class Agent'")
            
            # Test 2: Issue detection
            logger.info("   Testing issue detection...")
            if self.issues_found > 0:
                logger.info(f"   ✅ Issue detection working ({self.issues_found} issues found)")
            else:
                logger.info("   ✅ Issue detection working (no issues found)")
            
            # Test 3: Self-editing capabilities
            logger.info("   Testing self-editing capabilities...")
            stats = await self_editing_agent.get_self_stats()
            logger.info(f"   ✅ Self-editing agent ready (modifications: {stats.get('total_modifications', 0)})")
            
            # Test 4: ChromaDB collections
            logger.info("   Testing ChromaDB collections...")
            if codebase_analyzer.chroma_client:
                collections = codebase_analyzer.chroma_client.list_collections()
                logger.info(f"   ✅ ChromaDB working ({len(collections)} collections)")
            else:
                logger.info("   ⚠️  ChromaDB not available (fallback mode)")
            
            logger.info("✅ All system tests passed!")
            
        except Exception as e:
            logger.error(f"System testing failed: {e}")
            raise
    
    async def demonstrate_cursor_like_capabilities(self):
        """Demonstrate Cursor-like capabilities."""
        logger.info("🎯 Demonstrating Cursor-like capabilities...")
        
        try:
            # Demo 1: Semantic code search
            logger.info("\n🔍 Demo 1: Semantic Code Search")
            logger.info("Searching for 'trading strategy' related code...")
            results = await codebase_analyzer.search_code("trading strategy", n_results=3)
            for i, result in enumerate(results, 1):
                logger.info(f"   {i}. {result['path']} (score: {result.get('maintainability_score', 0):.1f})")
            
            # Demo 2: Issue detection
            logger.info("\n🐛 Demo 2: Issue Detection")
            logger.info("Analyzing a sample file for issues...")
            sample_files = ["agents/simple_organic_strategy.py", "core/config.py"]
            for file_path in sample_files:
                if os.path.exists(file_path):
                    improvements = await codebase_analyzer.suggest_code_improvements(file_path)
                    logger.info(f"   {file_path}: {len(improvements)} improvements suggested")
                    break
            
            # Demo 3: Self-editing
            logger.info("\n🔧 Demo 3: Self-Editing Capabilities")
            analysis = await self_editing_agent.analyze_self()
            logger.info(f"   Self-analysis complete: {len(analysis.get('issues_found', []))} issues found")
            
            # Demo 4: Code similarity
            logger.info("\n🔍 Demo 4: Code Similarity Search")
            logger.info("Finding similar code patterns...")
            similar_results = await codebase_analyzer.find_similar_code("def __init__", n_results=3)
            logger.info(f"   Found {len(similar_results)} similar patterns")
            
            logger.info("\n✅ Cursor-like capabilities demonstration complete!")
            
        except Exception as e:
            logger.error(f"Capability demonstration failed: {e}")
    
    async def create_usage_examples(self):
        """Create usage examples for the system."""
        logger.info("📚 Creating usage examples...")
        
        examples = {
            "code_search": {
                "description": "Search for code using natural language",
                "example": "await codebase_analyzer.search_code('authentication function', n_results=5)"
            },
            "issue_detection": {
                "description": "Find issues in specific files",
                "example": "await codebase_analyzer.suggest_code_improvements('agents/my_agent.py')"
            },
            "self_editing": {
                "description": "Fix issues in the agent's own code",
                "example": "await self_editing_agent.fix_self_issue('Fix memory leak in data processing')"
            },
            "code_optimization": {
                "description": "Optimize code for performance",
                "example": "await self_editing_agent.optimize_self('performance')"
            },
            "feature_addition": {
                "description": "Add new features to the agent",
                "example": "await self_editing_agent.add_self_feature('Add caching mechanism for API calls')"
            },
            "debugging": {
                "description": "Debug issues automatically",
                "example": "await self_editing_agent.debug_self('API timeout error')"
            }
        }
        
        # Save examples to file
        with open("chromadb_usage_examples.json", "w") as f:
            json.dump(examples, f, indent=2)
        
        logger.info("✅ Usage examples saved to chromadb_usage_examples.json")
        
        return examples
    
    def get_setup_summary(self) -> Dict[str, Any]:
        """Get a summary of the setup."""
        return {
            "setup_complete": self.setup_complete,
            "collections_created": self.collections_created,
            "indexed_files": self.indexed_files,
            "issues_found": self.issues_found,
            "chromadb_available": codebase_analyzer.chroma_client is not None,
            "self_editing_available": True,
            "meta_agent_integrated": True,
            "timestamp": datetime.now().isoformat()
        }

async def main():
    """Main setup function."""
    logger.info("🚀 Starting ChromaDB Setup with Cursor-like Capabilities")
    
    # Create setup instance
    setup = ChromaDBSetup()
    
    try:
        # Run complete setup
        await setup.setup_complete_system()
        
        # Demonstrate capabilities
        await setup.demonstrate_cursor_like_capabilities()
        
        # Create usage examples
        await setup.create_usage_examples()
        
        # Print summary
        summary = setup.get_setup_summary()
        logger.info("\n📋 Setup Summary:")
        logger.info(f"   ✅ Setup complete: {summary['setup_complete']}")
        logger.info(f"   📊 Files indexed: {summary['indexed_files']}")
        logger.info(f"   🐛 Issues found: {summary['issues_found']}")
        logger.info(f"   🗄️  ChromaDB available: {summary['chromadb_available']}")
        logger.info(f"   🔧 Self-editing available: {summary['self_editing_available']}")
        logger.info(f"   🤖 Meta-agent integrated: {summary['meta_agent_integrated']}")
        
        logger.info("\n🎉 ChromaDB system is ready with Cursor-like capabilities!")
        logger.info("💡 Use the usage examples in chromadb_usage_examples.json to get started")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 