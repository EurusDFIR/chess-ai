#!/usr/bin/env python3
"""Debug score oscillation"""

import sys
sys.path.insert(0, 'src')
import chess_engine

# Starting position
board = chess_engine.Board()
board.init_start_position()

print("Testing score oscillation...")
print("=" * 60)

# Test at different depths
for depth in range(1, 6):
    engine = chess_engine.SearchEngine(256)
    move = engine.get_best_move(board, depth, 10000)
    stats = engine.get_stats()
    
    print(f"Depth {depth}: Move={move}, Nodes={stats.nodes_searched}")

print("=" * 60)
