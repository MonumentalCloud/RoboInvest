#!/usr/bin/env python3
"""
Demo Script: ChromaDB Cursor-like Capabilities

This script demonstrates the key features of the ChromaDB system:
1. Natural language code search
2. Issue detection and suggestions
3. Self-editing capabilities
4. Code analysis and optimization
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.codebase_analyzer import codebase_analyzer
from agents.self_editing_agent import self_editing_agent
from core.config import config
from utils.logger import logger

async def demo_code_search():
    """Demonstrate natural language code search."""
    print("\n🔍 Demo 1: Natural Language Code Search")
    print("=" * 50)
    
    # Search queries to demonstrate
    search_queries = [
        "trading strategy implementation",
        "API client configuration", 
        "error handling patterns",
        "authentication and security",
        "data processing functions"
    ]
    
    for query in search_queries:
        print(f"\nSearching for: '{query}'")
        try:
            results = await codebase_analyzer.search_code(query, n_results=3)
            print(f"Found {len(results)} results:")
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['path']}")
                print(f"     Language: {result['language']}")
                print(f"     Lines: {result['lines']}")
                print(f"     Maintainability: {result.get('maintainability_score', 0):.1f}")
                
        except Exception as e:
            print(f"  Error: {e}")

async def demo_issue_detection():
    """Demonstrate issue detection and suggestions."""
    print("\n🐛 Demo 2: Issue Detection and Suggestions")
    print("=" * 50)
    
    # Sample files to analyze
    sample_files = [
        "agents/simple_organic_strategy.py",
        "core/config.py",
        "utils/logger.py"
    ]
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            print(f"\nAnalyzing: {file_path}")
            try:
                improvements = await codebase_analyzer.suggest_code_improvements(file_path)
                print(f"Found {len(improvements)} potential improvements:")
                
                for i, improvement in enumerate(improvements[:3], 1):
                    print(f"  {i}. {improvement.get('description', 'Unknown')}")
                    print(f"     Severity: {improvement.get('severity', 'medium')}")
                    print(f"     Suggestion: {improvement.get('suggestion', 'No suggestion')}")
                    
            except Exception as e:
                print(f"  Error: {e}")
        else:
            print(f"\nFile not found: {file_path}")

async def demo_self_editing():
    """Demonstrate self-editing capabilities."""
    print("\n🔧 Demo 3: Self-Editing Capabilities")
    print("=" * 50)
    
    try:
        # Self-analysis
        print("\nRunning self-analysis...")
        analysis = await self_editing_agent.analyze_self()
        
        print(f"Self-editing agent analysis results:")
        print(f"  Maintainability score: {analysis.get('maintainability_score', 0):.1f}")
        print(f"  Issues found: {len(analysis.get('issues_found', []))}")
        print(f"  Improvements suggested: {len(analysis.get('improvements_suggested', []))}")
        
        # Show some improvements
        improvements = analysis.get('improvements_suggested', [])
        if improvements:
            print("\nTop improvements suggested:")
            for i, improvement in enumerate(improvements[:3], 1):
                print(f"  {i}. {improvement.get('description', 'Unknown')}")
                print(f"     Priority: {improvement.get('priority', 'medium')}")
                print(f"     Impact: {improvement.get('impact', 'medium')}")
        
        # Self-stats
        print("\nSelf-editing statistics:")
        stats = await self_editing_agent.get_self_stats()
        print(f"  Total modifications: {stats.get('total_modifications', 0)}")
        print(f"  Total debug sessions: {stats.get('total_debug_sessions', 0)}")
        print(f"  Successful modifications: {stats.get('successful_modifications', 0)}")
        print(f"  Successful debug fixes: {stats.get('successful_debug_fixes', 0)}")
        
    except Exception as e:
        print(f"Error in self-editing demo: {e}")

async def demo_code_analysis():
    """Demonstrate code analysis capabilities."""
    print("\n📈 Demo 4: Code Analysis and Overview")
    print("=" * 50)
    
    try:
        # System overview
        print("\nGetting system overview...")
        overview = await codebase_analyzer.get_system_overview()
        
        print("System Overview:")
        print(f"  Total files: {overview.get('total_files', 0)}")
        print(f"  Total lines: {overview.get('total_lines', 0)}")
        print(f"  Average complexity: {overview.get('avg_complexity', 0):.1f}")
        print(f"  Average maintainability: {overview.get('avg_maintainability', 0):.1f}")
        print(f"  Total functions: {overview.get('total_functions', 0)}")
        print(f"  Total classes: {overview.get('total_classes', 0)}")
        print(f"  Total issues: {overview.get('total_issues', 0)}")
        
        # Language breakdown
        languages = overview.get("languages", {})
        if languages:
            print("\nLanguage breakdown:")
            for lang, count in languages.items():
                print(f"  {lang}: {count} files")
        
        # Code similarity search
        print("\nFinding similar code patterns...")
        similar_results = await codebase_analyzer.find_similar_code("def __init__", n_results=3)
        print(f"Found {len(similar_results)} similar constructor patterns")
        
        for i, result in enumerate(similar_results, 1):
            print(f"  {i}. {result['path']}")
            
    except Exception as e:
        print(f"Error in code analysis demo: {e}")

async def demo_real_time_modification():
    """Demonstrate real-time code modification."""
    print("\n⚡ Demo 5: Real-Time Code Modification")
    print("=" * 50)
    
    try:
        # Create a test file
        test_file = "demo_test_file.py"
        test_content = """
# Demo test file for modification
def demo_function():
    print("Hello World")
    return True

class DemoClass:
    def __init__(self):
        self.value = 0
    
    def get_value(self):
        return self.value
"""
        
        print(f"Creating test file: {test_file}")
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        # Apply a modification
        print("Applying modification: Add error handling to demo_function")
        success = await codebase_analyzer.apply_code_fix(test_file, "Add error handling to demo_function")
        
        if success:
            print("✅ Modification applied successfully!")
            
            # Show the modified content
            with open(test_file, 'r') as f:
                modified_content = f.read()
            
            print("\nModified content:")
            print(modified_content)
        else:
            print("❌ Modification failed")
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"Cleaned up test file: {test_file}")
            
    except Exception as e:
        print(f"Error in real-time modification demo: {e}")

async def demo_cursor_like_features():
    """Demonstrate Cursor-like features."""
    print("\n🎯 Demo 6: Cursor-like Features")
    print("=" * 50)
    
    try:
        # Feature 1: Find all agent classes
        print("\n1. Finding all agent classes...")
        agent_results = await codebase_analyzer.search_code("class Agent", n_results=5)
        print(f"Found {len(agent_results)} agent-related classes")
        
        # Feature 2: Find async functions
        print("\n2. Finding async functions...")
        async_results = await codebase_analyzer.search_code("async def", n_results=5)
        print(f"Found {len(async_results)} async functions")
        
        # Feature 3: Find configuration patterns
        print("\n3. Finding configuration patterns...")
        config_results = await codebase_analyzer.search_code("configuration settings", n_results=3)
        print(f"Found {len(config_results)} configuration-related files")
        
        # Feature 4: Find error handling patterns
        print("\n4. Finding error handling patterns...")
        error_results = await codebase_analyzer.search_code("try except error handling", n_results=3)
        print(f"Found {len(error_results)} error handling patterns")
        
    except Exception as e:
        print(f"Error in Cursor-like features demo: {e}")

async def main():
    """Main demonstration function."""
    print("🚀 ChromaDB Cursor-like System Demonstration")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"ChromaDB available: {codebase_analyzer.chroma_client is not None}")
    print(f"OpenAI available: {bool(config.openai_api_key)}")
    
    try:
        # Run all demos
        await demo_code_search()
        await demo_issue_detection()
        await demo_self_editing()
        await demo_code_analysis()
        await demo_real_time_modification()
        await demo_cursor_like_features()
        
        print("\n🎉 All demonstrations completed successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("  ✅ Natural language code search")
        print("  ✅ Issue detection and suggestions")
        print("  ✅ Self-editing capabilities")
        print("  ✅ Code analysis and overview")
        print("  ✅ Real-time code modification")
        print("  ✅ Cursor-like pattern matching")
        
        print("\n📚 For more examples, check:")
        print("  - chromadb_usage_examples.json")
        print("  - chromadb_cursor_usage_guide.json (if generated)")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 