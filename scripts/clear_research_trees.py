#!/usr/bin/env python3
"""
Script to clear all existing research trees from the database.
This will remove all stored trees so only fresh, real-time research data is visible.
"""

import sqlite3
import os
import json
from datetime import datetime

def clear_research_trees():
    """Clear all research trees from the database."""
    
    # Database path
    db_path = "research_data/research_trees.db"
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist. Nothing to clear.")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get count of existing trees
        cursor.execute("SELECT COUNT(*) FROM research_trees")
        count = cursor.fetchone()[0]
        
        print(f"Found {count} existing research trees in database.")
        
        if count == 0:
            print("No trees to clear.")
            return
        
        # Clear all trees
        cursor.execute("DELETE FROM research_trees")
        
        # Reset auto-increment counter
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='research_trees'")
        
        # Commit changes
        conn.commit()
        
        print(f"Successfully cleared {count} research trees from database.")
        print("Only fresh, real-time research data will now be visible.")
        
    except Exception as e:
        print(f"Error clearing trees: {e}")
    finally:
        if conn:
            conn.close()

def clear_ai_thoughts():
    """Clear all AI thoughts from the database."""
    
    # Database path
    db_path = "research_data/ai_thoughts.db"
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist. Nothing to clear.")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get count of existing thoughts
        cursor.execute("SELECT COUNT(*) FROM ai_thoughts")
        count = cursor.fetchone()[0]
        
        print(f"Found {count} existing AI thoughts in database.")
        
        if count == 0:
            print("No AI thoughts to clear.")
            return
        
        # Clear all thoughts
        cursor.execute("DELETE FROM ai_thoughts")
        
        # Reset auto-increment counter
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='ai_thoughts'")
        
        # Commit changes
        conn.commit()
        
        print(f"Successfully cleared {count} AI thoughts from database.")
        
    except Exception as e:
        print(f"Error clearing AI thoughts: {e}")
    finally:
        if conn:
            conn.close()

def main():
    """Main function to clear all research data."""
    print("Clearing all existing research data from databases...")
    print("=" * 50)
    
    # Clear research trees
    print("\n1. Clearing research trees...")
    clear_research_trees()
    
    # Clear AI thoughts
    print("\n2. Clearing AI thoughts...")
    clear_ai_thoughts()
    
    print("\n" + "=" * 50)
    print("Database cleanup complete!")
    print("The system will now show only fresh, real-time research data.")
    print("Restart the backend to see the clean state.")

if __name__ == "__main__":
    main() 
 
 