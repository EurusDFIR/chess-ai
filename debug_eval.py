#!/usr/bin/env python3
"""Debug evaluation differences between Python and C++"""

import chess
import chess_engine
from src.ai.evaluation_optimized import evaluate_incremental

# Test position: Starting position
board = chess.Board()

print("=" * 70)
print("DEBUG: EVALUATION COMPARISON")
print("=" * 70)
print(f"\nPosition: {board.fen()}")
print(board)
print(f"Side to move: {'WHITE' if board.turn else 'BLACK'}")

# Python evaluation
print("\n[Python Evaluation]")
py_eval = evaluate_incremental(board)
print(f"  Score: {py_eval} centipawns (from white's perspective)")

# C++ evaluation
print("\n[C++ Evaluation]")
cpp_board = chess_engine.Board()
cpp_board.from_fen(board.fen())
cpp_eval = chess_engine.Evaluator.evaluate(cpp_board)
print(f"  Score: {cpp_eval} centipawns (from side to move perspective)")


# Test after a move
print("\n" + "=" * 70)
print("After White plays e2e4:")
print("=" * 70)

board.push(chess.Move.from_uci("e2e4"))
print(board)

py_eval2 = evaluate_incremental(board)
print(f"\n[Python] Score: {py_eval2}cp (from white's perspective)")

cpp_board2 = chess_engine.Board()
cpp_board2.from_fen(board.fen())
cpp_eval2 = chess_engine.Evaluator.evaluate(cpp_board2)
print(f"[C++] Score: {cpp_eval2}cp (from side to move perspective)")


print("\n" + "=" * 70)
