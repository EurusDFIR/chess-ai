"""
Improved Chess GUI với tất cả features:
1. Threading cho AI (không bị đơ)
2. Timer hoạt động đúng
3. Highlight nước vừa đi
4. Hiện quân đã ăn
5. Hiện điểm material
"""
import os
import sys
import threading
import queue
import time

import chess
import pygame
import pygame_gui

from src.ai.minimax_optimized import get_best_move
from src.ai.opening_book import OpeningBook
from pygame_gui.core import ObjectID

# Add path to import from the root directory
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Opening book setup
BOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "opening_bin", "gm2600.bin")
BOOK_PATH = os.path.normpath(BOOK_PATH)

if os.path.exists(BOOK_PATH):
    opening_book = OpeningBook(BOOK_PATH)
else:
    print(f"⚠️  Warning: Opening book not found at {BOOK_PATH}")
    opening_book = None

# Global variables for AI threading
ai_move_queue = queue.Queue()
ai_thinking = False
ai_thread = None

# Game state
last_move = None
captured_white = []  # Quân trắng bị ăn
captured_black = []  # Quân đen bị ăn

# Material values
PIECE_VALUES = {
    'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0
}

def calculate_material(board):
    """Tính chênh lệch material (dương = trắng hơn, âm = đen hơn)"""
    white_material = 0
    black_material = 0
    
    for piece in board.piece_map().values():
        value = PIECE_VALUES.get(piece.symbol().upper(), 0)
        if piece.color == chess.WHITE:
            white_material += value
        else:
            black_material += value
    
    return white_material - black_material

def track_captured_pieces(move, board):
    """Track quân bị ăn từ move - PHẢI GỌI SAU KHI PUSH MOVE"""
    global captured_white, captured_black
    
    # Kiểm tra xem có phải capture move không
    # Vì đã push move rồi, ta phải check move history
    if len(board.move_stack) > 0:
        # Move vừa push có captured piece không?
        # Dùng chess library's built-in check
        try:
            # Undo để check piece tại to_square trước khi move
            board.pop()
            captured_piece = board.piece_at(move.to_square)
            board.push(move)  # Push lại
            
            if captured_piece:
                if captured_piece.color == chess.WHITE:
                    captured_white.append(captured_piece.symbol().upper())
                else:
                    captured_black.append(captured_piece.symbol().upper())
        except:
            pass  # Nếu có lỗi, bỏ qua

def ai_move_threaded(board_copy, depth=4, time_limit=5.0):
    """Chạy AI trong background thread"""
    global ai_thinking
    ai_thinking = True
    
    def run_ai():
        try:
            # Try opening book first
            move = None
            if opening_book is not None:
                try:
                    move = opening_book.get_move(board_copy)
                    if move:
                        print(f"📖 Opening book: {move}")
                except Exception as e:
                    print(f"⚠️  Opening book error: {e}")
            
            # Nếu không có book move, dùng AI
            if move is None:
                print("🤖 AI thinking...")
                start = time.time()
                move = get_best_move(board_copy, depth=depth, time_limit=time_limit)
                elapsed = time.time() - start
                print(f"✅ AI chose: {move} ({elapsed:.2f}s)")
            
            ai_move_queue.put(move)
        except Exception as e:
            print(f"❌ AI error: {e}")
            ai_move_queue.put(None)
        finally:
            # ai_thinking sẽ được set False trong main loop
            pass
    
    thread = threading.Thread(target=run_ai, daemon=True)
    thread.start()
    return thread

def draw_last_move_highlight(screen, last_move):
    """Tô màu ô from/to với style đẹp hơn, giống Lichess"""
    if last_move is None:
        return
    
    # Lichess-style highlight: màu vàng/xanh nhạt với border
    overlay = pygame.Surface((64, 64), pygame.SRCALPHA)
    
    # From square - màu xanh nhạt
    from_row = 7 - (last_move.from_square // 8)
    from_col = last_move.from_square % 8
    
    # Fill với màu nhạt
    pygame.draw.rect(overlay, (155, 199, 0, 100), (0, 0, 64, 64))
    screen.blit(overlay, (from_col * 64, from_row * 64))
    
    # Border đậm hơn
    pygame.draw.rect(screen, (155, 199, 0, 180), 
                    (from_col * 64, from_row * 64, 64, 64), width=3)
    
    # To square - màu vàng đậm hơn
    overlay.fill((0, 0, 0, 0))  # Clear
    pygame.draw.rect(overlay, (155, 199, 0, 150), (0, 0, 64, 64))
    
    to_row = 7 - (last_move.to_square // 8)
    to_col = last_move.to_square % 8
    screen.blit(overlay, (to_col * 64, to_row * 64))
    
    # Border đậm hơn cho to square
    pygame.draw.rect(screen, (155, 199, 0, 220), 
                    (to_col * 64, to_row * 64, 64, 64), width=4)
    
    # Subtle glow effect ở to square
    glow_surf = pygame.Surface((70, 70), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf, (255, 255, 100, 30), (0, 0, 70, 70), border_radius=35)
    screen.blit(glow_surf, (to_col * 64 - 3, to_row * 64 - 3))

def draw_captured_pieces(screen, captured_white_list, captured_black_list, piece_images):
    """Vẽ quân đã ăn đẹp hơn, giống Lichess"""
    # Panel bên phải với background đẹp
    panel_x = 535
    white_y = 60
    black_y = 380
    
    # Background panels với shadow effect
    panel_width = 250
    panel_height = 100
    
    # Shadow
    shadow_surface = pygame.Surface((panel_width + 4, panel_height + 4), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 40), (0, 0, panel_width + 4, panel_height + 4), border_radius=8)
    screen.blit(shadow_surface, (panel_x - 2, white_y - 2))
    screen.blit(shadow_surface, (panel_x - 2, black_y - 2))
    
    # Background với gradient effect (fake gradient bằng nhiều rectangles)
    for i in range(panel_height):
        alpha = 180 + int(i * 0.3)
        color = (30, 35, 40, min(alpha, 220))
        surf = pygame.Surface((panel_width, 1), pygame.SRCALPHA)
        surf.fill(color)
        screen.blit(surf, (panel_x, white_y + i))
        screen.blit(surf, (panel_x, black_y + i))
    
    # Border với accent color
    pygame.draw.rect(screen, (70, 130, 180, 200), (panel_x, white_y, panel_width, panel_height), width=2, border_radius=8)
    pygame.draw.rect(screen, (70, 130, 180, 200), (panel_x, black_y, panel_width, panel_height), width=2, border_radius=8)
    
    # Title với icon
    title_font = pygame.font.Font(None, 22)
    white_title = title_font.render("⚔ Captured (Black)", True, (220, 220, 220))
    black_title = title_font.render("⚔ Captured (White)", True, (200, 200, 200))
    screen.blit(white_title, (panel_x + 10, white_y + 8))
    screen.blit(black_title, (panel_x + 10, black_y + 8))
    
    # Vẽ icons quân với spacing đẹp hơn
    piece_size = 28
    spacing = 32
    start_y_offset = 35
    
    # Quân trắng bị ăn
    for i, piece_symbol in enumerate(captured_white_list):
        if f'w{piece_symbol.lower()}' in piece_images:
            img = pygame.transform.scale(piece_images[f'w{piece_symbol.lower()}'], (piece_size, piece_size))
            x = panel_x + 10 + (i % 7) * spacing
            y = white_y + start_y_offset + (i // 7) * spacing
            
            # Subtle glow effect
            glow_surf = pygame.Surface((piece_size + 4, piece_size + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 255, 255, 30), (piece_size // 2 + 2, piece_size // 2 + 2), piece_size // 2 + 2)
            screen.blit(glow_surf, (x - 2, y - 2))
            
            screen.blit(img, (x, y))
    
    # Quân đen bị ăn
    for i, piece_symbol in enumerate(captured_black_list):
        if f'b{piece_symbol.lower()}' in piece_images:
            img = pygame.transform.scale(piece_images[f'b{piece_symbol.lower()}'], (piece_size, piece_size))
            x = panel_x + 10 + (i % 7) * spacing
            y = black_y + start_y_offset + (i // 7) * spacing
            
            # Subtle glow effect
            glow_surf = pygame.Surface((piece_size + 4, piece_size + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 255, 255, 30), (piece_size // 2 + 2, piece_size // 2 + 2), piece_size // 2 + 2)
            screen.blit(glow_surf, (x - 2, y - 2))
            
            screen.blit(img, (x, y))

def draw_material_count(screen, board):
    """Vẽ material advantage đẹp hơn, như Lichess"""
    diff = calculate_material(board)
    
    # Position - góc dưới bên phải panel
    x = 600
    y = 300
    
    # Background card
    card_width = 150
    card_height = 70
    
    # Shadow
    shadow_surface = pygame.Surface((card_width + 4, card_height + 4), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 50), (0, 0, card_width + 4, card_height + 4), border_radius=10)
    screen.blit(shadow_surface, (x - 2, y - 2))
    
    # Background gradient
    for i in range(card_height):
        alpha = 200 + int(i * 0.3)
        if diff > 0:
            color = (240, 250, 255, min(alpha, 230))  # Light blue cho white advantage
        elif diff < 0:
            color = (50, 55, 60, min(alpha, 230))  # Dark cho black advantage
        else:
            color = (120, 130, 140, min(alpha, 230))  # Gray cho equal
        surf = pygame.Surface((card_width, 1), pygame.SRCALPHA)
        surf.fill(color)
        screen.blit(surf, (x, y + i))
    
    # Border
    border_color = (100, 180, 255) if diff > 0 else (180, 100, 100) if diff < 0 else (150, 150, 150)
    pygame.draw.rect(screen, (*border_color, 200), (x, y, card_width, card_height), width=2, border_radius=10)
    
    # Title
    font_small = pygame.font.Font(None, 20)
    title = font_small.render("Material", True, (180, 180, 180))
    screen.blit(title, (x + 10, y + 8))
    
    # Value với màu và size đẹp
    font_large = pygame.font.Font(None, 48)
    if diff > 0:
        text = f"+{diff}"
        color = (100, 200, 100)  # Green
        icon = "↑"
    elif diff < 0:
        text = f"{diff}"
        color = (220, 100, 100)  # Red
        icon = "↓"
    else:
        text = "="
        color = (200, 200, 100)  # Yellow
        icon = "="
    
    value = font_large.render(text, True, color)
    value_rect = value.get_rect(center=(x + card_width // 2, y + 45))
    screen.blit(value, value_rect)
    
    # Icon indicator
    icon_font = pygame.font.Font(None, 32)
    icon_text = icon_font.render(icon, True, color)
    screen.blit(icon_text, (x + card_width - 30, y + 35))

def draw_ai_thinking_indicator(screen, width, height):
    """Hiển thị thinking indicator nhỏ gọn như Lichess"""
    if not ai_thinking:
        return
    
    # Small indicator ở góc trên bên phải (giống Lichess)
    indicator_width = 180
    indicator_height = 40
    x = width - indicator_width - 20
    y = 20
    
    # Background với bo góc đẹp
    bg_surface = pygame.Surface((indicator_width, indicator_height), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, (40, 40, 40, 220), (0, 0, indicator_width, indicator_height), border_radius=8)
    
    # Border nhẹ
    pygame.draw.rect(bg_surface, (100, 100, 100, 150), (0, 0, indicator_width, indicator_height), width=2, border_radius=8)
    
    screen.blit(bg_surface, (x, y))
    
    # Animated spinner (loading circle)
    spinner_center = (x + 25, y + 20)
    spinner_radius = 12
    angle = (time.time() * 3) % (2 * 3.14159)
    
    # Vẽ arc animation
    for i in range(3):
        start_angle = angle + i * 2.0944  # 120 degrees apart
        arc_rect = pygame.Rect(spinner_center[0] - spinner_radius, 
                               spinner_center[1] - spinner_radius,
                               spinner_radius * 2, spinner_radius * 2)
        pygame.draw.arc(screen, (100, 180, 255), arc_rect, start_angle, start_angle + 1.5, 3)
    
    # Text nhỏ gọn
    font = pygame.font.Font(None, 24)
    # Text nhỏ gọn
    font = pygame.font.Font(None, 24)
    text = font.render("AI thinking", True, (200, 200, 200))
    screen.blit(text, (x + 45, y + 12))

# Export key functions needed by original main_window.py
__all__ = [
    'ai_move_threaded',
    'ai_move_queue',
    'ai_thinking',
    'last_move',
    'captured_white',
    'captured_black',
    'track_captured_pieces',
    'calculate_material',
    'draw_last_move_highlight',
    'draw_captured_pieces',
    'draw_material_count',
    'draw_ai_thinking_indicator'
]

print("✅ GUI improvements module loaded!")
print("Features: Threading, Timer fix, Highlight, Captured pieces, Material count")
