# cython: language_level=3
# src/ai/order_moves_cython.pyx

import chess
from collections import defaultdict
from src.ai.evaluation import piece_values  # Import piece_values từ evaluation.py

# Khai báo kiểu dữ liệu C để tăng tốc
cdef extern from "chess.h":
    ctypedef struct Piece:
        pass

    ctypedef struct Board:
        pass

    enum PieceType:
        PAWN
        KNIGHT
        BISHOP
        ROOK
        QUEEN
        KING

    enum Color:
        WHITE
        BLACK

    PieceType piece_type(Piece piece)
    Color piece_color(Piece piece)

piece_values_cython = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

def order_moves_cython(board, killer_moves_for_depth, history_heuristic_table):
    """Sắp xếp nước đi bằng Cython."""
    moves = list(board.legal_moves)
    ordered_moves = []

    # 1. Killer Moves
    if killer_moves_for_depth:
        for killer_move in killer_moves_for_depth:
            if killer_move in moves:
                ordered_moves.append(killer_move)
                moves.remove(killer_move)

    # 2. History Heuristic
    history_scored_moves = []
    for move in moves:
        history_score = history_heuristic_table[(move.from_square, move.to_square)]
        history_scored_moves.append((history_score, move))

    history_scored_moves.sort(reverse=True, key=lambda x: x[0])

    for score, move in history_scored_moves:
        ordered_moves.append(move)

    return ordered_moves