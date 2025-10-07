# demo_analysis_mode.py
"""
Demo script to showcase the new Analysis Mode feature
"""

import chess
from src.ai.analysis_engine import AnalysisEngine, MoveQuality

def demo_position_analysis():
    """Demo: Analyze a single position"""
    print("=" * 60)
    print("DEMO 1: Position Analysis")
    print("=" * 60)
    
    # Create a tactical position (White has a winning tactic)
    fen = "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 1"
    board = chess.Board(fen)
    
    print(f"Position (FEN): {fen}")
    print(f"Board:\n{board}\n")
    
    # Create analysis engine
    engine = AnalysisEngine(depth=3)
    
    # Analyze position
    print("Analyzing position...")
    result = engine.analyze_position(board, depth=3, get_alternatives=True)
    
    print(f"\n{result}")
    print(f"\nEvaluation: {result.evaluation/100:.2f} pawns")
    print(f"Best move: {board.san(result.best_move) if result.best_move else 'None'}")
    print(f"Time taken: {result.time_ms}ms")
    
    if result.alternatives:
        print(f"\nTop alternative moves:")
        for i, (move, eval_score) in enumerate(result.alternatives, 1):
            print(f"  {i}. {board.san(move)} (eval: {eval_score/100:+.2f})")


def demo_move_analysis():
    """Demo: Analyze played moves"""
    print("\n" + "=" * 60)
    print("DEMO 2: Move Quality Analysis")
    print("=" * 60)
    
    board = chess.Board()
    engine = AnalysisEngine(depth=3)
    
    # Test different quality moves
    test_cases = [
        # (move_uci, expected_quality_type, description)
        ("e2e4", "Good/Best", "Best opening move"),
        ("a2a4", "Dubious", "Dubious opening"),
        ("f2f3", "Mistake", "Weakening move"),
    ]
    
    for move_uci, expected, description in test_cases:
        board = chess.Board()  # Reset
        move = chess.Move.from_uci(move_uci)
        
        print(f"\nTesting: {board.san(move)} - {description}")
        analysis = engine.analyze_move(board, move, depth=2)
        
        print(f"  Quality: {analysis.quality.value} {analysis.quality.name}")
        print(f"  Comment: {analysis.comment}")
        print(f"  Eval change: {analysis.eval_before/100:+.2f} → {analysis.eval_after/100:+.2f}")
        print(f"  Accuracy loss: {analysis.eval_loss:.0f} centipawns")
        
        if analysis.best_move and analysis.best_move != move:
            board_temp = chess.Board()
            print(f"  Better was: {board_temp.san(analysis.best_move)}")


def demo_game_analysis():
    """Demo: Analyze a complete game"""
    print("\n" + "=" * 60)
    print("DEMO 3: Full Game Analysis")
    print("=" * 60)
    
    # Sample PGN (Scholar's Mate)
    pgn_string = """[Event "?"]
[Site "?"]
[Date "????.??.??"]
[Round "?"]
[White "?"]
[Black "?"]
[Result "1-0"]

1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7# 1-0"""
    
    print(f"Analyzing game:\n{pgn_string}\n")
    
    engine = AnalysisEngine(depth=2)  # Shallow depth for speed
    
    print("Running analysis...")
    
    def progress(move_num, total):
        print(f"  Progress: {move_num}/{total} moves analyzed")
    
    analyses = engine.analyze_game(pgn_string, depth=2, progress_callback=progress)
    
    print(f"\nGame Analysis Complete!")
    print(f"Total moves: {len(analyses)}")
    
    # Show summary
    print("\nMove-by-move breakdown:")
    for i, analysis in enumerate(analyses, 1):
        board_temp = chess.Board()
        for j in range(i-1):
            board_temp.push(analyses[j].move)
        
        move_san = board_temp.san(analysis.move)
        quality_str = f"{analysis.quality.value}" if analysis.quality.value else ""
        
        move_num = (i + 1) // 2
        color = "White" if i % 2 == 1 else "Black"
        
        print(f"  {move_num}. {color}: {move_san} {quality_str} "
              f"(eval: {analysis.eval_after/100:+.2f}, loss: {analysis.eval_loss:.0f}cp)")


def demo_annotation_symbols():
    """Demo: Move annotation symbols explanation"""
    print("\n" + "=" * 60)
    print("DEMO 4: Move Annotation Symbols")
    print("=" * 60)
    
    print("\nChess annotation symbols used:")
    print("  !! = Brilliant move")
    print("  !  = Good move") 
    print("  !? = Interesting move")
    print("  ?! = Dubious move")
    print("  ?  = Mistake")
    print("  ?? = Blunder")
    print("")
    print("Evaluation thresholds:")
    print("  < 10cp loss   : Good move (!)")
    print("  10-50cp loss  : Interesting (!?)")
    print("  50-100cp loss : Dubious (?!)")
    print("  100-300cp loss: Mistake (?)")
    print("  > 300cp loss  : Blunder (??)")


if __name__ == "__main__":
    print("\n" + "="*60)
    print(" Chess Analysis Engine - Demo")
    print("="*60)
    
    try:
        demo_position_analysis()
        demo_move_analysis()
        demo_game_analysis()
        demo_annotation_symbols()
        
        print("\n" + "="*60)
        print(" Demo Complete!")
        print("="*60)
        print("\nTo use in the GUI:")
        print("1. Start a game")
        print("2. Click the 'Analysis' button")
        print("3. The evaluation bar will show on the left")
        print("4. The analysis panel will show best moves and annotations")
        print("5. Click 'Analyze Position' to refresh analysis")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
