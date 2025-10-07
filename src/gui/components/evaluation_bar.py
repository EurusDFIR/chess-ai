# src/gui/components/evaluation_bar.py
"""
Evaluation Bar Widget
Visual bar showing position evaluation (like Lichess/Chess.com)
"""

import pygame
import math
from typing import Optional


class EvaluationBar:
    """
    Vertical bar showing chess position evaluation
    White advantage = top, Black advantage = bottom
    """
    
    def __init__(self, x: int, y: int, width: int, height: int):
        """
        Initialize evaluation bar
        
        Args:
            x, y: Top-left position
            width: Bar width (typically 20-30px)
            height: Bar height (should match board height)
        """
        self.rect = pygame.Rect(x, y, width, height)
        
        # Colors
        self.color_white = pygame.Color(240, 240, 240)
        self.color_black = pygame.Color(40, 40, 40)
        self.color_border = pygame.Color(100, 100, 100)
        self.color_text = pygame.Color(255, 255, 255)
        
        # Current evaluation
        self.evaluation = 0.0  # Centipawns (positive = white advantage)
        self._display_eval = 0.0  # Smoothed evaluation for animation
        
        # Fonts
        try:
            self.font = pygame.font.SysFont('Arial', 12, bold=True)
        except:
            self.font = pygame.font.Font(None, 14)
    
    def set_evaluation(self, evaluation: float):
        """
        Set the evaluation score
        
        Args:
            evaluation: Centipawn evaluation (positive = white advantage)
                       Use large values (±10000) for mate positions
        """
        self.evaluation = evaluation
    
    def update(self, dt: float):
        """
        Update animation (smooth evaluation changes)
        
        Args:
            dt: Delta time in seconds
        """
        # Smoothly interpolate to target evaluation
        diff = self.evaluation - self._display_eval
        
        if abs(diff) < 1:
            self._display_eval = self.evaluation
        else:
            # Smooth transition
            self._display_eval += diff * min(dt * 5, 1.0)
    
    def draw(self, surface: pygame.Surface):
        """Draw the evaluation bar"""
        # Draw border
        pygame.draw.rect(surface, self.color_border, self.rect, 2)
        
        # Calculate bar fill based on evaluation
        # Map evaluation to percentage (-1000 to +1000 cp → 0% to 100%)
        # Use tanh for smooth clamping
        normalized_eval = math.tanh(self._display_eval / 1000.0)  # -1 to +1
        
        # Convert to 0-1 range (0 = black advantage, 1 = white advantage)
        white_ratio = (normalized_eval + 1.0) / 2.0
        
        # Calculate fill height
        white_height = int(self.rect.height * white_ratio)
        black_height = self.rect.height - white_height
        
        # Draw black portion (top)
        if black_height > 0:
            black_rect = pygame.Rect(
                self.rect.x, 
                self.rect.y,
                self.rect.width,
                black_height
            )
            pygame.draw.rect(surface, self.color_black, black_rect)
        
        # Draw white portion (bottom)
        if white_height > 0:
            white_rect = pygame.Rect(
                self.rect.x,
                self.rect.y + black_height,
                self.rect.width,
                white_height
            )
            pygame.draw.rect(surface, self.color_white, white_rect)
        
        # Draw evaluation text
        self._draw_evaluation_text(surface)
    
    def _draw_evaluation_text(self, surface: pygame.Surface):
        """Draw the evaluation score as text"""
        # Format evaluation
        eval_cp = self._display_eval
        
        # Calculate white_height for text color determination
        normalized_eval = math.tanh(self._display_eval / 1000.0)
        white_ratio = (normalized_eval + 1.0) / 2.0
        white_height = int(self.rect.height * white_ratio)
        
        # Check for mate
        if abs(eval_cp) > 9000:
            mate_in = int((10000 - abs(eval_cp)) / 100)
            if eval_cp > 0:
                text = f"M{mate_in}"
                text_color = self.color_black
            else:
                text = f"M{mate_in}"
                text_color = self.color_white
        else:
            # Regular evaluation
            eval_pawns = eval_cp / 100.0
            text = f"{eval_pawns:+.1f}"
            
            # Color based on advantage
            if white_height > self.rect.height * 0.55:
                text_color = self.color_black
            else:
                text_color = self.color_white
        
        # Render text
        text_surface = self.font.render(text, True, text_color)
        text_rect = text_surface.get_rect()
        
        # Position text in center
        text_rect.centerx = self.rect.centerx
        text_rect.centery = self.rect.centery
        
        # Draw background box for better readability
        bg_padding = 2
        bg_rect = text_rect.inflate(bg_padding * 2, bg_padding * 2)
        
        # Semi-transparent background
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(180)
        bg_surface.fill((128, 128, 128))
        surface.blit(bg_surface, bg_rect)
        
        # Draw text
        surface.blit(text_surface, text_rect)
    
    def get_evaluation_string(self) -> str:
        """
        Get evaluation as formatted string
        
        Returns:
            String like "+1.5", "-0.3", "M5", etc.
        """
        if abs(self.evaluation) > 9000:
            mate_in = int((10000 - abs(self.evaluation)) / 100)
            return f"M{mate_in}" if self.evaluation > 0 else f"-M{mate_in}"
        else:
            return f"{self.evaluation/100:+.2f}"
    
    def reset(self):
        """Reset evaluation to 0"""
        self.evaluation = 0.0
        self._display_eval = 0.0
