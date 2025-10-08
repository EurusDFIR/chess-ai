# src/ai/minimax_fast.py
"""
OPTIMIZED Fast Minimax Engine
Combines best techniques from v2.4 with speed optimizations

Key optimizations:
1. Fast evaluation function (evaluation_fast.py)
2. Improved move ordering
3. Better transposition table usage
4. Reduced function call overhead
5. Early termination checks

Target: 30-50% faster than minimax_v2_4.py while maintaining strength
"""

import chess
import chess.polyglot
import time
from collections import defaultdict
from src.ai.evaluation_fast import evaluate_fast, evaluate_fast_material_only

# Constants
MATE_SCORE = 30000
MAX_PLY = 100
INFINITY = 999999

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}


class TranspositionTable:
    """Optimized TT with better replacement strategy."""
    EXACT = 0
    LOWER_BOUND = 1
    UPPER_BOUND = 2
    
    def __init__(self, size_mb=256):
        self.size = (size_mb * 1024 * 1024) // 40  # ~40 bytes per entry
        self.table = {}
        self.hits = 0
        self.misses = 0
    
    def probe(self, zobrist_hash):
        """Probe TT for position."""
        if zobrist_hash in self.table:
            self.hits += 1
            return self.table[zobrist_hash]
        self.misses += 1
        return None
    
    def store(self, zobrist_hash, depth, score, bound, best_move):
        """Store position in TT with depth-preferred replacement."""
        if len(self.table) >= self.size:
            if zobrist_hash not in self.table:
                # Replace random entry (simplified)
                # In production, use age + depth replacement
                if len(self.table) > self.size * 1.2:
                    # Clear 20% of entries
                    keys = list(self.table.keys())
                    for k in keys[:len(keys)//5]:
                        del self.table[k]
        
        # Store new entry
        self.table[zobrist_hash] = {
            'depth': depth,
            'score': score,
            'bound': bound,
            'best_move': best_move
        }
    
    def clear(self):
        """Clear TT."""
        self.table.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self):
        """Get TT statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'size': len(self.table),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }


class SearchInfo:
    """Search information and statistics."""
    def __init__(self, max_time=None, max_depth=None):
        self.nodes = 0
        self.tt_hits = 0
        self.cutoffs = 0
        self.start_time = time.time()
        self.max_time = max_time
        self.max_depth = max_depth if max_depth else 50
        self.stop_search = False
        
        # Transposition table
        self.tt = TranspositionTable(size_mb=256)
        
        # History heuristic
        self.history = defaultdict(int)
        
        # Killer moves
        self.killers = defaultdict(list)
    
    def check_time(self):
        """Check if time limit reached."""
        if self.stop_search:
            return True
        if self.max_time and (time.time() - self.start_time) > self.max_time:
            self.stop_search = True
            return True
        return False
    
    def elapsed_time(self):
        """Get elapsed time."""
        return time.time() - self.start_time


def get_zobrist_hash(board):
    """Get Zobrist hash for position."""
    return chess.polyglot.zobrist_hash(board)


def see(board, move):
    """
    Static Exchange Evaluation (SEE)
    Estimate material gain/loss of a capture.
    Optimized version - faster than full calculation.
    """
    if not board.is_capture(move):
        return 0
    
    # Quick material count
    to_square = move.to_square
    captured_piece = board.piece_at(to_square)
    if not captured_piece:
        return 0
    
    # Simple approximation - value of captured piece
    return PIECE_VALUES[captured_piece.piece_type]


def score_move_fast(board, move, info, ply, hash_move):
    """
    OPTIMIZED move scoring for ordering.
    Faster version with minimal overhead.
    """
    score = 0
    
    # 1. TT move (highest priority)
    if hash_move and move == hash_move:
        return 10000000
    
    # 2. Captures (MVV-LVA)
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        if victim and attacker:
            score = 1000000 + PIECE_VALUES[victim.piece_type] - PIECE_VALUES[attacker.piece_type]
    
    # 3. Killer moves
    if move in info.killers.get(ply, []):
        score += 900000
    
    # 4. History heuristic
    move_key = (move.from_square, move.to_square)
    score += info.history.get(move_key, 0)
    
    # 5. Promotions
    if move.promotion:
        score += 800000
    
    # 6. Checks (moderate bonus)
    board.push(move)
    if board.is_check():
        score += 500000
    board.pop()
    
    return score


def order_moves_fast(board, moves, info, ply, hash_move):
    """
    OPTIMIZED move ordering.
    Sort moves by score for better pruning.
    """
    scored_moves = []
    for move in moves:
        score = score_move_fast(board, move, info, ply, hash_move)
        scored_moves.append((score, move))
    
    # Sort descending by score
    scored_moves.sort(reverse=True, key=lambda x: x[0])
    
    return [move for score, move in scored_moves]


def quiescence_search_fast(board, alpha, beta, info, ply):
    """
    OPTIMIZED quiescence search.
    Only search captures to avoid horizon effect.
    """
    info.nodes += 1
    
    if ply >= MAX_PLY or info.check_time():
        return 0
    
    # Stand pat score
    stand_pat = evaluate_fast(board)
    
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat
    
    # Generate and order captures only
    captures = [m for m in board.legal_moves if board.is_capture(m)]
    
    # Delta pruning - skip if material gain can't improve alpha
    if not captures or (stand_pat + 900 < alpha):  # 900 = queen value
        return stand_pat
    
    # Order captures by SEE
    captures.sort(key=lambda m: see(board, m), reverse=True)
    
    for move in captures:
        # SEE pruning - skip bad captures
        if see(board, move) < -50:
            continue
        
        board.push(move)
        score = -quiescence_search_fast(board, -beta, -alpha, info, ply + 1)
        board.pop()
        
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    
    return alpha


def alpha_beta_fast(board, depth, alpha, beta, info, ply, do_null=True):
    """
    OPTIMIZED Alpha-Beta search.
    Combines best techniques with speed optimizations.
    """
    info.nodes += 1
    
    # Check time and depth limits
    if info.check_time() or ply >= info.max_depth:
        return quiescence_search_fast(board, alpha, beta, info, ply)
    
    # Mate distance pruning
    alpha = max(alpha, -MATE_SCORE + ply)
    beta = min(beta, MATE_SCORE - ply - 1)
    if alpha >= beta:
        return alpha
    
    # Check for draws
    if board.is_fifty_moves() or board.is_repetition(2):
        return 0
    
    # Checkmate and stalemate detection
    if board.is_checkmate():
        return -MATE_SCORE + ply
    if board.is_stalemate():
        return 0
    
    # Quiescence search at leaf nodes
    if depth <= 0:
        return quiescence_search_fast(board, alpha, beta, info, ply)
    
    # Transposition table probe
    zobrist_hash = get_zobrist_hash(board)
    tt_entry = info.tt.probe(zobrist_hash)
    hash_move = None
    
    if tt_entry:
        if tt_entry['depth'] >= depth:
            tt_score = tt_entry['score']
            tt_bound = tt_entry['bound']
            
            if tt_bound == TranspositionTable.EXACT:
                info.tt_hits += 1
                return tt_score
            elif tt_bound == TranspositionTable.LOWER_BOUND:
                alpha = max(alpha, tt_score)
            elif tt_bound == TranspositionTable.UPPER_BOUND:
                beta = min(beta, tt_score)
            
            if alpha >= beta:
                info.tt_hits += 1
                return tt_score
        
        hash_move = tt_entry['best_move']
    
    # Null move pruning
    if (do_null and depth >= 3 and not board.is_check() and 
        evaluate_fast_material_only(board) > beta):
        R = 3 if depth >= 6 else 2
        board.push(chess.Move.null())
        score = -alpha_beta_fast(board, depth - R - 1, -beta, -beta + 1, info, ply + 1, False)
        board.pop()
        
        if score >= beta:
            return beta
    
    # Generate and order moves
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return 0
    
    ordered_moves = order_moves_fast(board, legal_moves, info, ply, hash_move)
    
    # Futility pruning (at low depths)
    if depth <= 2 and not board.is_check():
        static_eval = evaluate_fast(board)
        futility_margin = 200 * depth
        if static_eval + futility_margin < alpha:
            # Only try captures and promotions
            ordered_moves = [m for m in ordered_moves 
                           if board.is_capture(m) or m.promotion]
    
    # Main search loop
    best_score = -INFINITY
    best_move = None
    moves_searched = 0
    
    for move in ordered_moves:
        board.push(move)
        
        # Late move reduction (LMR)
        if moves_searched >= 4 and depth >= 3 and not board.is_check():
            # Reduce depth for late moves
            reduction = 1 if moves_searched >= 8 else 0
            score = -alpha_beta_fast(board, depth - 1 - reduction, -beta, -alpha, 
                                    info, ply + 1, True)
            
            # Re-search if score improved
            if score > alpha and reduction > 0:
                score = -alpha_beta_fast(board, depth - 1, -beta, -alpha, 
                                        info, ply + 1, True)
        else:
            # Full depth search
            score = -alpha_beta_fast(board, depth - 1, -beta, -alpha, 
                                    info, ply + 1, True)
        
        board.pop()
        moves_searched += 1
        
        # Update best move
        if score > best_score:
            best_score = score
            best_move = move
        
        # Alpha-beta cutoff
        if best_score >= beta:
            info.cutoffs += 1
            
            # Update killer moves
            if not board.is_capture(move):
                killers = info.killers.get(ply, [])
                if move not in killers:
                    killers.insert(0, move)
                    if len(killers) > 2:
                        killers.pop()
                    info.killers[ply] = killers
            
            # Update history
            move_key = (move.from_square, move.to_square)
            info.history[move_key] += depth * depth
            
            # Store in TT
            info.tt.store(zobrist_hash, depth, beta, 
                         TranspositionTable.LOWER_BOUND, best_move)
            return beta
        
        if best_score > alpha:
            alpha = best_score
    
    # Store in TT
    bound = TranspositionTable.EXACT if best_score > alpha else TranspositionTable.UPPER_BOUND
    info.tt.store(zobrist_hash, depth, best_score, bound, best_move)
    
    return best_score


def get_best_move(board, depth=5, max_time=None):
    """
    Get best move using iterative deepening.
    
    Args:
        board: chess.Board instance
        depth: Maximum search depth
        max_time: Maximum search time in seconds
    
    Returns:
        best_move: Best move found
        info: Search info dictionary
    """
    info = SearchInfo(max_time=max_time, max_depth=depth)
    best_move = None
    best_score = -INFINITY
    
    # Iterative deepening
    for current_depth in range(1, depth + 1):
        if info.check_time():
            break
        
        alpha = -INFINITY
        beta = INFINITY
        legal_moves = list(board.legal_moves)
        
        # Get hash move from previous iteration
        zobrist_hash = get_zobrist_hash(board)
        tt_entry = info.tt.probe(zobrist_hash)
        hash_move = tt_entry['best_move'] if tt_entry else None
        
        # Order moves
        ordered_moves = order_moves_fast(board, legal_moves, info, 0, hash_move)
        
        current_best_move = None
        current_best_score = -INFINITY
        
        for move in ordered_moves:
            board.push(move)
            score = -alpha_beta_fast(board, current_depth - 1, -beta, -alpha, info, 1, True)
            board.pop()
            
            if info.check_time():
                break
            
            if score > current_best_score:
                current_best_score = score
                current_best_move = move
            
            if score > alpha:
                alpha = score
        
        # Update best move for this depth
        if not info.check_time() and current_best_move:
            best_move = current_best_move
            best_score = current_best_score
            
            # Store in TT
            info.tt.store(zobrist_hash, current_depth, best_score, 
                         TranspositionTable.EXACT, best_move)
    
    # Return result
    elapsed = info.elapsed_time()
    nps = int(info.nodes / elapsed) if elapsed > 0 else 0
    
    result = {
        'move': best_move,
        'score': best_score,
        'depth': depth,
        'nodes': info.nodes,
        'time': elapsed,
        'nps': nps,
        'tt_stats': info.tt.get_stats()
    }
    
    return best_move, result
