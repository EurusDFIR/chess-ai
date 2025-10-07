# Phân Tích Vấn Đề Engine - Eury Chess AI

## Ngày: 08/10/2025

## 1. Đánh Giá Độ Mạnh Thực Tế

**Kết quả test:**

- Eury Engine (Expert) ≈ Stockfish Level 5 on Lichess
- **THUA** Stockfish Level 6 (1-0, bị chiếu hết 45 nước)
- **HÒA** Stockfish Level 5 (1/2-1/2, lặp nước 3 lần)

**Phân tích từ PGN:**

### Trận vs Stockfish Level 6 (Thua 0-1)

```
Nước 5: 5... Qa5+ - Đưa hậu ra sớm
Nước 9: 9. Nc6 - Mã nhảy vô tận
Nước 12: 12... Ke7 - Nhập thành bằng tay, không castling
Nước 13: 13... Qc5 - Hậu đi lại nhiều lần
Nước 14: 14. Bf2 Qc7 - Lặp nước, không có kế hoạch
Nước 23: 23... Nb2 - Mã đi xa không có mục đích
Nước 29: 29. g3 Bxg3 - Bỏ tượng không cần thiết
```

**Vấn đề:**

1. Đưa Hậu ra quá sớm (nước 5-9)
2. Không castling đúng lúc
3. Di chuyển quân không có kế hoạch
4. Lặp nước nhiều lần không cần thiết

## 2. Nguyên Nhân Kỹ Thuật

### 2.1 Vấn đề Move Ordering & Evaluation

**Hiện tại:**

- PST (Piece-Square Tables) khuyến khích Hậu ở giữa bàn cờ
- Không có penalty cho việc đưa Hậu ra sớm
- Move ordering chỉ dựa vào captures, không xem xét development

**PST_QUEEN_MG hiện tại:**

```python
PST_QUEEN_MG = [
    -20, -10, -10, -5,  -5,  -10, -10, -20,
    -10, 0,   0,   0,   0,   0,   0,   -10,
    -10, 0,   5,   5,   5,   5,   0,   -10,  # Center: +5
    -5,  0,   5,   5,   5,   5,   0,   -5,
    0,   0,   5,   5,   5,   5,   0,   -5,
    -10, 5,   5,   5,   5,   5,   0,   -10,  # Early: +5
    -10, 0,   5,   0,   0,   0,   0,   -10,
    -20, -10, -10, -5,  -5,  -10, -10, -20   # Back rank: -5
]
```

➡️ **Khuyến khích Hậu di chuyển sớm vào giữa bàn (+5 điểm)**

### 2.2 Vấn đề Development Evaluation

**Thiếu:**

- Không có bonus cho development (Mã, Tượng ra sớm)
- Không có penalty cho việc di chuyển cùng 1 quân nhiều lần
- Không có bonus cho castling sớm
- Không có penalty cho việc đưa Hậu ra trước Mã/Tượng

### 2.3 Vấn đề Draw Detection

**Thiếu:**

```python
# Chỉ check:
board.is_fivefold_repetition()  # 5 lần lặp
board.is_seventyfive_moves()    # 75 nước

# KHÔNG check:
board.is_threefold_repetition()  # 3 lần lặp ← LUẬT HÒA
board.can_claim_draw()           # Claim draw
```

**Kết quả:** Engine không biết tránh lặp nước 3 lần, không biết claim hòa

### 2.4 Vấn đề Repetition Avoidance

**Hiện tại:**

- Không có penalty cho việc lặp lại vị trí
- Transposition Table không track số lần lặp
- Không có contempt factor để tránh hòa

## 3. Giải Pháp Đề Xuất

### 3.1 Sửa PST cho Opening Phase

**Nguyên tắc:**

1. **Hậu**: Phải ở back rank trong opening (penalty -20 đến -50 nếu ra sớm)
2. **Mã**: Khuyến khích đến c3/f3/c6/f6
3. **Tượng**: Khuyến khích đến e2/d3/e7/d6
4. **Vua**: Khuyến khích castling (+30)

### 3.2 Development Bonus/Penalty

**Thêm vào evaluation:**

```python
# Bonus cho phát triển quân
+ 15 điểm cho mỗi Mã/Tượng developed
+ 30 điểm cho castling
- 20 điểm cho mỗi lần di chuyển Hậu trong opening (trước nước 10)
- 10 điểm cho mỗi lần di chuyển cùng 1 quân 2 lần trong opening
```

### 3.3 Draw Detection & Avoidance

**Sửa đổi:**

```python
# 1. Check threefold repetition
if board.is_threefold_repetition():
    return 0  # Draw

# 2. Penalty cho việc lặp lại vị trí
if board.is_repetition(2):  # 2 lần lặp
    score -= 50  # Penalty

# 3. Contempt factor (tránh hòa khi có advantage)
if abs(score) < 50:  # Position gần hòa
    score += CONTEMPT * (1 if board.turn == chess.WHITE else -1)
```

### 3.4 Opening Principles

**Thêm vào evaluation:**

```python
def evaluate_opening_principles(board):
    score = 0
    move_count = board.fullmove_number

    if move_count <= 15:  # Opening phase
        # 1. Center control
        score += evaluate_center_control(board) * 10

        # 2. Development
        score += evaluate_development(board) * 15

        # 3. Castling
        if board.has_castling_rights(chess.WHITE):
            score += 20
        if board.has_castled(chess.WHITE):
            score += 30

        # 4. Queen early development penalty
        queen_sq = board.king(chess.WHITE)  # Get queen square
        if queen_sq and not in_back_rank(queen_sq):
            score -= 20 * count_queen_moves(board)

    return score
```

## 4. Kế Hoạch Triển Khai

### Phase 1: Critical Fixes (Ưu tiên cao)

1. ✅ Fix threefold repetition detection
2. ✅ Fix stalemate detection (đã có)
3. ✅ Add repetition penalty
4. ✅ Fix PST_QUEEN for opening phase

### Phase 2: Opening Improvements

5. ⏳ Add development evaluation
6. ⏳ Add opening principles bonus
7. ⏳ Add queen early movement penalty
8. ⏳ Improve center control evaluation

### Phase 3: Advanced

9. ⏳ Add contempt factor
10. ⏳ Add move repetition tracking
11. ⏳ Improve time management in drawish positions

## 5. Expected Improvements

**Sau khi fix:**

- Độ mạnh: ~2000-2200 Elo (gần Stockfish Level 6-7)
- Lối chơi: Tuân thủ nguyên tắc development cơ bản
- Draw handling: Đúng luật, tránh lặp nước không cần thiết

**Elo gain dự kiến:**

- Draw detection fix: +50 Elo
- Opening principles: +100-150 Elo
- Repetition avoidance: +30-50 Elo
- **Tổng: +180-250 Elo**

➡️ **Target: 2050-2300 Elo (Stockfish Level 6-7)**
