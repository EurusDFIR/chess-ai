# 🎵 Hướng Dẫn Thay Đổi Nhạc Nền Chess AI

## 📍 Vị Trí File Nhạc

Nhạc nền được lưu trong thư mục:

```
src/gui/assets/music/
```

### Các File Nhạc Hiện Có:

- `background_music.mp3` - Nhạc nền cũ
- `Same Blue_Piano .mp3` - Nhạc nền mới (đang dùng)

## 🔧 Cách Thay Đổi Nhạc Nền

### Bước 1: Thêm File Nhạc Mới

- Copy file nhạc MP3 vào thư mục `src/gui/assets/music/`
- Đặt tên file không có dấu cách hoặc ký tự đặc biệt

### Bước 2: Chỉnh Sửa Code

Trong file `src/gui/main_window_v2.py`, tìm method `_load_music()`:

```python
def _load_music(self):
    """Load background music"""
    music_path = os.path.join(os.path.dirname(__file__), "assets", "music",
                             "TÊN_FILE_NHẠC_MỚI.mp3")  # ← Thay đổi tên file ở đây
    if os.path.exists(music_path):
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.3)
            print("[Music] TÊN_NHẠC music loaded")  # ← Thay đổi thông báo
        except:
            print("[Warning] Could not load music")
```

### Bước 3: Test

```bash
# Test nhạc mới
python -c "
import pygame
import os
pygame.mixer.init()
music_path = 'src/gui/assets/music/TÊN_FILE.mp3'
pygame.mixer.music.load(music_path)
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)
import time
time.sleep(3)
pygame.mixer.music.stop()
pygame.mixer.quit()
print('✅ Test thành công!')
"
```

## 🎮 Chạy Game Với Nhạc Mới

```bash
python -m src.gui.main_window_v2
```

## 📝 Lưu Ý

- **Format**: Chỉ hỗ trợ MP3
- **Kích thước**: File lớn OK (Same Blue Piano: ~9.8MB)
- **Volume**: Mặc định 0.3 (30%), có thể điều chỉnh trong game
- **Loop**: Nhạc tự động lặp vô hạn

## 🎵 Nhạc Hiện Tại

**Đang dùng**: `Same Blue_Piano .mp3`

- Thể loại: Piano nhẹ nhàng
- Phù hợp: Game cờ vua tập trung

---

_Updated: October 8, 2025_
_Music: Same Blue Piano_
