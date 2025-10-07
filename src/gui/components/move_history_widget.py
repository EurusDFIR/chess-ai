"""
Move History Widget - Lichess-style compact design
"""
import pygame
import chess


class MoveHistoryWidget:
    """Widget hiển thị lịch sử các nước đi - Lichess style"""
    
    def __init__(self, screen, x, y, width=180, height=300):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Lichess-style fonts (smaller, cleaner)
        try:
            self.font = pygame.font.SysFont('Segoe UI', 13)
            self.move_num_font = pygame.font.SysFont('Segoe UI', 12)
        except:
            self.font = pygame.font.Font(None, 18)
            self.move_num_font = pygame.font.Font(None, 17)
        
        # Lichess-inspired colors (lighter for better visibility)
        self.bg_color = (48, 46, 44)  # Lighter brown
        self.text_color = (220, 210, 195)  # Brighter tan
        self.move_num_color = (160, 150, 135)  # Lighter muted tan
        self.highlight_color = (90, 85, 70)  # More visible highlight
        self.hover_color = (75, 70, 60)  # Hover effect
        
        self.visible = True
        self.scroll_offset = 0
    
    def draw(self, board):
        """Vẽ move history - Lichess style with proper SAN notation"""
        if not self.visible:
            return
            
        # Background
        pygame.draw.rect(self.screen, self.bg_color, 
                        (self.x, self.y, self.width, self.height))
        
        # Get moves and convert to SAN
        moves = list(board.move_stack)
        if not moves:
            # Show placeholder text
            text = self.font.render("No moves yet", True, self.move_num_color)
            self.screen.blit(text, (self.x + 10, self.y + 10))
            return
        
        # Generate SAN notation
        temp_board = chess.Board()
        san_moves = []
        for move in moves:
            san = temp_board.san(move)
            san_moves.append(san)
            temp_board.push(move)
        
        # Lichess-style compact layout
        y_offset = 8
        line_height = 22
        padding_left = 8
        
        # Column widths
        num_width = 28  # "1."
        move_width = (self.width - num_width - padding_left * 2) // 2
        
        # Calculate visible moves
        max_visible = (self.height - y_offset * 2) // line_height
        start_idx = max(0, len(san_moves) - max_visible * 2)
        
        move_number = start_idx // 2 + 1
        current_y = self.y + y_offset
        
        for i in range(start_idx, len(san_moves), 2):
            # Highlight last move pair
            is_last = (i >= len(san_moves) - 2)
            if is_last:
                pygame.draw.rect(self.screen, self.highlight_color, 
                               (self.x, current_y - 2, self.width, line_height))
            
            # Move number
            num_text = self.move_num_font.render(f"{move_number}.", True, self.move_num_color)
            self.screen.blit(num_text, (self.x + padding_left, current_y + 2))
            
            # White move (SAN)
            white_move = san_moves[i]
            white_text = self.font.render(white_move, True, self.text_color)
            self.screen.blit(white_text, (self.x + padding_left + num_width, current_y))
            
            # Black move (if exists)
            if i + 1 < len(san_moves):
                black_move = san_moves[i + 1]
                black_text = self.font.render(black_move, True, self.text_color)
                self.screen.blit(black_text, 
                               (self.x + padding_left + num_width + move_width, current_y))
            
            current_y += line_height
            move_number += 1
            
            # Stop if out of bounds
            if current_y > self.y + self.height - line_height:
                break
    
    def hide(self):
        """Hide the widget"""
        self.visible = False
    
    def show(self):
        """Show the widget"""
        self.visible = True
