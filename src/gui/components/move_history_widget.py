"""
Move History Widget - Hiển thị lịch sử nước đi
"""
import pygame
import chess


class MoveHistoryWidget:
    """Widget hiển thị lịch sử các nước đi"""
    
    def __init__(self, screen, x, y, width=180, height=300):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 22)
        
        # Colors
        self.bg_color = (40, 40, 40)
        self.text_color = (220, 220, 220)
        self.title_color = (180, 180, 180)
        
        self.visible = True  # Add visibility flag
    
    def draw(self, board):
        """Vẽ move history"""
        if not self.visible:  # Skip if hidden
            return
            
        # Vẽ background
        pygame.draw.rect(self.screen, self.bg_color, 
                        (self.x, self.y, self.width, self.height))
        
        # Vẽ border
        pygame.draw.rect(self.screen, (80, 80, 80), 
                        (self.x, self.y, self.width, self.height), 2)
        
        # Vẽ tiêu đề
        title = self.title_font.render("Move History", True, self.title_color)
        self.screen.blit(title, (self.x + 10, self.y + 10))
        
        # Vẽ moves
        y_offset = 40
        line_height = 25
        
        # Get moves from board
        moves = list(board.move_stack)
        
        # Scroll to show last moves
        max_visible = (self.height - 50) // line_height
        start_idx = max(0, len(moves) - max_visible * 2)
        
        # Group moves by pairs (white, black)
        move_number = start_idx // 2 + 1
        
        for i in range(start_idx, len(moves), 2):
            # White move
            white_move = self._format_move(moves[i])
            
            # Black move (if exists)
            black_move = ""
            if i + 1 < len(moves):
                black_move = self._format_move(moves[i + 1])
            
            # Render move pair
            move_text = f"{move_number}. {white_move}"
            if black_move:
                move_text += f"  {black_move}"
            
            text = self.font.render(move_text, True, self.text_color)
            
            # Highlight last move
            if i >= len(moves) - 2:
                pygame.draw.rect(self.screen, (60, 60, 80), 
                               (self.x + 5, self.y + y_offset - 2, 
                                self.width - 10, line_height))
            
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
