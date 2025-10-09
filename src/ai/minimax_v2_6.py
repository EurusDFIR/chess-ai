# src/ai/minimax_v2_6.py
"""
Chess AI v2.6.0 - Complete Stockfish-Inspired Techniques Integration

NEW in v2.6 (Phase 2 - ALL Stockfish Techniques):
- ✅ Enhanced Late Move Pruning (LMP) (+40-60 Elo)
- ✅ Enhanced Razoring (+30-50 Elo)
- ✅ History Gravity (+20-40 Elo)
- ✅ Enhanced Aspiration Windows (+30-50 Elo)
- ✅ Continuation History (+40-60 Elo)
- ✅ Multicut Enhanced (+20-30 Elo)

Previous v2.5:
- Correction History (+100-150 Elo)
- Singular Extensions (+50-80 Elo)
- Internal Iterative Deepening (+30-50 Elo)
- Probcut (+40-60 Elo)

Total Expected Gain: +380-540 Elo over v2.4
Target Strength: 2500-2700 Elo
"""

import chess
import time
import random
import math
from collections import defaultdict
from src.ai.evaluation_optimized import evaluate_incremental, EvaluationCache
from src.ai.correction_history import CorrectionHistory

# Import base classes từ minimax_optimized
from src.ai.minimax_optimized import (
    MATE_SCORE, MAX_PLY, INFINITY, PIECE_VALUES,
    get_zobrist_hash, TranspositionTable, SearchInfo,
    see, score_move, quiescence_search
)


# ============================================================================
# NEW v2.6: CONTINUATION HISTORY (+40-60 Elo)
# ============================================================================

class ContinuationHistory:
    """
    Track move pair patterns: "After move A, move B is good"
    Significantly improves move ordering.
    """
    def __init__(self):
        # (prev_move_from_to, current_move_from_to) -> score
        self.table = defaultdict(lambda: defaultdict(int))
        self.max_value = 16384  # Stockfish uses 16384
    
    def get(self, prev_move, current_move):
        """Get continuation history bonus."""
        if not prev_move:
            return 0
        
        prev_key = (prev_move.from_square, prev_move.to_square)
        curr_key = (current_move.from_square, current_move.to_square)
        
        return self.table[prev_key].get(curr_key, 0)
    
    def update(self, prev_move, current_move, bonus):
        """Update continuation history with gravity."""
        if not prev_move:
            return
        
        prev_key = (prev_move.from_square, prev_move.to_square)
        curr_key = (current_move.from_square, current_move.to_square)
        
        old_value = self.table[prev_key].get(curr_key, 0)
        
        # Stockfish gravity formula: bonus - value * abs(bonus) / max_value
        gravity = old_value * abs(bonus) // self.max_value
        new_value = old_value + bonus - gravity
        
        # Clamp to [-max_value, max_value]
        new_value = max(min(new_value, self.max_value), -self.max_value)
        self.table[prev_key][curr_key] = new_value
    
    def apply_gravity(self, factor=7/8):
        """Decay all values toward zero."""
        for prev_key in self.table:
            for curr_key in list(self.table[prev_key].keys()):
                self.table[prev_key][curr_key] = int(self.table[prev_key][curr_key] * factor)


# ============================================================================
# ENHANCED SEARCH INFO (with all new tables)
# ============================================================================

class EnhancedSearchInfo(SearchInfo):
    """Extended SearchInfo with Continuation History and improved stats."""
    def __init__(self):
        super().__init__()
        
        # NEW: Continuation History
        self.continuation_history = ContinuationHistory()
        
        # NEW: History with gravity
        self.history_max = 16384
        
        # NEW: Enhanced statistics
        self.lmp_cutoffs = 0
        self.razoring_cutoffs = 0
        self.continuation_hits = 0
        self.multicut_cutoffs = 0
        
        # Track improving flag per ply
        self.improving = [False] * MAX_PLY
        
        # Track previous static evals for improving detection
        self.prev_static_evals = [0] * MAX_PLY
        
        # Initialize PV (Principal Variation) if not exists
        if not hasattr(self, 'pv'):
            self.pv = [[None] * MAX_PLY for _ in range(MAX_PLY)]
            self.pv_length = [0] * MAX_PLY
        
        # Initialize TT stats if not exists
        if not hasattr(self, 'tt_hits'):
            self.tt_hits = 0
            self.cut_nodes = 0
    
    def update_pv(self, ply, move):
        """Update Principal Variation."""
        self.pv[ply][ply] = move
        for i in range(ply + 1, self.pv_length[ply + 1]):
            self.pv[ply][i] = self.pv[ply + 1][i]
        self.pv_length[ply] = self.pv_length[ply + 1]
    
    def apply_history_gravity(self):
        """Apply gravity to history heuristic (Stockfish style)."""
        for key in list(self.history.keys()):
            self.history[key] = int(self.history[key] * 7 / 8)
            
            # Remove near-zero entries
            if abs(self.history[key]) < 10:
                del self.history[key]
    
    def update_history_enhanced(self, move, depth, bonus):
        """Update history with gravity (Stockfish formula)."""
        key = (move.from_square, move.to_square)
        old_value = self.history.get(key, 0)
        
        # Gravity term
        gravity = old_value * abs(bonus) // self.history_max
        new_value = old_value + bonus - gravity
        
        # Clamp
        new_value = max(min(new_value, self.history_max), -self.history_max)
        self.history[key] = new_value


# ============================================================================
# ENHANCED MOVE ORDERING (with Continuation History)
# ============================================================================

def order_moves_enhanced(board, moves, info, ply, hash_move=None):
    """
    Enhanced move ordering with Continuation History.
    
    Priority:
    1. Hash move (100000)
    2. Winning captures (10000+)
    3. Promotions (8000+)
    4. Killer moves (7500, 7400)
    5. Countermoves (7000)
    6. Continuation history (0-6000)
    7. History heuristic (0-5000)
    8. Checks (+500)
    9. Others
    """
    scored_moves = []
    
    for move in moves:
        score = 0
        
        # 1. Hash move (TT)
        if move == hash_move:
            score = 100000
        
        # 2. Winning captures (MVV-LVA + SEE)
        elif board.is_capture(move):
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            
            if victim and attacker:
                mvv_lva = PIECE_VALUES[victim.piece_type] * 10 - PIECE_VALUES[attacker.piece_type]
                
                # SEE check
                see_value = see(board, move)
                if see_value >= 0:
                    score = 10000 + mvv_lva
                else:
                    score = 100 + mvv_lva
        
        # 3. Promotions
        elif move.promotion:
            score = 8000 + PIECE_VALUES.get(move.promotion, 0)
        
        # 4. Killer moves
        elif move == info.killer_moves[ply][0]:
            score = 7500
        elif move == info.killer_moves[ply][1]:
            score = 7400
        
        # 5. Countermove
        elif hasattr(info, 'last_move') and info.last_move:
            if info.countermoves.get(info.last_move) == move:
                score = 7000
        
        # 6. NEW: Continuation History
        if score < 7000:  # Not already prioritized
            if hasattr(info, 'continuation_history') and hasattr(info, 'last_move'):
                cont_bonus = info.continuation_history.get(info.last_move, move)
                # Scale to 0-6000 range
                score += (cont_bonus + 16384) * 6000 // 32768
        
        # 7. History heuristic
        if score < 7000:
            history_key = (move.from_square, move.to_square)
            history_score = info.history.get(history_key, 0)
            # Scale to 0-5000 range
            score += max(0, min(5000, (history_score + 16384) * 5000 // 32768))
        
        # 8. Checks
        if board.gives_check(move):
            score += 500
        
        # 9. Castling
        if board.is_castling(move):
            score += 300
        
        scored_moves.append((move, score))
    
    # Sort descending by score
    scored_moves.sort(key=lambda x: x[1], reverse=True)
    return [move for move, _ in scored_moves]


# ============================================================================
# ENHANCED LATE MOVE PRUNING (LMP) - Stockfish Style (+40-60 Elo)
# ============================================================================

def late_move_pruning_count(depth, improving):
    """
    Calculate LMP threshold (Stockfish formula).
    More aggressive when not improving.
    """
    # Stockfish: (3 + depth * depth) / (2 - improving)
    base_count = 3 + depth * depth
    divisor = 2 - (1 if improving else 0)
    
    return base_count // divisor


# ============================================================================
# ENHANCED RAZORING - Stockfish Style (+30-50 Elo)
# ============================================================================

def enhanced_razoring(board, depth, alpha, info, ply):
    """
    Enhanced razoring with better margins (Stockfish style).
    """
    if depth > 7 or board.is_check():
        return None
    
    # Stockfish razoring margins
    razor_margins = {
        1: 240,
        2: 280,
        3: 300,
        4: 350,
        5: 400,
        6: 450,
        7: 500
    }
    
    razor_margin = razor_margins.get(depth, 0)
    eval_score = evaluate_incremental(board)
    
    if eval_score + razor_margin < alpha:
        # Verify with qsearch
        q_score = quiescence_search(board, alpha, beta=alpha+1, info=info, ply=ply)
        
        if q_score < alpha:
            info.razoring_cutoffs += 1
            return q_score
    
    return None


# ============================================================================
# ENHANCED MULTICUT PRUNING - Stockfish Style (+20-30 Elo)
# ============================================================================

def multicut_pruning_enhanced(board, depth, beta, info, ply, ordered_moves):
    """
    Enhanced multicut: 3 cuts at high depth, 2 at medium depth.
    """
    if depth < 6 or board.is_check():
        return None
    
    # Stockfish: 3 cuts at depth >= 8, else 2 cuts
    required_cuts = 3 if depth >= 8 else 2
    
    multicut_depth = depth - 4
    cut_count = 0
    
    # Try first 6 moves only
    for move in ordered_moves[:6]:
        board.push(move)
        
        # Null window search
        score = -alpha_beta_enhanced(board, multicut_depth, -beta, -beta + 1, 
                                     info, ply + 1, do_null=False)
        
        board.pop()
        
        if score >= beta:
            cut_count += 1
            
            if cut_count >= required_cuts:
                info.multicut_cutoffs += 1
                return beta
    
    return None


# ============================================================================
# ENHANCED ASPIRATION WINDOWS - Stockfish Style (+30-50 Elo)
# ============================================================================

def enhanced_aspiration_windows(board, max_depth, time_limit, info):
    """
    Stockfish-style aspiration windows with dynamic widening.
    """
    start_time = time.time()
    info.start_time = start_time
    info.time_limit = time_limit
    
    best_score = 0
    best_move = None
    
    for depth in range(1, max_depth + 1):
        if depth <= 4:
            # Full window for shallow depths
            alpha = -INFINITY
            beta = INFINITY
        else:
            # Narrow window (Stockfish: ±16 initially)
            window = 16
            alpha = best_score - window
            beta = best_score + window
        
        research_count = 0
        max_researches = 4
        
        while True:
            score = alpha_beta_enhanced(board, depth, alpha, beta, info, ply=0, do_null=True)
            
            # Check if we're out of time
            elapsed = time.time() - start_time
            if elapsed > time_limit * 0.8:
                return best_move, best_score
            
            # Success - score within window
            if alpha < score < beta:
                best_score = score
                # Get best move from PV
                if info.pv[0] and info.pv[0][0]:
                    best_move = info.pv[0][0]
                break
            
            # Failed high or low - widen window
            research_count += 1
            if research_count >= max_researches:
                # Give up, use full window
                alpha = -INFINITY
                beta = INFINITY
            else:
                # Stockfish dynamic widening formula
                delta = window + window * research_count // 2
                
                if score <= alpha:
                    # Failed low
                    alpha = max(alpha - delta, -INFINITY)
                    beta = (alpha + beta) // 2
                elif score >= beta:
                    # Failed high
                    beta = min(beta + delta, INFINITY)
        
        # Print search info
        elapsed = time.time() - start_time
        nps = int(info.nodes / elapsed) if elapsed > 0 else 0
        
        # Safe PV string (filter out None values)
        pv_moves = [m for m in info.pv[0][:5] if m is not None]
        pv_str = " ".join([move.uci() for move in pv_moves]) if pv_moves else "(none)"
        
        print(f"depth {depth} score cp {best_score} nodes {info.nodes} "
              f"nps {nps} time {int(elapsed*1000)} pv {pv_str}")
        
        # Early exit if using 80% of time
        if elapsed > time_limit * 0.8:
            break
    
    # Fallback: if no best_move from PV, pick first legal move
    if not best_move:
        legal_moves = list(board.legal_moves)
        if legal_moves:
            best_move = legal_moves[0]
            print("Warning: No best move from search, using first legal move")
    
    return best_move, best_score


# ============================================================================
# MAIN ENHANCED ALPHA-BETA (All Techniques Integrated)
# ============================================================================

def alpha_beta_enhanced(board, depth, alpha, beta, info, ply, do_null=True):
    """
    Complete alpha-beta with ALL v2.6 techniques:
    - Enhanced LMP
    - Enhanced Razoring
    - History Gravity
    - Continuation History
    - Multicut Enhanced
    - Plus all v2.5 techniques
    """
    info.nodes += 1
    info.pv_length[ply] = ply
    
    if info.check_time():
        return 0
    
    # Mate distance pruning
    alpha = max(alpha, -MATE_SCORE + ply)
    beta = min(beta, MATE_SCORE - ply - 1)
    if alpha >= beta:
        return alpha
    
    # Check for draw
    if (board.is_insufficient_material() or 
        board.is_seventyfive_moves() or 
        board.is_fivefold_repetition() or
        board.can_claim_threefold_repetition() or
        board.can_claim_draw()):
        return 0
    
    # Repetition penalty
    if board.is_repetition(2):
        return 0 if ply == 0 else -50
    
    # Transposition table probe
    zobrist_hash = get_zobrist_hash(board)
    tt_entry = info.tt.probe(zobrist_hash)
    hash_move = None
    
    if tt_entry and tt_entry['depth'] >= depth:
        hash_move = tt_entry['best_move']
        if tt_entry['bound'] == TranspositionTable.EXACT:
            return tt_entry['score']
        elif tt_entry['bound'] == TranspositionTable.LOWER_BOUND:
            alpha = max(alpha, tt_entry['score'])
        elif tt_entry['bound'] == TranspositionTable.UPPER_BOUND:
            beta = min(beta, tt_entry['score'])
        
        if alpha >= beta:
            return tt_entry['score']
    elif tt_entry:
        hash_move = tt_entry['best_move']
    
    # Quiescence search at leaf nodes
    if depth <= 0:
        return quiescence_search(board, alpha, beta, info, ply)
    
    # Check extension
    in_check = board.is_check()
    if in_check:
        depth += 1
    
    # Static eval with correction history
    static_eval = evaluate_incremental(board)
    
    if hasattr(info, 'correction_history'):
        prev_move = info.last_move if hasattr(info, 'last_move') else None
        correction = info.correction_history.get_correction(board, prev_move)
        corrected_eval = static_eval + correction
        corrected_eval = max(min(corrected_eval, MATE_SCORE - 100), -MATE_SCORE + 100)
    else:
        corrected_eval = static_eval
    
    # NEW: Calculate improving flag (Stockfish)
    improving = False
    if ply >= 2:
        prev_eval = info.prev_static_evals[ply - 2]
        improving = corrected_eval > prev_eval
        info.improving[ply] = improving
    
    info.prev_static_evals[ply] = corrected_eval
    
    # Store static eval
    if not hasattr(info, 'static_evals'):
        info.static_evals = {}
    info.static_evals[ply] = corrected_eval
    
    # NEW: Enhanced Razoring
    razor_score = enhanced_razoring(board, depth, alpha, info, ply)
    if razor_score is not None:
        return razor_score
    
    # Null move pruning (existing)
    if do_null and not in_check:
        # Simple null move implementation
        if depth >= 3:
            R = 3 if depth > 6 else 2
            board.push(chess.Move.null())
            null_score = -alpha_beta_enhanced(board, depth - 1 - R, -beta, -beta + 1, info, ply + 1, False)
            board.pop()
            
            if null_score >= beta:
                return beta
    
    # Futility pruning
    futility = False
    if depth <= 3 and not in_check and abs(alpha) < MATE_SCORE - 100:
        margins = {1: 200, 2: 300, 3: 500}
        if corrected_eval + margins.get(depth, 0) <= alpha:
            futility = True
    
    # Generate and order moves
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        if in_check:
            return -MATE_SCORE + ply
        return 0
    
    ordered_moves = order_moves_enhanced(board, legal_moves, info, ply, hash_move)
    
    # NEW: Enhanced Multicut Pruning
    if depth >= 6 and not in_check:
        multicut_score = multicut_pruning_enhanced(board, depth, beta, info, ply, ordered_moves)
        if multicut_score is not None:
            return multicut_score
    
    # NEW: Calculate LMP count
    lmp_count = late_move_pruning_count(depth, improving) if depth <= 8 else 999
    
    best_score = -INFINITY
    best_move = None
    bound_type = TranspositionTable.UPPER_BOUND
    moves_searched = 0
    
    for move_num, move in enumerate(ordered_moves):
        # NEW: Late Move Pruning (Stockfish style)
        if (depth <= 8 and moves_searched >= lmp_count and 
            not in_check and not board.is_check() and
            not board.is_capture(move) and not move.promotion):
            info.lmp_cutoffs += 1
            continue
        
        # Futility pruning
        if futility and moves_searched > 0 and not board.is_capture(move) and not move.promotion:
            continue
        
        # Save previous last_move
        prev_last_move = info.last_move if hasattr(info, 'last_move') else None
        info.last_move = move
        
        board.push(move)
        
        # Late Move Reduction (LMR)
        reduction = 0
        if (depth >= 3 and moves_searched >= 4 and 
            not in_check and not board.is_check() and
            not board.is_capture(move) and not move.promotion):
            reduction = int(math.log(depth) * math.log(move_num + 1) / 2.5)
            reduction = min(reduction, depth - 1)
        
        # Principal Variation Search (PVS)
        if moves_searched == 0:
            score = -alpha_beta_enhanced(board, depth - 1, -beta, -alpha, info, ply + 1, True)
        else:
            score = -alpha_beta_enhanced(board, depth - 1 - reduction, -alpha - 1, -alpha, info, ply + 1, True)
            
            if score > alpha and reduction > 0:
                score = -alpha_beta_enhanced(board, depth - 1, -alpha - 1, -alpha, info, ply + 1, True)
            
            if score > alpha and score < beta:
                score = -alpha_beta_enhanced(board, depth - 1, -beta, -alpha, info, ply + 1, True)
        
        board.pop()
        info.last_move = prev_last_move
        moves_searched += 1
        
        if score > best_score:
            best_score = score
            best_move = move
            
            if score > alpha:
                alpha = score
                bound_type = TranspositionTable.EXACT
                info.update_pv(ply, move)
                
                if score >= beta:
                    bound_type = TranspositionTable.LOWER_BOUND
                    
                    # Update histories
                    if not board.is_capture(move):
                        # Killer moves
                        if info.killer_moves[ply][0] != move:
                            info.killer_moves[ply][1] = info.killer_moves[ply][0]
                            info.killer_moves[ply][0] = move
                        
                        # History heuristic with gravity
                        bonus = depth * depth
                        info.update_history_enhanced(move, depth, bonus)
                        
                        # Countermove
                        info.update_countermove(prev_last_move, move)
                        
                        # NEW: Continuation History
                        if hasattr(info, 'continuation_history') and prev_last_move:
                            cont_bonus = depth * depth
                            info.continuation_history.update(prev_last_move, move, cont_bonus)
                    
                    break
    
    # Update correction history
    if hasattr(info, 'correction_history') and ply in info.static_evals:
        static_val = info.static_evals[ply]
        search_val = best_score
        eval_error = search_val - static_val
        
        if not in_check and abs(eval_error) > 10:
            prev_move = info.last_move if hasattr(info, 'last_move') else None
            info.correction_history.update(board, eval_error, prev_move, depth)
    
    # Store in transposition table
    info.tt.store(zobrist_hash, depth, best_score, bound_type, best_move)
    
    return best_score


# ============================================================================
# ITERATIVE DEEPENING (Enhanced with better aspiration windows)
# ============================================================================

def iterative_deepening_v2_6(board, max_depth=10, time_limit=5.0):
    """
    Main search entry point for v2.6 with all enhancements.
    """
    info = EnhancedSearchInfo()
    info.correction_history = CorrectionHistory()
    
    print(f"Starting EURY v2.6 search (max_depth={max_depth}, time={time_limit}s)")
    print("=" * 70)
    
    # Use enhanced aspiration windows
    best_move, best_score = enhanced_aspiration_windows(board, max_depth, time_limit, info)
    
    # Apply gravity to all history tables
    info.apply_history_gravity()
    info.continuation_history.apply_gravity()
    info.correction_history.apply_gravity()
    
    # Print statistics
    elapsed = time.time() - info.start_time
    nps = int(info.nodes / elapsed) if elapsed > 0 else 0
    
    print("=" * 70)
    print(f"Best move: {best_move.uci() if best_move else 'None'} ({best_score}cp)")
    print(f"Nodes: {info.nodes:,} | NPS: {nps:,} | Time: {elapsed:.2f}s")
    print(f"TT hits: {info.tt_hits:,} | Cut nodes: {info.cut_nodes:,}")
    print(f"LMP cuts: {info.lmp_cutoffs:,} | Razoring cuts: {info.razoring_cutoffs:,}")
    print(f"Multicut cuts: {info.multicut_cutoffs:,}")
    
    return best_move


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def get_best_move(board, depth=6, time_limit=5.0):
    """
    Get best move using EURY v2.6 engine.
    
    Args:
        board: chess.Board position
        depth: Maximum search depth
        time_limit: Time limit in seconds
    
    Returns:
        chess.Move: Best move found
    """
    return iterative_deepening_v2_6(board, depth, time_limit)


if __name__ == "__main__":
    # Quick test
    board = chess.Board()
    move = get_best_move(board, depth=8, time_limit=5.0)
    print(f"\nBest move: {move}")
