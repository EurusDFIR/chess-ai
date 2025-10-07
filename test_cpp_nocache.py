#!/usr/bin/env python3
"""Test C++ engine với TT disabled để debug"""
import sys
import time
sys.path.insert(0, 'src')

import chess_engine

def test_no_cache():
    print("=" * 60)
    print("C++ ENGINE TEST - FRESH SEARCH (Clear TT mỗi lần)")
    print("=" * 60)
    
    board = chess_engine.Board()
    board.init_start_position()
    print(f"\n✅ Board: {board.to_fen()}\n")
    
    engine = chess_engine.SearchEngine(tt_size_mb=1)  # Small TT
    
    # Test nhiều lần, mỗi lần clear TT
    for i in range(3):
        print(f"{'='*60}")
        print(f"Test run #{i+1} - Depth 5 (TT cleared)")
        print(f"{'='*60}")
        
        engine.clear_tt()  # Clear transposition table
        
        start = time.time()
        best_move = engine.get_best_move(board, max_depth=5, time_limit=5000)
        elapsed = time.time() - start
        nodes = engine.get_nodes_searched()
        
        print(f"✅ Best move: {best_move.to_uci()}")
        print(f"   Nodes: {nodes:,}")
        print(f"   Time: {elapsed:.2f}s")
        print(f"   Speed: {nodes/elapsed:,.0f} nodes/sec")
        print()

if __name__ == "__main__":
    test_no_cache()
