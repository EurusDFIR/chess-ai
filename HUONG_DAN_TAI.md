# 🎮 HƯỚNG DẪN TẢI VÀ CÀI ĐẶT CHESS AI - EURY ENGINE

## 📥 CÁCH 1: TẢI TỪ GITHUB (KHUYÊN DÙNG)

### Bước 1: Vào trang tải

🔗 **Link:** https://github.com/EurusDFIR/chess-ai/releases/latest

### Bước 2: Tải file

- Kéo xuống phần **Assets**
- Click vào: **ChessAI-Portable-v2.1.zip** (354 MB)
- Đợi tải xong (mất 5-10 phút tùy mạng)

### Bước 3: Giải nén

1. Click phải vào file `ChessAI-Portable-v2.1.zip`
2. Chọn **"Extract All..."** (hoặc "Giải nén tất cả...")
3. Chọn thư mục muốn giải nén (VD: `C:\Games\ChessAI`)
4. Click **Extract**

### Bước 4: Chạy game

1. Vào thư mục vừa giải nén
2. Double-click file: **ChessAI-EuryEngine.exe**
3. Chơi!

### ⚠️ Windows SmartScreen cảnh báo?

**Nếu xuất hiện cảnh báo "Windows protected your PC":**

1. Click **"More info"** (Thông tin thêm)
2. Click **"Run anyway"** (Vẫn chạy)

**Tại sao?**

- App chưa được Microsoft ký số (cần $300/năm)
- Hoàn toàn an toàn, code nguồn mở tại GitHub

---

## 📥 CÁCH 2: TẢI TỪ GOOGLE DRIVE

### Link tải:

🔗 **[Nhấn vào đây để tải](link-drive-của-bạn)**

### Các bước giống như trên:

1. Tải file ZIP từ Drive
2. Giải nén
3. Chạy file .exe

---

## 💻 YÊU CẦU HỆ THỐNG

✅ **Windows 10 hoặc Windows 11** (64-bit)  
✅ **512 MB RAM** (khuyên dùng 2GB)  
✅ **400 MB ổ cứng trống**  
❌ **KHÔNG CẦN cài Python** (đã tích hợp sẵn)

---

## 🎮 HƯỚNG DẪN CHƠI

### Bắt đầu game mới

1. Click **"New Game"**
2. Chọn **"vs AI"** (chơi với máy) hoặc **"vs Human"** (2 người)
3. Chọn độ khó:
   - **Easy** - Dễ (AI suy nghĩ nhanh)
   - **Medium** - Trung bình
   - **Hard** - Khó (AI suy nghĩ lâu hơn)

### Điều khiển

| Thao tác           | Cách làm                     |
| ------------------ | ---------------------------- |
| **Di chuyển quân** | Click quân cờ → Click ô đích |
| **Kéo thả**        | Giữ chuột + kéo quân         |
| **Hủy chọn**       | Nhấn ESC hoặc click ô trống  |
| **Phân tích**      | Click nút "Analysis"         |
| **Đầu hàng**       | Click "Resign"               |
| **Hòa**            | Click "Draw"                 |
| **Ván mới**        | Click "Rematch"              |

### Chế độ phân tích (Analysis Mode)

1. Click nút **"Analysis"** (màu xanh)
2. Xem:
   - **Thanh đánh giá** (trắng thắng/đen thắng)
   - **Nước đi tốt nhất** (Best move)
   - **Đánh giá nước đi:**
     - `!!` = Nước đi xuất sắc
     - `!` = Nước đi tốt
     - `?` = Nước đi sai
     - `??` = Nước đi tệ

---

## ❓ GIẢI ĐÁP THẮC MẮC

### Q: Tại sao file .exe quá lớn (98 MB)?

**A:** File chứa:

- Toàn bộ Python runtime
- Chess engine (AI)
- 12 opening books (cơ sở khai cuộc)
- 538 endgame tablebases (cơ sở tàn cuộc)

### Q: Game chạy chậm?

**A:**

- Tắt Analysis Mode (giảm tải CPU)
- Giảm độ khó xuống Easy
- Đóng các app khác

### Q: Tại sao lần đầu Analysis Mode chậm?

**A:** Do AI đang "khởi động" cache. Từ lần 2 sẽ nhanh hơn.

### Q: Có thể chơi offline không?

**A:** Có! Game hoàn toàn offline, không cần internet.

### Q: Game có virus không?

**A:** Không! Code nguồn mở tại GitHub, kiểm tra được.

### Q: Có bản MacOS/Linux không?

**A:** Chưa có. Hiện tại chỉ Windows 64-bit.

---

## 🐛 BÁO LỖI

Gặp lỗi? Hãy báo tại:  
🔗 https://github.com/EurusDFIR/chess-ai/issues

**Thông tin cần cung cấp:**

1. Windows version (Win 10/11)
2. Mô tả lỗi chi tiết
3. Screenshot (nếu có)

---

## 📞 LIÊN HỆ

- **GitHub**: https://github.com/EurusDFIR/chess-ai
- **Issues**: https://github.com/EurusDFIR/chess-ai/issues

---

## 📜 BẢN QUYỀN

MIT License - Miễn phí sử dụng, sửa đổi, phân phối.

---

**Chúc bạn chơi vui! ♟️🎮**

_Phát triển bởi Eury Engine Team - Sinh viên TDMU_
