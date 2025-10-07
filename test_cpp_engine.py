#!/usr/bin/env python3
"""Test C++ chess engine performance"""
import sys
import time
sys.path.insert(0, 'src')

import chess_engine

def test_engine():
    print("=" * 60)
    print("C++ CHESS ENGINE PERFORMANCE TEST")
    print("=" * 60)
    
    # Create board
    board = chess_engine.Board()
    board.init_start_position()
    print(f"\n✅ Board initialized: {board.to_fen()}\n")
    
    # Create search engine
    engine = chess_engine.SearchEngine(tt_size_mb=64)  # 64 MB hash table
    print("✅ Search engine created with 64MB hash\n")
    
    # Test different depths
    for depth in [4, 5, 6]:
        print(f"{'='*60}")
        print(f"Searching at depth {depth}...")
        print(f"{'='*60}")
        
        start = time.time()
        best_move = engine.get_best_move(board, max_depth=depth, time_limit=10000)
        elapsed = time.time() - start
        nodes = engine.get_nodes_searched()
        
        print(f"✅ Best move: {best_move.to_uci()}")
        print(f"   Nodes: {nodes:,}")
        print(f"   Time: {elapsed:.2f}s")
        print(f"   Speed: {nodes/elapsed:,.0f} nodes/sec")
        print()

if __name__ == "__main__":
    test_engine()
