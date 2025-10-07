"""
Game Controls UI - Lichess style
Thêm các nút điều khiển game: Resign, Rematch, Settings, Home
"""
import pygame
import pygame_gui
from pygame_gui.core import ObjectID

class GameControls:
    """Class quản lý các nút điều khiển trong game"""
    
    def __init__(self, manager, screen_width=800, screen_height=600):
        self.manager = manager
        self.width = screen_width
        self.height = screen_height
        
        # Game control buttons
        self.resign_button = None
        self.draw_button = None
        self.rematch_button = None
        self.home_button = None
        
        # Game settings
        self.time_controls = {
            'bullet_1': {'time': 60, 'name': 'Bullet 1+0', 'increment': 0},
            'bullet_2': {'time': 120, 'name': 'Bullet 2+1', 'increment': 1},
            'blitz_3': {'time': 180, 'name': 'Blitz 3+0', 'increment': 0},
            'blitz_5': {'time': 300, 'name': 'Blitz 5+0', 'increment': 0},
            'rapid_10': {'time': 600, 'name': 'Rapid 10+0', 'increment': 0},
            'rapid_15': {'time': 900, 'name': 'Rapid 15+10', 'increment': 10},
            'classical': {'time': 1800, 'name': 'Classical 30+0', 'increment': 0},
        }
        
        self.ai_levels = {
            'easy': {'depth': 2, 'time': 1.0, 'name': 'Easy (Beginner)'},
            'medium': {'depth': 3, 'time': 3.0, 'name': 'Medium (Intermediate)'},
            'hard': {'depth': 4, 'time': 5.0, 'name': 'Hard (Advanced)'},
            'expert': {'depth': 5, 'time': 10.0, 'name': 'Expert (Master)'},
        }
        
        self.selected_time = 'blitz_5'  # Default
        self.selected_level = 'hard'    # Default
        
    def create_game_buttons(self):
        """Tạo các nút điều khiển trong game (hiện khi đang chơi)"""
        button_width = 100
        button_height = 40
        button_x = self.width - button_width - 20
        spacing = 50
        start_y = 180
        
        # Resign button (red)
        self.resign_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((button_x, start_y), (button_width, button_height)),
            text='⚔ Resign',
            manager=self.manager,
            object_id=ObjectID(class_id='@danger_button')
        )
        
        # Draw offer button
        self.draw_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((button_x, start_y + spacing), (button_width, button_height)),
            text='🤝 Draw',
            manager=self.manager,
            object_id=ObjectID(class_id='@secondary_button')
        )
        
        # Rematch button (hidden initially)
        self.rematch_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((button_x, start_y + spacing * 2), (button_width, button_height)),
            text='🔄 Rematch',
            manager=self.manager,
            object_id=ObjectID(class_id='@success_button')
        )
        self.rematch_button.hide()
        
        # Home button
        self.home_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((button_x, start_y + spacing * 3), (button_width, button_height)),
            text='🏠 Home',
            manager=self.manager,
            object_id=ObjectID(class_id='@secondary_button')
        )
        
        # Hide all initially
        self.hide_game_buttons()
        
    def show_game_buttons(self, game_active=True):
        """Hiện các nút điều khiển game"""
        if self.resign_button:
            if game_active:
                self.resign_button.show()
                self.draw_button.show()
                self.rematch_button.hide()
            else:  # Game ended
                self.resign_button.hide()
                self.draw_button.hide()
                self.rematch_button.show()
            self.home_button.show()
    
    def hide_game_buttons(self):
        """Ẩn tất cả nút điều khiển"""
        if self.resign_button:
            self.resign_button.hide()
            self.draw_button.hide()
            self.rematch_button.hide()
            self.home_button.hide()
    
    def create_time_selector(self):
        """Tạo dropdown chọn thời gian (cho màn hình settings)"""
        options = [control['name'] for control in self.time_controls.values()]
        
        time_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=options,
            starting_option=self.time_controls[self.selected_time]['name'],
            relative_rect=pygame.Rect((250, 200), (300, 40)),
            manager=self.manager,
            object_id=ObjectID(class_id='@dropdown')
        )
        return time_dropdown
    
    def create_level_selector(self):
        """Tạo dropdown chọn cấp độ AI (cho màn hình settings)"""
        options = [level['name'] for level in self.ai_levels.values()]
        
        level_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=options,
            starting_option=self.ai_levels[self.selected_level]['name'],
            relative_rect=pygame.Rect((250, 280), (300, 40)),
            manager=self.manager,
            object_id=ObjectID(class_id='@dropdown')
        )
        return level_dropdown
    
    def get_selected_time_control(self):
        """Lấy time control đã chọn"""
        return self.time_controls[self.selected_time]
    
    def get_selected_ai_level(self):
        """Lấy AI level đã chọn"""
        return self.ai_levels[self.selected_level]
    
    def set_time_control(self, time_name):
        """Set time control từ tên"""
        for key, control in self.time_controls.items():
            if control['name'] == time_name:
                self.selected_time = key
                return True
        return False
    
    def set_ai_level(self, level_name):
        """Set AI level từ tên"""
        for key, level in self.ai_levels.items():
            if level['name'] == level_name:
                self.selected_level = key
                return True
        return False
    
    def draw_game_status(self, screen, game_result=None):
        """Vẽ thông báo kết quả game (như Lichess)"""
        if not game_result:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Result card
        card_width = 400
        card_height = 200
        card_x = (self.width - card_width) // 2
        card_y = (self.height - card_height) // 2
        
        # Card background
        card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, (40, 45, 50, 250), (0, 0, card_width, card_height), border_radius=15)
        pygame.draw.rect(card_surface, (100, 150, 200, 200), (0, 0, card_width, card_height), width=3, border_radius=15)
        screen.blit(card_surface, (card_x, card_y))
        
        # Result text
        font_large = pygame.font.Font(None, 64)
        font_small = pygame.font.Font(None, 32)
        
        # Determine result
        if game_result == 'white_win':
            title = "White Wins!"
            subtitle = "by resignation"
            color = (100, 200, 100)
        elif game_result == 'black_win':
            title = "Black Wins!"
            subtitle = "by resignation"
            color = (220, 100, 100)
        elif game_result == 'draw':
            title = "Draw!"
            subtitle = "by agreement"
            color = (200, 200, 100)
        elif game_result == 'checkmate_white':
            title = "White Wins!"
            subtitle = "by checkmate"
            color = (100, 200, 100)
        elif game_result == 'checkmate_black':
            title = "Black Wins!"
            subtitle = "by checkmate"
            color = (220, 100, 100)
        elif game_result == 'stalemate':
            title = "Draw!"
            subtitle = "by stalemate"
            color = (200, 200, 100)
        elif game_result == 'timeout_white':
            title = "White Wins!"
            subtitle = "on time"
            color = (100, 200, 100)
        elif game_result == 'timeout_black':
            title = "Black Wins!"
            subtitle = "on time"
            color = (220, 100, 100)
        else:
            title = "Game Over"
            subtitle = ""
            color = (200, 200, 200)
        
        title_text = font_large.render(title, True, color)
        title_rect = title_text.get_rect(center=(self.width // 2, card_y + 70))
        screen.blit(title_text, title_rect)
        
        if subtitle:
            subtitle_text = font_small.render(subtitle, True, (180, 180, 180))
            subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, card_y + 130))
            screen.blit(subtitle_text, subtitle_rect)

# Singleton instance
_game_controls_instance = None

def get_game_controls(manager=None, width=800, height=600):
    """Get or create GameControls singleton"""
    global _game_controls_instance
    if _game_controls_instance is None and manager is not None:
        _game_controls_instance = GameControls(manager, width, height)
    return _game_controls_instance
