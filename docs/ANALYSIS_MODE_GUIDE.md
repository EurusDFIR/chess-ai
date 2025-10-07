# 📊 Game Analysis Mode - User Guide

## Overview

Game Analysis Mode là tính năng giúp bạn học hỏi từ các ván cờ bằng cách:

- **Xem nước đi tốt nhất** cho mỗi vị trí
- **Đánh giá chất lượng nước đi** (Brilliant, Good, Mistake, Blunder...)
- **Hiển thị evaluation bar** trực quan
- **Phân tích toàn bộ ván cờ** với annotations

---

## ✨ Features

### 1. **Evaluation Bar** 🎯

- Hiển thị ở bên trái bàn cờ
- Thanh dọc với 2 màu:
  - **Trắng** (dưới): White advantage
  - **Đen** (trên): Black advantage
- Số hiển thị ở giữa:
  - `+2.5`: White up 2.5 pawns
  - `-1.2`: Black up 1.2 pawns
  - `M5`: Mate in 5 moves

### 2. **Analysis Panel** 📈

- Thay thế Move History khi bật Analysis Mode
- Hiển thị:
  - **Current Evaluation**: Đánh giá vị trí hiện tại
  - **Best Move**: Nước tốt nhất engine tìm thấy
  - **Move Quality**: Chất lượng nước vừa đi
  - **Alternative Moves**: Top 3-5 nước khác
  - **Analysis Details**: Depth, time, nodes

### 3. **Move Annotations** 🏆

Standard chess symbols:

- `!!` **Brilliant**: Nước xuất sắc
- `!` **Good**: Nước tốt (best move)
- `!?` **Interesting**: Nước thú vị (có ý tưởng)
- `?!` **Dubious**: Nước đáng ngờ
- `?` **Mistake**: Sai lầm (loss 100-300cp)
- `??` **Blunder**: Lỗi nghiêm trọng (loss >300cp)

---

## 🎮 How to Use

### Basic Usage

1. **Start a game**: Click "Play vs AI"
2. **Enable Analysis Mode**: Click "Analysis" button
3. **View analysis**:

   - Evaluation bar updates automatically
   - Analysis panel shows best moves
   - Make moves to see live analysis

4. **Manual analysis**: Click "Analyze Position" to refresh

### During Game

```
┌─────────────────────────────────────────┐
│  Evaluation Bar │ Chess Board │ Analysis │
│      ████       │             │  Panel   │
│      ████       │   ♟ ♞ ♝    │          │
│      ▓▓▓▓       │   ♜ ♛ ♚    │  Best:   │
│      ▓▓▓▓       │             │  Nf3     │
│      ▓▓▓▓       │             │          │
│     +1.2        │             │  Eval:   │
│                 │             │  +1.2    │
└─────────────────────────────────────────┘
```

### Keyboard Shortcuts

- `A`: Toggle Analysis Mode (future feature)
- `←/→`: Navigate moves (future feature)
- `Esc`: Exit Analysis Mode

---

## 📚 Understanding Evaluations

### Evaluation Scale

| Evaluation   | Meaning                    |
| ------------ | -------------------------- |
| +3.0 or more | White is winning           |
| +1.0 to +2.9 | White has clear advantage  |
| +0.3 to +0.9 | White has slight advantage |
| -0.2 to +0.2 | Equal position             |
| -0.3 to -0.9 | Black has slight advantage |
| -1.0 to -2.9 | Black has clear advantage  |
| -3.0 or less | Black is winning           |
| M5           | Mate in 5 moves            |

### Move Quality Thresholds

| Loss (centipawns) | Quality     | Symbol |
| ----------------- | ----------- | ------ |
| < 0 (improvement) | Brilliant   | !!     |
| 0 - 10 cp         | Good        | !      |
| 10 - 50 cp        | Interesting | !?     |
| 50 - 100 cp       | Dubious     | ?!     |
| 100 - 300 cp      | Mistake     | ?      |
| > 300 cp          | Blunder     | ??     |

**Centipawn (cp)**: 100 cp = 1 pawn value

---

## 🔧 Technical Details

### Analysis Engine

- **Backend**: Custom minimax engine with alpha-beta pruning
- **Default Depth**: 3 plies (adjustable)
- **Caching**: LRU cache for analyzed positions
- **Threading**: Background analysis doesn't block GUI

### Performance

- **Single Position**: ~100-500ms (depth 3)
- **Full Game**: ~2-5 seconds (depth 2)
- **Memory**: ~50MB for 1000 cached positions

### Components

```python
AnalysisEngine      # Core analysis logic
├── analyze_position()     # Single position
├── analyze_move()         # Move quality
└── analyze_game()         # Full game PGN

EvaluationBar       # Visual evaluation display
├── set_evaluation()       # Update value
└── draw()                 # Render bar

AnalysisPanel       # GUI panel
├── update_analysis()      # Show results
└── update_move_analysis() # Show move quality
```

---

## 💡 Best Practices

### For Learning

1. **Analyze Your Losses**:

   - Focus on moves marked `?` or `??`
   - Understand why the best move was better
   - Look for patterns in your mistakes

2. **Study Critical Positions**:

   - Pause when evaluation swings sharply
   - Compare your move with engine's suggestion
   - Try to find the better move before seeing analysis

3. **Opening Preparation**:
   - Review early game for `!` moves
   - Note positions where you deviated
   - Build your opening repertoire

### For Training

1. **Set Challenges**:

   - Try to match engine's top moves
   - Aim for no `?` moves in a game
   - Minimize accuracy loss per move

2. **Review Patterns**:
   - Collect your `!!` brilliant moves
   - Analyze why certain moves worked
   - Learn from tactical opportunities

---

## 🎯 Use Cases

### 1. Post-Game Review

```python
# Analyze completed game
1. Load game PGN
2. Step through each move
3. See annotations and alternatives
4. Note critical moments
```

### 2. Position Study

```python
# Analyze specific position
1. Set up position on board
2. Click "Analyze Position"
3. Compare top 3 moves
4. Understand trade-offs
```

### 3. Training Mode

```python
# Real-time feedback
1. Enable Analysis Mode
2. Make your moves
3. Check if they match best moves
4. Learn from mistakes immediately
```

---

## 🚀 Advanced Features (Planned)

### Version 2.2+

- [ ] **Multi-PV Analysis**: Show top 3 variations
- [ ] **Depth Control**: Adjustable analysis depth
- [ ] **Cloud Engine**: Stockfish online integration
- [ ] **Opening Database**: Compare with master games
- [ ] **Position Database**: Check tablebase positions

### Version 2.5+

- [ ] **Game Import**: Load PGN files
- [ ] **Batch Analysis**: Analyze multiple games
- [ ] **Statistics**: Accuracy percentage, mistake rate
- [ ] **Report Export**: PDF analysis reports

---

## 📊 Example Session

### Analyzing the Scholar's Mate

```
Game: 1.e4 e5 2.Bc4 Nc6 3.Qh5 Nf6?? 4.Qxf7#

Move-by-move analysis:
1. e4   ! (Best opening)       Eval: +0.3
2. e5   ! (Symmetric)          Eval: +0.0
3. Bc4  ! (Aggressive)         Eval: +0.2
4. Nc6  ! (Development)        Eval: +0.0
5. Qh5  ?! (Premature)         Eval: +0.5
6. Nf6?? (Blunder!)           Eval: +8.0
7. Qxf7# !! (Checkmate)       Eval: M1

Black's mistake on move 6:
- Played: Nf6??
- Best was: Qe7! (defending f7)
- Accuracy loss: 800 centipawns
- Result: Immediate mate threat
```

---

## 🐛 Troubleshooting

### Analysis is slow

- Reduce depth in settings (default: 3)
- Close other programs
- Update to latest version

### Evaluation seems wrong

- Remember: Engine sees 3-5 moves ahead
- Human evaluation != Computer evaluation
- Trust the math, but understand the position

### Panel not showing

- Click "Analysis" button to toggle
- Check that game is active
- Try refreshing with "Analyze Position"

---

## 📖 Further Reading

- [Chess Evaluation Guide](https://www.chessprogramming.org/Evaluation)
- [Understanding Chess Engines](https://lichess.org/learn)
- [Opening Analysis Tutorial](https://www.chess.com/analysis)

---

## 🤝 Contributing

Help improve Analysis Mode:

- Report bugs on GitHub
- Suggest new features
- Submit pull requests
- Share your analysis insights

---

**Last Updated**: 2025-10-07  
**Version**: 2.1  
**Author**: Eury Engine Team

💬 Questions? Open an issue or discussion on GitHub!
