import cProfile
import pstats
from src.ai.minimax import get_best_move
import chess

board = chess.Board() # hoặc một bàn cờ cụ thể
depth = 3

profiler = cProfile.Profile()
profiler.enable()
best_move = get_best_move(board, depth) # Chạy hàm cần profile
profiler.disable()

stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats(20) # In ra 20 hàm tốn thời gian nhất