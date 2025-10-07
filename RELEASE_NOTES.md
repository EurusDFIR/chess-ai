# Chess AI v2.1.0 - Eury Engine

## ✨ New Features

### 🧠 Game Analysis Mode

- Real-time position evaluation with best moves suggestion
- Multi-threaded analysis (non-blocking UI)
- Minimax search with alpha-beta pruning integration
- Position caching with LRU (1000 positions)

### 📊 Evaluation Bar

- Visual representation of position strength
- Smooth interpolation animation
- Accurate pawn-unit scoring
- Color-coded advantage indicator

### 📝 Move Quality Annotations

- `!!` Brilliant move (best move found)
- `!` Good move (top 3)
- `!?` Interesting move
- `?!` Dubious move
- `?` Mistake
- `??` Blunder (significant eval drop)

### 🎨 Lichess-style UI Redesign

- Professional color scheme (brown/tan palette)
- Compact text buttons (no Unicode symbols)
- 2-column move history with SAN notation
- Minimal captured pieces display
- Green legal move indicators
- Lighter background colors for better visibility

### 📖 Opening Book Support

- Multiple opening books included:
  - Komodo.bin (GM-level repertoire)
  - gm2600.bin (2600+ Elo openings)
  - Performance.bin (Tournament book)
  - And 9 more books!
- Automatic book selection
- Opening names and ECO codes

### ♟️ Syzygy Tablebase Integration

- 3-7 piece endgame tablebases
- Perfect play in endgames
- 538 tablebase files included
- Automatic probe on compatible positions

## 🐛 Bug Fixes

- Fixed board synchronization in analysis mode
- Fixed UIScrollBar AttributeError crash
- Fixed evaluation bar perspective calculation
- Fixed move history SAN notation generation
- Fixed captured pieces color contrast
- Fixed control button rendering issues

## 🎯 Improvements

- Faster position evaluation (C++ minimax engine)
- Better memory usage with LRU caching
- Smoother animations throughout UI
- More responsive controls
- Cleaner code organization

## 📦 Download

### Recommended: Portable Package (354 MB)

**[ChessAI-Portable-v2.1.zip](https://github.com/Eurus-Infosec/chess-ai/releases/download/v2.1.0/ChessAI-Portable-v2.1.zip)**

**Contents:**

- `ChessAI-EuryEngine.exe` - Standalone executable (98.4 MB)
- `opening_bin/` - 12 opening books
- `syzygy/` - 538 endgame tablebases
- `README_NEW.md` - User guide
- `LICENSE` - MIT License
- `QUICK_START.md` - Getting started guide
- `GAME_CONTROLS_GUIDE.md` - Controls reference

**No Python installation required!**

## 🚀 Quick Start

1. **Download** `ChessAI-Portable-v2.1.zip`
2. **Extract** to any folder (e.g., `C:\Chess`)
3. **Run** `ChessAI-EuryEngine.exe`
4. **Play chess!**

### First Launch

- Choose game mode: vs AI or vs Human
- Select difficulty: Easy (depth 2) to Hard (depth 4)
- Click "New Game" to start

### Analysis Mode

- Toggle with **Analysis** button
- View best moves and evaluation in real-time
- See move quality annotations after each move

## 💻 System Requirements

### Minimum

- **OS**: Windows 10 (64-bit)
- **RAM**: 512 MB
- **Disk**: 400 MB free space
- **CPU**: Any modern processor

### Recommended

- **OS**: Windows 11 (64-bit)
- **RAM**: 2 GB
- **Disk**: 1 GB free space (for faster performance)
- **CPU**: Multi-core processor (for faster analysis)

## 🎮 Game Controls

| Action           | Keyboard          | Mouse                   |
| ---------------- | ----------------- | ----------------------- |
| Select piece     | Click             | Click square            |
| Move piece       | Click destination | Drag & drop             |
| Cancel selection | ESC               | Click empty square      |
| Toggle analysis  | A                 | Click "Analysis" button |
| Resign           | Ctrl+R            | Click "Resign"          |
| Offer draw       | Ctrl+D            | Click "Draw"            |
| New game         | Ctrl+N            | Click "Rematch"         |
| Back to menu     | ESC               | Click "Home"            |

## 🐛 Known Issues

### Minor

- First analysis may take 2-3 seconds (cache warming)
- Large opening books may cause slight startup delay
- Syzygy probing only works for 3-7 piece endgames

### Workarounds

- Wait for initial analysis to complete
- Reduce search depth if analysis is too slow
- Endgames with 8+ pieces use minimax evaluation

## 📝 Changelog

### Added

- Real-time game analysis with best moves
- Visual evaluation bar with smooth animation
- Move quality annotations (brilliant to blunder)
- Alternative moves display (top 3 options)
- Lichess-inspired UI redesign
- Text-based control buttons
- Compact 2-column move history
- Green legal move indicators
- 12 opening books with ECO codes
- 538 Syzygy tablebase files

### Changed

- Improved move history with SAN notation
- Better color contrast for readability
- Lighter backgrounds for widgets
- Faster position evaluation caching
- More responsive UI updates

### Fixed

- Board sync errors in analysis mode
- UIScrollBar crash on plain text
- Evaluation bar incorrect perspective
- Move history SAN generation bugs
- Captured pieces dark background
- Control button Unicode rendering

### Removed

- Old analysis_engine_old.py
- Duplicate component files
- Unused test scripts
- Development markdown files

## 🔧 Technical Details

### Architecture

- **Frontend**: Pygame CE 2.5.3 with pygame_gui
- **Backend**: python-chess 1.10.0
- **AI Engine**: C++ minimax with alpha-beta pruning
- **Threading**: Queue-based async analysis
- **Caching**: LRU cache (1000 positions)
- **Build**: PyInstaller 6.16.0 (onefile mode)

### Performance

- **Search depth**: 2-4 moves (configurable)
- **Nodes/second**: ~100,000 (depth 4)
- **Analysis time**: 1-3 seconds per position
- **Memory usage**: ~150 MB (including tablebase cache)

### File Structure

```
ChessAI-Portable/
├── ChessAI-EuryEngine.exe    # Main executable (98.4 MB)
├── opening_bin/               # Opening books (12 files)
│   ├── komodo.bin
│   ├── gm2600.bin
│   └── ...
├── syzygy/                    # Endgame tables (538 files)
│   ├── KBBBvK.rtbw
│   ├── KBBBvK.rtbz
│   └── ...
├── README_NEW.md              # User documentation
├── LICENSE                    # MIT License
├── QUICK_START.md            # Getting started
└── GAME_CONTROLS_GUIDE.md    # Controls reference
```

## 🤝 Contributing

Found a bug? Have a feature request?

1. Open an issue: https://github.com/Eurus-Infosec/chess-ai/issues
2. Fork the repository
3. Create a feature branch
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

**Eury Engine Team**

- GitHub: [@Eurus-Infosec](https://github.com/Eurus-Infosec)
- Repository: [chess-ai](https://github.com/Eurus-Infosec/chess-ai)

## 🙏 Acknowledgments

- **python-chess**: Chess logic and move generation
- **Pygame CE**: Graphics and UI framework
- **Syzygy**: Endgame tablebase format
- **Lichess**: UI design inspiration

---

**Enjoy playing chess with Eury Engine! ♟️**
