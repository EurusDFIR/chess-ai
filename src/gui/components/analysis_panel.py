# src/gui/components/analysis_panel.py
"""
Analysis Panel Widget
Shows best moves, evaluation, and move quality annotations
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIButton
from typing import Optional, List, Tuple
import chess

from src.ai.analysis_engine import AnalysisResult, MoveAnalysis, MoveQuality


class AnalysisPanel:
    """
    Panel showing position analysis with best moves and annotations
    """
    
    def __init__(
        self,
        rect: pygame.Rect,
        manager: pygame_gui.UIManager,
        board: chess.Board
    ):
        """
        Initialize analysis panel
        
        Args:
            rect: Panel rectangle
            manager: pygame_gui manager
            board: Chess board to analyze
        """
        self.rect = rect
        self.manager = manager
        self.board = board
        
        # Create panel
        self.panel = UIPanel(
            relative_rect=rect,
            starting_height=1,
            manager=manager,
            object_id=pygame_gui.core.ObjectID(class_id='@analysis_panel')
        )
        
        # Current analysis results
        self.current_analysis: Optional[AnalysisResult] = None
        self.move_analysis: Optional[MoveAnalysis] = None
        
        # UI Elements
        self._create_ui()
    
    def set_board(self, board: chess.Board):
        """Update the board reference for move conversions"""
        self.board = board
        
    def _create_ui(self):
        """Create UI elements"""
        padding = 10
        y_pos = padding
        
        # Title
        self.title_label = UILabel(
            relative_rect=pygame.Rect(padding, y_pos, self.rect.width - 2*padding, 30),
            text='Analysis',
            manager=self.manager,
            container=self.panel,
            object_id=pygame_gui.core.ObjectID(class_id='@analysis_title')
        )
        y_pos += 35
        
        # Evaluation display
        self.eval_label = UILabel(
            relative_rect=pygame.Rect(padding, y_pos, self.rect.width - 2*padding, 25),
            text='Evaluation: 0.00',
            manager=self.manager,
            container=self.panel
        )
        y_pos += 30
        
        # Best move display
        self.best_move_label = UILabel(
            relative_rect=pygame.Rect(padding, y_pos, self.rect.width - 2*padding, 25),
            text='Best move: --',
            manager=self.manager,
            container=self.panel
        )
        y_pos += 30
        
        # Move quality (when analyzing played moves)
        self.quality_label = UILabel(
            relative_rect=pygame.Rect(padding, y_pos, self.rect.width - 2*padding, 25),
            text='',
            manager=self.manager,
            container=self.panel
        )
        y_pos += 30
        
        # Analysis details (plain label instead of text box to avoid scrollbar bug)
        self.details_label = UILabel(
            relative_rect=pygame.Rect(
                padding,
                y_pos,
                self.rect.width - 2*padding,
                self.rect.height - y_pos - 60
            ),
            text='Position analysis will appear here...',
            manager=self.manager,
            container=self.panel
        )
        y_pos = self.rect.height - 50
        
        # Analyze button
        self.analyze_button = UIButton(
            relative_rect=pygame.Rect(
                padding,
                y_pos,
                self.rect.width - 2*padding,
                35
            ),
            text='Analyze Position',
            manager=self.manager,
            container=self.panel
        )
    
    def update_analysis(self, analysis: AnalysisResult):
        """
        Update panel with new analysis results
        
        Args:
            analysis: AnalysisResult from engine
        """
        self.current_analysis = analysis
        self.move_analysis = None  # Clear move analysis
        
        # Update evaluation
        eval_str = self._format_evaluation(analysis.evaluation)
        self.eval_label.set_text(f'Evaluation: {eval_str}')
        
        # Update best move
        if analysis.best_move:
            self.best_move_label.set_text(
                f'Best move: {self.board.san(analysis.best_move)}'
            )
        else:
            self.best_move_label.set_text('Best move: --')
        
        # Clear quality label
        self.quality_label.set_text('')
        
        # Update details
        self._update_details_label()
    
    def update_move_analysis(self, move_analysis: MoveAnalysis):
        """
        Update panel with move analysis
        
        Args:
            move_analysis: MoveAnalysis for a played move
        """
        self.move_analysis = move_analysis
        
        # Update evaluation
        eval_str = self._format_evaluation(move_analysis.eval_after)
        self.eval_label.set_text(f'Evaluation: {eval_str}')
        
        # Update best move (what should have been played)
        if move_analysis.best_move:
            self.best_move_label.set_text(
                f'Best was: {self._move_to_san(move_analysis.best_move, move_analysis.position_before)}'
            )
        else:
            self.best_move_label.set_text('Best move: --')
        
        # Update move quality
        quality_text = self._format_move_quality(move_analysis)
        self.quality_label.set_text(quality_text)
        
        # Update details
        self._update_details_label()
    
    def _update_details_label(self):
        """Update the details label with analysis information"""
        text_parts = []
        
        if self.move_analysis:
            # Showing move analysis
            ma = self.move_analysis
            
            text_parts.append(f'Move: {self._move_to_san(ma.move, ma.position_before)}')
            text_parts.append(f'Quality: {ma.quality.value} {ma.comment}')
            text_parts.append(f'Eval: {self._format_evaluation(ma.eval_before)} -> {self._format_evaluation(ma.eval_after)}')
            
            if ma.eval_loss > 0:
                text_parts.append(f'Loss: {ma.eval_loss:.0f} cp')
            
            text_parts.append('')
            text_parts.append('Alternatives:')
            
            if ma.alternatives:
                for i, (move, eval_score) in enumerate(ma.alternatives[:3], 1):
                    move_san = self._move_to_san(move, ma.position_before)
                    eval_str = self._format_evaluation(eval_score)
                    text_parts.append(f'{i}. {move_san} ({eval_str})')
            else:
                text_parts.append('None')
                
        elif self.current_analysis:
            # Showing position analysis
            analysis = self.current_analysis
            
            text_parts.append(f'Depth: {analysis.depth}')
            text_parts.append(f'Time: {analysis.time_ms}ms')
            
            if analysis.best_move:
                text_parts.append(f'Best: {self.board.san(analysis.best_move)}')
            
            text_parts.append('')
            text_parts.append('Top moves:')
            
            if analysis.alternatives:
                for i, (move, eval_score) in enumerate(analysis.alternatives[:3], 1):
                    move_san = self.board.san(move)
                    eval_str = self._format_evaluation(eval_score)
                    text_parts.append(f'{i}. {move_san} ({eval_str})')
            else:
                text_parts.append('Calculating...')
        else:
            text_parts.append('No analysis data')
            text_parts.append('')
            text_parts.append('Click "Analyze Position"')
        
        self.details_label.set_text('\n'.join(text_parts))
    
    def _format_evaluation(self, eval_cp: float) -> str:
        """Format evaluation as string (eval_cp is in raw score, need to convert to pawns)"""
        if abs(eval_cp) > 9000:
            mate_in = int((10000 - abs(eval_cp)) / 100)
            return f"M{mate_in}" if eval_cp > 0 else f"-M{mate_in}"
        else:
            # Convert centipawn (raw score) to pawn units
            return f"{eval_cp/100:+.2f}"
    
    def _format_move_quality(self, move_analysis: MoveAnalysis) -> str:
        """Format move quality with color coding"""
        quality = move_analysis.quality
        
        quality_colors = {
            MoveQuality.BRILLIANT: 'turquoise',
            MoveQuality.GOOD: 'green',
            MoveQuality.INTERESTING: 'yellow',
            MoveQuality.DUBIOUS: 'orange',
            MoveQuality.MISTAKE: 'orange',
            MoveQuality.BLUNDER: 'red',
        }
        
        color = quality_colors.get(quality, 'white')
        symbol = quality.value
        
        if symbol:
            return f'Move Quality: {symbol}'
        else:
            return 'Move Quality: Book/Forced'
    
    def _move_to_san(self, move: chess.Move, fen: str) -> str:
        """Convert move to SAN notation given a FEN position"""
        temp_board = chess.Board(fen)
        return temp_board.san(move)
    
    def clear(self):
        """Clear all analysis data"""
        self.current_analysis = None
        self.move_analysis = None
        
        self.eval_label.set_text('Evaluation: 0.00')
        self.best_move_label.set_text('Best move: --')
        self.quality_label.set_text('')
        self.details_label.set_text('No analysis data')
    
    def hide(self):
        """Hide the panel"""
        self.panel.hide()
    
    def show(self):
        """Show the panel"""
        self.panel.show()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.analyze_button:
                return True  # Signal to start analysis
        
        return False
