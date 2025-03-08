# src/test_ai.py

import chess
from src.ai.minimax import get_best_move
from src.gui.main_window import run_gui
def main():
    board = chess.Board()
    print("Bàn cờ hiện tại: ")
    print(board)

    depth = 2
    best_move = get_best_move(board, depth)
    print(f"Nước đi tốt nhất cho AI: {best_move}")

    board.push(best_move)
    print("Bàn cờ sau khi AI thực hiện nước đi:")
    print(board)
if __name__ == "__main__":
    run_gui()