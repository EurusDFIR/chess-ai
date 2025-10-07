# src/ai/analysis_engine.py
"""
Chess Analysis Engine
Provides detailed position analysis, best moves, and move annotations
"""

import chess
import chess.pgn
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import threading
import queue

from src.ai.minimax_optimized import get_best_move
from src.ai.evaluation import evaluate


class MoveQuality(Enum):
    """Move quality annotations"""
    BRILLIANT = "!!"      # Brilliant move
    GOOD = "!"            # Good move
    INTERESTING = "!?"    # Interesting move
    DUBIOUS = "?!"        # Dubious move
    MISTAKE = "?"         # Mistake
    BLUNDER = "??"        # Blunder
    BOOK = ""             # Book move
    FORCED = ""           # Only legal move


@dataclass
class AnalysisResult:
    """Result of position analysis"""
    position_fen: str
    evaluation: float           # Centipawn evaluation (positive = white advantage)
    best_move: Optional[chess.Move]
    best_line: List[chess.Move]  # Principal variation
    depth: int
    nodes_searched: int
    time_ms: int
    
    # Alternative moves
    alternatives: List[Tuple[chess.Move, float]]  # [(move, eval), ...]
    
    def __str__(self):
        eval_str = f"{self.evaluation/100:.2f}"
        if self.evaluation > 0:
            eval_str = f"+{eval_str}"
        
        best_move_str = self.best_move.uci() if self.best_move else "None"
        return f"Eval: {eval_str} | Best: {best_move_str} | Depth: {self.depth}"


@dataclass
class MoveAnalysis:
    """Analysis of a played move"""
    move: chess.Move
    position_before: str  # FEN
    position_after: str   # FEN
    
    eval_before: float
    eval_after: float
    eval_loss: float      # How much evaluation dropped
    
    best_move: Optional[chess.Move]
    quality: MoveQuality
    comment: str
    
    alternatives: List[Tuple[chess.Move, float]]


class AnalysisEngine:
    """
    Chess analysis engine with caching and threading support
    """
    
    def __init__(self, depth: int = 3, max_cache_size: int = 1000):
        self.depth = depth
        self.max_cache_size = max_cache_size
        self._analysis_cache: Dict[str, AnalysisResult] = {}
        
        # Threading
        self._analysis_thread: Optional[threading.Thread] = None
        self._stop_analysis = threading.Event()
        self._analysis_queue = queue.Queue()
        
    def analyze_position(
        self, 
        board: chess.Board, 
        depth: Optional[int] = None,
        get_alternatives: bool = True
    ) -> AnalysisResult:
        """
        Analyze a single position
        
        Args:
            board: Chess board to analyze
            depth: Search depth (uses default if None)
            get_alternatives: Whether to calculate alternative moves
            
        Returns:
            AnalysisResult with evaluation and best moves
        """
        if depth is None:
            depth = self.depth
            
        fen = board.fen()
        
        # Check cache
        cache_key = f"{fen}_{depth}"
        if cache_key in self._analysis_cache:
            return self._analysis_cache[cache_key]
        
        # Perform analysis
        import time
        start_time = time.time()
        
        # Get best move and evaluation using optimized minimax
        best_move = get_best_move(board.copy(), depth=depth, time_limit=10.0)
        
        # Get evaluation for best move
        if best_move:
            board_copy = board.copy()
            board_copy.push(best_move)
            evaluation = -evaluate(board_copy)  # Negate because we switched sides
        else:
            evaluation = evaluate(board)
        
        time_ms = int((time.time() - start_time) * 1000)
        
        # Get principal variation (simplified - just best move for now)
        best_line = [best_move] if best_move else []
        
        # Get alternative moves if requested
        alternatives = []
        if get_alternatives and best_move:
            alternatives = self._get_alternative_moves(board, depth, best_move, evaluation)
        
        result = AnalysisResult(
            position_fen=fen,
            evaluation=evaluation,
            best_move=best_move,
            best_line=best_line,
            depth=depth,
            nodes_searched=0,  # TODO: Track in minimax
            time_ms=time_ms,
            alternatives=alternatives
        )
        
        # Cache result
        if len(self._analysis_cache) >= self.max_cache_size:
            # Remove oldest entry (simple FIFO)
            self._analysis_cache.pop(next(iter(self._analysis_cache)))
        self._analysis_cache[cache_key] = result
        
        return result
    
    def _get_alternative_moves(
        self,
        board: chess.Board,
        depth: int,
        best_move: chess.Move,
        best_eval: float,
        top_n: int = 3
    ) -> List[Tuple[chess.Move, float]]:
        """Get top N alternative moves with evaluations"""
        alternatives = []
        
        for move in board.legal_moves:
            if move == best_move:
                continue
            
            # Evaluate this move
            board_copy = board.copy()
            board_copy.push(move)
            eval_score = -evaluate(board_copy)  # Negate for opponent's perspective
            
            alternatives.append((move, eval_score))
        
        # Sort by evaluation and return top N
        alternatives.sort(key=lambda x: x[1], reverse=(board.turn == chess.WHITE))
        return alternatives[:top_n]
    
    def analyze_move(
        self,
        board_before: chess.Board,
        move: chess.Move,
        depth: Optional[int] = None
    ) -> MoveAnalysis:
        """
        Analyze a specific move that was played
        
        Args:
            board_before: Board position before the move
            move: The move that was played
            depth: Analysis depth
            
        Returns:
            MoveAnalysis with quality assessment
        """
        if depth is None:
            depth = self.depth
        
        # Analyze position before move
        analysis_before = self.analyze_position(board_before, depth)
        
        # Make the move
        board_after = board_before.copy()
        board_after.push(move)
        
        # Analyze position after move
        analysis_after = self.analyze_position(board_after, depth)
        
        # Calculate evaluation loss (from perspective of player who moved)
        if board_before.turn == chess.WHITE:
            eval_before = analysis_before.evaluation
            eval_after = -analysis_after.evaluation  # Negate because turn switched
        else:
            eval_before = -analysis_before.evaluation
            eval_after = analysis_after.evaluation
        
        eval_loss = eval_before - eval_after
        
        # Determine move quality
        quality, comment = self._assess_move_quality(
            move,
            analysis_before.best_move,
            eval_loss,
            board_before
        )
        
        return MoveAnalysis(
            move=move,
            position_before=board_before.fen(),
            position_after=board_after.fen(),
            eval_before=eval_before,
            eval_after=eval_after,
            eval_loss=eval_loss,
            best_move=analysis_before.best_move,
            quality=quality,
            comment=comment,
            alternatives=analysis_before.alternatives
        )
    
    def _assess_move_quality(
        self,
        played_move: chess.Move,
        best_move: Optional[chess.Move],
        eval_loss: float,
        board: chess.Board
    ) -> Tuple[MoveQuality, str]:
        """
        Assess the quality of a move based on evaluation loss
        
        Thresholds (in centipawns):
        - Brilliant (!!): Best move in complex position
        - Good (!): Best move or eval loss < 10cp
        - Interesting (!?): Eval loss 10-50cp with compensation
        - Dubious (?!): Eval loss 50-100cp
        - Mistake (?): Eval loss 100-300cp
        - Blunder (??): Eval loss > 300cp
        """
        # Only one legal move = forced
        if board.legal_moves.count() == 1:
            return MoveQuality.FORCED, "Forced move"
        
        # Best move
        if best_move and played_move == best_move:
            # Check if position is complex for brilliant move
            if board.legal_moves.count() > 30 and eval_loss < 0:
                return MoveQuality.BRILLIANT, "Brilliant move!"
            return MoveQuality.GOOD, "Best move"
        
        # Assess based on evaluation loss
        if eval_loss < 0:
            return MoveQuality.BRILLIANT, "Even better than expected!"
        elif eval_loss < 10:
            return MoveQuality.GOOD, "Excellent move"
        elif eval_loss < 50:
            return MoveQuality.INTERESTING, "Interesting alternative"
        elif eval_loss < 100:
            return MoveQuality.DUBIOUS, "Dubious move"
        elif eval_loss < 300:
            return MoveQuality.MISTAKE, "Mistake - better was " + (best_move.uci() if best_move else "")
        else:
            return MoveQuality.BLUNDER, "Blunder! Play " + (best_move.uci() if best_move else "")
    
    def analyze_game(
        self,
        pgn_string: str,
        depth: Optional[int] = None,
        progress_callback=None
    ) -> List[MoveAnalysis]:
        """
        Analyze an entire game from PGN
        
        Args:
            pgn_string: PGN string of the game
            depth: Analysis depth
            progress_callback: Optional callback(move_num, total_moves)
            
        Returns:
            List of MoveAnalysis for each move
        """
        import io
        pgn = chess.pgn.read_game(io.StringIO(pgn_string))
        
        if not pgn:
            return []
        
        board = pgn.board()
        move_analyses = []
        
        moves = list(pgn.mainline_moves())
        total_moves = len(moves)
        
        for i, move in enumerate(moves):
            # Analyze this move
            analysis = self.analyze_move(board, move, depth)
            move_analyses.append(analysis)
            
            # Make the move
            board.push(move)
            
            # Progress callback
            if progress_callback:
                progress_callback(i + 1, total_moves)
        
        return move_analyses
    
    def start_background_analysis(self, board: chess.Board, callback):
        """
        Start analyzing position in background thread
        
        Args:
            board: Position to analyze
            callback: Function to call with AnalysisResult when done
        """
        self._stop_analysis.clear()
        
        def analyze_thread():
            result = self.analyze_position(board.copy())
            if not self._stop_analysis.is_set():
                callback(result)
        
        self._analysis_thread = threading.Thread(target=analyze_thread, daemon=True)
        self._analysis_thread.start()
    
    def stop_background_analysis(self):
        """Stop any running background analysis"""
        self._stop_analysis.set()
        if self._analysis_thread:
            self._analysis_thread.join(timeout=1.0)
    
    def clear_cache(self):
        """Clear the analysis cache"""
        self._analysis_cache.clear()
    
    def set_depth(self, depth: int):
        """Set analysis depth"""
        self.depth = depth
        self.clear_cache()  # Clear cache as depth changed
