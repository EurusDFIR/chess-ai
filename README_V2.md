# 🎮 Chess AI - Eury Engine v2.0

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![C++](https://img.shields.io/badge/C++-17-green.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Chess AI với hybrid architecture: C++ engine cho hiệu năng tối ưu + Python GUI với Pygame**

## ✨ Features

### 🎯 Game Features

- ♟️ **Full chess rules** - Tất cả luật cờ vua chuẩn
- 🤖 **AI đối thủ** - 4 cấp độ từ Easy đến Expert
- 📖 **Opening book** - Hỗ trợ nhiều opening book (Polyglot format)
- ⏱️ **Time controls** - Bullet, Blitz, Rapid, Classical với increment
- 🎨 **Modern UI** - Interface kiểu Lichess, responsive và đẹp mắt
- 🔄 **Move history** - Lịch sử nước đi với SAN notation
- 📊 **Material count** - Hiển thị quân bị ăn và material advantage
- ⚡ **Multithreading** - AI chạy background, không lag GUI

### 🎨 UI/UX Improvements

- ✅ **Clean layout** - Board centered, sidebar bên phải
- ✅ **Dark theme** - Giao diện tối đẹp mắt như Lichess
- ✅ **Smooth animations** - Drag & drop pieces mượt mà
- ✅ **Visual feedback** - Highlight last move, legal moves
- ✅ **Arrows & highlights** - Vẽ arrows và highlight squares
- ✅ **Game status** - Overlay hiển thị kết quả game
- ✅ **Responsive clocks** - Đồng hồ chạy chính xác với increment

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         PYTHON GUI LAYER (Pygame)               │
│  • Main Window (main_window_v2.py)              │
│  • Components (modular widgets)                 │
│    - BoardWidget: Bàn cờ và interaction        │
│    - ChessClock: Đồng hồ với increment         │
│    - CapturedPieces: Quân bị ăn                │
│    - MoveHistory: Lịch sử nước đi              │
│    - ControlPanel: Buttons điều khiển          │
└─────────────┬───────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────┐
│         C++ ENGINE LAYER (Performance)          │
│  • chess_engine.pyd (compiled module)           │
│  • Minimax + Alpha-Beta pruning                 │
│  • Bitboard representation                      │
│  • Transposition table                          │
│  • Move ordering optimization                   │
└─────────────────────────────────────────────────┘
```

## 📦 Installation

### Prerequisites

- Python 3.8+
- pip
- (Optional) Visual Studio 2019+ for C++ engine build

### Quick Start

```bash
# Clone repository
git clone https://github.com/Eurus-Infosec/chess-ai.git
cd chess-ai

# Install dependencies
pip install -r requirements.txt

# Run the game
python -m src.gui.main_window_v2

# Or use the old version
python -m src.gui.main_window
```

### Install from requirements.txt

```bash
pip install -r requirements.txt
```

**Requirements:**

- pygame>=2.5.0
- pygame-gui>=0.6.9
- chess>=1.10.0
- numpy>=1.24.0

## 🎮 How to Play

### Starting a Game

1. Click **"Play vs AI"** on home screen
2. Game starts with default settings (Blitz 5+0, Hard difficulty)
3. You play as White, AI plays as Black

### Controls

| Action           | Control                         |
| ---------------- | ------------------------------- |
| Move piece       | Left click drag & drop          |
| Draw arrow       | Right click drag                |
| Highlight square | Right click                     |
| Resign           | Click "Resign" button           |
| Offer draw       | Click "Draw" button             |
| New game         | Click "Rematch" after game ends |
| Back to menu     | Click "Home" button             |

### Settings

#### Time Controls

- **Bullet 1+0**: 1 minute, no increment
- **Bullet 2+1**: 2 minutes, 1 second increment
- **Blitz 3+0**: 3 minutes, no increment
- **Blitz 5+0**: 5 minutes, no increment (default)
- **Rapid 10+0**: 10 minutes
- **Rapid 15+10**: 15 minutes, 10 second increment
- **Classical 30+0**: 30 minutes

#### AI Difficulty Levels

- **Easy** (Beginner): Depth 2, 1 second thinking
- **Medium** (Intermediate): Depth 3, 3 seconds thinking
- **Hard** (Advanced): Depth 4, 5 seconds thinking (default)
- **Expert** (Master): Depth 5, 10 seconds thinking

## 🗂️ Project Structure

```
chess-ai/
├── src/
│   ├── gui/                      # GUI Module
│   │   ├── components/           # Modular components
│   │   │   ├── __init__.py
│   │   │   ├── board_widget.py       # Bàn cờ
│   │   │   ├── clock_widget.py       # Đồng hồ
│   │   │   ├── captured_pieces_widget.py
│   │   │   ├── move_history_widget.py
│   │   │   └── control_panel.py
│   │   ├── assets/               # Images, sounds, fonts
│   │   │   ├── pieces/           # Piece images
│   │   │   ├── backgrounds/
│   │   │   ├── music/
│   │   │   └── fonts/
│   │   ├── main_window_v2.py     # Main window (NEW - Refactored)
│   │   ├── main_window.py        # Old main window
│   │   ├── theme_improved.json   # UI theme
│   │   └── ...
│   ├── ai/                       # AI Module
│   │   ├── minimax_optimized.py  # Optimized minimax
│   │   └── opening_book.py       # Opening book handler
│   ├── engine_cpp/               # C++ Engine (optional)
│   │   ├── include/
│   │   └── src/
│   └── ...
├── opening_bin/                  # Opening books (.bin files)
├── docs/                         # Documentation (MD files)
├── requirements.txt
└── README.md
```

## 🚀 Performance

### Python AI (Current)

- **Speed**: ~7,000-10,000 nodes/sec
- **Depth**: 4-5 plies
- **Time per move**: 3-10 seconds
- **Estimated Elo**: ~2000-2200

### C++ Engine (If built)

- **Speed**: ~500,000-1,000,000 nodes/sec
- **Depth**: 8-10 plies
- **Time per move**: <1 second
- **Estimated Elo**: ~2500-2800

## 🔧 Build C++ Engine (Optional)

Để tăng hiệu năng gấp 100x, build C++ engine:

```bash
# Windows (với Visual Studio)
mkdir build
cd build
cmake ..
cmake --build . --config Release

# Copy chess_engine.pyd vào src/
cp Release/chess_engine.pyd ../src/
```

Chi tiết xem [BUILD_GUIDE.md](docs/BUILD_GUIDE.md)

## 📚 Documentation

Tất cả tài liệu đã được tổ chức trong thư mục `docs/`:

- [HYBRID_ARCHITECTURE.md](docs/HYBRID_ARCHITECTURE.md) - Kiến trúc hybrid Python+C++
- [GUI_IMPROVEMENTS.md](docs/GUI_IMPROVEMENTS.md) - Cải thiện GUI
- [BUILD_GUIDE.md](docs/BUILD_GUIDE.md) - Hướng dẫn build C++ engine
- [OPTIMIZATION_REPORT.md](docs/OPTIMIZATION_REPORT.md) - Báo cáo tối ưu
- [QUICK_START.md](docs/QUICK_START.md) - Hướng dẫn nhanh

## 🎨 Customization

### Change Theme Colors

Edit `src/gui/theme_improved.json`:

```json
{
  "button": {
    "colours": {
      "normal_bg": "#3d5a80",
      "hovered_bg": "#4a6fa5",
      ...
    }
  }
}
```

### Change Board Colors

Edit `src/gui/components/board_widget.py`:

```python
LIGHT_SQUARE = (240, 217, 181)  # Light square color
DARK_SQUARE = (181, 136, 99)    # Dark square color
```

### Add Opening Books

Place `.bin` files (Polyglot format) in `opening_bin/` folder.

## 🐛 Known Issues

1. ~~Clock không chạy đúng~~ ✅ FIXED
2. ~~GUI bị đơ khi AI suy nghĩ~~ ✅ FIXED (multithreading)
3. ~~Layout chưa đẹp~~ ✅ FIXED (refactored components)
4. ~~Quá nhiều file .md ở root~~ ✅ FIXED (moved to docs/)

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - see LICENSE file

## 👨‍💻 Author

**Eurus-Infosec**

- GitHub: [@Eurus-Infosec](https://github.com/Eurus-Infosec)

## 🙏 Acknowledgments

- [python-chess](https://python-chess.readthedocs.io/) - Chess library
- [Pygame](https://www.pygame.org/) - Game framework
- [Lichess](https://lichess.org/) - UI/UX inspiration
- Opening books from various sources

---

⭐ **Star this repo if you found it helpful!**

🐛 **Report bugs via GitHub Issues**

💡 **Suggestions? Open a discussion!**
