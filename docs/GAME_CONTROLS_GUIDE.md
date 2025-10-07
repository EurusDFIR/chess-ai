# 🎮 GAME CONTROLS INTEGRATION GUIDE

## Tổng quan

File `game_controls.py` cung cấp các tính năng như Lichess:

1. ⚔️ **Resign** - Đầu hàng
2. 🤝 **Draw** - Xin/chấp nhận hòa
3. 🔄 **Rematch** - Chơi lại
4. 🏠 **Home** - Về màn chính
5. ⏱️ **Time Controls** - Chọn thời gian (Bullet/Blitz/Rapid)
6. 🤖 **AI Levels** - Chọn độ khó (Easy/Medium/Hard/Expert)

---

## 📦 Files đã tạo

1. **`src/gui/game_controls.py`** - Class GameControls với tất cả tính năng
2. **`src/gui/theme.json`** - Updated với styles mới (@danger_button, @success_button, @secondary_button, @dropdown)
3. **`demo_game_controls.py`** - Demo standalone để test

---

## 🔧 Cách tích hợp vào main_window.py

### BƯỚC 1: Import GameControls

Thêm vào đầu file `main_window.py`:

```python
from src.gui.game_controls import get_game_controls
```

### BƯỚC 2: Tạo GameControls instance

Trong hàm `run_gui()`, sau khi tạo `manager`:

```python
# Tạo game controls
game_controls = get_game_controls(manager, WIDTH, HEIGHT)
game_controls.create_game_buttons()
```

### BƯỚC 3: Thêm variables cho game state

```python
# Game state
game_active = False
game_result = None
```

### BƯỚC 4: Show/Hide buttons khi cần

Khi bắt đầu game (user click Play):

```python
if event.ui_element == play_button:
    current_screen = "game"
    init_game_time()
    game_active = True
    game_result = None

    # Hide home buttons
    for button in home_buttons:
        button.hide()

    # Show game control buttons
    game_controls.show_game_buttons(game_active=True)

    # Show clock labels
    white_clock_label.show()
    black_clock_label.show()
```

Khi về home:

```python
elif event.ui_element == game_controls.home_button:
    current_screen = "home"
    game_active = False

    # Hide game buttons
    game_controls.hide_game_buttons()

    # Show home buttons
    for button in home_buttons:
        button.show()

    # Hide clocks
    white_clock_label.hide()
    black_clock_label.hide()
```

### BƯỚC 5: Xử lý các button events

Thêm vào phần xử lý `UI_BUTTON_PRESSED`:

```python
# Resign button
elif event.ui_element == game_controls.resign_button:
    print("🏳️ Player resigned!")
    game_result = 'black_win'  # AI wins
    game_active = False
    game_controls.show_game_buttons(game_active=False)

# Draw button
elif event.ui_element == game_controls.draw_button:
    print("🤝 Draw offered!")
    game_result = 'draw'
    game_active = False
    game_controls.show_game_buttons(game_active=False)

# Rematch button
elif event.ui_element == game_controls.rematch_button:
    print("🔄 Starting rematch...")
    # Reset game
    board = chess.Board()
    captured_white.clear()
    captured_black.clear()
    last_move = None
    init_game_time()
    game_active = True
    game_result = None
    game_controls.show_game_buttons(game_active=True)
```

### BƯỚC 6: Detect checkmate/stalemate/timeout

Sau mỗi move, check game over:

```python
# Check game over conditions
if board.is_checkmate():
    if board.turn == chess.WHITE:
        game_result = 'checkmate_black'  # Black wins
    else:
        game_result = 'checkmate_white'  # White wins
    game_active = False
    game_controls.show_game_buttons(game_active=False)

elif board.is_stalemate():
    game_result = 'stalemate'
    game_active = False
    game_controls.show_game_buttons(game_active=False)

# Check timeout
if white_time <= 0:
    game_result = 'timeout_black'  # Black wins
    game_active = False
    game_controls.show_game_buttons(game_active=False)
elif black_time <= 0:
    game_result = 'timeout_white'  # White wins
    game_active = False
    game_controls.show_game_buttons(game_active=False)
```

### BƯỚC 7: Draw game result overlay

Trong phần drawing (game screen):

```python
elif current_screen == "game":
    draw_board(...)
    draw_pieces(...)

    # Draw GUI improvements
    if last_move is not None:
        draw_last_move_highlight(screen, last_move)
    draw_captured_pieces(...)
    draw_material_count(...)
    if ai_thinking:
        draw_ai_thinking_indicator(...)

    # Draw game result overlay if game ended
    if game_result:
        game_controls.draw_game_status(screen, game_result)

    manager.draw_ui(screen)
```

### BƯỚC 8: Settings screen - Time & AI selection

Cập nhật màn hình Settings để có dropdown chọn time/AI:

```python
# Tạo dropdowns (global scope)
time_dropdown = None
level_dropdown = None

# Trong settings screen, tạo dropdowns nếu chưa có
if current_screen == "settings" and time_dropdown is None:
    time_dropdown = game_controls.create_time_selector()
    level_dropdown = game_controls.create_level_selector()

    # Hide khi ra khỏi settings
elif current_screen != "settings" and time_dropdown is not None:
    time_dropdown.kill()
    level_dropdown.kill()
    time_dropdown = None
    level_dropdown = None

# Xử lý dropdown selection change
if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
    if event.ui_element == time_dropdown:
        game_controls.set_time_control(event.text)
        print(f"⏱️ Time control: {event.text}")

    elif event.ui_element == level_dropdown:
        game_controls.set_ai_level(event.text)
        print(f"🤖 AI level: {event.text}")
```

### BƯỚC 9: Sử dụng settings khi init game

Trong `init_game_time()`:

```python
def init_game_time():
    global white_time, black_time, start_time, current_player, game_started

    # Get selected time control
    time_control = game_controls.get_selected_time_control()

    white_time = time_control['time']
    black_time = time_control['time']
    start_time = pygame.time.get_ticks()
    current_player = chess.WHITE
    game_started = True
```

Khi gọi AI, dùng selected level:

```python
def ai_move():
    # ... (opening book code)

    # Get AI settings
    ai_level = game_controls.get_selected_ai_level()

    # Use AI search với settings
    board_copy = board.copy()
    ai_move_threaded(board_copy, depth=ai_level['depth'], time_limit=ai_level['time'])
```

---

## 🎨 UI Components

### Button Styles

- `@danger_button` - Red (Resign)
- `@success_button` - Green (Rematch)
- `@secondary_button` - Gray (Draw, Home)
- `@dropdown` - Blue border

### Game Result Types

- `'white_win'` - Trắng thắng (resign/checkmate/time)
- `'black_win'` - Đen thắng (resign/checkmate/time)
- `'draw'` - Hòa (agreement/stalemate)
- `'checkmate_white'` - Trắng chiếu hết
- `'checkmate_black'` - Đen chiếu hết
- `'stalemate'` - Bí quân
- `'timeout_white'` - Trắng thắng do hết giờ
- `'timeout_black'` - Đen thắng do hết giờ

### Time Controls

| ID        | Name           | Time  | Increment |
| --------- | -------------- | ----- | --------- |
| bullet_1  | Bullet 1+0     | 60s   | 0s        |
| bullet_2  | Bullet 2+1     | 120s  | 1s        |
| blitz_3   | Blitz 3+0      | 180s  | 0s        |
| blitz_5   | Blitz 5+0      | 300s  | 0s        |
| rapid_10  | Rapid 10+0     | 600s  | 0s        |
| rapid_15  | Rapid 15+10    | 900s  | 10s       |
| classical | Classical 30+0 | 1800s | 0s        |

### AI Levels

| ID     | Name                  | Depth | Time Limit |
| ------ | --------------------- | ----- | ---------- |
| easy   | Easy (Beginner)       | 2     | 1.0s       |
| medium | Medium (Intermediate) | 3     | 3.0s       |
| hard   | Hard (Advanced)       | 4     | 5.0s       |
| expert | Expert (Master)       | 5     | 10.0s      |

---

## 🧪 Testing

Chạy demo:

```bash
python demo_game_controls.py
```

Test:

1. ✅ Click "⚔ Resign" → Thấy "Black Wins!" overlay
2. ✅ Click "🤝 Draw" → Thấy "Draw!" overlay
3. ✅ Click "🔄 Rematch" → Overlay biến mất, buttons reset
4. ✅ Click "🏠 Home" → Thoát demo

---

## 📝 TODO (Optional enhancements)

1. **Increment support** - Thêm giây sau mỗi move
2. **Sound effects** - Âm thanh cho resign/draw/checkmate
3. **Move history** - Panel hiện các nước đã đi
4. **Takeback** - Undo move
5. **Analysis mode** - Analyze game sau khi kết thúc
6. **Save/Load PGN** - Lưu/tải ván cờ
7. **Online multiplayer** - Chơi với người khác qua mạng

---

## 🎯 Expected Results

Sau khi tích hợp:

- ✅ Game có 4 nút: Resign, Draw, Rematch, Home
- ✅ Settings có dropdown chọn time/AI
- ✅ Game kết thúc hiện overlay đẹp
- ✅ Rematch reset game hoàn toàn
- ✅ Home button quay về màn chính
- ✅ UI professional như Lichess

---

**Estimated integration time**: 30-45 minutes

**Difficulty**: Medium (requires understanding of event handling and game state management)
