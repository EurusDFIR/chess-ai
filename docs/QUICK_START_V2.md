# 🚀 Quick Start - Chess AI v2.0

## Chạy ngay

```bash
# Version mới (Recommended)
python -m src.gui.main_window_v2

# Version cũ
python -m src.gui.main_window
```

## Điều khiển

| Thao tác | Cách thực hiện |
|----------|----------------|
| Di chuyển quân | Click chuột trái kéo thả |
| Vẽ mũi tên | Click chuột phải kéo |
| Đánh dấu ô | Click chuột phải |
| Từ chức | Nút "Resign" |
| Đề nghị hòa | Nút "Draw" |
| Đấu lại | Nút "Rematch" (sau khi hết game) |
| Về menu | Nút "Home" |

## Time Controls

- **Bullet 1+0**: 1 phút
- **Bullet 2+1**: 2 phút + 1 giây/nước
- **Blitz 3+0**: 3 phút
- **Blitz 5+0**: 5 phút (mặc định)
- **Rapid 10+0**: 10 phút
- **Rapid 15+10**: 15 phút + 10 giây/nước
- **Classical 30+0**: 30 phút

## AI Levels

- **Easy**: Độ sâu 2, dễ thắng
- **Medium**: Độ sâu 3, trung bình
- **Hard**: Độ sâu 4, khó (mặc định)
- **Expert**: Độ sâu 5, rất khó

## Giao diện

```
┌─────────────────────────────────────┐
│  ┌──────┐  ┌────────────────┐      │
│  │      │  │ ⏱️ Đồng hồ đen  │      │
│  │      │  ├────────────────┤      │
│  │      │  │ 🎯 Quân bị ăn   │      │
│  │ Bàn  │  ├────────────────┤      │
│  │ cờ   │  │ 📝 Lịch sử     │      │
│  │ 512px│  │    nước đi     │      │
│  │      │  ├────────────────┤      │
│  │      │  │ 🎮 Điều khiển  │      │
│  └──────┘  ├────────────────┤      │
│            │ ⏱️ Đồng hồ trắng│      │
│            └────────────────┘      │
└─────────────────────────────────────┘
```

## Tính năng mới v2.0

✅ Đồng hồ chạy đúng với increment
✅ Giao diện đẹp như Lichess
✅ Components tách riêng, dễ quản lý
✅ AI không làm lag GUI
✅ Lịch sử nước đi với SAN notation
✅ Hiển thị material advantage
✅ Visual feedback tốt hơn
✅ Theme system chuyên nghiệp

## Test

```bash
python test_components.py
```

## Troubleshooting

**Lỗi import pygame:**
```bash
pip install pygame pygame-gui
```

**Lỗi import chess:**
```bash
pip install chess
```

**Lỗi không tìm thấy module:**
```bash
# Đảm bảo chạy từ thư mục gốc
cd chess-ai
python -m src.gui.main_window_v2
```

**Opening book không load:**
- Kiểm tra file `.bin` trong `opening_bin/`
- Không ảnh hưởng gameplay, AI vẫn chạy

## Documentation

- [README_V2.md](README_V2.md) - Chi tiết đầy đủ
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - Tổng hợp thay đổi
- [docs/](docs/) - Tất cả tài liệu

## Support

🐛 Bugs: GitHub Issues
💡 Suggestions: GitHub Discussions
⭐ Star nếu thích!
