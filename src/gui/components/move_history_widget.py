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
        
        # Lichess-inspired colors
        self.bg_color = (37, 36, 34)  # Dark brown
        self.text_color = (189, 176, 153)  # Light tan
        self.move_num_color = (128, 120, 105)  # Muted tan
        self.highlight_color = (80, 70, 55)  # Subtle highlight
        self.hover_color = (60, 55, 45)  # Hover effect
        
        self.visible = True
        self.scroll_offset = 0
    
    def draw(self, board):
        """Vẽ move history - Lichess style"""
        if not self.visible:
            return
            
        # Background
        pygame.draw.rect(self.screen, self.bg_color, 
                        (self.x, self.y, self.width, self.height))
        
        # No border - cleaner look
        
        # Get moves
        moves = list(board.move_stack)
        if not moves:
            # Show placeholder text
            text = self.font.render("No moves yet", True, self.move_num_color)
            self.screen.blit(text, (self.x + 10, self.y + 10))
            return
        
        # Lichess-style compact layout
        y_offset = 8
        line_height = 22
        padding_left = 8
        
        # Column widths
        num_width = 28  # "1."
        move_width = (self.width - num_width - padding_left * 2) // 2
        
        # Calculate visible moves
        max_visible = (self.height - y_offset * 2) // line_height
        start_idx = max(0, len(moves) - max_visible * 2)
        
        move_number = start_idx // 2 + 1
        current_y = self.y + y_offset
        
        for i in range(start_idx, len(moves), 2):
            # Highlight last move pair
            is_last = (i >= len(moves) - 2)
            if is_last:
                pygame.draw.rect(self.screen, self.highlight_color, 
                               (self.x, current_y - 2, self.width, line_height))
            
            # Move number
            num_text = self.move_num_font.render(f"{move_number}.", True, self.move_num_color)
            self.screen.blit(num_text, (self.x + padding_left, current_y + 2))
            
            # White move
            white_move = self._format_move(moves[i])
            white_text = self.font.render(white_move, True, self.text_color)
            self.screen.blit(white_text, (self.x + padding_left + num_width, current_y))
            
            # Black move (if exists)
            if i + 1 < len(moves):
                black_move = self._format_move(moves[i + 1])
                black_text = self.font.render(black_move, True, self.text_color)
                self.screen.blit(black_text, 
                               (self.x + padding_left + num_width + move_width, current_y))
            
            current_y += line_height
            move_number += 1
            
            # Stop if out of bounds
            if current_y > self.y + self.height - line_height:
                break
            self.screen.blit(text, (self.x + 10, self.y + y_offset))
            
            y_offset += line_height
            move_number += 1
            
            # Stop if out of space
            if y_offset > self.height - 30:
                break
    
    def _format_move(self, move):
        """Format move to SAN notation"""
        # Simple formatting (không cần board state)
        from_sq = chess.SQUARE_NAMES[move.from_square]
        to_sq = chess.SQUARE_NAMES[move.to_square]
        
        # Basic format
        move_str = f"{from_sq}{to_sq}"
        
        # Add promotion
        if move.promotion:
            piece_symbols = {
                chess.QUEEN: 'Q',
                chess.ROOK: 'R', 
                chess.BISHOP: 'B',
                chess.KNIGHT: 'N'
            }
            move_str += piece_symbols.get(move.promotion, '')
        
        return move_str
    
    def draw_san(self, board):
        """Vẽ move history với proper SAN notation"""
        # Vẽ background
        pygame.draw.rect(self.screen, self.bg_color, 
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.screen, (80, 80, 80), 
                        (self.x, self.y, self.width, self.height), 2)
        
        # Title
        title = self.title_font.render("Move History", True, self.title_color)
        self.screen.blit(title, (self.x + 10, self.y + 10))
        
        # Get SAN moves
        y_offset = 40
        line_height = 25
        
        # Create a temporary board to generate SAN
        temp_board = chess.Board()
        san_moves = []
        
        for move in board.move_stack:
            san = temp_board.san(move)
            san_moves.append(san)
            temp_board.push(move)
        
        # Display moves
        max_visible = (self.height - 50) // line_height
        start_idx = max(0, len(san_moves) - max_visible * 2)
        move_number = start_idx // 2 + 1
        
        for i in range(start_idx, len(san_moves), 2):
            white_move = san_moves[i]
            black_move = san_moves[i + 1] if i + 1 < len(san_moves) else ""
            
            move_text = f"{move_number}. {white_move}"
            if black_move:
                move_text += f" {black_move}"
            
            text = self.font.render(move_text, True, self.text_color)
            
            # Highlight last move
            if i >= len(san_moves) - 2:
                pygame.draw.rect(self.screen, (60, 60, 80), 
                               (self.x + 5, self.y + y_offset - 2, 
                                self.width - 10, line_height))
            
            self.screen.blit(text, (self.x + 10, self.y + y_offset))
            
            y_offset += line_height
            move_number += 1
            
            if y_offset > self.height - 30:
                break
    
    def hide(self):
        """Hide the widget"""
        self.visible = False
    
    def show(self):
        """Show the widget"""
        self.visible = True
