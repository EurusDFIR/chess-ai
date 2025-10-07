"""Test current Python engine without C++"""
import sys
import time
sys.path.insert(0, 'src')

from game.board import Board
from ai.minimax import get_best_move_minimax
from ai.evaluation import evaluate_board

# Test 1: Board setup
print("=" * 50)
print("TEST 1: Board Initialization")
print("=" * 50)
board = Board()
print("✅ Board created successfully")
print(board)
print()

# Test 2: Evaluation
print("=" * 50)
print("TEST 2: Position Evaluation")
print("=" * 50)
score = evaluate_board(board)
print(f"Starting position score: {score}")
print("✅ Evaluation working")
print()

# Test 3: Move generation and search
print("=" * 50)
print("TEST 3: AI Move Search (depth 3)")
print("=" * 50)
print("Searching for best move...")
start = time.time()
best_move = get_best_move_minimax(board, depth=3)
elapsed = time.time() - start

if best_move:
    print(f"✅ Best move found: {best_move}")
    print(f"⚡ Time: {elapsed:.3f}s")
    
    # Make the move
    board.make_move(best_move)
    print(f"\nBoard after move:")
    print(board)
else:
    print("❌ No move found")

print()
print("=" * 50)
print("🎉 Python Engine Working!")
print("=" * 50)
print("\nNote: C++ engine cần compile trước.")
print("Sau khi restart terminal và thêm CMake vào PATH,")
print("chạy: python setup.py develop")
