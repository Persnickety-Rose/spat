#!/usr/bin/env python
"""
Verification script to confirm successful migration from traditional to plugin framework
"""

import os
import sys


def check_files_removed():
    """Check that traditional approach files have been removed"""
    files_to_check = [
        "code/sample_tests/apis/WP_APIs.py",
        "code/sample_tests/test_wpT01.py", 
        "code/sample_tests/test_wpT02.py"
    ]
    
    print("🔍 Checking for removed files...")
    all_removed = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"❌ File still exists: {file_path}")
            all_removed = False
        else:
            print(f"✅ File removed: {file_path}")
    
    return all_removed


def check_migrated_files():
    """Check that migrated files exist"""
    files_to_check = [
        "code/sample_tests/test_wpT01_migrated.py",
        "code/sample_tests/test_wpT02_migrated.py",
        "code/sample_tests/MIGRATION_GUIDE.md",
        "code/sample_tests/MIGRATION_SUMMARY.md"
    ]
    
    print("\n🔍 Checking for migrated files...")
    all_exist = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ File missing: {file_path}")
            all_exist = False
    
    return all_exist


def check_legacy_backup_absent():
    """Obsolete in-repo backups are removed; use git history if you need old files."""
    backup_dir = "code/sample_tests/backup_traditional_approach"
    print("\n🔍 Checking legacy backup directory is absent...")
    if os.path.exists(backup_dir):
        print(f"❌ Remove obsolete directory (breaks pytest if repopulated): {backup_dir}")
        return False
    print(f"✅ No legacy backup directory: {backup_dir}")
    return True


def check_plugin_framework():
    """Check that plugin framework files exist"""
    plugin_files = [
        "code/sample_tests/apis/wp_api_client.py",
        "code/pyrest/plugin.py"
    ]
    
    print("\n🔍 Checking for plugin framework files...")
    all_exist = True
    
    for file_path in plugin_files:
        if os.path.exists(file_path):
            print(f"✅ Plugin file exists: {file_path}")
        else:
            print(f"❌ Plugin file missing: {file_path}")
            all_exist = False
    
    return all_exist


def main():
    """Main verification function"""
    print("🔍 Migration Verification Script")
    print("=" * 50)
    
    # Check all aspects of migration
    files_removed = check_files_removed()
    migrated_files_exist = check_migrated_files()
    legacy_backup_absent = check_legacy_backup_absent()
    plugin_framework_exists = check_plugin_framework()
    
    # Summary
    print("\n" + "=" * 50)
    print("MIGRATION VERIFICATION SUMMARY:")
    print(f"✅ Traditional files removed: {files_removed}")
    print(f"✅ Migrated files created: {migrated_files_exist}")
    print(f"✅ Legacy backup directory absent: {legacy_backup_absent}")
    print(f"✅ Plugin framework available: {plugin_framework_exists}")
    
    if all([files_removed, migrated_files_exist, legacy_backup_absent, plugin_framework_exists]):
        print("\n🎉 MIGRATION SUCCESSFUL!")
        print("All traditional approach files have been successfully migrated to the plugin framework.")
        print("\nNext steps:")
        print("1. Run the migrated tests to verify functionality")
        print("2. Update any CI/CD pipelines to use new test files")
        print("3. Share migration guide with team members")
    else:
        print("\n⚠️  MIGRATION INCOMPLETE!")
        print("Some aspects of the migration need attention.")
        print("Please review the issues above and complete the migration.")
    
    return all([files_removed, migrated_files_exist, legacy_backup_absent, plugin_framework_exists])


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
