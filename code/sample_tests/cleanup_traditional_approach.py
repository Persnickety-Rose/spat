#!/usr/bin/env python
"""
Cleanup script to remove traditional approach from the codebase
This script helps identify and remove files and references to the traditional approach
"""

import os
import sys


def find_files_to_remove():
    """Find files that should be removed after migration"""
    files_to_remove = [
        "code/sample_tests/apis/WP_APIs.py",
        "code/sample_tests/test_wpT01.py",
        "code/sample_tests/test_wpT02.py",
    ]
    
    existing_files = []
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            existing_files.append(file_path)
        else:
            print(f"⚠️  File not found: {file_path}")
    
    return existing_files


def find_references_to_remove():
    """Find references to traditional approach that need to be updated"""
    references = []
    
    # Search for WP_APIs imports
    for root, dirs, files in os.walk("code"):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if 'WP_APIs' in content:
                            references.append(file_path)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return references


def remove_files(files_to_remove, dry_run=True):
    """Remove files (with dry run option)"""
    for file_path in files_to_remove:
        if dry_run:
            print(f"🔍 Would remove: {file_path}")
        else:
            try:
                os.remove(file_path)
                print(f"🗑️  Removed: {file_path}")
            except Exception as e:
                print(f"❌ Error removing {file_path}: {e}")


def update_documentation():
    """Update documentation to reflect migration"""
    docs_to_update = [
        "code/sample_tests/PLUGIN_VS_TRADITIONAL.md",
        "README.md"
    ]
    
    for doc_path in docs_to_update:
        if os.path.exists(doc_path):
            print(f"📝 Documentation to update: {doc_path}")
        else:
            print(f"⚠️  Documentation not found: {doc_path}")


def main():
    """Main cleanup function"""
    print("🧹 Traditional Approach Cleanup Script")
    print("=" * 50)
    
    # Find files to remove
    print("\n1. Finding files to remove...")
    files_to_remove = find_files_to_remove()
    
    if files_to_remove:
        print(f"Found {len(files_to_remove)} files to remove:")
        for file_path in files_to_remove:
            print(f"  - {file_path}")
    else:
        print("No files found to remove.")
    
    # Find references
    print("\n2. Finding references to traditional approach...")
    references = find_references_to_remove()
    
    if references:
        print(f"Found {len(references)} files with references:")
        for file_path in references:
            print(f"  - {file_path}")
    else:
        print("No references found.")
    
    # Update documentation
    print("\n3. Documentation to update...")
    update_documentation()
    
    # Ask for confirmation
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"- Files to remove: {len(files_to_remove)}")
    print(f"- Files with references: {len(references)}")
    print("- Use git history if you need copies of removed files.")
    
    if files_to_remove:
        response = input("\nDo you want to proceed with removal? (y/N): ")
        if response.lower() == 'y':
            print("\n4. Removing files...")
            remove_files(files_to_remove, dry_run=False)
            print("\n✅ Cleanup completed!")
        else:
            print("\n❌ Cleanup cancelled.")
    else:
        print("\n✅ No files to remove.")


if __name__ == "__main__":
    main()
