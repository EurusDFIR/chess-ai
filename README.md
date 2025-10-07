# 🎮 Chess AI - Eury Engine

> **Phần mềm chơi cờ vua với AI mạnh và giao diện đẹp**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)
![Version](https://img.shields.io/badge/version-2.1.0-green.svg)
![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)

---

## 📥 TẢI VỀ

### 🔥 Phiên bản mới nhất: v2.1.0

**[⬇️ TẢI NGAY](https://github.com/EurusDFIR/chess-ai/releases/latest/download/ChessAI-Portable-v2.1.zip)** (354 MB)

_Không cần cài Python! • Giải nén và chạy • Hoàn toàn offline_

**[📋 Hướng dẫn chi tiết](HUONG_DAN_TAI.md)** | **[📝 Release Notes](RELEASE_NOTES.md)** | **[🎮 Tất cả phiên bản](https://github.com/EurusDFIR/chess-ai/releases)**

---

## ✨ TÍNH NĂNG NỔI BẬT

### 🧠 Chế độ phân tích (v2.1.0)

- Phân tích vị trí real-time với AI
- Gợi ý nước đi tốt nhất
- Đánh giá chất lượng nước đi (!! → ??)
- Hiển thị 3 nước đi thay thế

### 🎨 Giao diện Lichess-style

- Thiết kế chuyên nghiệp, dễ nhìn
- Màu sắc brown/tan tối ưu
- Hiển thị nước đi hợp lệ (chấm xanh)
- Lịch sử nước đi 2 cột compact

### 📖 Opening Books

- 12 cơ sở khai cuộc chuyên nghiệp
- Komodo, GM2600, Performance
- Tự động chọn nước đi từ sách
- Hiển thị tên khai cuộc + ECO code

### ♟️ Endgame Tablebases

- 538 files Syzygy tablebase
- Chơi tàn cuộc hoàn hảo (3-7 quân)
- Tự động probe khi phù hợp

### 🤖 AI mạnh

- Minimax với alpha-beta pruning (C++)
- Độ sâu tìm kiếm 2-4 nước (configurable)
- ~100,000 nodes/giây
- LRU cache 1000 positions

---

## 🚀 HƯỚNG DẪN SỬ DỤNG

### Cho người dùng cuối (không cần code)

**Bước 1:** [Tải file ZIP](https://github.com/EurusDFIR/chess-ai/releases/latest)  
**Bước 2:** Giải nén vào thư mục bất kỳ  
**Bước 3:** Chạy `ChessAI-EuryEngine.exe`

⚠️ **Windows SmartScreen cảnh báo?** → Click "More info" → "Run anyway"

📖 **[Hướng dẫn đầy đủ cho người dùng](HUONG_DAN_TAI.md)**

### Cho developer (chạy từ source)

```bash
# 1. Clone repository
git clone https://github.com/EurusDFIR/chess-ai.git
cd chess-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run (v2.1 with Analysis Mode)
python -m src.gui.main_window_v2

# 4. Build executable (optional)
python build_release.py
```

---

## 💻 YÊU CẦU HỆ THỐNG

### Cho người dùng (executable)

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 512 MB (khuyên dùng 2GB)
- **Ổ cứng**: 400 MB trống
- **Python**: ❌ Không cần cài!

### Cho developer (source code)

- **Python**: 3.12+ (khuyên dùng 3.12.4)
- **OS**: Windows/Linux/MacOS
- **RAM**: 2GB+
- **Dependencies**: Xem `requirements.txt`

---

## 🎮 ĐIỀU KHIỂN GAME

| Thao tác            | Cách làm                     |
| ------------------- | ---------------------------- |
| **Di chuyển quân**  | Click quân → Click ô đích    |
| **Kéo thả**         | Giữ chuột trái + kéo         |
| **Vẽ mũi tên**      | Chuột phải + kéo             |
| **Highlight ô**     | Click chuột phải             |
| **Hủy chọn**        | Nhấn ESC hoặc click ô trống  |
| **Toggle Analysis** | Click "Analysis" hoặc phím A |
| **Đầu hàng**        | Click "Resign" hoặc Ctrl+R   |
| **Xin hòa**         | Click "Draw" hoặc Ctrl+D     |
| **Ván mới**         | Click "Rematch" hoặc Ctrl+N  |
| **Về menu**         | Click "Home" hoặc ESC        |

📖 **[Hướng dẫn điều khiển đầy đủ](GAME_CONTROLS_GUIDE.md)**

---

## 📸 SCREENSHOTS

### Giao diện chính v2.1

![Main UI](img_1.png)

### Chế độ phân tích

![Analysis Mode](img_2.png)

### Home Screen

![Home Screen](img_3.png)

---

## 🆕 CHANGELOG v2.1.0

### Thêm mới

- ✅ **Game Analysis Mode** - Phân tích real-time
- ✅ **Evaluation Bar** - Thanh đánh giá vị trí
- ✅ **Move Annotations** - Đánh giá nước đi (!! → ??)
- ✅ **Lichess UI** - Giao diện mới chuyên nghiệp
- ✅ **Opening Books** - 12 cơ sở khai cuộc
- ✅ **Syzygy Tables** - 538 endgame files

### Sửa lỗi

- ✅ Board sync trong analysis mode
- ✅ UIScrollBar crash
- ✅ Evaluation bar calculation
- ✅ Move history SAN notation
- ✅ Control button rendering

📝 **[Changelog đầy đủ](RELEASE_NOTES.md)**

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

```
┌─────────────────────────────────────┐
│         Python GUI Layer            │
│        (Pygame CE 2.5.3)           │
├─────────────────────────────────────┤
│        Component System             │
│  ┌───────────────────────────────┐ │
│  │ BoardWidget                   │ │
│  │ ChessClock                    │ │
│  │ MoveHistoryWidget             │ │
│  │ CapturedPiecesWidget          │ │
│  │ EvaluationBar                 │ │
│  │ AnalysisPanel                 │ │
│  │ ControlPanel                  │ │
│  └───────────────────────────────┘ │
├─────────────────────────────────────┤
│        Game Logic Layer             │
│       (python-chess 1.10.0)        │
├─────────────────────────────────────┤
│         AI Engine Layer             │
│  ┌───────────────────────────────┐ │
│  │ Minimax (C++ binding)         │ │
│  │ Alpha-Beta Pruning            │ │
│  │ Position Evaluation           │ │
│  │ Opening Book Loader           │ │
│  │ Syzygy Tablebase Probe        │ │
│  │ Analysis Engine               │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Tech Stack:**

- **Frontend**: Pygame CE + pygame_gui
- **Backend**: python-chess
- **AI**: C++ minimax (Python binding)
- **Threading**: Queue-based async
- **Caching**: LRU cache (functools)
- **Build**: PyInstaller 6.16.0

---

## 📚 TÀI LIỆU

### Cho người dùng

- 📖 [HUONG_DAN_TAI.md](HUONG_DAN_TAI.md) - Hướng dẫn tải và cài đặt
- 🎮 [GAME_CONTROLS_GUIDE.md](GAME_CONTROLS_GUIDE.md) - Điều khiển game
- 🚀 [QUICK_START.md](QUICK_START.md) - Bắt đầu nhanh

### Cho developer

- 🏗️ [HYBRID_ARCHITECTURE.md](HYBRID_ARCHITECTURE.md) - Kiến trúc hệ thống
- 🎨 [GUI_IMPROVEMENTS.md](GUI_IMPROVEMENTS.md) - Cải tiến UI/UX
- 🔨 [BUILD_GUIDE.md](BUILD_GUIDE.md) - Build C++ engine
- ⚙️ [CPP_IMPLEMENTATION_GUIDE.md](CPP_IMPLEMENTATION_GUIDE.md) - C++ implementation

### Release notes

- 📝 [RELEASE_NOTES.md](RELEASE_NOTES.md) - Chi tiết v2.1.0
- 📊 [OPTIMIZATION_REPORT.md](OPTIMIZATION_REPORT.md) - Performance analysis

---

## ❓ CÂU HỎI THƯỜNG GẶP

<details>
<summary><strong>Q: Tại sao file .exe lớn 98 MB?</strong></summary>

**A:** File chứa:

- Python 3.12 runtime đầy đủ (40MB)
- Pygame CE + pygame_gui (25MB)
- python-chess library (10MB)
- C++ chess engine (5MB)
- Assets (fonts, icons) (3MB)
- Opening books (12MB)
- Syzygy tablebases (3MB compressed)

Lợi ích: Không cần cài Python, chạy ngay!

</details>

<details>
<summary><strong>Q: Game có virus/malware không?</strong></summary>

**A:** Hoàn toàn KHÔNG!

- Code nguồn mở 100% tại GitHub
- Build bằng PyInstaller (official tool)
- Không kết nối internet
- Không thu thập dữ liệu
- Có thể kiểm tra code trước khi build

Windows SmartScreen cảnh báo vì app chưa được Microsoft ký số ($300/năm).

</details>

<details>
<summary><strong>Q: Có thể chơi offline không?</strong></summary>

**A:** Có! Game hoàn toàn offline:

- Không cần internet khi chơi
- Opening books đã tích hợp sẵn
- Tablebases cũng offline
- Chỉ cần internet khi tải lần đầu
</details>

<details>
<summary><strong>Q: Tại sao Analysis Mode chậm lần đầu?</strong></summary>

**A:**

- Lần đầu: AI đang "khởi động" cache → 2-3 giây
- Từ lần 2: Dùng cache → < 1 giây
- Cache lưu 1000 positions (LRU)

Tip: Để Analysis Mode bật liên tục để cache warm-up.

</details>

<details>
<summary><strong>Q: AI mạnh cỡ nào?</strong></summary>

**A:**

- **Easy** (~1200 Elo) - Người mới chơi
- **Medium** (~1500 Elo) - Trung bình
- **Hard** (~1800 Elo) - Khá mạnh
- **Expert** (~2000 Elo) - Rất mạnh

Với opening books + tablebases, AI có thể đạt 2200+ Elo trong một số vị trí.

</details>

<details>
<summary><strong>Q: Có bản MacOS/Linux không?</strong></summary>

**A:** Hiện tại chỉ Windows 64-bit. Nhưng có thể:

- Chạy từ source code trên Mac/Linux (cần Python)
- Build từ source bằng PyInstaller
- Sắp tới sẽ có cross-platform build

```bash
# Trên Mac/Linux:
git clone https://github.com/EurusDFIR/chess-ai.git
cd chess-ai
pip install -r requirements.txt
python -m src.gui.main_window_v2
```

</details>

<details>
<summary><strong>Q: Làm sao báo lỗi?</strong></summary>

**A:**

1. Vào: https://github.com/EurusDFIR/chess-ai/issues
2. Click "New Issue"
3. Cung cấp:
   - Windows version (10/11)
   - Mô tả lỗi chi tiết
   - Screenshot (nếu có)
   - Các bước tái hiện lỗi
   </details>

---

## 🛠️ DEVELOPMENT

### Setup môi trường

```bash
# Clone repo
git clone https://github.com/EurusDFIR/chess-ai.git
cd chess-ai

# Create virtual environment (khuyên dùng)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run game
python -m src.gui.main_window_v2
```

### Build executable

```bash
# Option 1: Use build script
python build_release.py

# Option 2: Manual PyInstaller
pyinstaller --name=ChessAI-EuryEngine \
            --onefile --windowed \
            --add-data="src/gui/assets:assets" \
            --add-data="opening_bin:opening_bin" \
            --hidden-import=pygame \
            --hidden-import=chess \
            src/gui/main_window_v2.py
```

### Project structure

```
chess-ai/
├── src/
│   ├── ai/                    # AI engine
│   │   ├── minimax_optimized.py
│   │   ├── evaluation.py
│   │   └── analysis_engine.py
│   ├── game/                  # Game logic
│   │   ├── chess_game.py
│   │   └── move_validator.py
│   ├── gui/                   # UI components
│   │   ├── components/
│   │   │   ├── board_widget.py
│   │   │   ├── evaluation_bar.py
│   │   │   ├── analysis_panel.py
│   │   │   └── ...
│   │   ├── main_window_v2.py
│   │   └── theme_improved.json
│   └── utils/                 # Utilities
├── opening_bin/               # Opening books (12 files)
├── syzygy/                    # Tablebases (538 files)
├── build_release.py           # Build script
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

### Testing

```bash
# Run tests
python -m pytest tests/

# Test AI engine
python test_current_engine.py

# Benchmark
python benchmark_engines.py
```

---

## 🤝 ĐÓNG GÓP

Contributions welcome! 🎉

### Cách contribute

1. **Fork** repo này
2. **Clone** fork của bạn: `git clone https://github.com/YOUR_USERNAME/chess-ai.git`
3. **Tạo branch**: `git checkout -b feature/TinhNangMoi`
4. **Commit**: `git commit -m 'Thêm tính năng ABC'`
5. **Push**: `git push origin feature/TinhNangMoi`
6. **Tạo Pull Request** trên GitHub

### Ý tưởng cho contributor

- [ ] MacOS/Linux build
- [ ] Online multiplayer
- [ ] Puzzle mode
- [ ] PGN import/export
- [ ] Custom themes
- [ ] Sound effects
- [ ] Tournament mode
- [ ] Neural network engine

---

## 📄 BẢN QUYỀN

**MIT License** - Xem [LICENSE](LICENSE) file

```
MIT License

Copyright (c) 2025 Eury Engine Team - TDMU

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```

**Tóm tắt:**

- ✅ Sử dụng miễn phí (cá nhân, thương mại)
- ✅ Sửa đổi tùy ý
- ✅ Phân phối lại
- ✅ Dùng cho mục đích thương mại
- ⚠️ Không bảo hành, tự chịu trách nhiệm

---

## 🐛 BÁO LỖI & HỖ TRỢ

### Tìm thấy lỗi?

**[🔴 Tạo Issue](https://github.com/EurusDFIR/chess-ai/issues/new)**

**Thông tin cần cung cấp:**

- Windows version (10/11, 64-bit?)
- Python version (nếu chạy từ source)
- Mô tả lỗi chi tiết
- Screenshot (nếu có)
- Các bước tái hiện

### Cần hỗ trợ?

- 📧 **Email**: (thêm email nếu muốn)
- 💬 **GitHub Discussions**: https://github.com/EurusDFIR/chess-ai/discussions
- 🐛 **Issues**: https://github.com/EurusDFIR/chess-ai/issues

---

## 👨‍💻 TÁC GIẢ

**Eury Engine Team - Trường Đại học Thủ Dầu Một (TDMU)**

- 🏫 **Trường**: TDMU - Thủ Dầu Một University
- 👤 **GitHub**: [@EurusDFIR](https://github.com/EurusDFIR)
- 📦 **Repository**: [chess-ai](https://github.com/EurusDFIR/chess-ai)
- 📅 **Năm**: 2024-2025
- 📚 **Môn học**: Trí tuệ nhân tạo (AI)

---

## 🙏 CẢM ƠN & CREDIT

### Libraries & Frameworks

- **[python-chess](https://python-chess.readthedocs.io/)** - Niklaus Fiekas - Chess logic và move generation
- **[Pygame CE](https://pyga.me/)** - Pygame Community - Graphics engine
- **[pygame_gui](https://pygame-gui.readthedocs.io/)** - Dan Lawrence - UI framework
- **[PyInstaller](https://pyinstaller.org/)** - PyInstaller Team - Executable builder

### Resources

- **[Syzygy Tablebases](https://syzygy-tables.info/)** - Ronald de Man - Endgame tablebases
- **[Polyglot Opening Books](http://hgm.nubati.net/book_format.html)** - Fabien Letouzey - Opening book format
- **[Lichess](https://lichess.org/)** - UI design inspiration
- **[Chess Programming Wiki](https://www.chessprogramming.org/)** - Chess AI resources

### Special Thanks

- 🎓 **TDMU** - Đại học Thủ Dầu Một
- 👨‍🏫 **Giảng viên môn AI** - Hướng dẫn và support
- 🧑‍💻 **Contributors** - Tất cả những người đóng góp code
- ☕ **Coffee** - Động lực coding ban đêm

---

## 📊 THỐNG KÊ PROJECT

![GitHub stars](https://img.shields.io/github/stars/EurusDFIR/chess-ai?style=social)
![GitHub forks](https://img.shields.io/github/forks/EurusDFIR/chess-ai?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/EurusDFIR/chess-ai?style=social)

![GitHub issues](https://img.shields.io/github/issues/EurusDFIR/chess-ai)
![GitHub pull requests](https://img.shields.io/github/issues-pr/EurusDFIR/chess-ai)
![GitHub last commit](https://img.shields.io/github/last-commit/EurusDFIR/chess-ai)

![GitHub code size](https://img.shields.io/github/languages/code-size/EurusDFIR/chess-ai)
![GitHub repo size](https://img.shields.io/github/repo-size/EurusDFIR/chess-ai)
![GitHub downloads](https://img.shields.io/github/downloads/EurusDFIR/chess-ai/total)

---

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-❤️-red.svg" alt="Made with love">
  <img src="https://img.shields.io/badge/Made%20in-Vietnam%20🇻🇳-green.svg" alt="Made in Vietnam">
  <img src="https://img.shields.io/badge/Built%20by-TDMU%20Students-blue.svg" alt="Built by TDMU">
</p>

<p align="center">
  <strong>♟️ Chúc bạn chơi vui! 🎮</strong><br>
  <sub>Developed with ❤️ by Eury Engine Team - TDMU 2024-2025</sub><br>
  <sub>Môn học: Trí tuệ nhân tạo • Khoa Công nghệ thông tin</sub>
</p>

---

**⭐ Nếu thích project này, hãy cho 1 star trên GitHub! ⭐**
│ │ ├── components/ # NEW: Modular widgets
│ │ ├── main_window_v2.py # NEW: Refactored main
│ │ ├── main_window.py # Old version
│ │ └── theme_improved.json # NEW: Better theme
│ ├── ai/ # AI algorithms
│ └── engine_cpp/ # C++ engine (optional)
├── docs/ # NEW: Documentation folder
├── opening_bin/ # Opening books
└── requirements.txt

```

## 🐛 Changelog

### v2.0 (Current)

- ✅ Refactored GUI to component-based architecture
- ✅ Fixed clock functionality with proper increment
- ✅ Organized all documentation files
- ✅ Improved UI/UX with Lichess-style design
- ✅ Added move history with SAN notation
- ✅ Better visual feedback and animations

### v1.0

- Initial release with basic functionality

## 📝 License

MIT License

## 👨‍💻 Author

**EurusDFIR**

- GitHub: [@EurusDFIR](https://github.com/EurusDFIR)

---

⭐ **Star this repo if you like it!**

See [README_V2.md](README_V2.md) for detailed documentation.
```
