#!/usr/bin/env python3
"""
Script to clear all existing research data JSON files.
This will remove all stored research data so only fresh, real-time data is visible.
"""

import os
import glob
import shutil
from datetime import datetime

def clear_research_data():
    """Clear all research data JSON files."""
    
    research_data_dir = "research_data"
    
    if not os.path.exists(research_data_dir):
        print(f"Research data directory {research_data_dir} does not exist. Nothing to clear.")
        return
    
    # Create backup directory with timestamp
    backup_dir = f"research_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Find all JSON files in research_data directory
    json_files = glob.glob(os.path.join(research_data_dir, "*.json"))
    
    if not json_files:
        print("No JSON files found in research_data directory.")
        return
    
    print(f"Found {len(json_files)} JSON files in research_data directory.")
    print(f"Backing up to {backup_dir}...")
    
    # Move files to backup directory
    moved_count = 0
    for file_path in json_files:
        try:
            filename = os.path.basename(file_path)
            backup_path = os.path.join(backup_dir, filename)
            shutil.move(file_path, backup_path)
            moved_count += 1
            print(f"  Moved: {filename}")
        except Exception as e:
            print(f"  Error moving {filename}: {e}")
    
    print(f"\nSuccessfully moved {moved_count} files to backup directory: {backup_dir}")
    print("The system will now show only fresh, real-time research data.")
    print("Restart the backend to see the clean state.")

def main():
    """Main function to clear research data."""
    print("Clearing all existing research data files...")
    print("=" * 50)
    
    clear_research_data()
    
    print("\n" + "=" * 50)
    print("Research data cleanup complete!")
    print("Only fresh, real-time research data will now be visible.")

if __name__ == "__main__":
    main() 
 
 