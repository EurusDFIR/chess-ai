#!/usr/bin/env python3
"""
Cleanup Script - Remove development files for distribution
"""
import os
import shutil
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent

# Files to delete (exact names)
DELETE_FILES = [
    'benchmark_engines.py',
    'demo_analysis_mode.py',
    'demo_game_controls.py',
    'demo_gui_improvements.py',
    'quick_test.py',
    'test_components.py',
    'test_cpp_engine.py',
    'test_cpp_nocache.py',
    'test_current_engine.py',
    'README_V2.md',
    'COMPLETION_SUMMARY.md',
    'img.png',
    'img_1.png',
    'img_2.png',
    'img_3.png',
    'img_4.png',
    'img_5.png',
    'img_6.png',
]

# Folders to delete
DELETE_FOLDERS = [
    'build',
    '.idea',
]

# Docs to delete (development docs)
DELETE_DOCS = [
    'BUILD_GUIDE.md',
    'BUILD_PROGRESS.md',
    'BUILD_STATUS.md',
    'COMPLETION_REPORT.md',
    'CPP_IMPLEMENTATION_GUIDE.md',
    'DETAILED_ANALYSIS.md',
    'DEVELOPER_GUIDE.md',
    'FINAL_REPORT.md',
    'FIXES_COMPLETED.md',
    'FIX_BUILD_ERROR.md',
    'GUI_FIXES_SUMMARY.md',
    'GUI_IMPROVEMENTS.md',
    'GUI_INTEGRATION_GUIDE.md',
    'HYBRID_ARCHITECTURE.md',
    'IMPLEMENTATION_STATUS.md',
    'INDEX.md',
    'NEXT_STEPS.md',
    'OPTIMIZATION_REPORT.md',
    'REFACTORING_SUMMARY.md',
    'TEST_RESULTS.md',
    'VS_INSTALL_GUIDE.md',
    'ARCHITECTURE_DIAGRAM.md',
    'GAME_CONTROLS_SUMMARY.md',
    'README_OPTIMIZED.md',
]

def cleanup():
    """Remove development files"""
    print("🧹 Cleaning up development files...")
    
    deleted_count = 0
    
    # Delete root files
    print("\n📁 Cleaning root directory...")
    for filename in DELETE_FILES:
        filepath = PROJECT_ROOT / filename
        if filepath.exists():
            try:
                filepath.unlink()
                print(f"  ✅ Deleted: {filename}")
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ Error deleting {filename}: {e}")
    
    # Delete folders
    print("\n📂 Cleaning folders...")
    for folder in DELETE_FOLDERS:
        folderpath = PROJECT_ROOT / folder
        if folderpath.exists():
            try:
                shutil.rmtree(folderpath)
                print(f"  ✅ Deleted folder: {folder}/")
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ Error deleting {folder}: {e}")
    
    # Delete docs
    print("\n📄 Cleaning docs...")
    docs_dir = PROJECT_ROOT / 'docs'
    for doc in DELETE_DOCS:
        docpath = docs_dir / doc
        if docpath.exists():
            try:
                docpath.unlink()
                print(f"  ✅ Deleted: docs/{doc}")
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ Error deleting {doc}: {e}")
    
    # Create images folder and suggest moving screenshots
    images_dir = docs_dir / 'images'
    if not images_dir.exists():
        images_dir.mkdir()
        print(f"\n📸 Created: docs/images/")
        print("  ℹ️  You can move screenshots here manually")
    
    print(f"\n✨ Cleanup complete! Removed {deleted_count} items.")
    print("\n📋 Remaining structure:")
    print("  ├── README.md")
    print("  ├── requirements.txt")
    print("  ├── setup.py")
    print("  ├── src/")
    print("  ├── opening_bin/")
    print("  ├── syzygy/")
    print("  └── docs/")
    print("      ├── QUICK_START.md")
    print("      ├── GAME_CONTROLS_GUIDE.md")
    print("      ├── ANALYSIS_MODE_GUIDE.md")
    print("      └── TODO.md")
    
    print("\n💡 Next steps:")
    print("  1. Review remaining files")
    print("  2. Update README.md with installation instructions")
    print("  3. Add LICENSE file")
    print("  4. Update .gitignore")
    print("  5. Create GitHub release or build executable")

if __name__ == '__main__':
    response = input("⚠️  This will DELETE development files. Continue? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        cleanup()
    else:
        print("❌ Cleanup cancelled.")
