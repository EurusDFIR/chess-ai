#!/usr/bin/env python3
"""Detailed evaluation breakdown"""

import chess

# Test starting position
board = chess.Board()

print("=" * 70)
print("PYTHON EVALUATION BREAKDOWN")
print("=" * 70)
print(board)

from src.ai.evaluation_optimized import (
    evaluate_piece_square_tables,
    evaluate_mobility,
    evaluate_king_safety,
    evaluate_pawn_structure,
    evaluate_rooks,
    evaluate_bishops,
    evaluate_opening_principles,
    game_phase
)

phase = game_phase(board)
print(f"\nGame phase: {phase}")

pst_score = evaluate_piece_square_tables(board, phase)
print(f"PST score: {pst_score}cp")

mob_score = evaluate_mobility(board)
print(f"Mobility: {mob_score}cp")

king_score = evaluate_king_safety(board)
print(f"King safety: {king_score}cp")

pawn_score = evaluate_pawn_structure(board)
print(f"Pawn structure: {pawn_score}cp")

rook_score = evaluate_rooks(board)
print(f"Rooks: {rook_score}cp")

bishop_score = evaluate_bishops(board)
print(f"Bishops: {bishop_score}cp")

opening_score = evaluate_opening_principles(board)
print(f"Opening principles: {opening_score}cp")

total = pst_score + mob_score + king_score + pawn_score + rook_score + bishop_score + opening_score
print(f"\nTOTAL (white's perspective): {total}cp")
print(f"From side to move: {total if board.turn else -total}cp")

print("\n" + "=" * 70)
