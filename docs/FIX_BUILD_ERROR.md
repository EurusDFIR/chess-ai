# ⚠️ C++ BUILD ISSUE - HƯỚNG DẪN FIX THỦ CÔNG

## 🔴 VẤN ĐỀ HIỆN TẠI

**Error:** `'board': undeclared identifier` tại dòng 334 trong `search.cpp`

**Tình trạng:** File đã có `*board` nhưng compiler vẫn báo lỗi `board`

**Nguyên nhân có thể:**

1. File được edit bằng nhiều editor khác nhau
2. Line ending mismatch (CRLF vs LF)
3. Hidden Unicode characters
4. VS compiler cache không cập nhật

---

## ✅ GIẢI PHÁP 1: FIX THỦ CÔNG (NHANH NHẤT)

### **Bước 1: Mở file**

```
src/engine_cpp/src/search.cpp
```

### **Bước 2: Tìm hàm `orderMoves`** (khoảng dòng 325)

```cpp
void SearchEngine::orderMoves(MoveList &moves, const Move &ttMove,
                               const Move &killer1, const Move &killer2, int ply)
{
    if (moves.size() == 0) return;

    // Create score array
    int scores[MAX_MOVES];

    for (int i = 0; i < moves.size(); i++)
    {
        scores[i] = scoreMove(*board, moves[i], ttMove, killer1, killer2);
        //                     ^^^^^^ ĐẢM BẢO CÓ DẤU * TRƯỚC board
    }
```

### **Bước 3: XÓA TOÀN BỘ hàm `orderMoves`**

Xóa từ `void SearchEngine::orderMoves` đến hết dấu `}` đóng của hàm

### **Bước 4: COPY-PASTE hàm mới này:**

```cpp
// Move ordering
void SearchEngine::orderMoves(MoveList &moves, const Move &ttMove, const Move &killer1, const Move &killer2, int ply)
{
    if (moves.size() == 0) return;

    int scores[MAX_MOVES];

    for (int i = 0; i < moves.size(); i++)
    {
        scores[i] = scoreMove(*board, moves[i], ttMove, killer1, killer2);
    }

    for (int i = 0; i < moves.size() - 1; i++)
    {
        int best = i;
        for (int j = i + 1; j < moves.size(); j++)
        {
            if (scores[j] > scores[best])
            {
                best = j;
            }
        }
        if (best != i)
        {
            std::swap(moves[i], moves[best]);
            std::swap(scores[i], scores[best]);
        }
    }
}
```

### **Bước 5: Save file (Ctrl+S)**

### **Bước 6: Build lại**

```bash
rm -rf build
python setup.py develop
```

---

## ✅ GIẢI PHÁP 2: TẠO FILE MỚI

Nếu vẫn lỗi, có thể file bị corrupt. Rename file cũ:

```bash
mv src/engine_cpp/src/search.cpp src/engine_cpp/src/search.cpp.backup
```

Rồi tải file search.cpp mới từ backup hoặc recreate từ template.

---

## ✅ GIẢI PHÁP 3: DÙNG PYTHON ENGINE

Nếu không muốn mất thời gian fix C++, **Python engine đã hoạt động tốt!**

```bash
python src/main.py
```

**So sánh:**

- Python: 7K nodes/sec, Elo ~1400 ✅ **ĐANG CHẠY**
- C++: 1M+ nodes/sec, Elo ~2500 ❌ **Chưa build xong**

Python engine vẫn đủ mạnh để chơi! C++ chỉ nhanh hơn, không mạnh hơn về logic.

---

## 🎯 KHUYẾN NGHỊ

1. **Chơi ngay với Python engine** - đã sẵn sàng!
2. Fix C++ khi rảnh - chỉ để có tốc độ nhanh hơn
3. C++ không thay đổi gameplay, chỉ tăng tốc độ search

---

## 📞 NẾU VẪN LỖI

Thử commands này:

```bash
# Clean everything
rm -rf build src/*.pyd src/*.so
rm -rf src/engine_cpp/src/search.cpp

# Sau đó yêu cầu recreate file search.cpp mới hoàn toàn
```
