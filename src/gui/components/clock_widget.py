"""
Chess Clock Widget - Lichess style
Quản lý đồng hồ cho cả hai người chơi với increment support
"""
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
import chess


class ChessClock:
    """Class quản lý đồng hồ cờ vua với increment"""
    
    def __init__(self, manager, screen_width=800, screen_height=600):
        self.manager = manager
        self.width = screen_width
        self.height = screen_height
        
        # Time settings
        self.white_time = 300.0  # 5 phút mặc định
        self.black_time = 300.0
        self.increment = 0  # Giây tăng thêm sau mỗi nước
        self.initial_time = 300.0
        
        # Game state
        self.current_player = chess.WHITE
        self.is_running = False
        self.is_paused = False
        self.last_update = None
        
        # UI elements
        self.white_clock_label = None
        self.black_clock_label = None
        self._create_ui()
        
    def _create_ui(self):
        """Tạo UI labels cho đồng hồ"""
        clock_width = 180
        clock_height = 60
        clock_margin = 20
        clock_x = self.width - clock_width - clock_margin
        
        # Black clock (top) - với màu nền tương ứng
        self.black_clock_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((clock_x, clock_margin), (clock_width, clock_height)),
            text=self._format_time(self.black_time),
            manager=self.manager,
            object_id=ObjectID(class_id='@clock_black')
        )
        
        # White clock (bottom)
        self.white_clock_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                (clock_x, self.height - clock_height - clock_margin), 
                (clock_width, clock_height)
            ),
            text=self._format_time(self.white_time),
            manager=self.manager,
            object_id=ObjectID(class_id='@clock_white')
        )
        
        # Hide initially
        self.hide()
    
    def _format_time(self, seconds):
        """Format thời gian thành MM:SS"""
        if seconds < 0:
            seconds = 0
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        
        # Nếu dưới 20 giây, hiển thị thêm phần thập phân
        if seconds < 20:
            return f"{minutes:02d}:{seconds:04.1f}"
        return f"{minutes:02d}:{secs:02d}"
    
    def set_time_control(self, time_seconds, increment_seconds=0):
        """Thiết lập time control (thời gian + increment)"""
        self.initial_time = time_seconds
        self.white_time = time_seconds
        self.black_time = time_seconds
        self.increment = increment_seconds
        self.update_display()
    
    def start(self, starting_player=chess.WHITE):
        """Bắt đầu đồng hồ"""
        self.current_player = starting_player
        self.is_running = True
        self.is_paused = False
        self.last_update = pygame.time.get_ticks()
        self.update_display()
    
    def stop(self):
        """Dừng đồng hồ"""
        self.is_running = False
        self.is_paused = False
    
    def pause(self):
        """Tạm dừng đồng hồ (khi AI đang suy nghĩ)"""
        if self.is_running:
            self.is_paused = True
    
    def resume(self):
        """Tiếp tục đồng hồ sau khi pause"""
        if self.is_running:
            self.is_paused = False
            self.last_update = pygame.time.get_ticks()
    
    def reset(self):
        """Reset đồng hồ về thời gian ban đầu"""
        self.white_time = self.initial_time
        self.black_time = self.initial_time
        self.current_player = chess.WHITE
        self.is_running = False
        self.is_paused = False
        self.last_update = None
        self.update_display()
    
    def switch_player(self):
        """Chuyển sang người chơi kế tiếp và thêm increment"""
        if not self.is_running:
            return
        
        # Thêm increment cho người vừa đi
        if self.current_player == chess.WHITE:
            self.white_time += self.increment
            self.current_player = chess.BLACK
        else:
            self.black_time += self.increment
            self.current_player = chess.WHITE
        
        self.last_update = pygame.time.get_ticks()
        self.update_display()
    
    def update(self, delta_time):
        """Cập nhật đồng hồ (gọi mỗi frame)"""
        if not self.is_running or self.is_paused:
            return
        
        # Giảm thời gian của người chơi hiện tại
        if self.current_player == chess.WHITE:
            self.white_time -= delta_time
            if self.white_time < 0:
                self.white_time = 0
                self.stop()
                return 'white_timeout'
        else:
            self.black_time -= delta_time
            if self.black_time < 0:
                self.black_time = 0
                self.stop()
                return 'black_timeout'
        
        self.update_display()
        return None
    
    def update_display(self):
        """Cập nhật hiển thị đồng hồ"""
        if self.white_clock_label:
            self.white_clock_label.set_text(self._format_time(self.white_time))
        if self.black_clock_label:
            self.black_clock_label.set_text(self._format_time(self.black_time))
    
    def show(self):
        """Hiển thị đồng hồ"""
        if self.white_clock_label:
            self.white_clock_label.show()
        if self.black_clock_label:
            self.black_clock_label.show()
    
    def hide(self):
        """Ẩn đồng hồ"""
        if self.white_clock_label:
            self.white_clock_label.hide()
        if self.black_clock_label:
            self.black_clock_label.hide()
    
    def get_times(self):
        """Lấy thời gian hiện tại của cả hai bên"""
        return {
            'white': self.white_time,
            'black': self.black_time,
            'current_player': self.current_player
        }
