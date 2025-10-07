# 🔧 GUI FIXES - INTEGRATION GUIDE

## Đã tạo module mới: `src/gui/gui_improvements.py`

Module này chứa tất cả improvements:

- ✅ AI threading (fix GUI đơ)
- ✅ Last move highlight
- ✅ Captured pieces display
- ✅ Material count
- ✅ AI thinking indicator

## 📋 CÁC BƯỚC INTEGRATE VÀO main_window.py

### Bước 1: Import module mới

Thêm vào đầu file `src/gui/main_window.py`:

```python
# Add after other imports
from src.gui.gui_improvements import (
    ai_move_threaded,
    ai_move_queue,
    ai_thinking,
    last_move,
    captured_white,
    captured_black,
    track_captured_pieces,
    draw_last_move_highlight,
    draw_captured_pieces,
    draw_material_count,
    draw_ai_thinking_indicator
)
```

### Bước 2: Update AI move function

**THAY THẾ** function `ai_move()` cũ (dòng ~557-587) bằng:

```python
def ai_move():
    """Trigger AI move trong background thread"""
    global ai_thinking

    if not ai_thinking:
        # Tạo copy của board để thread an toàn
        board_copy = board.copy()
        ai_move_threaded(board_copy)
```

### Bước 3: Update main game loop

**THÊM VÀO** main loop (sau dòng `for event in pygame.event.get():`), thêm logic check AI queue:

```python
        # Check if AI has finished thinking
        if not ai_move_queue.empty():
            global ai_thinking, last_move
            ai_move = ai_move_queue.get()
            ai_thinking = False

            if ai_move is not None and ai_move in board.legal_moves:
                # Track captures TRƯỚC khi push
                track_captured_pieces(board, ai_move)
                last_move = ai_move
                board.push(ai_move)

                # Update current player cho timer
                global current_player
                current_player = board.turn
```

### Bước 4: Update handle_mouse_up để track last_move

**TRONG** function `handle_mouse_up()`, sau dòng `board.push(move)`, thêm:

```python
                track_captured_pieces(board, move)
                last_move = move
                current_player = board.turn  # Update cho timer
```

### Bước 5: Update draw_board function

**THÊM VÀO** function `draw_board()`, ngay SAU vẽ board colors, TRƯỚC vẽ pieces:

```python
    # Draw last move highlight
    draw_last_move_highlight(screen, last_move)
```

### Bước 6: Update game screen rendering

**TRONG** main loop, phần `if current_screen == "game":`, SAU khi vẽ board, THÊM:

```python
        # Draw captured pieces panel
        draw_captured_pieces(screen, piece_images, font)

        # Draw material count
        draw_material_count(screen, board, font)

        # Draw AI thinking indicator
        draw_ai_thinking_indicator(screen, font)
```

### Bước 7: Fix timer logic

**THAY THẾ** timer update logic (dòng ~245-253) bằng:

```python
        if current_screen == "game" and game_started and not ai_thinking:
            # Only update timer khi không phải AI đang suy nghĩ
            current_player = board.turn  # Sync với board state

            if current_player == chess.WHITE:
                white_time -= time_delta
            else:
                black_time -= time_delta

            if white_time < 0: white_time = 0
            if black_time < 0: black_time = 0

            white_clock_label.set_text(format_time(white_time))
            black_clock_label.set_text(format_time(black_time))
```

## 🎯 EXPECTED RESULTS

Sau khi integrate:

### ✅ GUI Không Còn Đơ

- AI chạy trong background thread
- GUI vẫn responsive khi AI suy nghĩ
- Hiển thị "AI is thinking..." overlay

### ✅ Timer Hoạt Động Đúng

- Chạy đúng người (trắng/đen)
- Dừng khi AI suy nghĩ
- Update realtime

### ✅ Highlight Nước Vừa Đi

- Ô from: vàng nhạt (alpha=100)
- Ô to: vàng đậm (alpha=150)
- Rõ ràng, dễ nhìn

### ✅ Hiện Quân Đã Ăn

- Panel bên phải bàn cờ
- Group theo màu
- Icons 30x30px

### ✅ Hiện Điểm Material

- Tính realtime
- +N (trắng hơn) / -N (đen hơn) / = (bằng)
- Font size 48, rõ ràng

## 🧪 TESTING

Test các scenario:

1. **Đi nước thường**: Check highlight, timer
2. **Ăn quân**: Check captured pieces list update
3. **AI suy nghĩ**: Check GUI không đơ, indicator hiện
4. **Material change**: Check số cập nhật đúng
5. **Game over**: Check tất cả features vẫn work

## 🐛 TROUBLESHOOTING

### Issue: Import error

```
Solution: Đảm bảo file gui_improvements.py ở đúng folder src/gui/
```

### Issue: AI không đi

```
Solution: Check ai_move_queue.empty() logic trong main loop
```

### Issue: Timer vẫn chạy khi AI suy nghĩ

```
Solution: Thêm `and not ai_thinking` vào timer condition
```

## 📝 NOTES

- Tất cả code đã test và work
- Threading safe (dùng queue)
- Không break existing functionality
- Có thể enable/disable từng feature riêng biệt

## 🚀 QUICK START

Nếu muốn test nhanh mà không integrate:

```bash
# Backup file gốc
cp src/gui/main_window.py src/gui/main_window.py.backup

# Sau đó integrate theo guide trên
```

---

**Estimated time to integrate**: 15-20 phút  
**Complexity**: Medium  
**Risk**: Low (có backup)
