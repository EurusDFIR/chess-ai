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
        """Tạo các nút điều khiển - Icon-based như Lichess"""
        # Smaller, more compact buttons
        button_width = 45
        button_height = 45
        button_x = self.width - button_width - 20
        spacing = 8
        start_y = 390
        
        # Resign button - Flag icon
        self.resign_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((button_x, start_y), (button_width, button_height)),
            text='⚑',  # Flag icon
            manager=self.manager,
            object_id=ObjectID(class_id='@icon_button_danger'),
            tool_tip_text='Resign'
        )
        
        # Draw button - 1/2 symbol
        self.draw_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((button_x, start_y + (button_height + spacing)), 
                                     (button_width, button_height)),
            text='½',  # Half symbol
            manager=self.manager,
            object_id=ObjectID(class_id='@icon_button'),
            tool_tip_text='Offer Draw'
        )
        
        # Analysis button - Magnifying glass
        self.analysis_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((button_x, start_y + (button_height + spacing) * 2), 
                                     (button_width, button_height)),
            text='⚙',  # Settings/analysis icon
            manager=self.manager,
            object_id=ObjectID(class_id='@icon_button_info'),
            tool_tip_text='Toggle Analysis'
        )
        
        # Rematch button (hidden initially)
        self.rematch_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((button_x, start_y + (button_height + spacing) * 3), 
                                     (button_width, button_height)),
            text='↻',  # Refresh icon
            manager=self.manager,
            object_id=ObjectID(class_id='@icon_button_success'),
            tool_tip_text='Rematch'
        )
        
        # Home button
        self.home_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((button_x, start_y + (button_height + spacing) * 4), 
                                     (button_width, button_height)),
            text='⌂',  # Home icon
            manager=self.manager,
            object_id=ObjectID(class_id='@icon_button'),
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
