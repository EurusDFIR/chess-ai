#!/usr/bin/env python3
"""So sanh performance Python engine vs C++ engine"""
import sys
import time
sys.path.insert(0, 'src')

import chess
import chess_engine
from ai.minimax_optimized import ChessAI

def test_position(fen, depth=4):
    """Test mot vi tri voi ca 2 engines"""
    print(f"\n{'='*70}")
    print(f"Testing position: {fen}")
    print(f"Depth: {depth}")
    print(f"{'='*70}\n")
    
    # Test Python engine
    print("🐍 PYTHON ENGINE:")
    board_py = chess.Board(fen)
    ai_py = ChessAI(depth=depth)
    
    start = time.time()
    move_py, score_py = ai_py.get_best_move(board_py)
    time_py = time.time() - start
    nodes_py = ai_py.nodes_searched
    
    print(f"   Best move: {move_py}")
    print(f"   Score: {score_py}")
    print(f"   Nodes: {nodes_py:,}")
    print(f"   Time: {time_py:.3f}s")
    print(f"   Speed: {nodes_py/time_py:,.0f} nodes/sec\n")
    
    # Test C++ engine
    print("⚡ C++ ENGINE:")
    board_cpp = chess_engine.Board()
    board_cpp.from_fen(fen)
    engine_cpp = chess_engine.SearchEngine(tt_size_mb=64)
    
    start = time.time()
    move_cpp = engine_cpp.get_best_move(board_cpp, max_depth=depth, time_limit=30000)
    time_cpp = time.time() - start
    nodes_cpp = engine_cpp.get_nodes_searched()
    
    print(f"   Best move: {move_cpp.to_uci()}")
    print(f"   Nodes: {nodes_cpp:,}")
    print(f"   Time: {time_cpp:.3f}s")
    print(f"   Speed: {nodes_cpp/time_cpp:,.0f} nodes/sec\n")
    
    # Comparison
    print("📊 COMPARISON:")
    speedup = (nodes_py/time_py) / (nodes_cpp/time_cpp) if time_cpp > 0 else 0
    print(f"   C++ is {1/speedup:.1f}x faster than Python")
    print(f"   Time reduction: {(1 - time_cpp/time_py)*100:.1f}%")
    
    return {
        'python': {'move': str(move_py), 'nodes': nodes_py, 'time': time_py, 'nps': nodes_py/time_py},
        'cpp': {'move': move_cpp.to_uci(), 'nodes': nodes_cpp, 'time': time_cpp, 'nps': nodes_cpp/time_cpp}
    }

def main():
    print("\n" + "="*70)
    print("PYTHON vs C++ CHESS ENGINE COMPARISON")
    print("="*70)
    
    # Test positions
    positions = [
        ("Starting position", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 4),
        ("Mid-game", "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 5", 4),
        ("Tactical", "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4", 5),
    ]
    
    results = []
    for name, fen, depth in positions:
        print(f"\n\n{'#'*70}")
        print(f"# {name}")
        print(f"{'#'*70}")
        result = test_position(fen, depth)
        results.append((name, result))
    
    # Final summary
    print("\n\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    
    total_speedup = []
    for name, result in results:
        py_nps = result['python']['nps']
        cpp_nps = result['cpp']['nps']
        speedup = cpp_nps / py_nps
        total_speedup.append(speedup)
        print(f"\n{name}:")
        print(f"  Python: {py_nps:,.0f} nodes/sec in {result['python']['time']:.2f}s")
        print(f"  C++:    {cpp_nps:,.0f} nodes/sec in {result['cpp']['time']:.2f}s")
        print(f"  Speedup: {speedup:.1f}x")
    
    avg_speedup = sum(total_speedup) / len(total_speedup)
    print(f"\n{'='*70}")
    print(f"AVERAGE SPEEDUP: {avg_speedup:.1f}x faster with C++")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
