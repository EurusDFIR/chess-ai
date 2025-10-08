# src/ai/minimax_v2_4.py
"""
Chess AI v2.5.0 - Advanced Search Techniques with Correction History
New optimizations:
- Singular Extensions
- Multi-Cut Pruning  
- Internal Iterative Deepening (IID)
- Probcut
- Correction History (+100-150 Elo) ⭐ NEW in v2.5
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
    see, score_move, order_moves, quiescence_search,
    null_move_pruning, futility_pruning_margin
)


# ============================================================================
# 1. SINGULAR EXTENSIONS (+50-80 Elo)
# ============================================================================

def is_singular_move(board, hash_move, depth, beta, info, ply):
    """
    Check if hash_move is "singular" (significantly better than alternatives).
    If yes, extend search depth for this move.
    
    Concept:
    - Do reduced search excluding hash_move
    - If all other moves fail low (< beta - margin), hash_move is singular
    - Extend search depth by 1
    """
    if not hash_move or depth < 8:  # Only at high depths
        return False
    
    # Singular margin (typically beta - 2 * depth)
    singular_beta = beta - depth * 2
    singular_depth = (depth - 1) // 2  # Reduced depth
    
    # Generate moves excluding hash_move
    legal_moves = [m for m in board.legal_moves if m != hash_move]
    if not legal_moves:
        return False
    
    # Search other moves with null window
    for move in legal_moves[:8]:  # Check top 8 moves only (performance)
        board.push(move)
        score = -alpha_beta_singular(board, singular_depth, -singular_beta, -singular_beta + 1, 
                                     info, ply + 1, False)
        board.pop()
        
        # If any move >= singular_beta, hash_move is not singular
        if score >= singular_beta:
            return False
    
    # All other moves failed low - hash_move is singular!
    return True


def alpha_beta_singular(board, depth, alpha, beta, info, ply, do_null):
    """Helper alpha-beta for singular extension test (simplified)."""
    info.nodes += 1
    
    if depth <= 0 or info.check_time():
        return quiescence_search(board, alpha, beta, info, ply)
    
    # Quick TT probe
    zobrist_hash = get_zobrist_hash(board)
    tt_entry = info.tt.probe(zobrist_hash)
    if tt_entry and tt_entry['depth'] >= depth:
        if tt_entry['bound'] == TranspositionTable.EXACT:
            return tt_entry['score']
    
    # Simple search without extensions
    legal_moves = list(board.legal_moves)
    best_score = -INFINITY
    
    for move in legal_moves:
        board.push(move)
        score = -alpha_beta_singular(board, depth - 1, -beta, -alpha, info, ply + 1, True)
        board.pop()
        
        best_score = max(best_score, score)
        if best_score >= beta:
            break
    
    return best_score


# ============================================================================
# 2. MULTI-CUT PRUNING (+30-50 Elo)
# ============================================================================

def multi_cut_pruning(board, depth, beta, info, ply, ordered_moves):
    """
    If multiple moves (e.g., 3) cause beta cutoff at reduced depth,
    assume current position is too good and prune immediately.
    
    Concept:
    - Try M moves (typically 3-6) at reduced depth (depth - 3)
    - Count how many cause beta cutoff
    - If >= C cutoffs (typically 2-3), return beta immediately
    """
    if depth < 6:  # Only at sufficient depth
        return None
    
    M = 6  # Try first 6 moves
    C = 3  # Need 3 cutoffs to trigger
    cutoff_count = 0
    reduced_depth = depth - 4
    
    for move in ordered_moves[:M]:
        board.push(move)
        score = -alpha_beta_multi_cut(board, reduced_depth, -beta, -beta + 1, info, ply + 1)
        board.pop()
        
        if score >= beta:
            cutoff_count += 1
            if cutoff_count >= C:
                # Multiple cutoffs detected - position is too good
                return beta
    
    return None


def alpha_beta_multi_cut(board, depth, alpha, beta, info, ply):
    """Helper alpha-beta for multi-cut test (simplified)."""
    info.nodes += 1
    
    if depth <= 0 or info.check_time():
        return quiescence_search(board, alpha, beta, info, ply)
    
    legal_moves = list(board.legal_moves)
    best_score = -INFINITY
    
    for move in legal_moves:
        board.push(move)
        score = -alpha_beta_multi_cut(board, depth - 1, -beta, -alpha, info, ply + 1)
        board.pop()
        
        best_score = max(best_score, score)
        if best_score >= beta:
            return beta
    
    return best_score


# ============================================================================
# 3. INTERNAL ITERATIVE DEEPENING (IID) (+40-60 Elo)
# ============================================================================

def internal_iterative_deepening(board, depth, alpha, beta, info, ply):
    """
    When TT miss (no hash_move), do shallow search to find good move.
    
    Concept:
    - If no hash_move from TT, we have poor move ordering
    - Do reduced depth search (depth - 2 to depth - 4)
    - Store result in TT for move ordering
    """
    if depth < 4:  # Only worth it at sufficient depth
        return None
    
    iid_depth = max(1, depth - 4)  # Reduced depth
    
    # Do shallow search
    score = alpha_beta_iid(board, iid_depth, alpha, beta, info, ply)
    
    # Check if we got a best move from TT after shallow search
    zobrist_hash = get_zobrist_hash(board)
    tt_entry = info.tt.probe(zobrist_hash)
    
    if tt_entry and tt_entry['best_move']:
        return tt_entry['best_move']
    
    return None


def alpha_beta_iid(board, depth, alpha, beta, info, ply):
    """Helper alpha-beta for IID (simplified)."""
    info.nodes += 1
    
    if depth <= 0:
        return quiescence_search(board, alpha, beta, info, ply)
    
    # Check TT
    zobrist_hash = get_zobrist_hash(board)
    tt_entry = info.tt.probe(zobrist_hash)
    hash_move = tt_entry['best_move'] if tt_entry else None
    
    legal_moves = list(board.legal_moves)
    ordered_moves = order_moves(board, legal_moves, info, ply, hash_move)
    
    best_score = -INFINITY
    best_move = None
    
    for move in ordered_moves:
        board.push(move)
        score = -alpha_beta_iid(board, depth - 1, -beta, -alpha, info, ply + 1)
        board.pop()
        
        if score > best_score:
            best_score = score
            best_move = move
        
        if best_score >= beta:
            break
    
    # Store in TT
    info.tt.store(zobrist_hash, depth, best_score, 
                  TranspositionTable.EXACT if best_score < beta else TranspositionTable.LOWER_BOUND,
                  best_move)
    
    return best_score


# ============================================================================
# 4. PROBCUT (+60-100 Elo)
# ============================================================================

def probcut(board, depth, beta, info, ply):
    """
    Early cutoff using shallow search with margin.
    
    Concept:
    - If shallow search (depth - 3) score >= beta + margin
    - Assume deep search will also >= beta
    - Return beta immediately (cutoff)
    
    Based on statistical analysis: shallow scores correlate with deep scores.
    """
    if depth < 5:  # Only at sufficient depth
        return None
    
    probcut_depth = depth - 4
    probcut_beta = beta + 100  # Margin (typically 100-200 centipawns)
    
    # Do shallow search with raised beta
    score = alpha_beta_probcut(board, probcut_depth, probcut_beta - 1, probcut_beta, info, ply)
    
    # If shallow search >= probcut_beta, likely deep search >= beta
    if score >= probcut_beta:
        return beta  # Cutoff!
    
    return None


def alpha_beta_probcut(board, depth, alpha, beta, info, ply):
    """Helper alpha-beta for probcut (simplified)."""
    info.nodes += 1
    
    if depth <= 0:
        return quiescence_search(board, alpha, beta, info, ply)
    
    # Only try capturing moves for probcut (more forcing)
    legal_moves = [m for m in board.legal_moves if board.is_capture(m)]
    
    best_score = -INFINITY
    for move in legal_moves[:8]:  # Top 8 captures only
        board.push(move)
        score = -alpha_beta_probcut(board, depth - 1, -beta, -alpha, info, ply + 1)
        board.pop()
        
        best_score = max(best_score, score)
        if best_score >= beta:
            return beta
    
    return best_score


# ============================================================================
# MAIN ALPHA-BETA WITH ALL TECHNIQUES
# ============================================================================

def alpha_beta_advanced(board, depth, alpha, beta, info, ply, do_null=True):
    """
    Enhanced alpha-beta with all Phase 1 advanced techniques.
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
    
    # ========== NEW v2.5: Static Eval with Correction History ==========
    static_eval = evaluate_incremental(board)
    
    # Apply correction from history if available
    if hasattr(info, 'correction_history'):
        prev_move = info.last_move if hasattr(info, 'last_move') else None
        correction = info.correction_history.get_correction(board, prev_move)
        corrected_eval = static_eval + correction
        
        # Clamp to avoid tablebase range
        corrected_eval = max(min(corrected_eval, MATE_SCORE - 100), -MATE_SCORE + 100)
    else:
        corrected_eval = static_eval
    
    # Store static eval for later correction update (at root and PV nodes)
    if not hasattr(info, 'static_evals'):
        info.static_evals = {}
    info.static_evals[ply] = corrected_eval
    
    # ========== NEW: Internal Iterative Deepening (IID) ==========
    if not hash_move and depth >= 4 and not in_check:
        hash_move = internal_iterative_deepening(board, depth, alpha, beta, info, ply)
    
    # Null move pruning
    if do_null:
        null_score = null_move_pruning(board, depth, beta, info, ply)
        if null_score is not None and null_score >= beta:
            return beta
    
    # ========== NEW: Probcut ==========
    if not in_check and depth >= 5:
        probcut_score = probcut(board, depth, beta, info, ply)
        if probcut_score is not None:
            return probcut_score
    
    # Razoring
    if depth <= 3 and not in_check and abs(alpha) < MATE_SCORE - 100:
        eval_score = evaluate_incremental(board)
        razor_margin = [0, 300, 400, 600][depth]
        
        if eval_score + razor_margin < alpha:
            q_score = quiescence_search(board, alpha, beta, info, ply)
            if q_score < alpha:
                return q_score
    
    # Futility pruning
    futility = False
    if depth <= 3 and not in_check and abs(alpha) < MATE_SCORE - 100:
        eval_score = evaluate_incremental(board)
        if eval_score + futility_pruning_margin(depth) <= alpha:
            futility = True
    
    # Generate and order moves
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        if in_check:
            return -MATE_SCORE + ply
        return 0
    
    ordered_moves = order_moves(board, legal_moves, info, ply, hash_move)
    
    # ========== NEW: Multi-Cut Pruning ==========
    if depth >= 6 and not in_check:
        multi_cut_score = multi_cut_pruning(board, depth, beta, info, ply, ordered_moves)
        if multi_cut_score is not None:
            return multi_cut_score
    
    # ========== NEW: Singular Extension ==========
    singular_extension = 0
    if hash_move and depth >= 8 and not in_check:
        if is_singular_move(board, hash_move, depth, beta, info, ply):
            singular_extension = 1  # Extend by 1 ply
    
    best_score = -INFINITY
    best_move = None
    bound_type = TranspositionTable.UPPER_BOUND
    moves_searched = 0
    
    for move_num, move in enumerate(ordered_moves):
        # Futility pruning
        if futility and moves_searched > 0 and not board.is_capture(move) and not move.promotion:
            continue
        
        # Save previous last_move
        prev_last_move = info.last_move
        info.last_move = move
        
        board.push(move)
        
        # Extension for singular move
        extension = singular_extension if move == hash_move else 0
        
        # Late Move Reduction (LMR)
        reduction = 0
        if (depth >= 3 and moves_searched >= 4 and 
            not in_check and not board.is_check() and
            not board.is_capture(move) and not move.promotion):
            reduction = int(math.log(depth) * math.log(move_num + 1) / 2.5)
            reduction = min(reduction, depth - 1)
        
        # Principal Variation Search (PVS)
        if moves_searched == 0:
            score = -alpha_beta_advanced(board, depth - 1 + extension, -beta, -alpha, info, ply + 1, True)
        else:
            score = -alpha_beta_advanced(board, depth - 1 - reduction + extension, -alpha - 1, -alpha, info, ply + 1, True)
            
            if score > alpha and reduction > 0:
                score = -alpha_beta_advanced(board, depth - 1 + extension, -alpha - 1, -alpha, info, ply + 1, True)
            
            if score > alpha and score < beta:
                score = -alpha_beta_advanced(board, depth - 1 + extension, -beta, -alpha, info, ply + 1, True)
        
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
                    
                    # Update killer moves and history
                    if not board.is_capture(move):
                        if info.killer_moves[ply][0] != move:
                            info.killer_moves[ply][1] = info.killer_moves[ply][0]
                            info.killer_moves[ply][0] = move
                        
                        bonus = depth * depth
                        info.history[(move.from_square, move.to_square)] += bonus
                        
                        if info.history[(move.from_square, move.to_square)] > 10000:
                            for key in info.history:
                                info.history[key] //= 2
                        
                        info.update_countermove(info.last_move, move)
                    
                    break
    
    # ========== NEW v2.5: Update Correction History ==========
    # Update correction history based on search result vs static eval
    if hasattr(info, 'correction_history') and ply in info.static_evals:
        static_val = info.static_evals[ply]
        search_val = best_score
        
        # Calculate evaluation error (search found vs static estimate)
        eval_error = search_val - static_val
        
        # Only update for non-tactical positions (avoid noise)
        if not in_check and abs(eval_error) > 10:  # Threshold 10cp
            prev_move = info.last_move if hasattr(info, 'last_move') else None
            info.correction_history.update(board, eval_error, prev_move, depth)
    
    # Store in transposition table
    info.tt.store(zobrist_hash, depth, best_score, bound_type, best_move)
    
    return best_score


# ============================================================================
# ITERATIVE DEEPENING WITH ADVANCED SEARCH
# ============================================================================

def iterative_deepening_advanced(board, max_depth, time_limit=10.0):
    """
    Iterative deepening using advanced alpha-beta with correction history.
    v2.5: Added Correction History for +100-150 Elo gain.
    """
    info = SearchInfo(time_limit)
    info.tt.new_search()
    
    # ========== NEW v2.5: Initialize Correction History ==========
    info.correction_history = CorrectionHistory()
    info.static_evals = {}  # Store static evals for correction updates
    
    best_move = None
    best_score = 0
    
    print(f"\n{'Depth':<8} {'Score':<10} {'Nodes':<12} {'Time':<10} {'PV':<40}")
    print("-" * 80)
    
    for depth in range(1, max_depth + 1):
        if info.stopped:
            break
        
        # Aspiration window
        if depth > 4:
            window = 25
            alpha = best_score - window
            beta = best_score + window
        else:
            alpha = -INFINITY
            beta = INFINITY
        
        # Search with aspiration window
        research_count = 0
        while True:
            score = alpha_beta_advanced(board, depth, alpha, beta, info, 0, True)
            
            if score <= alpha:
                alpha = max(alpha - window * (2 ** research_count), -INFINITY)
                research_count += 1
            elif score >= beta:
                beta = min(beta + window * (2 ** research_count), INFINITY)
                research_count += 1
            else:
                best_score = score
                if info.pv_table[0][0]:
                    best_move = info.pv_table[0][0]
                break
            
            if info.stopped or research_count > 3:
                break
        
        # Print search info
        elapsed = time.time() - info.start_time
        pv_moves = [str(info.pv_table[0][i]) for i in range(info.pv_length[0])]
        pv_str = ' '.join(pv_moves[:5])
        
        print(f"{depth:<8} {best_score:<10} {info.nodes:<12} {elapsed:<10.3f} {pv_str:<40}")
        
        # ========== NEW v2.5: Apply Gravity to Correction History ==========
        # Every few depths, decay correction history to keep data fresh
        if depth % 3 == 0 and hasattr(info, 'correction_history'):
            info.correction_history.apply_gravity(factor=0.875)  # 7/8 decay
        
        if abs(best_score) > MATE_SCORE - 100:
            break
        
        if elapsed > time_limit * 0.8:
            break
    
    print("-" * 80)
    print(f"Best move: {best_move} | Score: {best_score} | Nodes: {info.nodes}\n")
    
    return best_move


def get_best_move_advanced(board, depth=6, time_limit=10.0):
    """Get best move using advanced techniques."""
    return iterative_deepening_advanced(board, depth, time_limit)


# Export for compatibility
get_best_move = get_best_move_advanced
