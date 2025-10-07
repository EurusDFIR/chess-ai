#src/gui/main_window.py
import os
import sys

import chess
import pygame
import pygame_gui

# Use optimized AI instead of old one
from src.ai.minimax_optimized import get_best_move
from src.ai.opening_book import OpeningBook
from pygame_gui.core import ObjectID

from src.gui.gui_improvements import (
    ai_move_threaded,
    ai_move_queue,
    ai_thinking,
    last_move,
    captured_white,
    captured_black,
    track_captured_pieces,
    draw_last_move_highlight,
    draw_captured_pieces,
    draw_material_count,
    draw_ai_thinking_indicator
)

from src.gui.game_controls import get_game_controls

# Add path to import from the root directory
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Fix opening book path - use relative path from script location
BOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "opening_bin", "gm2600.bin")
BOOK_PATH = os.path.normpath(BOOK_PATH)

# Check if opening book exists, if not use None
if os.path.exists(BOOK_PATH):
    opening_book = OpeningBook(BOOK_PATH)
else:
    print(f"⚠️  Warning: Opening book not found at {BOOK_PATH}")
    print("AI will use minimax search from the start.")
    opening_book = None

# Load piece images
def load_pieces():
    pieces = {}
    colors = ['w', 'b']
    piece_names = ['P', 'N', 'B', 'R', 'Q', 'K']
    for color in colors:
        for name in piece_names:
            key = f"{color}{name.lower()}"
            path = os.path.join(os.path.dirname(__file__), "assets", "pieces", f"{color}{name}.png")
            try:
                img = pygame.image.load(path).convert_alpha()
                pieces[key] = img
            except pygame.error as e:
                print(f"Error loading image for key {key} from path {path}: {e}")
    return pieces

# Global game_controls - needed by ai_move()
game_controls = None

def run_gui():
    global game_controls

    pygame.init()
    pygame.mixer.init()  # Khoi tao mixer de choi nhac
    pygame.display.set_caption("Eury engine v1")
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # **DOAN CODE TEST AM THANH DUOC CHEN VAO DAY**
    print("--- AM THANH TEST BAT DAU ---")  # Them dong nay de de nhan biet output test
    music_path_test = os.path.join(os.path.dirname(__file__), "..", "gui", "assets", "music", "background_music.mp3")
    music_path_test = os.path.normpath(music_path_test)

    if not os.path.exists(music_path_test):
        print(f"Loi TEST: File nhac khong tim thay tai '{music_path_test}'. Vui long kiem tra duong dan.")
    else:
        try:
            pygame.mixer.music.load(music_path_test)
            pygame.mixer.music.play(-1)  # Phat nhac lap lai
            pygame.mixer.music.set_volume(0.7)
            print("TEST THANH CONG: Dang phat nhac...")
        except pygame.error as e:
            print(f"Loi TEST khi tai file nhac: {e}")
    print("--- AM THANH TEST KET THUC ---")  # Them dong nay de de nhan biet output test
    # **KET THUC DOAN CODE TEST AM THANH**



    # Load font for coordinates
    font = pygame.font.Font(None, 24)

    # Load background image
    bg_path = os.path.join(os.path.dirname(__file__), "assets", "backgrounds",
                           "background.png")  # Đường dẫn đến ảnh nền, bạn có thể thay đổi
    try:
        background_image = pygame.image.load(bg_path).convert()  # .convert() để tối ưu hiển thị
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    except pygame.error as e:
        print(f"Error loading background image from path {bg_path}: {e}")
        background_image = None  # Xử lý trường hợp không tải được ảnh

    # Load background image for home screen
    home_bg_path = os.path.join(os.path.dirname(__file__), "assets", "backgrounds",
                                "home_background.png")  # Đường dẫn ảnh nền Home, bạn có thể thay đổi
    try:
        home_background_image = pygame.image.load(home_bg_path).convert()
        home_background_image = pygame.transform.scale(home_background_image, (WIDTH, HEIGHT))
    except pygame.error as e:
        print(f"Error loading home background image from path {home_bg_path}: {e}")
        home_background_image = None

        # Load background music
        music_path = os.path.join(os.path.dirname(__file__), "assets", "music",
                                  "background_music.mp3")  # Đường dẫn đến file nhạc, bạn có thể thay đổi
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
        else:
            print("Music file not found at:", music_path)
        try:
            pygame.mixer.music.load(music_path)
            print("Music loaded successfully.")
        except pygame.error as e:
            print(f"Error loading music from path {music_path}: {e}")
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1)  # Play in a loop

    clock = pygame.time.Clock()
    theme_path = os.path.join(os.path.dirname(__file__), 'theme.json')
    manager = pygame_gui.UIManager((WIDTH, HEIGHT), theme_path)  # Load theme file

    # Create game controls
    game_controls = get_game_controls(manager, WIDTH, HEIGHT)
    game_controls.create_game_buttons()

    HOME_BG_COLOR = (220, 220, 220) # Màu nền trang chủ
    LIGHT = (220, 230, 240)  # Xanh lam rất nhạt
    DARK = (150, 170, 190)  # Xanh lam xám
    HIGHLIGHT = (180, 210, 230)  # Xanh lam nhạt hơn
    ARROW_COLOR = (0, 180, 0)
    CLOCK_FONT_COLOR = (0, 0, 0)
    CLOCK_BG_COLOR = (240, 240, 240)

    # Biến thời gian
    global white_time, black_time, start_time, current_player
    white_time = 300
    black_time = 300
    start_time = 0
    current_player = chess.WHITE

    global board
    board = chess.Board()
    global piece_images
    piece_images = load_pieces()

    global dragging_piece, dragging_start_pos, legal_moves, selected_square
    dragging_piece = None
    dragging_start_pos = None
    legal_moves = []
    selected_square = None

    global drawing_arrow, arrow_start_square, arrow_end_square, drawn_arrows, highlighted_squares
    drawing_arrow = False
    arrow_start_square = None
    arrow_end_square = None
    drawn_arrows = []
    highlighted_squares = set()

    current_screen = "home"
    
    # Game state for controls
    game_active = False
    game_result = None
    time_dropdown = None
    level_dropdown = None

    # Create buttons
    global home_buttons
    title_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250, 50), (300, 100)),
                                                text='Eury engine v1',
                                                manager=manager,
                                                object_id=ObjectID(class_id='@home_title'))
    play_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 150), (100, 50)),
                                               text='Play',
                                               manager=manager,
                                               object_id=ObjectID(class_id='@home_button'))
    settings_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 220), (100, 50)),
                                                   text='Settings',
                                                   manager=manager,
                                                   object_id=ObjectID(class_id='@home_button'))
    about_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 290), (100, 50)),
                                                text='About',
                                                manager=manager,
                                                object_id=ObjectID(class_id='@home_button'))
    theme_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 360), (100, 50)),
                                                text='Theme',
                                                manager=manager,
                                                object_id=ObjectID(class_id='@home_button'))

    home_buttons = [play_button, settings_button, about_button, theme_button, title_label]

    # Hide home buttons initially
    for button in home_buttons:
        button.hide()

    # Tạo UI Labels cho đồng hồ
    clock_width = 150
    clock_height = 50
    clock_margin_top = 20
    clock_pos_x = 650

    global white_clock_label, black_clock_label
    def format_time(seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return "{:02d}:{:02d}".format(minutes, secs)

    white_clock_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((clock_pos_x, clock_margin_top), (clock_width, clock_height)),
                                                 text=format_time(white_time),
                                                 manager=manager,
                                                 object_id=ObjectID(class_id='@clock_label'))
    black_clock_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((clock_pos_x, HEIGHT - clock_height - clock_margin_top), (clock_width, clock_height)),
                                                 text=format_time(black_time),
                                                 manager=manager,
                                                 object_id=ObjectID(class_id='@clock_label'))
    # Hide clock labels initially
    white_clock_label.hide()
    black_clock_label.hide()


    global settings_back_button
    global about_back_button
    global theme_back_button

    settings_back_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (100, 50)),
                                                        text='Back',
                                                        manager=manager,
                                                        object_id=ObjectID(class_id='@back_button'))
    about_back_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (100, 50)),
                                                     text='Back',
                                                     manager=manager,
                                                     object_id=ObjectID(class_id='@back_button'))
    theme_back_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (100, 50)),
                                                     text='Back',
                                                     manager=manager,
                                                     object_id=ObjectID(class_id='@back_button'))

    # Hide back buttons initially
    settings_back_button.hide()
    about_back_button.hide()
    theme_back_button.hide()


    running = True
    game_started = False
    def init_game_time():
        global white_time, black_time, start_time, current_player, game_started

        # Get selected time control from game_controls
        time_control = game_controls.get_selected_time_control()
        white_time = time_control['time']
        black_time = time_control['time']
        start_time = pygame.time.get_ticks()
        current_player = chess.WHITE
        game_started = True
        
        print(f"⏱️ Game started with {time_control['name']}")


    # Show home screen buttons initially
    for button in home_buttons:
        button.show()

    while running:
        global ai_thinking, last_move
        time_delta = clock.tick(60)/1000.0
        
        # Update timer only when game is active and AI is not thinking
        if current_screen == "game" and game_started and not ai_thinking:
            if current_player == chess.WHITE:
                white_time -= time_delta  # Sử dụng time_delta trực tiếp
            else:
                black_time -= time_delta

            if white_time < 0: white_time = 0
            if black_time < 0: black_time = 0

            white_clock_label.set_text(format_time(white_time))
            black_clock_label.set_text(format_time(black_time))
            
            # Check timeout
            if white_time <= 0 and game_active:
                game_result = 'timeout_black'
                print("⏰ White timeout! Black wins!")
                game_active = False
                game_controls.show_game_buttons(game_active=False)
            elif black_time <= 0 and game_active:
                game_result = 'timeout_white'
                print("⏰ Black timeout! White wins!")
                game_active = False
                game_controls.show_game_buttons(game_active=False)


        # Check for AI move completion (from queue)
        if not ai_move_queue.empty():
            move = ai_move_queue.get()
            if move is not None:
                print(f"✅ AI chọn: {move}")
                board.push(move)
                track_captured_pieces(move, board)
                last_move = move
            else:
                print("AI returned None for move.")
            ai_thinking = False
            current_player = board.turn
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == play_button:
                        current_screen = "game"
                        init_game_time()
                        game_active = True
                        game_result = None
                        
                        # Reset board
                        board = chess.Board()
                        captured_white.clear()
                        captured_black.clear()
                        last_move = None
                        
                        # Hide home screen buttons when switching to game
                        for button in home_buttons:
                            button.hide()
                        # Show clock labels when switching to game
                        white_clock_label.show()
                        black_clock_label.show()
                        # Show game control buttons
                        game_controls.show_game_buttons(game_active=True)
                        
                    elif event.ui_element == settings_button:
                        current_screen = "settings"
                        # Hide home screen buttons, show back button for settings
                        for button in home_buttons:
                            button.hide()
                        settings_back_button.show()
                        # Hide clock labels when switching from game
                        white_clock_label.hide()
                        black_clock_label.hide()
                    elif event.ui_element == about_button:
                        current_screen = "about"
                        # Hide home screen buttons, show back button for about
                        for button in home_buttons:
                            button.hide()
                        about_back_button.show()
                        # Hide clock labels when switching from game
                        white_clock_label.hide()
                        black_clock_label.hide()
                    elif event.ui_element == theme_button:
                        current_screen = "theme"
                        # Hide home screen buttons, show theme back button
                        for button in home_buttons:
                            button.hide()
                        theme_back_button.show()
                        # Hide clock labels when switching from game
                        white_clock_label.hide()
                        black_clock_label.hide()
                    elif event.ui_element in [settings_back_button, about_back_button, theme_back_button]:
                        current_screen = "home"
                        # Show home screen buttons when switching to home
                        for button in home_buttons:
                            button.show()
                        # Hide back buttons
                        settings_back_button.hide()
                        about_back_button.hide()
                        theme_back_button.hide()
                        # Hide clock labels when switching from game
                        white_clock_label.hide()
                        black_clock_label.hide()
                        # Hide game control buttons
                        game_controls.hide_game_buttons()
                        # Kill dropdowns if exist
                        if time_dropdown:
                            time_dropdown.kill()
                            time_dropdown = None
                        if level_dropdown:
                            level_dropdown.kill()
                            level_dropdown = None
                    
                    # Game control buttons
                    elif event.ui_element == game_controls.resign_button:
                        print("🏳️ Player resigned!")
                        game_result = 'black_win'
                        game_active = False
                        game_controls.show_game_buttons(game_active=False)
                    
                    elif event.ui_element == game_controls.draw_button:
                        print("🤝 Draw agreed!")
                        game_result = 'draw'
                        game_active = False
                        game_controls.show_game_buttons(game_active=False)
                    
                    elif event.ui_element == game_controls.rematch_button:
                        print("🔄 Starting rematch...")
                        # Reset game
                        board = chess.Board()
                        captured_white.clear()
                        captured_black.clear()
                        last_move = None
                        init_game_time()
                        game_active = True
                        game_result = None
                        game_controls.show_game_buttons(game_active=True)
                    
                    elif event.ui_element == game_controls.home_button:
                        print("🏠 Going home...")
                        current_screen = "home"
                        game_active = False
                        game_result = None
                        
                        # Show home buttons
                        for button in home_buttons:
                            button.show()
                        
                        # Hide game buttons and clocks
                        game_controls.hide_game_buttons()
                        white_clock_label.hide()
                        black_clock_label.hide()
                
                # Dropdown selection handlers
                elif event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if time_dropdown and event.ui_element == time_dropdown:
                        game_controls.set_time_control(event.text)
                        print(f"⏱️ Time control: {event.text}")
                    
                    elif level_dropdown and event.ui_element == level_dropdown:
                        game_controls.set_ai_level(event.text)
                        print(f"🤖 AI level: {event.text}")


            elif event.type == pygame.MOUSEBUTTONDOWN and current_screen == "game":
                handle_mouse_down(event.pos, event.button)
            elif event.type == pygame.MOUSEBUTTONUP and current_screen == "game":
                move_made = handle_mouse_up(event.pos, event.button)
                if move_made:
                    move = board.peek()  # Get the last move that was just made
                    track_captured_pieces(move, board)
                    last_move = move
                    current_player = board.turn
                    start_time = pygame.time.get_ticks()
                    
                    # Check game over conditions
                    if board.is_checkmate():
                        if board.turn == chess.WHITE:
                            game_result = 'checkmate_black'
                            print("♔ Black wins by checkmate!")
                        else:
                            game_result = 'checkmate_white'
                            print("♔ White wins by checkmate!")
                        game_active = False
                        game_controls.show_game_buttons(game_active=False)
                    
                    elif board.is_stalemate():
                        game_result = 'stalemate'
                        print("🤝 Draw by stalemate!")
                        game_active = False
                        game_controls.show_game_buttons(game_active=False)

            elif event.type == pygame.MOUSEMOTION and current_screen == "game":
                handle_mouse_motion(event.pos)

            manager.process_events(event)

        manager.update(time_delta)

        screen.fill(HOME_BG_COLOR)
        if current_screen == "home":
            if home_background_image:  # Vẽ ảnh nền Home nếu đã tải thành công
                screen.blit(home_background_image, (0, 0))
            else:  # Nếu không có ảnh nền Home, vẫn tô màu nền mặc định như cũ
                screen.fill(HOME_BG_COLOR)
            manager.draw_ui(screen)  # Vẽ UI Manager lên trên ảnh nền (hoặc màu nền)
        elif current_screen == "game":
            draw_board(screen, board, piece_images, LIGHT, DARK, HIGHLIGHT, dragging_piece, dragging_start_pos, legal_moves, ARROW_COLOR, drawn_arrows, arrow_start_square, arrow_end_square, drawing_arrow, highlighted_squares, background_image,font)
            
            # Draw GUI improvements
            if last_move is not None:
                draw_last_move_highlight(screen, last_move)
            draw_captured_pieces(screen, captured_white, captured_black, piece_images)
            draw_material_count(screen, board)
            if ai_thinking:
                draw_ai_thinking_indicator(screen, WIDTH, HEIGHT)
            
            draw_pieces(screen, board, piece_images, dragging_piece, dragging_start_pos)
            
            # Draw game result overlay if game ended
            if game_result:
                game_controls.draw_game_status(screen, game_result)
            
            manager.draw_ui(screen)
        elif current_screen == "settings":
            # Create dropdowns if not exist
            if time_dropdown is None:
                time_dropdown = game_controls.create_time_selector()
                level_dropdown = game_controls.create_level_selector()
            
            draw_settings(screen, WIDTH, HEIGHT, HOME_BG_COLOR)
            manager.draw_ui(screen)
        elif current_screen == "about":
            draw_about(screen, WIDTH, HEIGHT, HOME_BG_COLOR)
            manager.draw_ui(screen)
        elif current_screen == "theme":
            draw_theme(screen, WIDTH, HEIGHT, HOME_BG_COLOR)
            manager.draw_ui(screen)

        pygame.display.flip()

    pygame.quit()

# Draw chess board
def draw_board(screen, board, piece_images, LIGHT, DARK, HIGHLIGHT, dragging_piece, dragging_start_pos, legal_moves, ARROW_COLOR, drawn_arrows, arrow_start_square, arrow_end_square, drawing_arrow, highlighted_squares, background_image,font): # Thêm background_image vào đây
    if background_image:
        screen.blit(background_image, (0, 0))

        # Vẽ tọa độ chữ cái (a-h) dưới bàn cờ
        font_color = (0, 0, 0)  # Màu chữ tọa độ (đen)
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for i, letter in enumerate(letters):
            text_surface = font.render(letter, True, font_color)
            text_rect = text_surface.get_rect(
                center=((i * 64) + 32, 8 * 64 - 15))  # X: center ô, Y: dưới hàng 8, lùi lên 1 chút
            screen.blit(text_surface, text_rect)

        # Vẽ tọa độ số (1-8) bên trái bàn cờ
        numbers = ['8', '7', '6', '5', '4', '3', '2', '1']  # Đảo ngược thứ tự để '8' ở trên cùng
        for i, number in enumerate(numbers):
            text_surface = font.render(number, True, font_color)
            text_rect = text_surface.get_rect(center=(-15, (i * 64) + 32))  # X: lùi về bên trái, Y: center ô
            screen.blit(text_surface, text_rect)

        # Vẽ viền bàn cờ (màu xanh đậm, ví dụ)
        BORDER_COLOR = (70, 130, 180)  # SteelBlue
        BORDER_WIDTH = 10
        BOARD_RECT = pygame.Rect(0, 0, 8 * 64 + 2 * BORDER_WIDTH,
                                 8 * 64 + 2 * BORDER_WIDTH)  # Rect bao quanh bàn cờ và viền
        BOARD_RECT.center = (4 * 64, 4 * 64)  # Canh giữa viền
        pygame.draw.rect(screen, BORDER_COLOR, BOARD_RECT, border_radius=5)  # Vẽ viền hình chữ nhật bo tròn góc

    for row in range(8):
        for col in range(8):
            color = LIGHT if (row + col) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, (col * 64, row * 64, 64, 64))

    if selected_square is not None:
        for move in legal_moves:
            row = 7 - (move.to_square // 8)
            col = move.to_square % 8
            pygame.draw.rect(screen, HIGHLIGHT, (col * 64, row * 64, 64, 64))

    # Vẽ vòng tròn khoanh vùng cho NHIỀU ô vuông
    for sq in highlighted_squares:
        center = get_square_center(sq)
        radius = 30
        pygame.draw.circle(screen, ARROW_COLOR, center, radius, 3)

    # Draw existing arrows
    for start_sq, end_sq in drawn_arrows:
        start_pos = get_square_center(start_sq)
        end_pos = get_square_center(end_sq)
        draw_arrow(screen, ARROW_COLOR, start_pos, end_pos)

    # Draw arrow being drawn currently
    if drawing_arrow and arrow_start_square is not None and arrow_end_square is not None:
        start_pos = get_square_center(arrow_start_square)
        end_pos = arrow_end_square
        draw_arrow(screen, ARROW_COLOR, start_pos, end_pos)


def draw_arrow(screen, color, start_pos, end_pos):
    pygame.draw.line(screen, color, start_pos, end_pos, 5)
    arrowhead_points = calculate_arrowhead_points(start_pos, end_pos)
    pygame.draw.polygon(screen, color, arrowhead_points)

def calculate_arrowhead_points(start_pos, end_pos):
    arrow_length = 20
    arrow_width = 10
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    length = (dx**2 + dy**2)**0.5
    if length == 0:
        return []

    normalized_dx = dx / length
    normalized_dy = dy / length

    arrow_tip = end_pos

    arrow_left = (
        int(end_pos[0] - arrow_length * normalized_dx + arrow_width * normalized_dy),
        int(end_pos[1] - arrow_length * normalized_dy - arrow_width * normalized_dx)
    )
    arrow_right = (
        int(end_pos[0] - arrow_length * normalized_dx - arrow_width * normalized_dy),
        int(end_pos[1] - arrow_length * normalized_dy + arrow_width * normalized_dx)
    )
    return [arrow_tip, arrow_left, arrow_right]


def get_square_center(square):
    row = 7 - (square // 8)
    col = square % 8
    return (col * 64 + 32, row * 64 + 32)

def get_square_from_pos(pos):
    col = pos[0] // 64
    row = 7 - (pos[1] // 64)
    if 0 <= col < 8 and 0 <= row < 8:
        return chess.square(col, row)
    return None

# Draw pieces on the board
def draw_pieces(screen, board, piece_images, dragging_piece, dragging_start_pos):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_symbol = piece.symbol()
            piece_name_lowercase = piece_symbol.lower()
            piece_key = f"{'w' if piece.color else 'b'}{piece_name_lowercase}"
            img = piece_images[piece_key]
            row = 7 - (square // 8)
            col = square % 8
            screen.blit(img, (col * 64, row * 64))

    if dragging_piece:
        screen.blit(dragging_piece, (dragging_start_pos[0] - 32, dragging_start_pos[1] - 32))

# Draw settings screen
def draw_settings(screen, WIDTH, HEIGHT, bg_color):
    screen.fill(bg_color)
    font = pygame.font.Font(None, 36)
    text = font.render("Settings Screen", True, (0, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

# Draw about screen
def draw_about(screen, WIDTH, HEIGHT, bg_color):
    screen.fill(bg_color)
    font = pygame.font.Font(None, 36)
    text = font.render("About Screen", True, (0, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

# Draw theme screen
def draw_theme(screen, WIDTH, HEIGHT, bg_color):
    screen.fill(bg_color)
    font = pygame.font.Font(None, 36)
    text = font.render("Theme Screen", True, (0, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

selected_square = None

def handle_mouse_down(pos, button):
    global selected_square, dragging_piece, dragging_start_pos, legal_moves
    global drawing_arrow, arrow_start_square, arrow_end_square, drawn_arrows, highlighted_squares

    square = get_square_from_pos(pos)

    if button == 1: # Left mouse button
        drawn_arrows = []
        highlighted_squares.clear()
        selected_square = None
        if square is not None:
            if board.piece_at(square) and board.piece_at(square).color == board.turn:
                selected_square = square
                dragging_piece = piece_images[f"{'w' if board.piece_at(square).color else 'b'}{board.piece_at(square).symbol().lower()}"]
                dragging_start_pos = pos
                legal_moves = [move for move in board.legal_moves if move.from_square == selected_square]
    elif button == 3: # Right mouse button
        if square is not None:
            drawing_arrow = True
            arrow_start_square = square
            arrow_end_square = pos
            if square in highlighted_squares:
                highlighted_squares.remove(square)
            else:
                highlighted_squares.add(square)

def handle_mouse_up(pos, button):
    global selected_square, dragging_piece, dragging_start_pos, legal_moves
    global drawing_arrow, arrow_start_square, arrow_end_square, drawn_arrows, highlighted_squares
    global game_controls
    move_made = False

    square = get_square_from_pos(pos)

    if button == 1: # Left mouse button
        if selected_square is not None and square is not None:
            move = chess.Move(selected_square, square)
            if move in board.legal_moves:
                board.push(move)
                move_made = True
                if not board.is_game_over() and board.turn == chess.BLACK:
                    ai_move()
        selected_square = None
        dragging_piece = None
        dragging_start_pos = None
        legal_moves = []
    elif button == 3: # Right mouse button
        drawing_arrow = False
        if arrow_start_square is not None and square is not None and square != arrow_start_square:
            drawn_arrows.append((arrow_start_square, square))
        arrow_start_square = None
        arrow_end_square = None
    return move_made

def handle_mouse_motion(pos):
    global dragging_start_pos
    global arrow_end_square

    dragging_start_pos = pos
    arrow_end_square = pos

# AI move function - UPDATED with threading and AI level
def ai_move():
    global ai_thinking, game_controls
    
    # Set AI thinking flag
    ai_thinking = True
    
    # Try opening book first (if available)
    move = None
    if opening_book is not None:
        try:
            move = opening_book.get_move(board)
            if move is not None:
                print(f"📖 Opening book: {move}")
                board.push(move)
                track_captured_pieces(move, board)
                ai_thinking = False
                return
        except Exception as e:
            print(f"⚠️  Error using opening book: {e}")
    
    # If no book move, use AI search in background thread
    # Get AI settings from game_controls
    ai_level = game_controls.get_selected_ai_level()
    print(f"🤖 AI thinking... (Level: {ai_level['name']})")
    
    board_copy = board.copy()
    ai_move_threaded(board_copy, depth=ai_level['depth'], time_limit=ai_level['time'])

if __name__ == "__main__":
    run_gui()