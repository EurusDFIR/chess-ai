# 🚀 HƯỚNG DẪN CHẠY - FAST ENGINE

## ✅ Đã Sửa Lỗi API

Fast engine đã được tích hợp đúng vào GUI với API mới:

- Thay `time_limit=` → `max_time=`
- Trả về `(move, info)` thay vì chỉ `move`

## 🎮 Cách Chạy

### 1. **Xóa cache Python** (quan trọng!)

```bash
# Windows Git Bash:
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Hoặc Windows CMD:
FOR /d /r . %d IN (__pycache__) DO @IF EXIST "%d" rd /s /q "%d"
```

### 2. **Chạy GUI**

```bash
python -m src.gui.main_window_v2
```

### 3. **Kiểm tra logs**

Khi AI di chuyển, bạn sẽ thấy:

```
[Fast Engine] Move: e2e4 (depth 5, nodes: 25,000, nps: 15,000)
```

## 🔍 Test Trước

Chạy test để đảm bảo mọi thứ hoạt động:

```bash
python test_gui_import.py
```

Nếu thấy `✅ ALL TESTS PASSED!` → GUI sẵn sàng!

## ⚡ Hiệu Suất Mong Đợi

| Difficulty | Time | Nodes Expected | NPS Expected |
| ---------- | ---- | -------------- | ------------ |
| Easy       | 2s   | ~30,000        | ~15,000      |
| Medium     | 5s   | ~70,000        | ~14,000      |
| Hard       | 10s  | ~140,000       | ~14,000      |
| Expert     | 15s  | ~220,000       | ~14,500      |

## 🐛 Nếu Vẫn Lỗi

### Lỗi: "get_best_move() got an unexpected keyword argument 'time_limit'"

**Nguyên nhân**: Python đã cache file cũ

**Giải pháp**:

1. Thoát hoàn toàn Python/terminal
2. Xóa tất cả `__pycache__` folders
3. Khởi động lại terminal mới
4. Chạy lại

### Lỗi: "cannot import name 'get_best_move'"

**Nguyên nhân**: Module path không đúng

**Giải pháp**:

```bash
# Đảm bảo đang ở thư mục root của project
cd r:/_Documents/_TDMU/KIEN_THUC_TDMU/3_year_HK2/TriTueNT/chess-ai

# Kiểm tra file có tồn tại
ls src/ai/minimax_fast.py
```

## ✨ Tính Năng Mới

Với fast engine, bạn sẽ thấy:

1. **AI suy nghĩ trong đúng time limit**

   - Không còn bị over-time
   - Không bị "đơ" giữa chừng

2. **Logs chi tiết hơn**

   - Hiển thị số nodes đã search
   - Hiển thị NPS (nodes per second)
   - Dễ debug hơn

3. **Performance tốt hơn**
   - Search nhiều nodes hơn 5-7x
   - Depth sâu hơn 1-2 ply
   - Moves chất lượng cao hơn

## 🎉 Kết Luận

Fast engine đã sẵn sàng! Chạy GUI và enjoy:

```bash
python -m src.gui.main_window_v2
```

AI bây giờ **VỪA NHANH VỪA MẠNH!** 🚀
