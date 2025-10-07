# 👨‍💻 Developer Guide - Chess AI v2.0

## 🎯 Overview

Hướng dẫn cho developers muốn hiểu, modify, hoặc contribute vào dự án.

## 📁 Project Structure

```
chess-ai/
├── src/
│   ├── gui/                          # GUI Module
│   │   ├── components/               # Modular widgets
│   │   │   ├── __init__.py          # Exports
│   │   │   ├── board_widget.py      # 360 lines - Board logic
│   │   │   ├── clock_widget.py      # 180 lines - Timer logic
│   │   │   ├── captured_pieces_widget.py  # 80 lines
│   │   │   ├── move_history_widget.py     # 160 lines
│   │   │   └── control_panel.py     # 120 lines
│   │   ├── assets/                   # Images, sounds, fonts
│   │   ├── main_window_v2.py        # 580 lines - NEW main
│   │   ├── main_window.py           # 756 lines - OLD main
│   │   └── theme_improved.json      # UI theme
│   ├── ai/                           # AI Module
│   │   ├── minimax_optimized.py     # Minimax algorithm
│   │   └── opening_book.py          # Opening book handler
│   ├── engine_cpp/                   # C++ Engine (optional)
│   └── game/                         # Game logic
├── docs/                             # Documentation
├── opening_bin/                      # Opening books
└── tests/                            # Tests (TODO)
```

## 🏗️ Architecture Principles

### 1. Separation of Concerns

- **GUI** handles display and user interaction
- **Game logic** (chess.Board) handles rules
- **AI** handles move calculation
- Each component has single responsibility

### 2. Component-Based Design

```python
# Each component is independent
class BoardWidget:
    def __init__(self, screen, pieces, x, y)
    def draw()
    def handle_mouse_down(pos, button)
    def handle_mouse_up(pos, button)
```

### 3. Event-Driven

```python
# Main loop dispatches events to components
for event in pygame.event.get():
    if event.type == MOUSEBUTTONDOWN:
        board_widget.handle_mouse_down(event.pos, event.button)
```

## 🔧 How to Add Features

### Adding a New Widget

1. **Create widget file** in `src/gui/components/`:

```python
# my_widget.py
import pygame

class MyWidget:
    def __init__(self, screen, x, y, width, height):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self):
        """Draw the widget"""
        # Your drawing code here
        pass

    def update(self, delta_time):
        """Update widget state"""
        pass
```

2. **Export in **init**.py**:

```python
from .my_widget import MyWidget

__all__ = [
    'ChessClock',
    'BoardWidget',
    # ...
    'MyWidget'  # Add here
]
```

3. **Use in main_window_v2.py**:

```python
from src.gui.components import MyWidget

class ChessGame:
    def _create_components(self):
        # ...
        self.my_widget = MyWidget(self.screen, x, y, w, h)

    def _draw_game(self):
        # ...
        self.my_widget.draw()
```

### Adding a New Button

```python
# In ChessGame._create_home_ui() or similar
self.my_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((x, y), (width, height)),
    text='My Button',
    manager=self.manager,
    object_id=pygame_gui.core.ObjectID(class_id='@home_button')
)

# Handle in _handle_button_press()
def _handle_button_press(self, button):
    if button == self.my_button:
        # Your action here
        pass
```

### Adding a New Screen

1. **Add to current_screen states**:

```python
self.current_screen = "home"  # home, game, settings, my_screen
```

2. **Create draw method**:

```python
def _draw_my_screen(self):
    """Draw your screen"""
    self.screen.fill(BG_COLOR)
    # Your drawing code
```

3. **Add to main draw**:

```python
def draw(self):
    # ...
    elif self.current_screen == "my_screen":
        self._draw_my_screen()
```

### Adding a New AI Level

```python
self.ai_levels = {
    'Easy': (2, 1.0),      # (depth, time_limit)
    'Medium': (3, 3.0),
    'Hard': (4, 5.0),
    'Expert': (5, 10.0),
    'MyLevel': (6, 15.0),  # Add here
}
```

### Adding a New Time Control

```python
self.time_controls = {
    'Bullet 1+0': (60, 0),     # (seconds, increment)
    'Blitz 5+0': (300, 0),
    'MyControl': (420, 3),     # Add here
}
```

## 🎨 Styling and Theming

### Editing Theme

Edit `src/gui/theme_improved.json`:

```json
{
  "@my_button": {
    "colours": {
      "normal_bg": "#3d5a80",
      "hovered_bg": "#4a6fa5",
      "active_bg": "#2e4057",
      "normal_text": "#ffffff"
    },
    "font": {
      "size": "16",
      "bold": "1"
    },
    "misc": {
      "border_width": "2",
      "shape_corner_radius": "8"
    }
  }
}
```

### Board Colors

Edit `src/gui/components/board_widget.py`:

```python
class BoardWidget:
    LIGHT_SQUARE = (240, 217, 181)  # RGB
    DARK_SQUARE = (181, 136, 99)
    HIGHLIGHT = (255, 255, 102, 150)  # RGBA (with alpha)
```

## 🧪 Testing

### Manual Testing

```bash
# Test components
python test_components.py

# Run game
python -m src.gui.main_window_v2
```

### Unit Testing (TODO)

```python
# tests/test_clock.py
import unittest
from src.gui.components import ChessClock

class TestChessClock(unittest.TestCase):
    def test_countdown(self):
        clock = ChessClock(None, 800, 600)
        clock.set_time_control(300, 0)
        clock.start()

        clock.update(1.0)
        times = clock.get_times()

        self.assertLess(times['white'], 300)
```

## 🐛 Debugging

### Enable Debug Mode

```python
# In main_window_v2.py
DEBUG = True

if DEBUG:
    print(f"Clock state: {self.chess_clock.get_times()}")
    print(f"Board FEN: {self.board.fen()}")
```

### Common Issues

**Clock not updating:**

- Check `self.game_active` is True
- Check `ai_thinking` is False
- Check `delta_time` is being passed

**Components not visible:**

- Check `.show()` is called
- Check z-order (draw order)
- Check positions are within screen

**Events not firing:**

- Check event is in event loop
- Check `manager.process_events(event)` is called
- Check button is not hidden

## 📝 Code Style

### Python Style Guide

```python
# Use descriptive names
def calculate_material_difference(board):
    pass

# Use type hints (optional but recommended)
def update(self, delta_time: float) -> None:
    pass

# Document complex functions
def ai_move_threaded(board_copy, depth=4, time_limit=5.0):
    """
    Run AI in background thread.

    Args:
        board_copy: Copy of the board state
        depth: Search depth (default 4)
        time_limit: Max thinking time in seconds
    """
    pass

# Use constants for magic numbers
SQUARE_SIZE = 64
BOARD_SIZE = SQUARE_SIZE * 8
```

### Component Structure

```python
class MyWidget:
    """Widget description"""

    # Class constants
    DEFAULT_WIDTH = 200
    DEFAULT_HEIGHT = 100

    def __init__(self, screen, x, y):
        """Initialize widget"""
        # Public attributes
        self.screen = screen
        self.x = x
        self.y = y

        # Private attributes (prefixed with _)
        self._internal_state = None

    def draw(self):
        """Public method - draw the widget"""
        self._draw_background()
        self._draw_content()

    def _draw_background(self):
        """Private method - draw background"""
        pass
```

## 🔍 Understanding the Code

### Key Files to Read

1. **main_window_v2.py** - Start here

   - ChessGame class
   - Game loop
   - Event handling

2. **components/board_widget.py** - Board logic

   - Drawing
   - Mouse interaction
   - Move validation

3. **components/clock_widget.py** - Timer logic
   - Countdown
   - Increment
   - Pause/resume

### Execution Flow

```
1. run_gui()
   ↓
2. ChessGame.__init__()
   ├─ Create components
   ├─ Load assets
   └─ Create home UI
   ↓
3. ChessGame.run()
   ↓
4. Game loop (60 FPS)
   ├─ Handle events
   ├─ Update state
   └─ Draw
   ↓
5. Player action
   ↓
6. update() → handle_move_made()
   ↓
7. AI turn? → make_ai_move()
   ↓
8. AI thread → ai_move_queue
   ↓
9. Main loop gets result
   ↓
10. Apply move → update() → draw()
```

## 🚀 Performance Tips

### Drawing Optimization

```python
# Bad - draw every frame even if not changed
def draw(self):
    self._draw_everything()

# Good - only redraw when needed
def draw(self):
    if self._needs_redraw:
        self._draw_everything()
        self._needs_redraw = False
```

### Caching

```python
# Cache surfaces that don't change
def __init__(self):
    self._background_cache = None

def draw(self):
    if not self._background_cache:
        self._background_cache = self._render_background()
    self.screen.blit(self._background_cache, (0, 0))
```

## 🌐 Adding Multiplayer (Future)

Suggested architecture:

```python
# src/network/network_manager.py
class NetworkManager:
    def __init__(self, server_url):
        self.socket = socket.connect(server_url)

    def send_move(self, move):
        self.socket.emit('move', move.uci())

    def on_opponent_move(self, callback):
        self.socket.on('move', callback)
```

Integration:

```python
# In ChessGame
def handle_move_made(self):
    # ...
    if self.multiplayer_mode:
        self.network_manager.send_move(move)
```

## 📚 Resources

### Python Chess

- [python-chess docs](https://python-chess.readthedocs.io/)
- Board representation
- Move generation
- FEN/PGN handling

### Pygame

- [Pygame docs](https://www.pygame.org/docs/)
- Drawing
- Events
- Sound

### Pygame GUI

- [pygame-gui docs](https://pygame-gui.readthedocs.io/)
- UI elements
- Themes
- Event handling

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
   ```bash
   git checkout -b feature/my-feature
   ```
3. **Make** your changes
4. **Test** thoroughly
5. **Commit** with clear messages
   ```bash
   git commit -m "Add feature: description"
   ```
6. **Push** to your fork
   ```bash
   git push origin feature/my-feature
   ```
7. **Create** a Pull Request

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Example:

```
feat: Add move history widget

- Created MoveHistoryWidget component
- Displays moves in SAN notation
- Scrollable history
- Highlights last move

Closes #123
```

## 📞 Getting Help

- 📖 Read the [docs/](../docs/)
- 🐛 Check [GitHub Issues](https://github.com/Eurus-Infosec/chess-ai/issues)
- 💡 Start a [Discussion](https://github.com/Eurus-Infosec/chess-ai/discussions)
- 📧 Contact maintainer

## 🎓 Learning Path

1. **Beginner**: Modify colors, add buttons
2. **Intermediate**: Create new widgets, screens
3. **Advanced**: Modify AI, add features
4. **Expert**: C++ engine, multiplayer

Start small, learn by doing! 🚀

---

**Happy Coding!** 👨‍💻
