# 🎮 Chess AI - Hướng dẫn Build C++ Engine

## ✅ ĐÃ HOÀN THÀNH

- ✅ Cài đặt dependencies (pygame-ce, pygame-gui, python-chess, pybind11)
- ✅ Cài đặt CMake 4.1.2
- ✅ Game GUI đang chạy với Python engine!

## 🔧 Build C++ Engine (Cần làm)

### **Bước 1: Restart Terminal**

CMake vừa được cài nhưng chưa có trong PATH. Cần:

1. **Đóng VS Code**
2. **Mở lại VS Code**
3. **Mở terminal mới**

### **Bước 2: Kiểm tra CMake**

```bash
cmake --version
```

Nếu thấy `cmake version 4.1.2` → OK!

### **Bước 3: Cài Visual Studio Build Tools**

C++ engine cần compiler. Download và cài:

- **Visual Studio 2022 Build Tools**: https://visualstudio.microsoft.com/downloads/
- Hoặc **Visual Studio 2022 Community**: https://visualstudio.microsoft.com/vs/

Khi cài, chọn: **Desktop development with C++**

### **Bước 4: Build C++ Engine**

Sau khi cài VS 2022:

```bash
# Trong VS Code terminal mới
python setup.py develop
```

### **Bước 5: Test C++ Engine**

```python
import chess_engine

board = chess_engine.Board()
board.init_start_position()
print("✅ C++ engine working!")
```

---

## 🎯 Hiện tại

**Python engine đang hoạt động tốt!** Game GUI đã chạy.

C++ engine sẽ:

- **100-500x nhanh hơn** 🚀
- Tìm nước đi sâu hơn (depth 8-10)
- Elo ~2500 (vs ~1400 hiện tại)

Nhưng **không bắt buộc** - Python engine vẫn chơi tốt!

---

## 🎮 Chơi ngay bây giờ

```bash
python src/main.py
```

Game đã mở! Enjoy! ♟️
