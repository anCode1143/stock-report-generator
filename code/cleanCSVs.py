#!/usr/bin/env python3
"""
Script to clean CSV files by:
1. Removing the first 50 rows (keeping from row 51 onwards)
"""

import pandas as pd
import os
import glob

def clean_csv_file(file_path):
    """Clean a single CSV file by removing the first 50 rows."""
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Check if file has enough rows
        if len(df) <= 50:
            print(f"⚠️ Skipping {os.path.basename(file_path)}: Only {len(df)} rows (need >50)")
            return False
        
        # Remove first 50 rows (keep from index 50 onwards, which is row 51)
        df_cleaned = df.iloc[50:].reset_index(drop=True)
        
        print(f"📊 {os.path.basename(file_path)}: Removed first 50 rows")
        
        # Save the cleaned data back to the same file
        df_cleaned.to_csv(file_path, index=False)
        
        print(f"✅ {os.path.basename(file_path)}: {len(df)} → {len(df_cleaned)} rows")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {os.path.basename(file_path)}: {e}")
        return False

def clean_all_csvs(csv_directory):
    """Clean all CSV files in the specified directory."""
    # Get all CSV files in the directory
    csv_pattern = os.path.join(csv_directory, "*.csv")
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print(f"No CSV files found in {csv_directory}")
        return
    
    print(f"🚀 Found {len(csv_files)} CSV files to process")
    print(f"📁 Directory: {csv_directory}")
    print("-" * 60)
    
    successful = 0
    failed = 0
    skipped = 0
    
    for file_path in sorted(csv_files):
        result = clean_csv_file(file_path)
        if result is True:
            successful += 1
        elif result is False:
            if "Skipping" in str(result):
                skipped += 1
            else:
                failed += 1
    
    print("-" * 60)
    print(f"📈 Processing Summary:")
    print(f"✅ Successfully processed: {successful}")
    print(f"⚠️ Skipped (too few rows): {skipped}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total files: {len(csv_files)}")

if __name__ == "__main__":
    # Set the CSV directory path - use relative path from project root
    csv_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CSVs")
    
    # Confirm with user before proceeding
    print("🚨 WARNING: This script will modify CSV files in place!")
    print(f"📁 Target directory: {csv_directory}")
    print("📝 Operations:")
    print("   - Remove first 50 rows from each CSV")
    print()
    
    response = input("Do you want to proceed? (yes/no): ").lower().strip()
    
    if response in ['yes', 'y']:
        clean_all_csvs(csv_directory)
    else:
        print("❌ Operation cancelled.")
