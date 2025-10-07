#!/usr/bin/env python3
"""
Build Script - Create standalone executable
Requires: pip install pyinstaller
"""
import subprocess
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

def build_executable():
    """Build standalone executable using PyInstaller"""
    print("🔨 Building Chess AI executable...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=ChessAI-EuryEngine",
        "--onefile",  # Single executable
        "--windowed",  # No console window (GUI only)
        "--icon=src/gui/assets/icon.ico",  # Icon (if exists)
        "--add-data=src/gui/assets:assets",  # Include assets
        "--add-data=src/gui/theme_improved.json:.",  # Include theme
        "--add-data=opening_bin:opening_bin",  # Include opening books
        "--hidden-import=pygame",
        "--hidden-import=chess",
        "--hidden-import=pygame_gui",
        "--clean",  # Clean build
        "src/gui/main_window_v2.py"
    ]
    
    print(f"\n📦 Running: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True)
        
        if result.returncode == 0:
            print("\n✅ Build successful!")
            print(f"\n📂 Executable location: dist/ChessAI-EuryEngine.exe")
            print("\n💡 Distribution tips:")
            print("  1. Test the executable on a clean system")
            print("  2. Include README.md and LICENSE")
            print("  3. Create installer with Inno Setup (optional)")
            print("  4. Upload to GitHub Releases")
            
            # Show file size
            exe_path = PROJECT_ROOT / "dist" / "ChessAI-EuryEngine.exe"
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"\n📊 Executable size: {size_mb:.1f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        return False
    
    return True

def create_portable_package():
    """Create portable ZIP package"""
    print("\n📦 Creating portable package...")
    
    import zipfile
    from datetime import datetime
    
    version = "v2.1.0"
    date = datetime.now().strftime("%Y%m%d")
    zip_name = f"ChessAI-{version}-{date}-portable.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add executable
        zipf.write("dist/ChessAI-EuryEngine.exe", "ChessAI.exe")
        
        # Add documentation
        zipf.write("README.md", "README.md")
        zipf.write("LICENSE", "LICENSE")
        zipf.write("docs/QUICK_START.md", "docs/QUICK_START.md")
        
        # Add opening books (optional)
        for book in Path("opening_bin").glob("*.bin"):
            zipf.write(book, f"opening_bin/{book.name}")
    
    print(f"✅ Created: {zip_name}")
    return zip_name

if __name__ == '__main__':
    print("🎮 Chess AI - Eury Engine Builder")
    print("=" * 50)
    
    choice = input("\nSelect build type:\n  1. Executable only\n  2. Portable package (exe + docs)\n\nChoice (1/2): ")
    
    if choice == '1':
        build_executable()
    elif choice == '2':
        if build_executable():
            create_portable_package()
    else:
        print("❌ Invalid choice")
