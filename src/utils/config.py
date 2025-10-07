# src/utils/config.py
"""
Configuration file for Chess AI
"""

# AI Configuration
AI_CONFIG = {
    # Search parameters
    'max_depth': 6,              # Maximum search depth (6-8 recommended)
    'time_limit': 10.0,          # Time limit per move in seconds
    'use_iterative_deepening': True,  # Use iterative deepening
    
    # Opening book
    'use_opening_book': True,
    'opening_book_path': r'opening_bin\Performance.bin',  # Default opening book
    
    # Endgame tablebases
    'use_endgame_tb': True,
    'syzygy_path': r'syzygy',
    
    # Transposition table
    'tt_size_mb': 256,           # Transposition table size in MB
    
    # Search techniques
    'use_null_move': True,
    'null_move_r': 2,            # Null move reduction (2 or 3)
    
    'use_lmr': True,             # Late Move Reduction
    'lmr_threshold': 4,          # Start LMR after this many moves
    
    'use_futility': True,        # Futility pruning
    'use_delta_pruning': True,   # Delta pruning in quiescence
    
    'use_aspiration': True,      # Aspiration windows
    'aspiration_window': 50,     # Initial window size
    
    # Move ordering
    'killer_moves': 2,           # Number of killer moves per ply
    'use_history': True,         # History heuristic
    'use_see': True,             # Static Exchange Evaluation
    
    # Debug options
    'debug_mode': False,
    'show_search_info': True,    # Print search statistics
    'log_file': 'chess_ai.log'
}

# Evaluation weights (advanced tuning)
EVAL_WEIGHTS = {
    'mobility': 1.0,
    'king_safety': 1.0,
    'pawn_structure': 1.0,
    'rook_placement': 1.0,
    'bishop_pair': 1.0,
}

# GUI Configuration
GUI_CONFIG = {
    'window_width': 1000,
    'window_height': 800,
    'board_size': 640,
    'fps': 60,
    
    # Colors (RGB)
    'light_square': (240, 217, 181),
    'dark_square': (181, 136, 99),
    'highlight_color': (186, 202, 68),
    'last_move_color': (206, 210, 107),
    
    # Sounds
    'enable_sound': True,
    'move_sound': True,
    'capture_sound': True,
    
    # Music
    'enable_music': True,
    'music_volume': 0.3,
    
    # AI difficulty presets
    'difficulty': 'expert',  # 'beginner', 'intermediate', 'advanced', 'expert'
}

# Difficulty presets
DIFFICULTY_PRESETS = {
    'beginner': {
        'max_depth': 3,
        'time_limit': 5.0,
        'use_opening_book': False,
        'use_endgame_tb': False,
    },
    'intermediate': {
        'max_depth': 4,
        'time_limit': 7.0,
        'use_opening_book': True,
        'use_endgame_tb': False,
    },
    'advanced': {
        'max_depth': 5,
        'time_limit': 10.0,
        'use_opening_book': True,
        'use_endgame_tb': True,
    },
    'expert': {
        'max_depth': 6,
        'time_limit': 15.0,
        'use_opening_book': True,
        'use_endgame_tb': True,
    },
}

def get_ai_config(difficulty='expert'):
    """Get AI configuration for specified difficulty."""
    config = AI_CONFIG.copy()
    if difficulty in DIFFICULTY_PRESETS:
        config.update(DIFFICULTY_PRESETS[difficulty])
    return config

def set_difficulty(difficulty):
    """Set AI difficulty."""
    if difficulty in DIFFICULTY_PRESETS:
        AI_CONFIG.update(DIFFICULTY_PRESETS[difficulty])
        print(f"AI difficulty set to: {difficulty}")
        print(f"Max depth: {AI_CONFIG['max_depth']}")
        print(f"Time limit: {AI_CONFIG['time_limit']}s")
    else:
        print(f"Unknown difficulty: {difficulty}")
        print(f"Available: {list(DIFFICULTY_PRESETS.keys())}")
