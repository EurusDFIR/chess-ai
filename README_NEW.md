# ♟️ Chess AI - Eury Engine v2.1

A modern, feature-rich chess application with AI opponent and analysis tools. Built with Python and Pygame, featuring a clean Lichess-inspired UI.

![Chess AI Screenshot](docs/images/screenshot.png)

## ✨ Features

### 🎮 Game Modes

- **Play vs AI** - Multiple difficulty levels (Easy to Hard)
- **Time Controls** - Blitz, Rapid, and Classical formats
- **Opening Book** - Professional opening database support
- **Endgame Tablebases** - Syzygy tablebase integration

### 📊 Analysis Tools

- **Position Analysis** - Real-time evaluation
- **Best Move Suggestions** - AI-powered recommendations
- **Move Quality** - Annotations (Brilliant!, Good, Mistake, Blunder)
- **Alternative Moves** - See top 3 alternatives
- **Evaluation Bar** - Visual advantage indicator

### 🎨 Modern UI

- **Lichess-Inspired Design** - Clean, professional interface
- **Move History** - SAN notation with 2-column layout
- **Material Count** - Captured pieces display
- **Legal Move Indicators** - Green dots for valid moves
- **Custom Themes** - Dark mode with smooth animations

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Quick Start

#### Windows

```bash
# Clone repository
git clone https://github.com/Eurus-Infosec/chess-ai.git
cd chess-ai

# Install dependencies
pip install -r requirements.txt

# Run application
python -m src.gui.main_window_v2
```

#### Linux/Mac

```bash
# Clone repository
git clone https://github.com/Eurus-Infosec/chess-ai.git
cd chess-ai

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python -m src.gui.main_window_v2
```

### Alternative: Install as Package

```bash
# Clone and install
git clone https://github.com/Eurus-Infosec/chess-ai.git
cd chess-ai
pip install .

# Run from anywhere
chess-ai
```

## 🎯 Quick Guide

### Starting a Game

1. **Launch** - Run the application
2. **Play** - Click "Play" button
3. **Select Time** - Choose time control (Blitz/Rapid/Classical)
4. **Select Difficulty** - Choose AI level (Easy/Medium/Hard)
5. **Start** - Begin playing!

### Controls

- **Click** - Select and move pieces
- **Right-click** - Draw arrows
- **Resign** - Give up current game
- **Draw** - Offer draw to AI
- **Analysis** - Toggle analysis mode
- **Home** - Return to main menu

### Analysis Mode

1. Click **Analysis** button during game
2. View evaluation bar and best moves
3. See move quality annotations
4. Explore alternative continuations
5. Click **Analysis** again to return to game

## 📚 Documentation

- [Quick Start Guide](docs/QUICK_START.md) - Detailed setup instructions
- [Game Controls](docs/GAME_CONTROLS_GUIDE.md) - Complete control reference
- [Analysis Mode](docs/ANALYSIS_MODE_GUIDE.md) - Analysis features guide
- [Roadmap](docs/TODO.md) - Future features and improvements

## 🛠️ Technical Details

### Built With

- **Python 3.12** - Core language
- **Pygame CE 2.5** - Graphics and game engine
- **python-chess 1.10** - Chess logic and rules
- **pygame_gui** - UI components

### Architecture

- **Minimax Algorithm** - AI search with alpha-beta pruning
- **Evaluation Function** - Material, position, mobility, safety
- **Opening Book** - Polyglot format support
- **Endgame Tablebases** - Syzygy format
- **LRU Caching** - Position analysis optimization

### Performance

- **Search Depth**: 1-6 ply (depending on difficulty)
- **Positions/Second**: ~50,000 (optimized evaluation)
- **Opening Book**: 1M+ positions
- **Memory Usage**: ~100MB base + tablebases

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **python-chess** - Excellent chess library
- **Lichess.org** - UI/UX inspiration
- **Pygame Community** - Graphics engine

## 📧 Contact

- **GitHub**: [Eurus-Infosec](https://github.com/Eurus-Infosec)
- **Issues**: [Report bugs](https://github.com/Eurus-Infosec/chess-ai/issues)

## 🗺️ Roadmap

See [TODO.md](docs/TODO.md) for planned features:

- [ ] Save/Load games (PGN format)
- [ ] Sound effects and music
- [ ] Online multiplayer
- [ ] Chess variants (Chess960, etc.)
- [ ] Puzzle mode
- [ ] Opening trainer

---

**Made with ❤️ by Eurus-DFIR**
