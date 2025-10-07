#!/usr/bin/env python3
"""
Demo script để test GUI improvements
Chạy standalone để xem các features mới hoạt động
"""
import sys
import os
sys.path.insert(0, 'src')

import pygame
import chess
from gui.gui_improvements import (
    draw_last_move_highlight,
    draw_captured_pieces,
    draw_material_count,
    draw_ai_thinking_indicator,
    calculate_material,
    track_captured_pieces,
    captured_white,
    captured_black,
    last_move,
    ai_thinking
)

# Load piece images helper
def load_pieces():
    pieces = {}
    colors = ['w', 'b']
    piece_names = ['P', 'N', 'B', 'R', 'Q', 'K']
    for color in colors:
        for name in piece_names:
            key = f"{color}{name.lower()}"
            path = os.path.join("src", "gui", "assets", "pieces", f"{color}{name}.png")
            try:
                img = pygame.image.load(path).convert_alpha()
                pieces[key] = img
            except pygame.error as e:
                print(f"Warning: Could not load {key}: {e}")
                # Create placeholder
                surf = pygame.Surface((64, 64))
                surf.fill((255, 0, 255))
                pieces[key] = surf
    return pieces

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("GUI Improvements Demo")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    
    # Load pieces
    print("Loading piece images...")
    piece_images = load_pieces()
    
    # Create test board with some moves played
    board = chess.Board()
    
    # Play some moves to create test scenario
    test_moves = [
        chess.Move.from_uci("e2e4"),  # e4
        chess.Move.from_uci("e7e5"),  # e5
        chess.Move.from_uci("g1f3"),  # Nf3
        chess.Move.from_uci("b8c6"),  # Nc6
        chess.Move.from_uci("f1c4"),  # Bc4
        chess.Move.from_uci("g8f6"),  # Nf6
        chess.Move.from_uci("d2d4"),  # d4
        chess.Move.from_uci("e5d4"),  # exd4 (capture!)
    ]
    
    global last_move, captured_white, captured_black, ai_thinking
    
    print("\n" + "="*60)
    print("Applying test moves...")
    print("="*60)
    
    for move in test_moves:
        # Track captures
        track_captured_pieces(board, move)
        board.push(move)
        last_move = move
        print(f"Move: {move.uci()} | Material: {calculate_material(board):+d}")
    
    print(f"\nCaptured white pieces: {captured_white}")
    print(f"Captured black pieces: {captured_black}")
    print(f"Material advantage: {calculate_material(board):+d}")
    
    # Demo mode toggle
    ai_thinking = False
    demo_mode = 0  # 0=normal, 1=AI thinking
    
    print("\n" + "="*60)
    print("DEMO CONTROLS:")
    print("="*60)
    print("SPACE - Toggle AI thinking indicator")
    print("ESC   - Quit")
    print("="*60 + "\n")
    
    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    ai_thinking = not ai_thinking
                    print(f"AI thinking: {ai_thinking}")
        
        # Draw
        screen.fill((48, 46, 43))  # Dark background
        
        # Draw board squares
        for row in range(8):
            for col in range(8):
                color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
                pygame.draw.rect(screen, color, (col * 64, row * 64, 64, 64))
        
        # Draw last move highlight
        draw_last_move_highlight(screen, last_move)
        
        # Draw pieces (simplified - just show some pieces)
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                key = f"{'w' if piece.color == chess.WHITE else 'b'}{piece.symbol().lower()}"
                if key in piece_images:
                    row = 7 - (square // 8)
                    col = square % 8
                    img = pygame.transform.scale(piece_images[key], (64, 64))
                    screen.blit(img, (col * 64, row * 64))
        
        # Draw captured pieces panel
        draw_captured_pieces(screen, piece_images, font)
        
        # Draw material count
        draw_material_count(screen, board, font)
        
        # Draw AI thinking indicator (if active)
        draw_ai_thinking_indicator(screen, font)
        
        # Draw instructions
        small_font = pygame.font.Font(None, 20)
        instructions = [
            "Features Demo:",
            "1. Yellow highlight on last move (e5xd4)",
            "2. Captured pieces on right panel",
            "3. Material count (+/- advantage)",
            "4. Press SPACE for AI thinking overlay",
        ]
        for i, text in enumerate(instructions):
            surf = small_font.render(text, True, (200, 200, 200))
            screen.blit(surf, (520, 500 + i * 20))
        
        pygame.display.flip()
    
    pygame.quit()
    print("\n✅ Demo finished!")

if __name__ == "__main__":
    main()
