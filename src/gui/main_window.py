# src/gui/main_window.py

import pygame
import chess
import os
import sys

from src.game import board

# Thêm đường dẫn để import từ thư mục gốc
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.ai.minimax import get_best_move
from src.ai.opening_book import OpeningBook

BOOK_PATH = r"R:\TDMU\KIEN_THUC_TDMU\3_year_HK2\TriTueNT\chess-ai\opening_bin\gm2600.bin"  # Update this path to the downloaded book
opening_book = OpeningBook(BOOK_PATH)


# Load hình ảnh quân cờ
def load_pieces():
    pieces = {}
    colors = ['w', 'b']
    piece_names = ['P', 'N', 'B', 'R', 'Q', 'K']
    for color in colors:
        for name in piece_names:
            key = f"{color}{name.lower()}" # Chuyển name thành chữ thường ở đây
            path = os.path.join(os.path.dirname(__file__), "assets", "pieces", f"{color}{name}.png")
            print(f"Đang thử load ảnh từ đường dẫn: {path}")
            try:
                img = pygame.image.load(path).convert_alpha()
                pieces[key] = img
                print(f"Đã load thành công ảnh cho key: {key}")
            except pygame.error as e:
                print(f"Lỗi load ảnh cho key {key} từ đường dẫn {path}: {e}")
    return pieces


def run_gui():
    # Khởi tạo Pygame
    pygame.init()

    # Cấu hình cửa sổ
    WIDTH, HEIGHT = 512, 512
    global screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess AI")

    # Màu sắc
    global LIGHT, DARK
    LIGHT = (235, 235, 208)
    DARK = (119, 149, 86)

    # Khởi tạo bàn cờ
    global board
    board = chess.Board()



    global piece_images
    piece_images = load_pieces()

# Vòng lặp chính
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not board.is_game_over():
                handle_mouse_click(event.pos)

        # AI di chuyển (chơi quân đen)
        # if board.turn == chess.BLACK and not board.is_game_over():
        #     best_move = get_best_move(board, depth=3)
        #     board.push(best_move)

        # Cập nhật giao diện
        draw_board()
        draw_pieces()
        pygame.display.flip()

    pygame.quit()


# Vẽ bàn cờ
def draw_board():  # Ensure LIGHT and DARK are imported from the global scope
    for row in range(8):
        for col in range(8):
            color = LIGHT if (row + col) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, (col * 64, row * 64, 64, 64))


# Vẽ quân cờ
def draw_pieces():
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_symbol = piece.symbol() # Lấy ký hiệu quân cờ (có thể là 'R' hoặc 'r')
            piece_name_lowercase = piece_symbol.lower() # Chuyển ký hiệu quân cờ thành chữ thường
            piece_key = f"{'w' if piece.color else 'b'}{piece_name_lowercase}" # Tạo key với ký hiệu chữ thường
            img = piece_images[piece_key]
            row = 7 - (square // 8)
            col = square % 8
            screen.blit(img, (col * 64, row * 64))

# Xử lý di chuyển của người chơi
selected_square = None


def handle_mouse_click(pos):
    global selected_square
    x, y = pos
    col = x // 64
    row = 7 - (y // 64)
    square = chess.square(col, row)

    if selected_square is None:
        # Chọn quân cờ
        if board.piece_at(square) and board.piece_at(square).color == board.turn:
            selected_square = square
    else:
        # Di chuyển quân cờ
        move = chess.Move(selected_square, square)
        if move in board.legal_moves:
            board.push(move)
        selected_square = None
        # GỌI AI DI CHUYỂN NGAY SAU KHI NGƯỜI CHƠI ĐI THÀNH CÔNG
        if not board.is_game_over() and board.turn == chess.BLACK:  # Kiểm tra game chưa kết thúc và đến lượt đen
            ai_move()  # Gọi hàm ai_move để AI đi

        else:
            selected_square = None  # Hủy chọn nếu nước đi không hợp lệ

# HÀM ĐỂ AI DI CHUYỂN
def ai_move():
    move = opening_book.get_move(board)
    if move is None:  # Nếu không tìm thấy nước đi trong sách khai cuộc, sử dụng thuật toán tìm kiếm
        move = get_best_move(board, depth=2)
    if move is not None:  # Check if move is not None
        board.push(move)
    else:
        print("AI returned None for move. No move pushed.")  # Optional: Log when AI returns None