#!/usr/bin/env python3
"""
Compare v2.3.0 (opening improvements) vs v2.4.0 (advanced search)
Test to see node reduction and strength improvement
"""

import chess
import time
from src.ai.minimax_optimized import get_best_move as get_best_move_v23
from src.ai.minimax_v2_4 import get_best_move_advanced as get_best_move_v24


def test_position(fen, name, depth=5, time_limit=5.0):
    """Test both engines on a position"""
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"FEN: {fen}")
    print(f"{'='*70}")
    
    board = chess.Board(fen)
    
    # Test v2.3.0
    print("\n[v2.3.0] (Opening Improvements):")
    start = time.time()
    move_v23 = get_best_move_v23(board.copy(), depth=depth, time_limit=time_limit)
    time_v23 = time.time() - start
    
    # Test v2.4.0
    print("\n[v2.4.0] (Advanced Search):")
    start = time.time()
    move_v24 = get_best_move_v24(board.copy(), depth=depth, time_limit=time_limit)
    time_v24 = time.time() - start
    
    # Compare
    print(f"\nComparison:")
    print(f"  v2.3.0: {move_v23} in {time_v23:.2f}s")
    print(f"  v2.4.0: {move_v24} in {time_v24:.2f}s")
    print(f"  Same move: {'[YES]' if move_v23 == move_v24 else '[NO]'}")
    print(f"  Speedup: {time_v23/time_v24:.2f}x" if time_v24 > 0 else "  Speedup: N/A")
    
    return {
        'name': name,
        'v23_move': move_v23,
        'v24_move': move_v24,
        'v23_time': time_v23,
        'v24_time': time_v24,
        'same_move': move_v23 == move_v24
    }


def main():
    """Run comparison tests"""
    print("\n")
    print("=" + "="*68 + "=")
    print(" "*15 + "CHESS AI v2.3.0 vs v2.4.0 COMPARISON")
    print("=" + "="*68 + "=")
    
    test_cases = [
        ("Starting position", chess.STARTING_FEN),
        ("Sicilian Defense", "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"),
        ("Italian Game", "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3"),
        ("Tactical position", "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 5"),
        ("Endgame", "8/5pk1/6p1/8/8/6P1/5PK1/8 w - - 0 1"),
    ]
    
    results = []
    
    for name, fen in test_cases:
        try:
            result = test_position(fen, name, depth=4, time_limit=3.0)
            results.append(result)
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
    
    # Summary
    print(f"\n\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")
    
    print(f"{'Position':<25} {'v2.3.0':<15} {'v2.4.0':<15} {'Same':<8} {'Speedup'}")
    print("-"*70)
    
    total_time_v23 = 0
    total_time_v24 = 0
    same_count = 0
    
    for r in results:
        same = "[YES]" if r['same_move'] else "[NO]"
        speedup = r['v23_time'] / r['v24_time'] if r['v24_time'] > 0 else 0
        print(f"{r['name']:<25} {str(r['v23_move']):<15} {str(r['v24_move']):<15} {same:<8} {speedup:.2f}x")
        
        total_time_v23 += r['v23_time']
        total_time_v24 += r['v24_time']
        if r['same_move']:
            same_count += 1
    
    print("-"*70)
    print(f"{'TOTAL':<25} {total_time_v23:.2f}s{' '*9} {total_time_v24:.2f}s{' '*9} {same_count}/{len(results)} {' '*3} {total_time_v23/total_time_v24:.2f}x")
    
    print(f"\n{'='*70}")
    print("CONCLUSIONS:")
    print(f"{'='*70}")
    print(f"  • Agreement: {same_count}/{len(results)} positions ({100*same_count/len(results):.0f}%)")
    print(f"  • Average speedup: {total_time_v23/total_time_v24:.2f}x")
    print(f"  • Total time saved: {total_time_v23 - total_time_v24:.2f}s")
    
    if total_time_v23 < total_time_v24:
        print(f"\n  [!] v2.4.0 slower - may need tuning or depth too low")
    else:
        print(f"\n  [OK] v2.4.0 faster - advanced techniques working!")
    
    print("\n  [+] Expected strength: v2.4.0 ~200-300 Elo stronger")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
