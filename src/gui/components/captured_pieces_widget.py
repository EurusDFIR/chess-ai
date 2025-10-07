"""
Captured Pieces Widget - Hiển thị quân bị ăn và material difference
"""
import pygame
import chess


class CapturedPiecesWidget:
    """Widget hiển thị quân đã bị ăn"""
    
    PIECE_VALUES = {
        'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0
    }
    
    def __init__(self, screen, piece_images, x, y, width=180):
        self.screen = screen
        self.piece_images = piece_images
        self.x = x
        self.y = y
        self.width = width
        
        self.captured_white = []  # Quân trắng bị ăn
        self.captured_black = []  # Quân đen bị ăn
        
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 20)
        
        self.visible = True  # Add visibility flag
    
    def track_capture(self, move, board):
        """Track quân bị ăn từ move - GỌI TRƯỚC KHI PUSH"""
        # Kiểm tra xem có phải capture không (TRƯỚC khi push move)
        captured_piece = board.piece_at(move.to_square)
        
        if captured_piece:
            # Có quân ở ô đích = capture move
            if captured_piece.color == chess.WHITE:
                self.captured_white.append(captured_piece.symbol().upper())
                print(f"⚪ Captured white {captured_piece.symbol()}")
            else:
                self.captured_black.append(captured_piece.symbol().upper())
                print(f"⚫ Captured black {captured_piece.symbol()}")
    
    def draw(self):
        """Vẽ captured pieces"""
        if not self.visible:  # Skip if hidden
            return
            
        # Vẽ tiêu đề
        title = self.title_font.render("Captured", True, (200, 200, 200))
        self.screen.blit(title, (self.x, self.y))
        
        # Tính material difference
        white_material = sum(self.PIECE_VALUES.get(p, 0) for p in self.captured_black)
        black_material = sum(self.PIECE_VALUES.get(p, 0) for p in self.captured_white)
        material_diff = white_material - black_material
        
        y_offset = 30
        
        # Vẽ captured black pieces (white đã ăn)
        self._draw_captured_side(self.captured_black, self.y + y_offset, 
                                material_diff if material_diff > 0 else 0, 'w')
        
        y_offset += 50
        
        # Vẽ captured white pieces (black đã ăn)
        self._draw_captured_side(self.captured_white, self.y + y_offset, 
                                -material_diff if material_diff < 0 else 0, 'b')
    
    def _draw_captured_side(self, pieces, y, advantage, color_prefix):
        """Vẽ quân bị ăn cho một bên"""
        x_offset = 0
        piece_size = 30
        
        for piece_symbol in pieces:
            piece_key = f"{color_prefix}{piece_symbol.lower()}"
            if piece_key in self.piece_images:
                img = self.piece_images[piece_key]
                # Scale down image
                scaled_img = pygame.transform.scale(img, (piece_size, piece_size))
                self.screen.blit(scaled_img, (self.x + x_offset, y))
                x_offset += piece_size + 2
        
        # Hiển thị material advantage
        if advantage > 0:
            adv_text = self.font.render(f"+{int(advantage)}", True, (100, 255, 100))
            self.screen.blit(adv_text, (self.x + x_offset + 10, y + 5))
    
    def reset(self):
        """Reset captured pieces"""
        self.captured_white.clear()
        self.captured_black.clear()
    
    def hide(self):
        """Hide the widget"""
        self.visible = False
    
    def show(self):
        """Show the widget"""
        self.visible = True
