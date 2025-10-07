#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick test script - Kiểm tra nhanh hệ thống
Chạy: python quick_test.py
"""

import sys
import os
import time

# Add to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test 1: Kiểm tra imports."""
    print("="*60)
    print("TEST 1: Kiểm tra imports")
    print("="*60)
    
    try:
        import chess
        print("✅ chess")
    except:
        print("❌ chess - Run: pip install python-chess")
        return False
    
    try:
        import pygame
        print("✅ pygame")
    except:
        print("❌ pygame - Run: pip install pygame")
        return False
    
    try:
        import numpy
        print("✅ numpy")
    except:
        print("❌ numpy - Run: pip install numpy")
        return False
    
    try:
        from src.ai.minimax_optimized import get_best_move
        print("✅ minimax_optimized")
    except Exception as e:
        print(f"❌ minimax_optimized - Error: {e}")
        return False
    
    try:
        from src.ai.evaluation_optimized import evaluate
        print("✅ evaluation_optimized")
    except Exception as e:
        print(f"❌ evaluation_optimized - Error: {e}")
        return False
    
    print("\n✅ Tất cả imports OK!\n")
    return True


def test_ai_basic():
    """Test 2: Test AI cơ bản."""
    print("="*60)
    print("TEST 2: Test AI cơ bản")
    print("="*60)
    
    try:
        import chess
        from src.ai.minimax_optimized import get_best_move
        
        board = chess.Board()
        print(f"Position:\n{board}\n")
        
        print("Tìm nước đi tốt nhất (depth 3, 5s timeout)...")
        start = time.time()
        move = get_best_move(board, depth=3, time_limit=5.0)
        elapsed = time.time() - start
        
        print(f"\n✅ Best move: {move}")
        print(f"⏱️  Time: {elapsed:.3f}s")
        
        if elapsed > 6.0:
            print("⚠️  Warning: Chậm hơn expected (>6s)")
        
        print()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_comparison():
    """Test 3: So sánh OLD vs NEW."""
    print("="*60)
    print("TEST 3: So sánh OLD vs NEW")
    print("="*60)
    
    try:
        import chess
        from src.ai.minimax import get_best_move as old_ai
        from src.ai.minimax_optimized import get_best_move as new_ai
        
        board = chess.Board()
        
        # OLD AI
        print("🔴 OLD AI (depth 3)...")
        start = time.time()
        move_old = old_ai(board.copy(), 3)
        time_old = time.time() - start
        print(f"   Move: {move_old}, Time: {time_old:.3f}s")
        
        # NEW AI
        print("🟢 NEW AI (depth 3)...")
        start = time.time()
        move_new = new_ai(board.copy(), 3, 10.0)
        time_new = time.time() - start
        print(f"   Move: {move_new}, Time: {time_new:.3f}s")
        
        # Compare
        speedup = time_old / time_new if time_new > 0 else 0
        print(f"\n📊 SPEEDUP: {speedup:.2f}x")
        
        if speedup < 2.0:
            print("⚠️  Warning: Speedup < 2x (expected 3-5x)")
        elif speedup >= 3.0:
            print("✅ Excellent speedup!")
        else:
            print("✅ Good speedup!")
        
        print()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_evaluation():
    """Test 4: Test evaluation."""
    print("="*60)
    print("TEST 4: Test evaluation")
    print("="*60)
    
    try:
        import chess
        from src.ai.evaluation_optimized import evaluate
        
        positions = [
            (chess.STARTING_FEN, "Starting", 0),
            ("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1", "After 1.e4", 50),
            ("8/8/8/4k3/8/3K4/4P3/8 w - - 0 1", "K+P endgame", 100),
        ]
        
        all_ok = True
        for fen, desc, expected_range in positions:
            board = chess.Board(fen)
            eval_score = evaluate(board)
            print(f"{desc:20s}: {eval_score:+8.0f}")
            
            if abs(eval_score) > 5000 and "endgame" not in desc.lower():
                print(f"  ⚠️  Warning: Unusual eval score")
                all_ok = False
        
        if all_ok:
            print("\n✅ Evaluation OK!\n")
        else:
            print("\n⚠️  Evaluation có vấn đề\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all quick tests."""
    print("\n" + "="*60)
    print("QUICK TEST - Kiểm tra nhanh hệ thống Chess AI")
    print("="*60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("AI Basic", test_ai_basic),
        ("Comparison", test_comparison),
        ("Evaluation", test_evaluation),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except KeyboardInterrupt:
            print("\n⚠️  Test interrupted!\n")
            break
        except Exception as e:
            print(f"❌ Test '{name}' failed: {e}\n")
            failed += 1
    
    # Summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 TẤT CẢ TESTS PASS! Hệ thống sẵn sàng!")
    else:
        print("\n⚠️  Có lỗi. Xem chi tiết ở trên.")
    
    print("="*60 + "\n")
    
    # Next steps
    print("NEXT STEPS:")
    print("1. Run full tests: python src/tests/test_optimized_ai.py")
    print("2. Run benchmark: python src/tests/benchmark_comparison.py")
    print("3. Play game: python src/main.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user.\n")
    except Exception as e:
        print(f"\n❌ Quick test failed: {e}\n")
        import traceback
        traceback.print_exc()
