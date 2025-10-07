"""
Main Window - Chess AI GUI (Refactored)
Lichess-style interface with modular components
"""
import os
import sys
import threading
import queue

import chess
import pygame
import pygame_gui

# Components
from src.gui.components import (
    ChessClock, 
    BoardWidget, 
    CapturedPiecesWidget,
    MoveHistoryWidget,
    ControlPanel
)
from src.gui.components.evaluation_bar import EvaluationBar
from src.gui.components.analysis_panel import AnalysisPanel

# AI
from src.ai.minimax_optimized import get_best_move
from src.ai.opening_book import OpeningBook
from src.ai.analysis_engine import AnalysisEngine

# Add path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
BOARD_SIZE = 512  # 8 * 64

# Colors - Dark theme like Lichess
BG_COLOR = (28, 28, 28)
SIDEBAR_COLOR = (40, 40, 40)
TEXT_COLOR = (220, 220, 220)

# Opening book
BOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "opening_bin", "gm2600.bin")
BOOK_PATH = os.path.normpath(BOOK_PATH)

opening_book = None
if os.path.exists(BOOK_PATH):
    opening_book = OpeningBook(BOOK_PATH)
else:
    print(f"⚠️  Warning: Opening book not found")

# Global AI state
ai_move_queue = queue.Queue()
ai_thinking = False


def load_pieces():
    """Load piece images"""
    pieces = {}
    colors = ['w', 'b']
    piece_names = ['P', 'N', 'B', 'R', 'Q', 'K']
    
    for color in colors:
        for name in piece_names:
            key = f"{color}{name.lower()}"
            path = os.path.join(os.path.dirname(__file__), "assets", "pieces", 
                              f"{color}{name}.png")
            try:
                img = pygame.image.load(path).convert_alpha()
                # Scale to 64x64
                pieces[key] = pygame.transform.scale(img, (64, 64))
            except pygame.error as e:
                print(f"Error loading {key}: {e}")
    
    return pieces


def ai_move_threaded(board_copy, depth=4, time_limit=5.0):
    """Run AI in background thread"""
    global ai_thinking
    ai_thinking = True
    
    def run_ai():
        try:
            # Try opening book first
            move = None
            if opening_book:
                try:
                    move = opening_book.get_move(board_copy)
                    if move:
                        print(f"📖 Opening book: {move}")
                except:
                    pass
            
            # If no book move, use engine
            if not move:
                move = get_best_move(board_copy, depth=depth, time_limit=time_limit)
                print(f"🤖 AI calculated: {move}")
            
            ai_move_queue.put(move)
        except Exception as e:
            print(f"❌ AI error: {e}")
            ai_move_queue.put(None)
    
    thread = threading.Thread(target=run_ai, daemon=True)
    thread.start()


class ChessGame:
    """Main game class"""
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Chess AI - Eury Engine v2")
        
        self.clock = pygame.time.Clock()
        
        # UI Manager với theme
        theme_path = os.path.join(os.path.dirname(__file__), "theme_improved.json")
        self.manager = pygame_gui.UIManager(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            theme_path if os.path.exists(theme_path) else None
        )
        
        # Load pieces
        self.piece_images = load_pieces()
        
        # Game state - Initialize BEFORE components
        self.current_screen = "home"  # home, game, settings
        self.game_active = False
        self.game_result = None
        
        # Board - Initialize BEFORE components need it
        self.board = chess.Board()
        
        # Create components
        self._create_components()
        
        # Time control settings
        self.time_controls = {
            'Bullet 1+0': (60, 0),
            'Bullet 2+1': (120, 1),
            'Blitz 3+0': (180, 0),
            'Blitz 5+0': (300, 0),
            'Rapid 10+0': (600, 0),
            'Rapid 15+10': (900, 10),
            'Classical 30+0': (1800, 0),
        }
        self.selected_time_control = 'Blitz 5+0'
        
        # AI difficulty
        self.ai_levels = {
            'Easy': (2, 1.0),
            'Medium': (3, 3.0),
            'Hard': (4, 5.0),
            'Expert': (5, 10.0),
        }
        self.selected_ai_level = 'Hard'
        
        # Analysis Engine
        self.analysis_engine = AnalysisEngine(depth=3)
        self.analysis_mode = False  # Toggle analysis mode on/off
        
        # Music
        self._load_music()
        
        # Home screen UI
        self._create_home_ui()
    
    def _create_components(self):
        """Create game components"""
        # Board widget (centered-left)
        board_x = 20
        board_y = (WINDOW_HEIGHT - BOARD_SIZE) // 2
        self.board_widget = BoardWidget(
            self.screen, 
            self.piece_images,
            board_x, 
            board_y
        )
        
        # Evaluation bar (left of board)
        eval_bar_width = 30
        eval_bar_x = board_x - eval_bar_width - 5
        self.evaluation_bar = EvaluationBar(
            eval_bar_x,
            board_y,
            eval_bar_width,
            BOARD_SIZE
        )
        
        # Sidebar position (right side)
        sidebar_x = board_x + BOARD_SIZE + 20
        sidebar_width = WINDOW_WIDTH - sidebar_x - 20
        
        # Clock
        self.chess_clock = ChessClock(self.manager, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Captured pieces
        self.captured_widget = CapturedPiecesWidget(
            self.screen,
            self.piece_images,
            sidebar_x,
            100,
            sidebar_width
        )
        
        # Move history
        self.move_history = MoveHistoryWidget(
            self.screen,
            sidebar_x,
            200,
            sidebar_width,
            250
        )
        
        # Analysis panel (hidden by default, shown when analysis button clicked)
        # Smaller height to not overlap control buttons
        self.analysis_panel = AnalysisPanel(
            pygame.Rect(sidebar_x, 100, sidebar_width, 280),
            self.manager,
            self.board
        )
        self.analysis_panel.hide()
        
        # Control panel
        self.control_panel = ControlPanel(self.manager, WINDOW_WIDTH)
    
    def _create_home_ui(self):
        """Create home screen UI"""
        # Title
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((WINDOW_WIDTH//2 - 250, 50), (500, 80)),
            text='Chess AI - Eury Engine',
            manager=self.manager,
            object_id=pygame_gui.core.ObjectID(class_id='@title_label')
        )
        
        button_width = 280
        button_height = 55
        start_y = 180
        spacing = 75
        
        # Play button
        self.play_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (WINDOW_WIDTH//2 - button_width//2, start_y),
                (button_width, button_height)
            ),
            text='Play vs AI',
            manager=self.manager,
            object_id=pygame_gui.core.ObjectID(class_id='@home_button')
        )
        
        # Settings button
        self.settings_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (WINDOW_WIDTH//2 - button_width//2, start_y + spacing),
                (button_width, button_height)
            ),
            text='Settings',
            manager=self.manager,
            object_id=pygame_gui.core.ObjectID(class_id='@home_button')
        )
        
        # About button
        self.about_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (WINDOW_WIDTH//2 - button_width//2, start_y + spacing * 2),
                (button_width, button_height)
            ),
            text='About',
            manager=self.manager,
            object_id=pygame_gui.core.ObjectID(class_id='@home_button')
        )
        
        self.home_buttons = [
            self.title_label,
            self.play_button,
            self.settings_button,
            self.about_button
        ]
        
        # Back buttons for settings/about
        self.settings_back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, 20), (100, 40)),
            text='< Back',
            manager=self.manager,
            object_id=pygame_gui.core.ObjectID(class_id='@back_button')
        )
        self.settings_back_button.hide()
        
        self.about_back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, 20), (100, 40)),
            text='< Back',
            manager=self.manager,
            object_id=pygame_gui.core.ObjectID(class_id='@back_button')
        )
        self.about_back_button.hide()
    
    def _load_music(self):
        """Load background music"""
        music_path = os.path.join(os.path.dirname(__file__), "assets", "music", 
                                 "background_music.mp3")
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.3)
                print("🎵 Music loaded")
            except:
                print("⚠️ Could not load music")
    
    def start_game(self):
        """Start a new game"""
        self.current_screen = "game"
        self.game_active = True
        self.game_result = None
        
        # Reset board
        self.board = chess.Board()
        self.board_widget.reset()
        self.board_widget.set_board(self.board)
        self.captured_widget.reset()
        
        # Setup clock
        time_setting = self.time_controls[self.selected_time_control]
        self.chess_clock.set_time_control(time_setting[0], time_setting[1])
        self.chess_clock.start(chess.WHITE)
        
        # Hide home UI
        for btn in self.home_buttons:
            btn.hide()
        
        # Show game UI
        self.chess_clock.show()
        self.control_panel.show_playing()
        
        print(f"🎮 Game started: {self.selected_time_control}, AI: {self.selected_ai_level}")
    
    def make_ai_move(self):
        """Trigger AI to make a move"""
        global ai_thinking
        
        if not self.game_active or ai_thinking:
            return
        
        # Pause clock while AI thinks
        self.chess_clock.pause()
        
        # Get AI settings
        depth, time_limit = self.ai_levels[self.selected_ai_level]
        
        # Run AI in thread
        board_copy = self.board.copy()
        ai_move_threaded(board_copy, depth, time_limit)
    
    def handle_move_made(self):
        """Handle after a move is made"""
        # Track captured pieces (get last move from board)
        if len(self.board.move_stack) > 0:
            last_move = self.board.peek()
            # Note: capture already tracked before push in handle_event
        
        # Switch clock
        self.chess_clock.switch_player()
        
        # Check game over
        if self.board.is_checkmate():
            winner = "White" if self.board.turn == chess.BLACK else "Black"
            self.game_result = f"checkmate_{winner.lower()}"
            self.end_game()
        elif self.board.is_stalemate():
            self.game_result = "stalemate"
            self.end_game()
        elif self.board.is_insufficient_material():
            self.game_result = "insufficient_material"
            self.end_game()
        else:
            # AI's turn?
            if self.board.turn == chess.BLACK and self.game_active:
                self.make_ai_move()
    
    def end_game(self):
        """End the game"""
        self.game_active = False
        self.chess_clock.stop()
        self.control_panel.show_finished()
        
        print(f"🏁 Game over: {self.game_result}")
    
    def draw_status_overlay(self):
        """Draw game status overlay when game ends"""
        if not self.game_result:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Status box
        box_width = 400
        box_height = 200
        box_x = (WINDOW_WIDTH - box_width) // 2
        box_y = (WINDOW_HEIGHT - box_height) // 2
        
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (box_x, box_y, box_width, box_height), 
                        border_radius=15)
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (box_x, box_y, box_width, box_height), 
                        3, border_radius=15)
        
        # Result text
        font = pygame.font.Font(None, 48)
        
        result_texts = {
            'checkmate_white': 'White Wins!',
            'checkmate_black': 'Black Wins!',
            'stalemate': 'Draw - Stalemate',
            'insufficient_material': 'Draw - Insufficient Material',
            'white_timeout': 'Black Wins (Timeout)',
            'black_timeout': 'White Wins (Timeout)',
            'draw': 'Draw Agreed',
        }
        
        result_text = result_texts.get(self.game_result, 'Game Over')
        text_surface = font.render(result_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        self.screen.blit(text_surface, text_rect)
    
    def update(self, time_delta):
        """Update game state"""
        global ai_thinking
        
        # Update clock
        if self.current_screen == "game" and self.game_active:
            timeout = self.chess_clock.update(time_delta)
            if timeout:
                self.game_result = timeout
                self.end_game()
        
        # Update evaluation bar animation
        self.evaluation_bar.update(time_delta)
        
        # Check for AI move completion
        if not ai_move_queue.empty():
            move = ai_move_queue.get()
            ai_thinking = False
            
            if move and move in self.board.legal_moves:
                # Track capture BEFORE pushing
                self.captured_widget.track_capture(move, self.board)
                
                # Push move
                self.board.push(move)
                self.board_widget.set_board(self.board)
                self.handle_move_made()
                
                # Update analysis if in analysis mode
                if self.analysis_mode:
                    self._analyze_current_position()
            
            # Resume clock
            self.chess_clock.resume()
        
        # Update UI manager
        self.manager.update(time_delta)
    
    def draw(self):
        """Draw everything"""
        self.screen.fill(BG_COLOR)
        
        if self.current_screen == "home":
            self._draw_home()
        elif self.current_screen == "game":
            self._draw_game()
        elif self.current_screen == "settings":
            self._draw_settings()
        
        self.manager.draw_ui(self.screen)
        pygame.display.flip()
    
    def _draw_home(self):
        """Draw home screen"""
        # Could add background image here
        pass
    
    def _draw_game(self):
        """Draw game screen"""
        # Draw evaluation bar
        self.evaluation_bar.draw(self.screen)
        
        # Draw board
        self.board_widget.draw()
        
        # Draw sidebar components (widgets handle their own visibility)
        self.captured_widget.draw()
        self.move_history.draw(self.board)
        
        # Draw thinking indicator
        if ai_thinking:
            self._draw_thinking_indicator()
        
        # Draw game over overlay
        if self.game_result:
            self.draw_status_overlay()
    
    def _draw_thinking_indicator(self):
        """Draw AI thinking animation"""
        font = pygame.font.Font(None, 24)
        text = font.render("AI is thinking...", True, (100, 255, 100))
        
        # Position at top of sidebar
        x = 560
        y = 470
        
        # Animated dots
        dots = "." * (int(pygame.time.get_ticks() / 500) % 4)
        dots_text = font.render(dots, True, (100, 255, 100))
        
        self.screen.blit(text, (x, y))
        self.screen.blit(dots_text, (x + text.get_width(), y))
    
    def _draw_settings(self):
        """Draw settings screen"""
        # Background
        self.screen.fill(BG_COLOR)
        
        # Title
        font_large = pygame.font.Font(None, 64)
        title = font_large.render("Settings", True, TEXT_COLOR)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 80))
        
        # Content
        font_medium = pygame.font.Font(None, 32)
        y = 200
        
        texts = [
            "Time Control: Blitz 5+0",
            "AI Difficulty: Hard",
            "",
            "Coming soon:",
            "- Customizable time controls",
            "- AI difficulty selector", 
            "- Board themes",
            "- Sound settings"
        ]
        
        for text in texts:
            if text:
                surface = font_medium.render(text, True, TEXT_COLOR)
                self.screen.blit(surface, (100, y))
            y += 45
    
    def _draw_about(self):
        """Draw about screen"""
        # Background
        self.screen.fill(BG_COLOR)
        
        # Title
        font_large = pygame.font.Font(None, 64)
        title = font_large.render("About", True, TEXT_COLOR)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 80))
        
        # Content
        font_medium = pygame.font.Font(None, 28)
        y = 180
        
        texts = [
            "Chess AI - Eury Engine v2.0",
            "",
            "Hybrid Architecture:",
            "  Python GUI (Pygame)",
            "  C++ Engine (Performance)",
            "",
            "Features:",
            "  - Full chess rules",
            "  - AI with 4 difficulty levels",
            "  - Opening book support",
            "  - Time controls with increment",
            "  - Move history & analysis",
            "",
            "Author: Eurus-Infosec",
            "License: MIT"
        ]
        
        for text in texts:
            if text:
                surface = font_medium.render(text, True, TEXT_COLOR)
                self.screen.blit(surface, (100, y))
            y += 35
    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.QUIT:
            return False
        
        # UI events
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                self._handle_button_press(event.ui_element)
        
        # Analysis panel events
        if self.analysis_mode and self.analysis_panel.handle_event(event):
            # Analysis button pressed in panel
            self._analyze_current_position()
        
        # Game events
        if self.current_screen == "game" and self.game_active:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.board.turn == chess.WHITE:  # Only allow player moves
                    self.board_widget.handle_mouse_down(event.pos, event.button)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.board.turn == chess.WHITE:
                    # Track capture BEFORE move
                    square = self.board_widget.get_square_from_pos(event.pos)
                    if self.board_widget.selected_square and square:
                        move = chess.Move(self.board_widget.selected_square, square)
                        # Check if this is a capture
                        if move in self.board.legal_moves:
                            self.captured_widget.track_capture(move, self.board)
                    
                    # Now make the move
                    move_made = self.board_widget.handle_mouse_up(event.pos, event.button)
                    if move_made:
                        self.board = self.board_widget.board
                        self.handle_move_made()
                        
                        # Update analysis if in analysis mode
                        if self.analysis_mode:
                            self._analyze_current_position()
            
            elif event.type == pygame.MOUSEMOTION:
                self.board_widget.handle_mouse_motion(event.pos)
        
        self.manager.process_events(event)
        return True
    
    def _handle_button_press(self, button):
        """Handle button presses"""
        if button == self.play_button:
            self.start_game()
        
        elif button == self.control_panel.home_button:
            self.current_screen = "home"
            self.game_active = False
            self.analysis_mode = False
            self.chess_clock.hide()
            self.control_panel.hide_all()
            self.analysis_panel.hide()
            self.captured_widget.reset()
            self.move_history.clear()
            for btn in self.home_buttons:
                btn.show()
        
        elif button == self.control_panel.resign_button:
            self.game_result = "checkmate_black"
            self.end_game()
        
        elif button == self.control_panel.draw_button:
            self.game_result = "draw"
            self.end_game()
        
        elif button == self.control_panel.rematch_button:
            self.start_game()
        
        elif button == self.control_panel.analysis_button:
            self._toggle_analysis_mode()
        
        elif button == self.settings_button:
            self.current_screen = "settings"
            for btn in self.home_buttons:
                btn.hide()
            self.settings_back_button.show()
        
        elif button == self.about_button:
            self.current_screen = "about"
            for btn in self.home_buttons:
                btn.hide()
            self.about_back_button.show()
        
        elif button == self.settings_back_button:
            self.current_screen = "home"
            self.settings_back_button.hide()
            for btn in self.home_buttons:
                btn.show()
        
        elif button == self.about_back_button:
            self.current_screen = "home"
            self.about_back_button.hide()
            for btn in self.home_buttons:
                btn.show()
    
    def _toggle_analysis_mode(self):
        """Toggle analysis mode on/off"""
        self.analysis_mode = not self.analysis_mode
        
        if self.analysis_mode:
            # Show analysis panel, hide other widgets
            self.captured_widget.hide()
            self.move_history.hide()
            self.analysis_panel.show()
            
            # Start analysis of current position
            self._analyze_current_position()
        else:
            # Hide analysis panel, show game widgets
            self.analysis_panel.hide()
            self.captured_widget.show()
            self.move_history.show()
    
    def _analyze_current_position(self):
        """Analyze the current board position"""
        if not self.game_active:
            return
        
        # Sync board state with panel
        self.analysis_panel.set_board(self.board)
        
        def analyze_callback(result):
            """Callback when analysis completes"""
            self.analysis_panel.update_analysis(result)
            
            # Convert evaluation to centipawn (divide by 100) from white's perspective
            # result.evaluation is from side-to-move perspective
            eval_cp = result.evaluation / 100.0
            if self.board.turn == chess.BLACK:
                eval_cp = -eval_cp  # Flip for white perspective
            
            self.evaluation_bar.set_evaluation(eval_cp)
        
        # Run analysis in background
        self.analysis_engine.start_background_analysis(
            self.board,
            analyze_callback
        )
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            time_delta = self.clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False
                    break
            
            self.update(time_delta)
            self.draw()
        
        pygame.quit()


def run_gui():
    """Entry point"""
    game = ChessGame()
    game.run()


if __name__ == "__main__":
    run_gui()
