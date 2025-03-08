# src/ai/evaluation.py

import chess
import chess.syzygy

# Định nghĩa giá trị quân cờ có thể dùng ở mức module
piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

position_values = {
    chess.PAWN: [
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 10, -20, -20, 10, 10, 5,
        5, -5, -10, 0, 0, -10, -5, 5,
        0, 0, 0, 20, 20, 0, 0, 0,
        5, 5, 10, 25, 25, 10, 5, 5,
        10, 10, 20, 30, 30, 20, 10, 10,
        50, 50, 50, 50, 50, 50, 50, 50,
        0, 0, 0, 0, 0, 0, 0, 0
    ],
    chess.KNIGHT: [
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 0, 15, 20, 20, 15, 0, -30,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50
    ],
    chess.BISHOP: [
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 5, 5, 10, 10, 5, 5, -10,
        -10, 0, 10, 10, 10, 10, 0, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10, 5, 0, 0, 0, 0, 5, -10,
        -20, -10, -10, -10, -10, -10, -10, -20
    ],
    chess.ROOK: [
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 10, 10, 10, 10, 10, 5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        0, 0, 0, 5, 5, 0, 0, 0
    ],
    chess.QUEEN: [
        -20, -10, -10, -5, -5, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 5, 5, 5, 0, -10,
        -5, 0, 5, 5, 5, 5, 0, -5,
        0, 0, 5, 5, 5, 5, 0, -5,
        -10, 5, 5, 5, 5, 5, 0, -10,
        -10, 0, 5, 0, 0, 0, 0, -10,
        -20, -10, -10, -5, -5, -10, -10, -20
    ],
    chess.KING: [
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        20, 20, 0, 0, 0, 0, 20, 20,
        20, 30, 10, 0, 0, 10, 30, 20
    ]
}

# Load Syzygy tablebases
syzygy_path =r'R:\TDMU\KIEN_THUC_TDMU\3_year_HK2\TriTueNT\chess-ai\syzygy'  # Update this path to your actual Syzygy tablebase files
tablebase = chess.syzygy.open_tablebase(syzygy_path)

def evaluate(board):
    """Optimized evaluation function for the board state."""
    if tablebase:
        num_pieces = len(board.piece_map())
        if num_pieces <= 6 and not board.has_castling_rights(chess.WHITE) and not board.has_castling_rights(chess.BLACK):
            try:
                wdl = tablebase.probe_wdl(board)
                if wdl is not None:
                    return wdl * 10000
            except Exception as e:
                print(f"Error probing tablebase: {e}")

    score = 0
    piece_map = board.piece_map()
    for square, piece in piece_map.items():
        value = piece_values[piece.piece_type]
        pos_value = position_values[piece.piece_type][square] if piece.color == chess.WHITE else position_values[piece.piece_type][chess.square_mirror(square)]
        score += value + pos_value if piece.color == chess.WHITE else -(value + pos_value)

    white_mobility = sum(1 for move in board.legal_moves if board.turn == chess.WHITE)
    black_mobility = sum(1 for move in board.legal_moves if board.turn == chess.BLACK)
    mobility_score = (white_mobility - black_mobility) * 0.1
    score += mobility_score

    center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
    white_center_control = sum(1 for sq in center_squares if board.is_attacked_by(chess.WHITE, sq))
    black_center_control = sum(1 for sq in center_squares if board.is_attacked_by(chess.BLACK, sq))
    center_control_score = (white_center_control - black_center_control) * 0.1
    score += center_control_score

    development_positions = [chess.B1, chess.G1, chess.C1, chess.F1, chess.B8, chess.G8, chess.C8, chess.F8]
    development_score = sum(1 for pos in development_positions[:4] if board.piece_at(pos) is None)
    development_score -= sum(1 for pos in development_positions[4:] if board.piece_at(pos) is None)
    score += development_score * 0.1

    isolated_pawn_penalty = -50
    for color in [chess.WHITE, chess.BLACK]:
        for square in board.pieces(chess.PAWN, color):
            file = chess.square_file(square)
            is_isolated = all(board.piece_at(chess.square(f, chess.square_rank(square))) is None for f in [file - 1, file + 1] if 0 <= f < 8)
            if is_isolated:
                score += isolated_pawn_penalty if color == chess.WHITE else -isolated_pawn_penalty

    king_safety_weight = -50
    white_king_attackers = len(board.attackers(chess.BLACK, board.king(chess.WHITE))) if board.king(chess.WHITE) else 0
    black_king_attackers = len(board.attackers(chess.WHITE, board.king(chess.BLACK))) if board.king(chess.BLACK) else 0
    king_safety_score = (white_king_attackers - black_king_attackers) * king_safety_weight
    score += king_safety_score

    hanging_piece_penalty_weight = -50
    for color in [chess.WHITE, chess.BLACK]:
        opponent_color = not color
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            for square in board.pieces(piece_type, color):
                if not board.attackers(color, square) and board.attackers(opponent_color, square):
                    penalty = hanging_piece_penalty_weight * piece_values[piece_type]
                    score += penalty if color == chess.WHITE else -penalty

    attack_potential_weight = 5
    king_square_opponent = board.king(chess.BLACK if board.turn == chess.WHITE else chess.WHITE)
    attack_potential_score = sum(0.1 * piece_values[piece.piece_type] for square in chess.SQUARES for piece in [board.piece_at(square)] if piece and piece.color == board.turn and square in board.attackers(board.turn, king_square_opponent))
    score += attack_potential_score * attack_potential_weight

    return score