"""
Board Widget - Xử lý vẽ và tương tác với bàn cờ
"""
import pygame
import chess
import os


class BoardWidget:
    """Class quản lý bàn cờ và tương tác"""
    
    # Kích thước
    SQUARE_SIZE = 64
    BOARD_SIZE = SQUARE_SIZE * 8
    
    # Colors - Lichess Blue Theme
    LIGHT_SQUARE = (240, 217, 181)  # Nâu sáng
    DARK_SQUARE = (181, 136, 99)    # Nâu đậm
    HIGHLIGHT = (255, 255, 102, 150)  # Vàng trong suốt
    LAST_MOVE = (155, 199, 0, 100)   # Xanh lá trong suốt
    ARROW_COLOR = (255, 170, 0)      # Cam
    
    def __init__(self, screen, piece_images, x=0, y=0):
        self.screen = screen
        self.piece_images = piece_images
        self.x = x
        self.y = y
        
        # Board state
        self.board = chess.Board()
        self.selected_square = None
        self.legal_moves = []
        self.last_move = None
        
        # Dragging
        self.dragging_piece = None
        self.dragging_pos = None
        self.dragging_start_square = None
        
        # Arrows and highlights
        self.drawn_arrows = []
        self.highlighted_squares = set()
        self.drawing_arrow = False
        self.arrow_start = None
        self.arrow_end = None
        
        # Font for coordinates
        self.font = pygame.font.Font(None, 20)
        
        # Background
        self.background = self._load_background()
        
    def _load_background(self):
        """Load background image nếu có"""
        bg_path = os.path.join(os.path.dirname(__file__), "..", "assets", 
                              "backgrounds", "background.png")
        try:
            if os.path.exists(bg_path):
                return pygame.image.load(bg_path).convert()
        except:
            pass
        return None
    
    def draw(self):
        """Vẽ toàn bộ bàn cờ"""
        # Draw background nếu có
        if self.background:
            self.screen.blit(self.background, (self.x, self.y))
        
        # Draw squares
        self._draw_squares()
        
        # Draw coordinates
        self._draw_coordinates()
        
        # Draw highlights
        self._draw_highlights()
        
        # Draw arrows
        self._draw_arrows()
        
        # Draw pieces (không vẽ quân đang được kéo)
        self._draw_pieces()
        
        # Draw dragging piece last (để nó ở trên cùng)
        if self.dragging_piece:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.screen.blit(self.dragging_piece, 
                           (mouse_x - self.SQUARE_SIZE // 2, 
                            mouse_y - self.SQUARE_SIZE // 2))
    
    def _draw_squares(self):
        """Vẽ các ô vuông của bàn cờ"""
        for row in range(8):
            for col in range(8):
                color = self.LIGHT_SQUARE if (row + col) % 2 == 0 else self.DARK_SQUARE
                rect = pygame.Rect(
                    self.x + col * self.SQUARE_SIZE,
                    self.y + row * self.SQUARE_SIZE,
                    self.SQUARE_SIZE,
                    self.SQUARE_SIZE
                )
                pygame.draw.rect(self.screen, color, rect)
    
    def _draw_coordinates(self):
        """Vẽ tọa độ a-h và 1-8"""
        # Files (a-h)
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for i, file in enumerate(files):
            text = self.font.render(file, True, (50, 50, 50))
            x = self.x + i * self.SQUARE_SIZE + self.SQUARE_SIZE - 15
            y = self.y + 8 * self.SQUARE_SIZE - 15
            self.screen.blit(text, (x, y))
        
        # Ranks (1-8)
        for i in range(8):
            text = self.font.render(str(8 - i), True, (50, 50, 50))
            x = self.x + 5
            y = self.y + i * self.SQUARE_SIZE + 5
            self.screen.blit(text, (x, y))
    
    def _draw_highlights(self):
        """Vẽ highlight cho ô được chọn và nước đi hợp lệ"""
        # Last move highlight
        if self.last_move:
            self._draw_square_highlight(self.last_move.from_square, self.LAST_MOVE)
            self._draw_square_highlight(self.last_move.to_square, self.LAST_MOVE)
        
        # Selected square và legal moves
        if self.selected_square is not None:
            self._draw_square_highlight(self.selected_square, self.HIGHLIGHT)
            
            # Draw dots/circles cho legal moves
            for move in self.legal_moves:
                self._draw_legal_move_indicator(move.to_square)
    
    def _draw_square_highlight(self, square, color):
        """Vẽ highlight cho một ô"""
        row = 7 - (square // 8)
        col = square % 8
        
        # Tạo surface trong suốt
        s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
        s.fill(color)
        
        self.screen.blit(s, (
            self.x + col * self.SQUARE_SIZE,
            self.y + row * self.SQUARE_SIZE
        ))
    
    def _draw_legal_move_indicator(self, square):
        """Vẽ chấm tròn cho nước đi hợp lệ"""
        row = 7 - (square // 8)
        col = square % 8
        
        center_x = self.x + col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
        center_y = self.y + row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
        
        # Kiểm tra xem có quân ở đó không (capture move)
        if self.board.piece_at(square):
            # Vẽ viền tròn lớn hơn cho capture
            pygame.draw.circle(self.screen, (200, 50, 50, 180), 
                             (center_x, center_y), 28, 4)
        else:
            # Vẽ chấm tròn nhỏ cho move bình thường
            pygame.draw.circle(self.screen, (50, 50, 50, 100), 
                             (center_x, center_y), 10)
    
    def _draw_arrows(self):
        """Vẽ các mũi tên"""
        # Drawn arrows (đã vẽ xong)
        for start_sq, end_sq in self.drawn_arrows:
            start_pos = self._get_square_center(start_sq)
            end_pos = self._get_square_center(end_sq)
            self._draw_arrow(start_pos, end_pos, self.ARROW_COLOR)
        
        # Arrow đang vẽ
        if self.drawing_arrow and self.arrow_start and self.arrow_end:
            start_pos = self._get_square_center(self.arrow_start)
            self._draw_arrow(start_pos, self.arrow_end, self.ARROW_COLOR)
    
    def _draw_arrow(self, start_pos, end_pos, color):
        """Vẽ một mũi tên"""
        # Điều chỉnh tọa độ theo offset của board
        start = (start_pos[0] + self.x, start_pos[1] + self.y)
        if isinstance(end_pos, tuple) and len(end_pos) == 2:
            end = end_pos
        else:
            end = (end_pos[0] + self.x, end_pos[1] + self.y)
        
        # Vẽ đường thẳng
        pygame.draw.line(self.screen, color, start, end, 5)
        
        # Vẽ đầu mũi tên
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = (dx**2 + dy**2)**0.5
        
        if length > 0:
            ndx = dx / length
            ndy = dy / length
            
            arrow_size = 15
            arrow_width = 8
            
            tip = end
            left = (
                int(end[0] - arrow_size * ndx + arrow_width * ndy),
                int(end[1] - arrow_size * ndy - arrow_width * ndx)
            )
            right = (
                int(end[0] - arrow_size * ndx - arrow_width * ndy),
                int(end[1] - arrow_size * ndy + arrow_width * ndx)
            )
            
            pygame.draw.polygon(self.screen, color, [tip, left, right])
    
    def _draw_pieces(self):
        """Vẽ các quân cờ"""
        for square in chess.SQUARES:
            # Không vẽ quân đang được kéo
            if self.dragging_start_square == square:
                continue
                
            piece = self.board.piece_at(square)
            if piece:
                row = 7 - (square // 8)
                col = square % 8
                
                piece_key = f"{'w' if piece.color else 'b'}{piece.symbol().lower()}"
                if piece_key in self.piece_images:
                    img = self.piece_images[piece_key]
                    self.screen.blit(img, (
                        self.x + col * self.SQUARE_SIZE,
                        self.y + row * self.SQUARE_SIZE
                    ))
    
    def _get_square_center(self, square):
        """Lấy tọa độ trung tâm của ô (relative to board)"""
        row = 7 - (square // 8)
        col = square % 8
        return (
            col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2,
            row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
        )
    
    def get_square_from_pos(self, pos):
        """Chuyển tọa độ màn hình thành square"""
        x, y = pos
        
        # Kiểm tra có trong board không
        if (x < self.x or x >= self.x + self.BOARD_SIZE or
            y < self.y or y >= self.y + self.BOARD_SIZE):
            return None
        
        col = (x - self.x) // self.SQUARE_SIZE
        row = 7 - ((y - self.y) // self.SQUARE_SIZE)
        
        if 0 <= col < 8 and 0 <= row < 8:
            return chess.square(col, row)
        return None
    
    def handle_mouse_down(self, pos, button):
        """Xử lý click chuột"""
        square = self.get_square_from_pos(pos)
        
        if button == 1:  # Left click
            # Clear arrows và highlights
            self.drawn_arrows.clear()
            self.highlighted_squares.clear()
            
            if square is not None:
                piece = self.board.piece_at(square)
                # Chỉ cho phép chọn quân của người chơi hiện tại
                if piece and piece.color == self.board.turn:
                    self.selected_square = square
                    self.dragging_start_square = square
                    self.legal_moves = [m for m in self.board.legal_moves 
                                      if m.from_square == square]
                    
                    # Set dragging piece
                    piece_key = f"{'w' if piece.color else 'b'}{piece.symbol().lower()}"
                    if piece_key in self.piece_images:
                        self.dragging_piece = self.piece_images[piece_key]
                        self.dragging_pos = pos
        
        elif button == 3:  # Right click
            if square is not None:
                self.drawing_arrow = True
                self.arrow_start = square
                self.arrow_end = pos
    
    def handle_mouse_up(self, pos, button):
        """Xử lý thả chuột - trả về True nếu có nước đi"""
        square = self.get_square_from_pos(pos)
        move_made = False
        
        if button == 1:  # Left click
            if self.selected_square is not None and square is not None:
                move = chess.Move(self.selected_square, square)
                
                # Kiểm tra promotion
                piece = self.board.piece_at(self.selected_square)
                if (piece and piece.piece_type == chess.PAWN and 
                    ((piece.color == chess.WHITE and square // 8 == 7) or
                     (piece.color == chess.BLACK and square // 8 == 0))):
                    move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)
                
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.last_move = move
                    move_made = True
            
            # Reset dragging
            self.selected_square = None
            self.dragging_piece = None
            self.dragging_pos = None
            self.dragging_start_square = None
            self.legal_moves = []
        
        elif button == 3:  # Right click
            self.drawing_arrow = False
            if self.arrow_start and square and square != self.arrow_start:
                self.drawn_arrows.append((self.arrow_start, square))
            self.arrow_start = None
            self.arrow_end = None
        
        return move_made
    
    def handle_mouse_motion(self, pos):
        """Xử lý di chuyển chuột"""
        if self.dragging_piece:
            self.dragging_pos = pos
        
        if self.drawing_arrow:
            self.arrow_end = pos
    
    def reset(self):
        """Reset bàn cờ về trạng thái ban đầu"""
        self.board = chess.Board()
        self.selected_square = None
        self.legal_moves = []
        self.last_move = None
        self.dragging_piece = None
        self.dragging_pos = None
        self.dragging_start_square = None
        self.drawn_arrows.clear()
        self.highlighted_squares.clear()
    
    def set_board(self, board):
        """Set board state"""
        self.board = board
        self.last_move = board.peek() if len(board.move_stack) > 0 else None
