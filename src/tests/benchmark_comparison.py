#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Benchmark script to compare old vs new AI
"""

import sys
import os
import time
import chess

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.ai.minimax import get_best_move as get_best_move_old
from src.ai.minimax_optimized import get_best_move as get_best_move_new


def benchmark_position(fen, depth, description=""):
    """Benchmark a single position."""
    board = chess.Board(fen)
    
    print(f"\n{'='*80}")
    print(f"Position: {description}")
    print(f"FEN: {fen}")
    print(f"{'='*80}\n")
    
    # Old AI
    print("🔴 OLD AI:")
    start = time.time()
    move_old = get_best_move_old(board.copy(), depth)
    time_old = time.time() - start
    print(f"Move: {move_old}")
    print(f"Time: {time_old:.3f}s\n")
    
    # New AI
    print("🟢 NEW AI:")
    start = time.time()
    move_new = get_best_move_new(board.copy(), depth, time_limit=30.0)
    time_new = time.time() - start
    print(f"Move: {move_new}")
    print(f"Time: {time_new:.3f}s\n")
    
    # Comparison
    speedup = time_old / time_new if time_new > 0 else 0
    print(f"📊 SPEEDUP: {speedup:.2f}x")
    print(f"⚡ TIME SAVED: {time_old - time_new:.3f}s")
    
    return {
        'description': description,
        'move_old': move_old,
        'move_new': move_new,
        'time_old': time_old,
        'time_new': time_new,
        'speedup': speedup
    }


def run_benchmark_suite():
    """Run comprehensive benchmark."""
    
    # Test positions
    positions = [
        {
            'fen': chess.STARTING_FEN,
            'description': 'Starting position',
            'depth': 4
        },
        {
            'fen': 'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3',
            'description': 'After 1.e4 e5 2.Nf3 Nc6',
            'depth': 4
        },
        {
            'fen': 'rnbqkb1r/pp2pppp/5n2/2pp4/3P4/2N2N2/PPP1PPPP/R1BQKB1R w KQkq - 0 4',
            'description': 'Queens Gambit Declined',
            'depth': 4
        },
        {
            'fen': 'r1bq1rk1/ppp2ppp/2n2n2/2bpp3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 7',
            'description': 'Italian Game',
            'depth': 4
        },
        {
            'fen': 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1',
            'description': 'Tactical position (Perft test)',
            'depth': 3
        },
        {
            'fen': '8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1',
            'description': 'Endgame position',
            'depth': 5
        }
    ]
    
    print("\n" + "="*80)
    print(" "*20 + "CHESS AI BENCHMARK SUITE")
    print("="*80)
    
    results = []
    
    for pos in positions:
        try:
            result = benchmark_position(pos['fen'], pos['depth'], pos['description'])
            results.append(result)
        except Exception as e:
            print(f"❌ Error in position: {e}")
            continue
    
    # Summary
    print("\n" + "="*80)
    print(" "*30 + "SUMMARY")
    print("="*80 + "\n")
    
    avg_speedup = sum(r['speedup'] for r in results) / len(results) if results else 0
    total_time_old = sum(r['time_old'] for r in results)
    total_time_new = sum(r['time_new'] for r in results)
    time_saved = total_time_old - total_time_new
    
    print(f"Total positions tested: {len(results)}")
    print(f"Average speedup: {avg_speedup:.2f}x")
    print(f"Total time (OLD): {total_time_old:.3f}s")
    print(f"Total time (NEW): {total_time_new:.3f}s")
    print(f"Time saved: {time_saved:.3f}s ({100*time_saved/total_time_old:.1f}%)")
    
    print("\n" + "="*80)
    print("Individual results:")
    print("="*80 + "\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['description']}")
        print(f"   OLD: {result['move_old']} ({result['time_old']:.3f}s)")
        print(f"   NEW: {result['move_new']} ({result['time_new']:.3f}s)")
        print(f"   Speedup: {result['speedup']:.2f}x\n")
    
    return results


if __name__ == "__main__":
    print("Starting benchmark comparison...")
    print("This will compare OLD AI vs NEW AI on various positions.\n")
    
    try:
        results = run_benchmark_suite()
        print("\n✅ Benchmark completed successfully!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Benchmark failed with error: {e}")
        import traceback
        traceback.print_exc()
