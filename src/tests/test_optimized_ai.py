#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick test script for the optimized AI
"""

import sys
import os
import chess
import time

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.ai.minimax_optimized import get_best_move
from src.ai.evaluation_optimized import evaluate


def test_basic():
    """Test basic functionality."""
    print("="*80)
    print("TEST 1: Basic Functionality")
    print("="*80 + "\n")
    
    board = chess.Board()
    print(f"Starting position:\n{board}\n")
    
    print("Finding best move (depth 4)...")
    start = time.time()
    best_move = get_best_move(board, depth=4, time_limit=10.0)
    elapsed = time.time() - start
    
    print(f"\n✅ Best move: {best_move}")
    print(f"⏱️  Time: {elapsed:.3f}s\n")


def test_tactical():
    """Test tactical awareness."""
    print("="*80)
    print("TEST 2: Tactical Awareness")
    print("="*80 + "\n")
    
    # Position with a tactical shot
    # White to move and win material
    fen = "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 w kq - 0 6"
    board = chess.Board(fen)
    
    print(f"Position (Scholar's Mate setup):\n{board}\n")
    print("Expected: Qh5 or similar attacking move")
    
    print("\nFinding best move (depth 5)...")
    start = time.time()
    best_move = get_best_move(board, depth=5, time_limit=15.0)
    elapsed = time.time() - start
    
    print(f"\n✅ Best move: {best_move}")
    print(f"⏱️  Time: {elapsed:.3f}s\n")


def test_endgame():
    """Test endgame play."""
    print("="*80)
    print("TEST 3: Endgame Play")
    print("="*80 + "\n")
    
    # King and pawn endgame
    fen = "8/8/8/4k3/8/3K4/4P3/8 w - - 0 1"
    board = chess.Board(fen)
    
    print(f"Endgame position:\n{board}\n")
    
    print("Finding best move (depth 6)...")
    start = time.time()
    best_move = get_best_move(board, depth=6, time_limit=10.0)
    elapsed = time.time() - start
    
    print(f"\n✅ Best move: {best_move}")
    print(f"⏱️  Time: {elapsed:.3f}s\n")


def test_evaluation():
    """Test evaluation function."""
    print("="*80)
    print("TEST 4: Evaluation Function")
    print("="*80 + "\n")
    
    positions = [
        (chess.STARTING_FEN, "Starting position"),
        ("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1", "After 1.e4"),
        ("rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3", "After 1.e4 e5 2.Nf3 Nf6"),
        ("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4", "Italian Opening"),
    ]
    
    for fen, description in positions:
        board = chess.Board(fen)
        eval_score = evaluate(board)
        print(f"{description}:")
        print(f"  Evaluation: {eval_score:+.2f} (from white's perspective)")
        print()


def test_speed():
    """Test search speed at different depths."""
    print("="*80)
    print("TEST 5: Speed Test at Different Depths")
    print("="*80 + "\n")
    
    board = chess.Board()
    
    for depth in [3, 4, 5, 6]:
        print(f"Depth {depth}:")
        start = time.time()
        best_move = get_best_move(board, depth=depth, time_limit=60.0)
        elapsed = time.time() - start
        print(f"  Move: {best_move}")
        print(f"  Time: {elapsed:.3f}s")
        print()


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*80)
    print(" "*20 + "CHESS AI OPTIMIZED - TEST SUITE")
    print("="*80 + "\n")
    
    tests = [
        ("Basic Functionality", test_basic),
        ("Tactical Awareness", test_tactical),
        ("Endgame Play", test_endgame),
        ("Evaluation Function", test_evaluation),
        ("Speed Test", test_speed),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ Test '{name}' FAILED with error: {e}\n")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
