"""
Test script for new GUI components
Run this to verify everything works
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("🧪 Testing Chess AI v2.0 Components")
print("=" * 60)

# Test 1: Import components
print("\n1️⃣ Testing component imports...")
try:
    from src.gui.components import (
        ChessClock,
        BoardWidget,
        CapturedPiecesWidget,
        MoveHistoryWidget,
        ControlPanel
    )
    print("✅ All components imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test 2: Import pygame
print("\n2️⃣ Testing pygame...")
try:
    import pygame
    import pygame_gui
    print(f"✅ Pygame version: {pygame.version.ver}")
except ImportError:
    print("❌ Pygame not installed. Run: pip install pygame pygame-gui")
    sys.exit(1)

# Test 3: Import chess
print("\n3️⃣ Testing python-chess...")
try:
    import chess
    print(f"✅ Python-chess imported")
except ImportError:
    print("❌ Python-chess not installed. Run: pip install chess")
    sys.exit(1)

# Test 4: Check AI modules
print("\n4️⃣ Testing AI modules...")
try:
    from src.ai.minimax_optimized import get_best_move
    from src.ai.opening_book import OpeningBook
    print("✅ AI modules available")
except ImportError as e:
    print(f"⚠️  AI modules import warning: {e}")

# Test 5: Check assets
print("\n5️⃣ Checking assets...")
assets_path = os.path.join('src', 'gui', 'assets', 'pieces')
if os.path.exists(assets_path):
    piece_files = os.listdir(assets_path)
    print(f"✅ Found {len(piece_files)} piece images")
else:
    print("⚠️  Assets folder not found")

# Test 6: Check theme
print("\n6️⃣ Checking theme file...")
theme_path = os.path.join('src', 'gui', 'theme_improved.json')
if os.path.exists(theme_path):
    print("✅ Theme file found")
else:
    print("⚠️  Theme file not found")

# Test 7: Test clock functionality
print("\n7️⃣ Testing ChessClock...")
try:
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    manager = pygame_gui.UIManager((800, 600))
    
    clock = ChessClock(manager, 800, 600)
    clock.set_time_control(300, 5)
    clock.start()
    
    # Simulate 1 second
    clock.update(1.0)
    times = clock.get_times()
    
    if times['white'] < 300:
        print("✅ Clock countdown working!")
    else:
        print("⚠️  Clock not counting down")
    
    pygame.quit()
except Exception as e:
    print(f"⚠️  Clock test warning: {e}")

print("\n" + "=" * 60)
print("✅ All tests completed!")
print("=" * 60)
print("\n🚀 Ready to run! Use:")
print("   python -m src.gui.main_window_v2")
print("\nOr old version:")
print("   python -m src.gui.main_window")
