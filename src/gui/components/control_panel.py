"""
Control Panel - Lichess-style icon buttons
"""
import pygame
import pygame_gui
from pygame_gui.core import ObjectID


class ControlPanel:
    """Panel chứa các nút điều khiển - Lichess style"""
    
    def __init__(self, manager, screen_width=800):
        self.manager = manager
        self.width = screen_width
        
        # Buttons
        self.resign_button = None
        self.draw_button = None
        self.rematch_button = None
        self.home_button = None
        self.analysis_button = None
        
        self._create_buttons()
    
    def _create_buttons(self):
        """Tạo các nút điều khiển - Compact text buttons"""
        # Smaller, more compact buttons
        button_width = 80
        button_height = 35
        button_x = self.width - button_width - 20
        spacing = 8
        start_y = 390
        
        # Resign button
        self.resign_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((button_x, start_y), (button_width, button_height)),
            text='Resign',
            manager=self.manager,
            object_id=ObjectID(class_id='@compact_danger'),
            tool_tip_text='Resign the game'
        )
        
        # Draw button
        self.draw_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((button_x, start_y + (button_height + spacing)), 
                                     (button_width, button_height)),
            text='Draw',
            manager=self.manager,
            object_id=ObjectID(class_id='@compact_button'),
            tool_tip_text='Offer Draw'
        )
        
        # Analysis button
        self.analysis_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((button_x, start_y + (button_height + spacing) * 2), 
                                     (button_width, button_height)),
            text='Analysis',
            manager=self.manager,
            object_id=ObjectID(class_id='@compact_info'),
            tool_tip_text='Toggle Analysis'
        )
        
        # Rematch button (hidden initially)
        self.rematch_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((button_x, start_y + (button_height + spacing) * 3), 
                                     (button_width, button_height)),
            text='Rematch',
            manager=self.manager,
            object_id=ObjectID(class_id='@compact_success'),
            tool_tip_text='Play Again'
        )
        
        # Home button
        self.home_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((button_x, start_y + (button_height + spacing) * 4), 
                                     (button_width, button_height)),
            text='Home',
            manager=self.manager,
            object_id=ObjectID(class_id='@compact_button'),
            tool_tip_text='Return Home'
        )
        
        self.hide_all()
    
    def show_playing(self):
        """Hiển thị buttons khi đang chơi"""
        self.resign_button.show()
        self.draw_button.show()
        self.analysis_button.show()
        self.rematch_button.hide()
        self.home_button.show()
    
    def show_finished(self):
        """Hiển thị buttons khi game kết thúc"""
        self.resign_button.hide()
        self.draw_button.hide()
        self.analysis_button.show()
        self.rematch_button.show()
        self.home_button.show()
    
    def hide_all(self):
        """Ẩn tất cả buttons"""
        if self.resign_button:
            self.resign_button.hide()
        if self.draw_button:
            self.draw_button.hide()
        if self.analysis_button:
            self.analysis_button.hide()
        if self.rematch_button:
            self.rematch_button.hide()
        if self.home_button:
            self.home_button.hide()
