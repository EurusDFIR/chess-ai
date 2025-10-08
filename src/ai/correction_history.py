# src/ai/correction_history.py
"""
Correction History - Inspired by Stockfish
Tracks evaluation errors and corrects static eval dynamically.

Concept:
- During search, compare static eval vs actual search result
- Record the error (bonus/penalty) in history tables
- Use history to correct future evals in similar positions

Impact: +100-150 Elo (Stockfish's biggest non-NNUE gain)
"""

from collections import defaultdict
import chess

class CorrectionHistory:
    """
    Tracks evaluation corrections for different position features.
    Based on Stockfish's correction history system.
    """
    
    def __init__(self):
        # Pawn structure corrections (by pawn hash)
        self.pawn_corrections = defaultdict(lambda: [0, 0])  # [WHITE, BLACK]
        
        # Minor piece corrections (by piece count signature)
        self.minor_piece_corrections = defaultdict(lambda: [0, 0])
        
        # Non-pawn material corrections
        self.non_pawn_corrections = defaultdict(lambda: [0, 0])
        
        # Continuation corrections (move sequence)
        self.continuation_corrections = defaultdict(lambda: defaultdict(int))
        
        # Gravity parameter (decay factor)
        self.gravity = 128  # Out of 128 (no decay yet, can tune)
        
        # Max correction value
        self.max_correction = 2048
    
    def pawn_structure_key(self, board):
        """
        Generate key for pawn structure (simplified zobrist).
        In production, use actual pawn hash from board.
        """
        pawn_bb = board.pawns
        # Simple key: pawn bitboard hash
        return hash(int(pawn_bb)) % 10000  # Modulo for memory efficiency
    
    def minor_piece_key(self, board):
        """
        Key based on minor piece configuration.
        Format: (num_knights, num_bishops) tuple
        """
        white_knights = len(board.pieces(chess.KNIGHT, chess.WHITE))
        white_bishops = len(board.pieces(chess.BISHOP, chess.WHITE))
        black_knights = len(board.pieces(chess.KNIGHT, chess.BLACK))
        black_bishops = len(board.pieces(chess.BISHOP, chess.BLACK))
        return (white_knights, white_bishops, black_knights, black_bishops)
    
    def non_pawn_key(self, board, color):
        """
        Key based on non-pawn material for one side.
        """
        queens = len(board.pieces(chess.QUEEN, color))
        rooks = len(board.pieces(chess.ROOK, color))
        knights = len(board.pieces(chess.KNIGHT, color))
        bishops = len(board.pieces(chess.BISHOP, color))
        return (queens, rooks, knights, bishops)
    
    def get_correction(self, board, prev_move=None):
        """
        Get total correction value for current position.
        Combines all correction tables like Stockfish.
        
        Returns: correction in centipawns (positive = increase eval)
        """
        color = board.turn
        color_idx = 0 if color == chess.WHITE else 1
        
        # 1. Pawn correction
        pawn_key = self.pawn_structure_key(board)
        pawn_corr = self.pawn_corrections[pawn_key][color_idx]
        
        # 2. Minor piece correction
        minor_key = self.minor_piece_key(board)
        minor_corr = self.minor_piece_corrections[minor_key][color_idx]
        
        # 3. Non-pawn correction
        white_np_key = self.non_pawn_key(board, chess.WHITE)
        black_np_key = self.non_pawn_key(board, chess.BLACK)
        white_np_corr = self.non_pawn_corrections[white_np_key][color_idx]
        black_np_corr = self.non_pawn_corrections[black_np_key][color_idx]
        
        # 4. Continuation correction (if prev_move provided)
        cont_corr = 0
        if prev_move and prev_move.to_square is not None:
            piece = board.piece_at(prev_move.to_square)
            if piece:
                cont_key = (piece.piece_type, prev_move.to_square)
                cont_corr = self.continuation_corrections[cont_key].get(color, 0)
        
        # Combine with Stockfish-like weights (scaled down)
        # Stockfish uses: 9536*pawn + 8494*minor + 10132*nonpawn + 7156*cont
        # We use simpler: 100*pawn + 80*minor + 100*nonpawn + 70*cont
        total = (100 * pawn_corr + 
                 80 * minor_corr + 
                 100 * (white_np_corr + black_np_corr) + 
                 70 * cont_corr)
        
        # Scale down (Stockfish divides by 131072, we use 128 for simplicity)
        correction = total // 128
        
        # Clamp to max correction
        return max(-self.max_correction, min(self.max_correction, correction))
    
    def update(self, board, eval_error, prev_move=None, depth=1):
        """
        Update correction history based on evaluation error.
        
        Args:
            board: Current position
            eval_error: search_score - static_eval (in centipawns)
            prev_move: Previous move (for continuation history)
            depth: Search depth (higher depth = more weight)
        """
        color = board.turn
        color_idx = 0 if color == chess.WHITE else 1
        
        # Calculate bonus (positive if search found position better than static eval)
        # Scale by depth: deeper search = more reliable
        bonus = eval_error * min(depth, 8) // 4
        bonus = max(-256, min(256, bonus))  # Clamp bonus
        
        # 1. Update pawn correction
        pawn_key = self.pawn_structure_key(board)
        self._update_entry(self.pawn_corrections[pawn_key], color_idx, bonus)
        
        # 2. Update minor piece correction (scaled by 145/128 like Stockfish)
        minor_key = self.minor_piece_key(board)
        minor_bonus = bonus * 145 // 128
        self._update_entry(self.minor_piece_corrections[minor_key], color_idx, minor_bonus)
        
        # 3. Update non-pawn corrections
        white_np_key = self.non_pawn_key(board, chess.WHITE)
        black_np_key = self.non_pawn_key(board, chess.BLACK)
        np_bonus = bonus * 165 // 128  # Stockfish uses 165/128
        self._update_entry(self.non_pawn_corrections[white_np_key], color_idx, np_bonus)
        self._update_entry(self.non_pawn_corrections[black_np_key], color_idx, np_bonus)
        
        # 4. Update continuation correction
        if prev_move and prev_move.to_square is not None:
            piece = board.piece_at(prev_move.to_square)
            if piece:
                cont_key = (piece.piece_type, prev_move.to_square)
                cont_bonus = bonus * 137 // 128
                self._update_continuation(cont_key, color, cont_bonus)
    
    def _update_entry(self, entry, color_idx, bonus):
        """
        Update a correction entry with bonus.
        Uses Stockfish-style update: value += bonus - value * abs(bonus) / 512
        """
        old_value = entry[color_idx]
        # Gravity term: pull toward zero to avoid stale data
        gravity_term = old_value * abs(bonus) // 512
        new_value = old_value + bonus - gravity_term
        # Clamp
        entry[color_idx] = max(-self.max_correction, min(self.max_correction, new_value))
    
    def _update_continuation(self, cont_key, color, bonus):
        """Update continuation correction."""
        old_value = self.continuation_corrections[cont_key].get(color, 0)
        gravity_term = old_value * abs(bonus) // 512
        new_value = old_value + bonus - gravity_term
        self.continuation_corrections[cont_key][color] = max(-self.max_correction, 
                                                             min(self.max_correction, new_value))
    
    def apply_gravity(self, factor=7/8):
        """
        Apply gravity to all tables (decay toward zero).
        Call periodically (e.g., every 10k nodes) to keep data fresh.
        """
        # Decay pawn corrections
        for key in self.pawn_corrections:
            self.pawn_corrections[key][0] = int(self.pawn_corrections[key][0] * factor)
            self.pawn_corrections[key][1] = int(self.pawn_corrections[key][1] * factor)
        
        # Decay minor piece corrections
        for key in self.minor_piece_corrections:
            self.minor_piece_corrections[key][0] = int(self.minor_piece_corrections[key][0] * factor)
            self.minor_piece_corrections[key][1] = int(self.minor_piece_corrections[key][1] * factor)
        
        # Decay non-pawn corrections
        for key in self.non_pawn_corrections:
            self.non_pawn_corrections[key][0] = int(self.non_pawn_corrections[key][0] * factor)
            self.non_pawn_corrections[key][1] = int(self.non_pawn_corrections[key][1] * factor)
        
        # Decay continuation corrections
        for cont_key in self.continuation_corrections:
            for color in [chess.WHITE, chess.BLACK]:
                if color in self.continuation_corrections[cont_key]:
                    val = self.continuation_corrections[cont_key][color]
                    self.continuation_corrections[cont_key][color] = int(val * factor)
    
    def clear(self):
        """Clear all correction tables (start fresh)."""
        self.pawn_corrections.clear()
        self.minor_piece_corrections.clear()
        self.non_pawn_corrections.clear()
        self.continuation_corrections.clear()


# Example usage:
if __name__ == "__main__":
    import chess
    
    ch = CorrectionHistory()
    board = chess.Board()
    
    # Simulate: static eval was 50cp, but search found 120cp
    # This means position was underestimated by 70cp
    eval_error = 120 - 50  # 70cp
    ch.update(board, eval_error, depth=5)
    
    # Next time we see similar position, get correction
    correction = ch.get_correction(board)
    print(f"Correction: {correction}cp")  # Should be positive
    
    # Apply to static eval
    static_eval = 50
    corrected_eval = static_eval + correction
    print(f"Static: {static_eval}cp -> Corrected: {corrected_eval}cp")
