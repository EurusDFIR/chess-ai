# src/ai/evaluation_optimized.py
"""
Optimized evaluation function with:
- Piece-Square Tables (PST) for all game phases
- Material evaluation
- King safety
- Pawn structure
- Mobility
- Rook on open files
- Bishop pair
- Passed pawns
- Incremental evaluation (future improvement)
"""

import chess
import chess.syzygy
import os

# Piece values
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Piece-Square Tables (PST) - Middle game
# Values are from white's perspective, will be mirrored for black

PST_PAWN_MG = [
    0,   0,   0,   0,   0,   0,   0,   0,
    50,  50,  50,  50,  50,  50,  50,  50,
    10,  10,  20,  30,  30,  20,  10,  10,
    5,   5,   10,  25,  25,  10,  5,   5,
    0,   0,   0,   20,  20,  0,   0,   0,
    5,   -5,  -10, 0,   0,   -10, -5,  5,
    5,   10,  10,  -20, -20, 10,  10,  5,
    0,   0,   0,   0,   0,   0,   0,   0
]

PST_KNIGHT_MG = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0,   0,   0,   0,   -20, -40,
    -30, 0,   10,  15,  15,  10,  0,   -30,
    -30, 5,   15,  20,  20,  15,  5,   -30,
    -30, 0,   15,  20,  20,  15,  0,   -30,
    -30, 5,   10,  15,  15,  10,  5,   -30,
    -40, -20, 0,   5,   5,   0,   -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

PST_BISHOP_MG = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 0,   0,   0,   0,   0,   0,   -10,
    -10, 0,   5,   10,  10,  5,   0,   -10,
    -10, 5,   5,   10,  10,  5,   5,   -10,
    -10, 0,   10,  10,  10,  10,  0,   -10,
    -10, 10,  10,  10,  10,  10,  10,  -10,
    -10, 5,   0,   0,   0,   0,   5,   -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]

PST_ROOK_MG = [
    0,   0,   0,   0,   0,   0,   0,   0,
    5,   10,  10,  10,  10,  10,  10,  5,
    -5,  0,   0,   0,   0,   0,   0,   -5,
    -5,  0,   0,   0,   0,   0,   0,   -5,
    -5,  0,   0,   0,   0,   0,   0,   -5,
    -5,  0,   0,   0,   0,   0,   0,   -5,
    -5,  0,   0,   0,   0,   0,   0,   -5,
    0,   0,   0,   5,   5,   0,   0,   0
]

PST_QUEEN_MG = [
    # Hậu nên ở back rank trong opening, penalty nếu ra sớm
    -20, -10, -10, -5,  -5,  -10, -10, -20,  # Rank 1 (back): OK
    -10, -20, -20, -20, -20, -20, -20, -10,  # Rank 2: penalty -20
    -10, -20, -10, -10, -10, -10, -20, -10,  # Rank 3: penalty -20/-10
    -5,  -10, -5,  0,   0,   -5,  -10, -5,   # Rank 4: penalty -10/-5
    0,   -5,  0,   5,   5,   0,   -5,  0,    # Rank 5: chút bonus +5
    -10, -5,  0,   5,   5,   0,   -5,  -10,  # Rank 6: trung bình
    -10, -10, -5,  0,   0,   -5,  -10, -10,  # Rank 7: penalty
    -20, -10, -10, -5,  -5,  -10, -10, -20   # Rank 8: OK
]

PST_KING_MG = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20,  20,  0,   0,   0,   0,   20,  20,
    20,  30,  10,  0,   0,   10,  30,  20
]

# Endgame PST - King should be active
PST_KING_EG = [
    -50, -40, -30, -20, -20, -30, -40, -50,
    -30, -20, -10, 0,   0,   -10, -20, -30,
    -30, -10, 20,  30,  30,  20,  -10, -30,
    -30, -10, 30,  40,  40,  30,  -10, -30,
    -30, -10, 30,  40,  40,  30,  -10, -30,
    -30, -10, 20,  30,  30,  20,  -10, -30,
    -30, -30, 0,   0,   0,   0,   -30, -30,
    -50, -30, -30, -30, -30, -30, -30, -50
]

# Pawn structure bonuses
PST_PAWN_EG = [
    0,   0,   0,   0,   0,   0,   0,   0,
    80,  80,  80,  80,  80,  80,  80,  80,
    50,  50,  50,  50,  50,  50,  50,  50,
    30,  30,  30,  30,  30,  30,  30,  30,
    20,  20,  20,  20,  20,  20,  20,  20,
    10,  10,  10,  10,  10,  10,  10,  10,
    10,  10,  10,  10,  10,  10,  10,  10,
    0,   0,   0,   0,   0,   0,   0,   0
]

# Combine PST into dictionary
PST_MG = {
    chess.PAWN: PST_PAWN_MG,
    chess.KNIGHT: PST_KNIGHT_MG,
    chess.BISHOP: PST_BISHOP_MG,
    chess.ROOK: PST_ROOK_MG,
    chess.QUEEN: PST_QUEEN_MG,
    chess.KING: PST_KING_MG
}

PST_EG = {
    chess.PAWN: PST_PAWN_EG,
    chess.KNIGHT: PST_KNIGHT_MG,  # Same as MG
    chess.BISHOP: PST_BISHOP_MG,  # Same as MG
    chess.ROOK: PST_ROOK_MG,      # Same as MG
    chess.QUEEN: PST_QUEEN_MG,    # Same as MG
    chess.KING: PST_KING_EG
}

# Load Syzygy tablebases
try:
    syzygy_path = os.path.join(os.path.dirname(__file__), "..", "..", "syzygy")
    syzygy_path = os.path.abspath(syzygy_path)
    if os.path.exists(syzygy_path):
        tablebase = chess.syzygy.open_tablebase(syzygy_path)
    else:
        tablebase = None
except Exception:
    tablebase = None


class EvaluationCache:
    """Cache for evaluation to avoid recalculation."""
    def __init__(self):
        self.cache = {}
    
    def get(self, zobrist_hash):
        return self.cache.get(zobrist_hash)
    
    def store(self, zobrist_hash, score):
        if len(self.cache) > 10000:  # Limit cache size
            self.cache.clear()
        self.cache[zobrist_hash] = score


eval_cache = EvaluationCache()


def game_phase(board):
    """Calculate game phase (0=endgame, 256=opening)."""
    phase = 0
    phase += len(board.pieces(chess.KNIGHT, chess.WHITE)) * 1
    phase += len(board.pieces(chess.KNIGHT, chess.BLACK)) * 1
    phase += len(board.pieces(chess.BISHOP, chess.WHITE)) * 1
    phase += len(board.pieces(chess.BISHOP, chess.BLACK)) * 1
    phase += len(board.pieces(chess.ROOK, chess.WHITE)) * 2
    phase += len(board.pieces(chess.ROOK, chess.BLACK)) * 2
    phase += len(board.pieces(chess.QUEEN, chess.WHITE)) * 4
    phase += len(board.pieces(chess.QUEEN, chess.BLACK)) * 4
    return min(phase, 24) * 256 // 24  # Scale to 0-256


def evaluate_piece_square_tables(board, phase):
    """Evaluate using piece-square tables with game phase interpolation."""
    score_mg = 0
    score_eg = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            # Get PST index
            sq_index = square if piece.color == chess.WHITE else chess.square_mirror(square)
            
            # Middle game and endgame values
            mg_value = PST_MG[piece.piece_type][sq_index]
            eg_value = PST_EG[piece.piece_type][sq_index]
            
            if piece.color == chess.WHITE:
                score_mg += PIECE_VALUES[piece.piece_type] + mg_value
                score_eg += PIECE_VALUES[piece.piece_type] + eg_value
            else:
                score_mg -= PIECE_VALUES[piece.piece_type] + mg_value
                score_eg -= PIECE_VALUES[piece.piece_type] + eg_value
    
    # Interpolate between middle game and endgame
    score = (score_mg * phase + score_eg * (256 - phase)) // 256
    return score


def evaluate_mobility(board):
    """Evaluate piece mobility."""
    original_turn = board.turn
    
    # White mobility
    board.turn = chess.WHITE
    white_mobility = len(list(board.legal_moves))
    
    # Black mobility
    board.turn = chess.BLACK
    black_mobility = len(list(board.legal_moves))
    
    # Restore turn
    board.turn = original_turn
    
    return (white_mobility - black_mobility) * 1  # Weight: 1 per move


def evaluate_king_safety(board):
    """Evaluate king safety with pawn shield."""
    score = 0
    
    for color in [chess.WHITE, chess.BLACK]:
        king_square = board.king(color)
        if not king_square:
            continue
        
        safety = 0
        
        # Pawn shield
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)
        
        for file_offset in [-1, 0, 1]:
            file = king_file + file_offset
            if 0 <= file < 8:
                for rank_offset in [1, 2] if color == chess.WHITE else [-1, -2]:
                    rank = king_rank + rank_offset
                    if 0 <= rank < 8:
                        sq = chess.square(file, rank)
                        piece = board.piece_at(sq)
                        if piece and piece.piece_type == chess.PAWN and piece.color == color:
                            safety += 10
        
        # Penalty for exposed king
        attackers = len(board.attackers(not color, king_square))
        safety -= attackers * 20
        
        if color == chess.WHITE:
            score += safety
        else:
            score -= safety
    
    return score


def evaluate_pawn_structure(board):
    """Evaluate pawn structure (isolated, doubled, passed pawns)."""
    score = 0
    
    for color in [chess.WHITE, chess.BLACK]:
        pawns = board.pieces(chess.PAWN, color)
        
        for pawn_square in pawns:
            file = chess.square_file(pawn_square)
            rank = chess.square_rank(pawn_square)
            
            # Check for isolated pawns
            is_isolated = True
            for adj_file in [file - 1, file + 1]:
                if 0 <= adj_file < 8:
                    adj_pawns = [p for p in pawns if chess.square_file(p) == adj_file]
                    if adj_pawns:
                        is_isolated = False
                        break
            
            if is_isolated:
                penalty = -15
                score += penalty if color == chess.WHITE else -penalty
            
            # Check for doubled pawns
            same_file_pawns = [p for p in pawns if chess.square_file(p) == file]
            if len(same_file_pawns) > 1:
                penalty = -10
                score += penalty if color == chess.WHITE else -penalty
            
            # Check for passed pawns
            is_passed = True
            opponent_pawns = board.pieces(chess.PAWN, not color)
            
            for opp_pawn in opponent_pawns:
                opp_file = chess.square_file(opp_pawn)
                opp_rank = chess.square_rank(opp_pawn)
                
                # Check if opponent pawn can block this pawn
                if abs(opp_file - file) <= 1:
                    if color == chess.WHITE and opp_rank > rank:
                        is_passed = False
                        break
                    elif color == chess.BLACK and opp_rank < rank:
                        is_passed = False
                        break
            
            if is_passed:
                # Passed pawn bonus increases with proximity to promotion
                bonus = 20 + (rank if color == chess.WHITE else (7 - rank)) * 10
                score += bonus if color == chess.WHITE else -bonus
    
    return score


def evaluate_rooks(board):
    """Evaluate rook placement (open files, 7th rank)."""
    score = 0
    
    for color in [chess.WHITE, chess.BLACK]:
        rooks = board.pieces(chess.ROOK, color)
        
        for rook_square in rooks:
            file = chess.square_file(rook_square)
            rank = chess.square_rank(rook_square)
            
            # Rook on open file
            pawns_on_file = [p for p in board.pieces(chess.PAWN, chess.WHITE) 
                           if chess.square_file(p) == file]
            pawns_on_file += [p for p in board.pieces(chess.PAWN, chess.BLACK) 
                            if chess.square_file(p) == file]
            
            if not pawns_on_file:
                # Open file
                bonus = 20
                score += bonus if color == chess.WHITE else -bonus
            elif not any(board.piece_at(p).color == color for p in pawns_on_file):
                # Semi-open file
                bonus = 10
                score += bonus if color == chess.WHITE else -bonus
            
            # Rook on 7th rank
            if (color == chess.WHITE and rank == 6) or (color == chess.BLACK and rank == 1):
                bonus = 20
                score += bonus if color == chess.WHITE else -bonus
    
    return score


def evaluate_bishops(board):
    """Evaluate bishop pair."""
    score = 0
    
    white_bishops = len(board.pieces(chess.BISHOP, chess.WHITE))
    black_bishops = len(board.pieces(chess.BISHOP, chess.BLACK))
    
    if white_bishops >= 2:
        score += 30  # Bishop pair bonus
    if black_bishops >= 2:
        score -= 30
    
    return score


def evaluate_center_control(board):
    """Evaluate center control (e4, d4, e5, d5)."""
    score = 0
    center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
    
    for square in center_squares:
        # Pawns in center
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.PAWN:
            score += 20 if piece.color == chess.WHITE else -20
        
        # Control of center squares
        white_control = len(board.attackers(chess.WHITE, square))
        black_control = len(board.attackers(chess.BLACK, square))
        score += (white_control - black_control) * 5
    
    return score


def evaluate_development(board):
    """Evaluate piece development in opening."""
    score = 0
    
    # White development
    # Knights
    white_knights = board.pieces(chess.KNIGHT, chess.WHITE)
    for square in white_knights:
        if square not in [chess.B1, chess.G1]:  # Moved from starting position
            score += 15
    
    # Bishops
    white_bishops = board.pieces(chess.BISHOP, chess.WHITE)
    for square in white_bishops:
        if square not in [chess.C1, chess.F1]:  # Moved from starting position
            score += 15
    
    # Queen penalty if moved early
    white_queens = board.pieces(chess.QUEEN, chess.WHITE)
    for square in white_queens:
        if square != chess.D1:  # Moved from starting position
            score -= 20  # Penalty for early queen development
    
    # Black development
    # Knights
    black_knights = board.pieces(chess.KNIGHT, chess.BLACK)
    for square in black_knights:
        if square not in [chess.B8, chess.G8]:  # Moved from starting position
            score -= 15
    
    # Bishops
    black_bishops = board.pieces(chess.BISHOP, chess.BLACK)
    for square in black_bishops:
        if square not in [chess.C8, chess.F8]:  # Moved from starting position
            score -= 15
    
    # Queen penalty if moved early
    black_queens = board.pieces(chess.QUEEN, chess.BLACK)
    for square in black_queens:
        if square != chess.D8:  # Moved from starting position
            score += 20  # Penalty for early queen development (negative for black)
    
    return score


def evaluate_castling_rights(board):
    """Evaluate castling and castling rights."""
    score = 0
    
    # Bonus for having castled
    if board.has_kingside_castling_rights(chess.WHITE) or board.has_queenside_castling_rights(chess.WHITE):
        score += 20  # Bonus for maintaining castling rights
    
    if board.has_kingside_castling_rights(chess.BLACK) or board.has_queenside_castling_rights(chess.BLACK):
        score -= 20
    
    # Bigger bonus for having actually castled (king on g1/g8 or c1/c8)
    white_king_sq = board.king(chess.WHITE)
    if white_king_sq in [chess.G1, chess.C1]:
        score += 30
    
    black_king_sq = board.king(chess.BLACK)
    if black_king_sq in [chess.G8, chess.C8]:
        score -= 30
    
    return score


def evaluate_opening_principles(board):
    """Evaluate opening principles (only in opening phase)."""
    move_count = board.fullmove_number
    
    # Only apply in opening (first 15 moves)
    if move_count > 15:
        return 0
    
    score = 0
    
    # Center control
    score += evaluate_center_control(board) * 2
    
    # Development
    score += evaluate_development(board) * 2
    
    # Castling
    score += evaluate_castling_rights(board)
    
    return score


def evaluate_incremental(board):
    """Main evaluation function with all components."""
    
    # Probe tablebase for positions with few pieces
    if tablebase and len(board.piece_map()) <= 6:
        try:
            wdl = tablebase.probe_wdl(board)
            if wdl is not None:
                return wdl * 10000  # Convert to centipawns
        except:
            pass
    
    # Calculate game phase
    phase = game_phase(board)
    
    # Material and position (PST)
    score = evaluate_piece_square_tables(board, phase)
    
    # Positional factors
    score += evaluate_mobility(board)
    score += evaluate_king_safety(board)
    score += evaluate_pawn_structure(board)
    score += evaluate_rooks(board)
    score += evaluate_bishops(board)
    
    # Opening principles (first 15 moves)
    score += evaluate_opening_principles(board)
    
    # Return score from perspective of side to move
    return score if board.turn == chess.WHITE else -score


# Backward compatibility
def evaluate(board):
    """Wrapper for backward compatibility."""
    return evaluate_incremental(board)


# Export piece values for minimax
piece_values = PIECE_VALUES
