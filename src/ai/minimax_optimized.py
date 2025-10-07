# src/ai/minimax_optimized.py
"""
Optimized Chess AI with advanced techniques:
- Iterative Deepening
- Late Move Reduction (LMR)
- Null Move Pruning
- Futility Pruning
- Delta Pruning
- Principal Variation Search (PVS)
- Advanced Move Ordering
- Persistent Transposition Table
"""

import chess
import time
import random
import math
from collections import defaultdict
from src.ai.evaluation_optimized import evaluate_incremental, EvaluationCache

# Constants
MATE_SCORE = 100000
MAX_PLY = 100
INFINITY = float('inf')

# Zobrist Hashing
zobrist_table = {}
random.seed(42)

for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]:
    for color in [chess.WHITE, chess.BLACK]:
        for square in chess.SQUARES:
            zobrist_table[(piece_type, color, square)] = random.randint(0, 2**64 - 1)

zobrist_table['turn'] = random.randint(0, 2**64 - 1)
for color in [chess.WHITE, chess.BLACK]:
    for castle_type in ['K', 'Q']:
        zobrist_table[('castling', color, castle_type)] = random.randint(0, 2**64 - 1)
for file in range(8):
    zobrist_table[('en_passant', file)] = random.randint(0, 2**64 - 1)


def get_zobrist_hash(board):
    """Calculate Zobrist hash for position."""
    hash_value = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            hash_value ^= zobrist_table[(piece.piece_type, piece.color, square)]
    
    if board.turn == chess.WHITE:
        hash_value ^= zobrist_table['turn']
    
    for color in [chess.WHITE, chess.BLACK]:
        if board.has_kingside_castling_rights(color):
            hash_value ^= zobrist_table[('castling', color, 'K')]
        if board.has_queenside_castling_rights(color):
            hash_value ^= zobrist_table[('castling', color, 'Q')]
    
    if board.ep_square is not None:
        hash_value ^= zobrist_table[('en_passant', chess.square_file(board.ep_square))]
    
    return hash_value


class TranspositionTable:
    """Persistent transposition table with aging."""
    
    EXACT = 0
    LOWER_BOUND = 1
    UPPER_BOUND = 2
    
    def __init__(self, size_mb=256):
        # Estimate: each entry ~50 bytes, so 1MB ≈ 20K entries
        self.max_entries = (size_mb * 1024 * 1024) // 50
        self.table = {}
        self.current_age = 0
    
    def clear(self):
        """Clear the table."""
        self.table.clear()
        self.current_age = 0
    
    def new_search(self):
        """Increment age for new search."""
        self.current_age += 1
        # Clean old entries if table is too large
        if len(self.table) > self.max_entries:
            self._clean_old_entries()
    
    def _clean_old_entries(self):
        """Remove old entries to free space."""
        # Remove entries older than 8 searches
        old_keys = [k for k, v in self.table.items() if self.current_age - v['age'] > 8]
        for key in old_keys[:len(old_keys)//2]:  # Remove half of old entries
            del self.table[key]
    
    def store(self, zobrist_hash, depth, score, bound_type, best_move=None):
        """Store position in transposition table."""
        self.table[zobrist_hash] = {
            'depth': depth,
            'score': score,
            'bound': bound_type,
            'best_move': best_move,
            'age': self.current_age
        }
    
    def probe(self, zobrist_hash):
        """Probe transposition table."""
        return self.table.get(zobrist_hash)


class SearchInfo:
    """Information for search management."""
    
    def __init__(self, time_limit=10.0):
        self.start_time = time.time()
        self.time_limit = time_limit
        self.nodes = 0
        self.tt = TranspositionTable(256)
        self.killer_moves = [[None, None] for _ in range(MAX_PLY)]
        self.history = defaultdict(int)
        self.countermoves = {}  # Countermove heuristic
        self.pv_table = [[None] * MAX_PLY for _ in range(MAX_PLY)]
        self.pv_length = [0] * MAX_PLY
        self.stopped = False
        self.last_move = None  # Track last move for countermove
    
    def check_time(self):
        """Check if we should stop search."""
        if self.nodes % 2048 == 0:  # Check every 2048 nodes
            if time.time() - self.start_time > self.time_limit:
                self.stopped = True
        return self.stopped
    
    def update_pv(self, ply, move):
        """Update principal variation."""
        self.pv_table[ply][ply] = move
        for next_ply in range(ply + 1, self.pv_length[ply + 1]):
            self.pv_table[ply][next_ply] = self.pv_table[ply + 1][next_ply]
        self.pv_length[ply] = self.pv_length[ply + 1]
    
    def update_countermove(self, prev_move, current_move):
        """Update countermove table."""
        if prev_move:
            self.countermoves[prev_move] = current_move


# Piece values for SEE
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}


def see(board, move):
    """Static Exchange Evaluation - more accurate implementation."""
    if not board.is_capture(move):
        return 0
    
    from_square = move.from_square
    to_square = move.to_square
    
    # Get piece values
    attacker = board.piece_at(from_square)
    victim = board.piece_at(to_square)
    
    if not attacker or not victim:
        return 0
    
    # Initial gain from capture
    gain = [PIECE_VALUES[victim.piece_type]]
    
    # Simulate exchange
    board.push(move)
    
    # Get all attackers to the target square
    defending_side = not attacker.color
    attackers = list(board.attackers(defending_side, to_square))
    
    if not attackers:
        # No defenders, capture is winning
        board.pop()
        return gain[0]
    
    # Find least valuable attacker
    min_attacker_value = float('inf')
    next_attacker_square = None
    
    for sq in attackers:
        piece = board.piece_at(sq)
        if piece and PIECE_VALUES[piece.piece_type] < min_attacker_value:
            min_attacker_value = PIECE_VALUES[piece.piece_type]
            next_attacker_square = sq
    
    board.pop()
    
    if next_attacker_square is None:
        return gain[0]
    
    # Simple evaluation: gain - attacker_value if recapture exists
    gain.append(-PIECE_VALUES[attacker.piece_type])
    
    return sum(gain)


def score_move(board, move, info, ply, hash_move):
    """Score move for ordering with enhanced heuristics."""
    score = 0
    
    # 1. Hash move (from TT) - highest priority
    if move == hash_move:
        return 100000
    
    # 2. Winning captures (MVV-LVA with SEE)
    if board.is_capture(move):
        see_score = see(board, move)
        if see_score > 0:
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            if victim and attacker:
                # MVV-LVA: Most Valuable Victim - Least Valuable Attacker
                score = 10000 + PIECE_VALUES[victim.piece_type] - PIECE_VALUES[attacker.piece_type] // 10
        elif see_score == 0:
            score = 9000  # Equal captures
        else:
            score = 100  # Losing captures - search last
    
    # 3. Promotions
    if move.promotion:
        score = 8000 + PIECE_VALUES.get(move.promotion, 0)
    
    # 4. Killer moves - two killer slots
    if move == info.killer_moves[ply][0]:
        return 7500  # First killer
    elif move == info.killer_moves[ply][1]:
        return 7400  # Second killer
    
    # 5. Countermove heuristic
    if info.last_move and info.countermoves.get(info.last_move) == move:
        score = 7000
    
    # 6. History heuristic (capped at 5000)
    history_score = info.history.get((move.from_square, move.to_square), 0)
    score += min(history_score, 5000)
    
    # 7. Checks bonus
    if board.gives_check(move):
        score += 500
    
    # 8. Castling bonus
    if board.is_castling(move):
        score += 300
    
    return score


def order_moves(board, moves, info, ply, hash_move=None):
    """Order moves for better alpha-beta pruning."""
    scored_moves = [(score_move(board, move, info, ply, hash_move), move) for move in moves]
    scored_moves.sort(reverse=True, key=lambda x: x[0])
    return [move for _, move in scored_moves]


def quiescence_search(board, alpha, beta, info, ply):
    """Quiescence search to avoid horizon effect."""
    info.nodes += 1
    
    if info.check_time():
        return 0
    
    # Stand pat score
    stand_pat = evaluate_incremental(board)
    
    if stand_pat >= beta:
        return beta
    
    # Delta pruning
    BIG_DELTA = 900  # Queen value
    if stand_pat < alpha - BIG_DELTA:
        return alpha
    
    if alpha < stand_pat:
        alpha = stand_pat
    
    # Only search captures and promotions
    moves = [m for m in board.legal_moves if board.is_capture(m) or m.promotion]
    
    # Order captures by SEE
    moves = sorted(moves, key=lambda m: see(board, m), reverse=True)
    
    for move in moves:
        # Delta pruning for captures
        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            if victim and stand_pat + PIECE_VALUES[victim.piece_type] + 200 < alpha:
                continue
        
        # Skip losing captures in quiescence
        if see(board, move) < 0:
            continue
        
        board.push(move)
        score = -quiescence_search(board, -beta, -alpha, info, ply + 1)
        board.pop()
        
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    
    return alpha


def null_move_pruning(board, depth, beta, info, ply):
    """Null move pruning - skip turn to check if position is too good."""
    R = 3 if depth > 6 else 2  # Adaptive reduction
    
    if depth > R and not board.is_check():
        # Don't do null move in endgame (zugzwang risk)
        if len(board.piece_map()) > 10:
            board.push(chess.Move.null())
            score = -alpha_beta(board, depth - 1 - R, -beta, -beta + 1, info, ply + 1, False)
            board.pop()
            
            if score >= beta:
                return score
    
    return None


def futility_pruning_margin(depth):
    """Get futility pruning margin for depth."""
    margins = [0, 300, 500, 700]
    if depth < len(margins):
        return margins[depth]
    return 1000


def alpha_beta(board, depth, alpha, beta, info, ply, do_null=True):
    """Alpha-beta search with pruning techniques."""
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
    if board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
        return 0
    
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
    
    # Null move pruning
    if do_null:
        null_score = null_move_pruning(board, depth, beta, info, ply)
        if null_score is not None and null_score >= beta:
            return beta
    
    # Razoring - if eval is very low, go straight to quiescence
    if depth <= 3 and not in_check and abs(alpha) < MATE_SCORE - 100:
        eval_score = evaluate_incremental(board)
        razor_margin = [0, 300, 400, 600][depth]
        
        if eval_score + razor_margin < alpha:
            # Do quiescence search to verify
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
            return -MATE_SCORE + ply  # Checkmate
        return 0  # Stalemate
    
    ordered_moves = order_moves(board, legal_moves, info, ply, hash_move)
    
    best_score = -INFINITY
    best_move = None
    bound_type = TranspositionTable.UPPER_BOUND
    moves_searched = 0
    
    for move_num, move in enumerate(ordered_moves):
        # Futility pruning - skip quiet moves in low depth
        if futility and moves_searched > 0 and not board.is_capture(move) and not move.promotion:
            continue
        
        # Save previous last_move
        prev_last_move = info.last_move
        info.last_move = move
        
        board.push(move)
        
        # Late Move Reduction (LMR)
        reduction = 0
        if (depth >= 3 and moves_searched >= 4 and 
            not in_check and not board.is_check() and
            not board.is_capture(move) and not move.promotion):
            # LMR formula: reduction = log(depth) * log(move_num) / 2.5
            reduction = int(math.log(depth) * math.log(move_num + 1) / 2.5)
            reduction = min(reduction, depth - 1)
        
        # Principal Variation Search (PVS)
        if moves_searched == 0:
            # Full window search for first move
            score = -alpha_beta(board, depth - 1, -beta, -alpha, info, ply + 1, True)
        else:
            # Null window search
            score = -alpha_beta(board, depth - 1 - reduction, -alpha - 1, -alpha, info, ply + 1, True)
            
            # Re-search if necessary
            if score > alpha and reduction > 0:
                score = -alpha_beta(board, depth - 1, -alpha - 1, -alpha, info, ply + 1, True)
            
            if score > alpha and score < beta:
                score = -alpha_beta(board, depth - 1, -beta, -alpha, info, ply + 1, True)
        
        board.pop()
        
        # Restore last_move
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
                    # Beta cutoff
                    bound_type = TranspositionTable.LOWER_BOUND
                    
                    # Update killer moves and countermoves for quiet moves
                    if not board.is_capture(move):
                        # Update killer moves
                        if info.killer_moves[ply][0] != move:
                            info.killer_moves[ply][1] = info.killer_moves[ply][0]
                            info.killer_moves[ply][0] = move
                        
                        # Update history heuristic with bonus
                        bonus = depth * depth
                        info.history[(move.from_square, move.to_square)] += bonus
                        
                        # Cap history values to prevent overflow
                        if info.history[(move.from_square, move.to_square)] > 10000:
                            # Age all history values
                            for key in info.history:
                                info.history[key] //= 2
                        
                        # Update countermove
                        info.update_countermove(info.last_move, move)
                    
                    break
    
    # Store in transposition table
    info.tt.store(zobrist_hash, depth, best_score, bound_type, best_move)
    
    return best_score


def iterative_deepening(board, max_depth, time_limit=10.0):
    """Iterative deepening with aspiration windows."""
    info = SearchInfo(time_limit)
    info.tt.new_search()
    
    best_move = None
    best_score = 0
    
    print(f"\n{'Depth':<8} {'Score':<10} {'Nodes':<12} {'Time':<10} {'PV':<40}")
    print("-" * 80)
    
    for depth in range(1, max_depth + 1):
        if info.stopped:
            break
        
        # Aspiration window with dynamic widening
        if depth > 4:
            window = 25  # Start with narrow window
            alpha = best_score - window
            beta = best_score + window
        else:
            alpha = -INFINITY
            beta = INFINITY
        
        # Search with aspiration window and progressive widening
        research_count = 0
        while True:
            score = alpha_beta(board, depth, alpha, beta, info, 0, True)
            
            # Check if we need to re-search
            if score <= alpha:
                # Fail low - widen window down
                alpha = max(alpha - window * (2 ** research_count), -INFINITY)
                research_count += 1
            elif score >= beta:
                # Fail high - widen window up
                beta = min(beta + window * (2 ** research_count), INFINITY)
                research_count += 1
            else:
                # Success
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
        
        # Stop if mate found
        if abs(best_score) > MATE_SCORE - 100:
            break
        
        # Early exit if running out of time (use 80% of time for current depth)
        if elapsed > time_limit * 0.8:
            break
    
    print("-" * 80)
    print(f"Best move: {best_move} | Score: {best_score} | Nodes: {info.nodes}\n")
    
    return best_move


def get_best_move(board, depth=6, time_limit=10.0):
    """Get best move using iterative deepening."""
    return iterative_deepening(board, depth, time_limit)
