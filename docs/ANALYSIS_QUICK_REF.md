# ⚡ Analysis Mode - Quick Reference

## Activation

```
Game Screen → Click "Analysis" Button
```

## Features at a Glance

### 📊 Evaluation Bar

```
┌────┐
│ ▓▓ │ ← Black advantage
│ ▓▓ │
│-1.2│ ← Evaluation score
│ ██ │
│ ██ │ ← White advantage
└────┘
```

**Location**: Left side of board  
**Updates**: Real-time after each move

### 📈 Analysis Panel

Shows:

- **Evaluation**: Current position assessment
- **Best Move**: Engine recommendation (SAN notation)
- **Move Quality**: Annotation (!, ?, !!, etc.)
- **Alternatives**: Top 3 other moves
- **Details**: Depth, time, evaluation changes

### 🏆 Move Annotations

| Symbol | Name        | Loss (cp)                  |
| ------ | ----------- | -------------------------- |
| `!!`   | Brilliant   | < 0 (better than expected) |
| `!`    | Good        | 0-10                       |
| `!?`   | Interesting | 10-50                      |
| `?!`   | Dubious     | 50-100                     |
| `?`    | Mistake     | 100-300                    |
| `??`   | Blunder     | > 300                      |

**cp** = centipawns (100cp = 1 pawn)

## Quick Actions

| Action                   | Result                           |
| ------------------------ | -------------------------------- |
| Click "Analysis"         | Toggle mode on/off               |
| Click "Analyze Position" | Refresh current analysis         |
| Make a move              | Auto-analyzes new position       |
| Navigate game            | Shows analysis for each position |

## Evaluation Guide

```
+3.0+   White is winning     ████████████
+1.0    White advantage      ████████▓▓▓▓
+0.5    White slightly better ██████▓▓▓▓▓▓
 0.0    Equal position        ████████████
-0.5    Black slightly better ▓▓▓▓▓▓██████
-1.0    Black advantage       ▓▓▓▓████████
-3.0-   Black is winning     ▓▓▓▓▓▓▓▓▓▓▓▓

M5      Mate in 5 moves      !!
```

## Typical Workflow

1. **Start Game** → Click "Play vs AI"
2. **Enable Analysis** → Click "Analysis"
3. **Play Moves** → See real-time evaluation
4. **Review** → Check best moves and annotations
5. **Learn** → Compare your moves with engine

## Performance Tips

- **Default depth**: 3 (good balance)
- **Faster**: Reduce depth to 2
- **More accurate**: Increase depth to 4+
- **Cache**: Revisited positions are instant

## Reading the Panel

```
┌─────────────────────────────┐
│ Analysis                    │
├─────────────────────────────┤
│ Evaluation: +1.2            │ ← Position value
│ Best move: Nf3              │ ← Engine choice
│ Move Quality: ! Good move   │ ← Your move rating
├─────────────────────────────┤
│ Top moves:                  │
│ 1. Nf3 (+1.2)              │ ← Best
│ 2. Nc3 (+1.0)              │ ← Good alternative
│ 3. d4 (+0.8)               │ ← Also playable
├─────────────────────────────┤
│ Depth: 3 | Time: 250ms     │
└─────────────────────────────┘
```

## Common Use Cases

### 🎓 Learning

- Review your games
- Find your mistakes
- Understand why moves are bad/good

### 🎯 Training

- Try to match engine moves
- Minimize blunders
- Improve accuracy

### 📚 Study

- Analyze master games
- Explore opening variations
- Understand complex positions

### 🔍 Position Puzzles

- Find the best move
- Compare with engine
- Learn tactics

## Troubleshooting

**Slow analysis?**
→ Reduce depth or close other programs

**Wrong evaluation?**
→ Remember: computers see ahead, humans see patterns

**No updates?**
→ Click "Analyze Position" to refresh

**Panel hidden?**
→ Click "Analysis" button to toggle

## Keyboard Shortcuts (Planned)

- `A` - Toggle Analysis Mode
- `←/→` - Navigate moves
- `Space` - Analyze Position
- `Esc` - Exit Analysis

## Tips & Tricks

1. **Compare before moving**: Enable analysis, think about your move, then compare with engine
2. **Learn from patterns**: Save positions where you made mistakes
3. **Don't blindly follow**: Understand WHY a move is best
4. **Focus on mistakes**: Learn more from `?` and `??` than from `!` moves

## Integration with Game

```
Normal Mode:         Analysis Mode:
┌────────────┐       ┌────────────┐
│ Clock      │       │ Clock      │
│ Captured   │       │ Eval Bar   │
│ Moves      │  →    │ Analysis   │
│ Controls   │       │ Controls   │
└────────────┘       └────────────┘
```

---

## 🔗 Related Docs

- [Full Analysis Mode Guide](ANALYSIS_MODE_GUIDE.md)
- [Game Controls](../GAME_CONTROLS_GUIDE.md)
- [Quick Start](../QUICK_START.md)

---

**Version**: 2.1  
**Updated**: 2025-10-07

💡 **Pro Tip**: Use Analysis Mode to review every game - it's the fastest way to improve!
