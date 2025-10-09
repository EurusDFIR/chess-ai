# src/ai/stockfish_techniques.py
"""
Stockfish-inspired techniques for EURY v2.6+
Implements missing advanced techniques:
- Late Move Pruning (LMP) 
- Enhanced Razoring
- History Gravity
- Enhanced Aspiration Windows
- Continuation History
- Enhanced Multicut
"""

import chess
import math
from collections import defaultdict

# ============================================================================
# 1. LATE MOVE PRUNING (LMP) - Stockfish Style (+40-60 Elo)
# ============================================================================

def get_lmp_threshold(depth, improving):
    """
    Get Late Move Pruning threshold based on depth and improving flag.
    
    Stockfish formula: (3 + depth * depth) / (2 - improving)
    
    Args:
        depth: Current search depth
        improving: True if static eval is improving
    
    Returns:
        Number of moves to search before pruning
    """
    if depth <= 0:
        return 999  # No pruning at leaf
    
    # Stockfish-style formula
    base_count = 3 + depth * depth
    divisor = 2 - (1 if improving else 0)
    
    return base_count // divisor


def should_prune_late_move(move_count, depth, improving, in_check, is_capture, is_promotion):
    """
    Decide if we should prune this late move.
    
    Args:
        move_count: Number of moves already searched (0-indexed)
        depth: Current depth
        improving: Static eval is improving
        in_check: In check
        is_capture: Move is a capture
        is_promotion: Move is a promotion
    
    Returns:
        True if should prune (skip) this move
    """
    # Never prune in check, captures, or promotions
    if in_check or is_capture or is_promotion:
        return False
    
    # Only prune at low depths
    if depth > 8:
        return False
    
    # Get LMP threshold
    threshold = get_lmp_threshold(depth, improving)
    
    # Prune if we've searched enough moves
    return move_count >= threshold


# ============================================================================
# 2. ENHANCED RAZORING - Stockfish Style (+30-50 Elo)
# ============================================================================

def get_razor_margin(depth):
    """
    Get razoring margin based on depth (Stockfish values).
    
    Args:
        depth: Current search depth
    
    Returns:
        Margin in centipawns
    """
    # Stockfish-inspired margins
    if depth == 1:
        return 250
    elif depth == 2:
        return 350
    elif depth == 3:
        return 450
    elif depth <= 7:
        return 450 + (depth - 3) * 50
    else:
        return 999999  # No razoring at high depth


def should_razor(depth, eval_score, alpha, in_check, alpha_near_mate):
    """
    Decide if we should apply razoring.
    
    Args:
        depth: Current depth
        eval_score: Static evaluation
        alpha: Alpha bound
        in_check: In check
        alpha_near_mate: Alpha is near mate score
    
    Returns:
        True if should drop to qsearch immediately
    """
    # Never razor in check or near mate
    if in_check or alpha_near_mate:
        return False
    
    # Only razor at low depths
    if depth > 7 or depth <= 0:
        return False
    
    # Check if eval + margin < alpha
    margin = get_razor_margin(depth)
    return eval_score + margin < alpha


# ============================================================================
# 3. HISTORY GRAVITY - Stockfish Style (+20-40 Elo)
# ============================================================================

class HistoryWithGravity:
    """
    History tables with gravity (decay) to prevent stale data.
    """
    
    def __init__(self):
        self.history = defaultdict(int)
        self.nodes_since_gravity = 0
        self.gravity_interval = 4096  # Apply gravity every 4096 nodes
        
    def get(self, key):
        """Get history score for a key."""
        return self.history.get(key, 0)
    
    def update(self, key, bonus):
        """
        Update history with bonus and apply gravity.
        
        Args:
            key: History key (e.g., (from_square, to_square))
            bonus: Bonus to add (can be negative)
        """
        old_value = self.history[key]
        
        # Stockfish gravity formula: decay toward zero
        # gravity_term = old_value * abs(bonus) / 512
        gravity_term = old_value * abs(bonus) // 512
        
        # Update with gravity
        new_value = old_value + bonus - gravity_term
        
        # Clamp to reasonable range
        self.history[key] = max(-16000, min(16000, new_value))
        
    def apply_periodic_gravity(self, nodes):
        """
        Apply periodic gravity based on node count.
        
        Args:
            nodes: Current node count
        """
        self.nodes_since_gravity += 1
        
        # Every N nodes, apply global decay
        if self.nodes_since_gravity >= self.gravity_interval:
            self.apply_global_gravity(factor=7/8)  # 12.5% decay
            self.nodes_since_gravity = 0
    
    def apply_global_gravity(self, factor=7/8):
        """
        Apply global gravity to all history entries.
        
        Args:
            factor: Decay factor (0.875 = 7/8 in Stockfish)
        """
        for key in self.history:
            self.history[key] = int(self.history[key] * factor)
    
    def clear(self):
        """Clear all history."""
        self.history.clear()
        self.nodes_since_gravity = 0


# ============================================================================
# 4. ENHANCED ASPIRATION WINDOWS - Stockfish Style (+30-50 Elo)
# ============================================================================

def get_aspiration_delta(alpha, prev_score, fail_count):
    """
    Get dynamic aspiration window delta (Stockfish formula).
    
    Args:
        alpha: Current alpha
        prev_score: Previous iteration score
        fail_count: Number of consecutive fails
    
    Returns:
        Delta to widen window
    """
    # Stockfish formula: delta = 11 + alpha^2 / 15620
    base_delta = 11 + (abs(alpha) * abs(alpha)) // 15620
    
    # Exponential widening on consecutive fails
    fail_multiplier = 2 ** fail_count
    
    return base_delta * fail_multiplier


def get_initial_aspiration_window(prev_score, depth):
    """
    Get initial aspiration window for iterative deepening.
    
    Args:
        prev_score: Score from previous iteration
        depth: Current depth
    
    Returns:
        (alpha, beta) tuple
    """
    if depth <= 4:
        # Wide window at low depths
        return (-30000, 30000)
    
    # Narrow window (Stockfish uses ~11-25 centipawns)
    window = 17  # Starting window
    
    alpha = prev_score - window
    beta = prev_score + window
    
    return (alpha, beta)


def widen_aspiration_window(alpha, beta, prev_score, fail_high, fail_low, fail_count):
    """
    Widen aspiration window after fail-high or fail-low.
    
    Args:
        alpha: Current alpha
        beta: Current beta
        prev_score: Previous score
        fail_high: Failed high (score >= beta)
        fail_low: Failed low (score <= alpha)
        fail_count: Consecutive fail count
    
    Returns:
        (new_alpha, new_beta, new_fail_count)
    """
    delta = get_aspiration_delta(alpha, prev_score, fail_count)
    
    if fail_high:
        # Widen beta
        new_beta = beta + delta
        new_alpha = alpha
        new_fail_count = fail_count + 1
    elif fail_low:
        # Widen alpha
        new_alpha = alpha - delta
        new_beta = beta
        new_fail_count = fail_count + 1
    else:
        # No fail, reset
        new_alpha = alpha
        new_beta = beta
        new_fail_count = 0
    
    # Clamp to reasonable bounds
    INFINITY = 30000
    new_alpha = max(new_alpha, -INFINITY)
    new_beta = min(new_beta, INFINITY)
    
    return (new_alpha, new_beta, new_fail_count)


# ============================================================================
# 5. CONTINUATION HISTORY - Stockfish Style (+40-60 Elo)
# ============================================================================

class ContinuationHistory:
    """
    Continuation history tracks move sequences (not just single moves).
    "If move A, then move B is good" logic.
    """
    
    def __init__(self):
        # Key: ((prev_from, prev_to), (cur_from, cur_to)) -> score
        self.cont_history = defaultdict(int)
        
        # For gravity
        self.nodes_since_gravity = 0
        self.gravity_interval = 4096
    
    def get_continuation_bonus(self, prev_move, current_move):
        """
        Get continuation bonus for a move sequence.
        
        Args:
            prev_move: Previous move (chess.Move or None)
            current_move: Current move being considered
        
        Returns:
            Bonus score (0 if no data)
        """
        if prev_move is None:
            return 0
        
        key = ((prev_move.from_square, prev_move.to_square),
               (current_move.from_square, current_move.to_square))
        
        return self.cont_history.get(key, 0)
    
    def update_continuation(self, prev_move, current_move, bonus):
        """
        Update continuation history for a move pair.
        
        Args:
            prev_move: Previous move
            current_move: Current move
            bonus: Bonus to add
        """
        if prev_move is None:
            return
        
        key = ((prev_move.from_square, prev_move.to_square),
               (current_move.from_square, current_move.to_square))
        
        old_value = self.cont_history[key]
        
        # Apply gravity like regular history
        gravity_term = old_value * abs(bonus) // 512
        new_value = old_value + bonus - gravity_term
        
        # Clamp
        self.cont_history[key] = max(-16000, min(16000, new_value))
    
    def apply_periodic_gravity(self, nodes):
        """Apply periodic global gravity."""
        self.nodes_since_gravity += 1
        
        if self.nodes_since_gravity >= self.gravity_interval:
            self.apply_global_gravity(factor=7/8)
            self.nodes_since_gravity = 0
    
    def apply_global_gravity(self, factor=7/8):
        """Apply global decay to all entries."""
        for key in self.cont_history:
            self.cont_history[key] = int(self.cont_history[key] * factor)
    
    def clear(self):
        """Clear all continuation history."""
        self.cont_history.clear()
        self.nodes_since_gravity = 0


# ============================================================================
# 6. ENHANCED MULTICUT - Stockfish Style (+20-30 Elo)
# ============================================================================

def get_multicut_threshold(depth):
    """
    Get number of beta cutoffs needed for multicut (Stockfish).
    
    Args:
        depth: Current search depth
    
    Returns:
        Number of cutoffs required (2 or 3)
    """
    # Stockfish uses 3 cuts at high depth, 2 at low depth
    if depth >= 8:
        return 3
    else:
        return 2


def try_multicut_pruning(board, depth, beta, info, ply, ordered_moves, cutoff_threshold):
    """
    Try multicut pruning with Stockfish-style thresholds.
    
    Args:
        board: Chess board
        depth: Current depth
        beta: Beta bound
        info: Search info
        ply: Current ply
        ordered_moves: Ordered move list
        cutoff_threshold: Number of cutoffs needed
    
    Returns:
        beta if multicut succeeds, None otherwise
    """
    if depth < 6:
        return None
    
    # Reduced depth for multicut search
    reduced_depth = depth - 3
    cutoff_count = 0
    
    # Try first N moves
    max_moves_to_try = min(8, len(ordered_moves))
    
    for i in range(max_moves_to_try):
        move = ordered_moves[i]
        
        board.push(move)
        
        # Null-window search at reduced depth
        score = -alpha_beta_multicut(board, reduced_depth, -beta, -beta + 1, info, ply + 1)
        
        board.pop()
        
        # Check for beta cutoff
        if score >= beta:
            cutoff_count += 1
            
            # If enough cutoffs, prune node
            if cutoff_count >= cutoff_threshold:
                return beta
    
    return None


def alpha_beta_multicut(board, depth, alpha, beta, info, ply):
    """
    Simplified alpha-beta for multicut testing.
    """
    # Import to avoid circular dependency
    from src.ai.minimax_optimized import quiescence_search
    
    info.nodes += 1
    
    if depth <= 0:
        return quiescence_search(board, alpha, beta, info, ply)
    
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        if board.is_check():
            return -30000 + ply
        return 0
    
    best_score = -30000
    
    for move in legal_moves:
        board.push(move)
        score = -alpha_beta_multicut(board, depth - 1, -beta, -alpha, info, ply + 1)
        board.pop()
        
        best_score = max(best_score, score)
        if best_score >= beta:
            return beta
    
    return best_score


# ============================================================================
# INTEGRATION HELPERS
# ============================================================================

def calculate_improving_flag(board, static_eval, prev_static_eval):
    """
    Calculate 'improving' flag for LMP and other techniques.
    
    Args:
        board: Current board
        static_eval: Current static evaluation (from White's perspective)
        prev_static_eval: Static eval from 2 plies ago (from White's perspective)
    
    Returns:
        True if position is improving for side to move
    """
    if prev_static_eval is None:
        return False
    
    # Improving if eval increased for side to move
    # Note: eval is always from White's perspective
    # For Black, improving means eval decreased (became more negative)
    if board.turn == chess.WHITE:
        return static_eval > prev_static_eval
    else:
        # Black: lower eval (more negative) is better
        return static_eval < prev_static_eval


def get_history_bonus(depth, is_cutoff):
    """
    Get history bonus based on depth and result.
    
    Args:
        depth: Search depth where move was found
        is_cutoff: Move caused beta cutoff
    
    Returns:
        Bonus value (positive for good moves)
    """
    if is_cutoff:
        # Cutoff moves get big bonus
        return depth * depth
    else:
        # Non-cutoff moves get smaller bonus or penalty
        return -(depth * depth) // 2
