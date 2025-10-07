# Chess AI - Changelog v2.2.0

## 🎨 Cải tiến Giao diện (7 Oct 2025)

### ✅ Tính năng mới

#### 1. **Settings Menu với Dropdown**

- ✅ **Time Control Selector**: Chọn chế độ thời gian từ dropdown menu

  - Bullet 1+0 (1 phút)
  - Bullet 2+1 (2 phút + 1 giây increment)
  - Blitz 3+0 (3 phút)
  - **Blitz 5+0** (5 phút - mặc định)
  - Rapid 10+0 (10 phút)
  - Rapid 15+10 (15 phút + 10 giây increment)
  - Classical 30+0 (30 phút)

- ✅ **AI Difficulty Selector**: Chọn độ khó AI từ dropdown menu

  - Easy (depth 2, 1 giây)
  - Medium (depth 3, 3 giây)
  - **Hard** (depth 4, 5 giây - mặc định)
  - Expert (depth 5, 10 giây)

- ✅ **Music Volume Control**: Slider điều chỉnh âm lượng nhạc nền
  - Phạm vi: 0% - 100%
  - Mặc định: 30%
  - Hiển thị real-time volume percentage

#### 2. **Bàn cờ mới - Chess.com Theme**

- ✅ Đổi màu từ Lichess (nâu) sang **Chess.com** (xanh-trắng)
  - Ô sáng: Kem sáng `#EBECD0`
  - Ô tối: Xanh lá `#739552`
  - Highlight: Xanh vàng trong suốt
  - Last move: Vàng xanh trong suốt

#### 3. **Kiểm soát thời gian cải thiện**

- ✅ AI giờ đây tuân theo settings được chọn
- ✅ Thay đổi độ khó AI trong settings sẽ áp dụng cho game tiếp theo
- ✅ Thay đổi time control sẽ áp dụng đồng hồ đếm ngược mới
- ✅ **QUAN TRỌNG**: Đồng hồ AI giờ đây chạy đúng - không bị đứng yên

#### 4. **About & Settings Screen cải tiến**

- ✅ About screen với layout đẹp hơn, có icons

  - Phân chia rõ ràng: Architecture, Features
  - Version number và subtitle
  - Color coding cho từng section
  - Footer với author info

- ✅ Settings screen với instructions
  - Volume slider với percentage display
  - Game controls guide
  - Organized layout

### 🐛 Sửa lỗi

#### 1. **Đồng hồ AI bị đứng yên - ĐÃ SỬA**

**Vấn đề**: Khi AI suy nghĩ, đồng hồ của AI bị pause, chỉ đồng hồ người chơi chạy.

**Nguyên nhân**: Code gọi `chess_clock.pause()` khi AI bắt đầu suy nghĩ, sau đó `resume()` khi xong. Điều này pause CẢ HAI đồng hồ.

**Giải pháp**:

- Xóa `chess_clock.pause()` trong `make_ai_move()`
- Xóa `chess_clock.resume()` sau khi AI xong
- Đồng hồ giờ chạy liên tục cho cả hai bên

#### 2. **Warnings đã được loại bỏ**

- ✅ Syzygy tablebase warning (im lặng nếu không tìm thấy)
- ✅ DeprecationWarning về `event.user_type` → `event.type`
- ✅ Font warnings trong pygame_gui (đổi từ fira_code → consolas)
- ✅ Unicode emoji errors trên Windows (đổi sang text prefix)

#### 3. **Print statements clean hơn**

- `🎵` → `[Music]`
- `🎮` → `[Game]`
- `📖` → `[Opening]`
- `🤖` → `[AI]`
- `⚪⚫` → `[Capture]`

### 📝 Technical Details

**Files changed:**

- `src/gui/main_window_v2.py`: Thêm dropdown menus, event handlers
- `src/gui/components/board_widget.py`: Đổi màu bàn cờ
- `src/gui/theme_improved.json`: Đổi font từ fira_code sang consolas
- `src/ai/evaluation_optimized.py`: Silent syzygy warning
- `src/gui/components/captured_pieces_widget.py`: Clean print statements

**New UI Components:**

- `time_control_dropdown`: UIDropDownMenu cho time control
- `ai_level_dropdown`: UIDropDownMenu cho AI difficulty

**Event Handling:**

- `pygame_gui.UI_DROP_DOWN_MENU_CHANGED`: Xử lý thay đổi settings

### 🎯 Cách sử dụng

1. **Thay đổi Time Control:**

   - Vào Settings từ home screen
   - Chọn time control từ dropdown menu đầu tiên
   - Click Back và bắt đầu game mới

2. **Thay đổi AI Difficulty:**

   - Vào Settings từ home screen
   - Chọn AI level từ dropdown menu thứ hai
   - Click Back và bắt đầu game mới

3. **Settings được lưu:**
   - Settings sẽ được giữ nguyên giữa các game
   - Chỉ reset khi đóng ứng dụng

### 📊 AI Performance

| Difficulty | Depth | Time Limit | Use Case                  |
| ---------- | ----- | ---------- | ------------------------- |
| Easy       | 2     | 1s         | Người mới bắt đầu         |
| Medium     | 3     | 3s         | Người chơi trung bình     |
| **Hard**   | 4     | 5s         | Người chơi giỏi (default) |
| Expert     | 5     | 10s        | Thử thách cao             |

### 🚀 Next Steps

- [ ] Theme selector (Lichess, Chess.com, Custom)
- [ ] Sound settings (volume control)
- [ ] Save/Load games (PGN format)
- [ ] Online play vs other players
- [ ] Engine analysis depth slider

---

**Version:** 2.2.0  
**Date:** October 7, 2025  
**Author:** Eurus-Infosec
