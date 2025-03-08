# src/ai/minimax.py
import chess
from collections import defaultdict
from src.ai.evaluation import evaluate, piece_values
import time
import random
import math
from concurrent.futures import ThreadPoolExecutor
import numpy as np

# Khởi tạo bảng Zobrist Hash
zobrist_table = {}
random.seed(42)  # Seed để đảm bảo tính nhất quán khi test

KINGSIDE = True
QUEENSIDE = False
castling_rights_flags = [KINGSIDE, QUEENSIDE]

# Số ngẫu nhiên cho mỗi quân trên mỗi ô vuông
for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]:
    for color in [chess.WHITE, chess.BLACK]:
        for square in chess.SQUARES:
            zobrist_table[(piece_type, color, square)] = random.randint(0, 2**64 - 1)

# Số ngẫu nhiên cho lượt đi (Trắng vs Đen)
zobrist_table['turn'] = random.randint(0, 2**64 - 1)

# Số ngẫu nhiên cho quyền nhập thành
for color in [chess.WHITE, chess.BLACK]:
    for castle_type in ['K', 'Q']:
        zobrist_table[('castling', color, castle_type)] = random.randint(0, 2**64 - 1)

# Số ngẫu nhiên cho ô phong tốt qua đường (en passant)
for file in range(8):
    zobrist_table[('en_passant', file)] = random.randint(0, 2**64 - 1)

# Hàm tính Zobrist Hash cho bàn cờ hiện tại
def get_zobrist_hash(board):
    hash_value = 0

    # Quân cờ trên bàn cờ
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            hash_value ^= zobrist_table[(piece.piece_type, piece.color, square)]

    # Lượt đi hiện tại
    if board.turn == chess.WHITE:
        hash_value ^= zobrist_table['turn']

    # Quyền nhập thành
    for color in [chess.WHITE, chess.BLACK]:
        if board.has_kingside_castling_rights(color):
            hash_value ^= zobrist_table[('castling', color, 'K')]
        if board.has_queenside_castling_rights(color):
            hash_value ^= zobrist_table[('castling', color, 'Q')]

    # Ô phong tốt qua đường (en passant)
    if board.ep_square is not None:
        hash_value ^= zobrist_table[('en_passant', chess.square_file(board.ep_square))]

    return hash_value

# Bảng chuyển đổi
transposition_table = {}

# Placeholder for NNUE evaluation (assuming we have a model)
def nnue_evaluate(board):
    # Placeholder for NNUE evaluation logic
    # Assuming there's a pre-trained model that can be used for evaluation
    return random.randint(-1000, 1000)

def order_moves(board, killer_moves_for_depth, history_heuristic_table):
    """Sắp xếp nước đi theo độ ưu tiên để tối ưu Alpha Beta Pruning."""
    moves = list(board.legal_moves)
    scored_moves = []
    ordered_moves = []

    if killer_moves_for_depth:
        for killer_move in killer_moves_for_depth:
            if killer_move in moves:
                ordered_moves.append(killer_move)
                moves.remove(killer_move)

    ordered_moves.extend(moves)

    for move in ordered_moves:
        score = 0
        history_score = history_heuristic_table[(move.from_square, move.to_square)]
        score += history_score
        if board.gives_check(move):
            score += 1000
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            attacker_piece = board.piece_at(move.from_square)
            if captured_piece and attacker_piece:
                victim_value = piece_values[captured_piece.piece_type]
                attacker_value = piece_values[attacker_piece.piece_type]
                score += 10 * (victim_value - attacker_value / 10.0)
        if move.promotion:
            score += 900
        scored_moves.append((score, move))
    scored_moves.sort(reverse=True, key=lambda x: x[0])
    return [move for (score, move) in scored_moves]

def quiescence_search(board, alpha, beta, transposition_table):
    hash_value = get_zobrist_hash(board)
    if hash_value in transposition_table:
        stored_entry = transposition_table[hash_value]
        if stored_entry['depth'] >= 0:
            return stored_entry['eval']
    stand_pat = evaluate(board)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat
    capture_moves = [move for move in board.legal_moves if board.is_capture(move)]
    ordered_capture_moves = order_moves(board, [], defaultdict(int))
    for move in ordered_capture_moves:
        if board.is_capture(move):
            board.push(move)
            score = -quiescence_search(board, -beta, -alpha, transposition_table)
            board.pop()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
    transposition_table[hash_value] = {'eval': alpha, 'depth': 0, 'type': 'exact'}
    return alpha

def null_move_pruning(board, depth, alpha, beta, transposition_table):
    R = 2
    if depth > R and not board.is_check():
        board.push(chess.Move.null())
        value = -minimax(board, depth - 1 - R, -beta, -beta + 1, False, {}, defaultdict(int), transposition_table)
        board.pop()
        if value >= beta:
            return value
    return None

def minimax(board, depth, alpha, beta, maximizing_player, killer_moves, history_heuristic_table, transposition_table):
    hash_value = get_zobrist_hash(board)
    if hash_value in transposition_table:
        stored_entry = transposition_table[hash_value]
        if stored_entry['depth'] >= depth:
            if stored_entry['type'] == 'exact':
                return stored_entry['eval']
            elif stored_entry['type'] == 'lowerbound':
                alpha = max(alpha, stored_entry['eval'])
            elif stored_entry['type'] == 'upperbound':
                beta = min(beta, stored_entry['eval'])
            if alpha >= beta:
                return stored_entry['eval']

    if depth == 0 or board.is_game_over():
        return quiescence_search(board, alpha, beta, transposition_table)

    null_move_value = null_move_pruning(board, depth, alpha, beta, transposition_table)
    if null_move_value is not None:
        return null_move_value

    if maximizing_player:
        max_eval = -float('inf')
        best_move_local = None
        for move in order_moves(board, killer_moves.get(depth, []), history_heuristic_table):
            board.push(move)
            eval_val = minimax(board, depth - 1, alpha, beta, False, killer_moves, history_heuristic_table, transposition_table)
            board.pop()
            if eval_val > max_eval:
                max_eval = eval_val
                best_move_local = move
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                killer_moves.setdefault(depth, []).append(move)
                break
        eval_to_store = max_eval
        tt_type = 'exact'
        if best_move_local:
            history_heuristic_table[(best_move_local.from_square, best_move_local.to_square)] += math.log(depth + 1)
        transposition_table[hash_value] = {'eval': eval_to_store, 'depth': depth, 'type': tt_type}
        return max_eval
    else:
        min_eval = float('inf')
        best_move_local = None
        for move in order_moves(board, killer_moves.get(depth, []), history_heuristic_table):
            board.push(move)
            eval_val = minimax(board, depth - 1, alpha, beta, True, killer_moves, history_heuristic_table, transposition_table)
            board.pop()
            if eval_val < min_eval:
                min_eval = eval_val
                best_move_local = move
            beta = min(beta, eval_val)
            if beta <= alpha:
                killer_moves.setdefault(depth, []).append(move)
                break
        eval_to_store = min_eval
        tt_type = 'exact'
        if best_move_local:
            history_heuristic_table[(best_move_local.from_square, best_move_local.to_square)] += math.log(depth + 1)
        transposition_table[hash_value] = {'eval': eval_to_store, 'depth': depth, 'type': tt_type}
        return min_eval

def get_best_move(board, depth):
    best_move = None
    max_eval = -float('inf')
    killer_moves = {}
    history_heuristic_table = defaultdict(int)
    global transposition_table
    transposition_table = {}

    with ThreadPoolExecutor() as executor:
        futures = []
        move_results = []
        for move in order_moves(board, killer_moves.get(1, []), history_heuristic_table):
            board.push(move)
            futures.append(executor.submit(minimax, board.copy(), depth - 1, -float('inf'), float('inf'), False, killer_moves, history_heuristic_table, transposition_table))
            board.pop()
            move_results.append(move)

        for i, future in enumerate(futures):
            eval = future.result()
            if eval > max_eval:
                max_eval = eval
                best_move = move_results[i]
    return best_move