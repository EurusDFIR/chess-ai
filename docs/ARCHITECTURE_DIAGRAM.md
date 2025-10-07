# 🏗️ Architecture Overview - Chess AI v2.0

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│                   (main_window_v2.py)                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ BoardWidget  │  │ ChessClock   │  │ ControlPanel │  │
│  │              │  │              │  │              │  │
│  │ • Drawing    │  │ • Timer      │  │ • Buttons    │  │
│  │ • Interaction│  │ • Increment  │  │ • Events     │  │
│  │ • Moves      │  │ • Pause      │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ CapturedPcs  │  │ MoveHistory  │                    │
│  │              │  │              │                    │
│  │ • Display    │  │ • SAN        │                    │
│  │ • Material   │  │ • Scrolling  │                    │
│  └──────────────┘  └──────────────┘                    │
│                                                           │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                    GAME LOGIC LAYER                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────────┐       │
│  │         chess.Board (python-chess)           │       │
│  │  • Game rules                                 │       │
│  │  • Move validation                            │       │
│  │  • Game state                                 │       │
│  └──────────────────────────────────────────────┘       │
│                                                           │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                      AI LAYER                            │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌───────────────┐        ┌─────────────────┐           │
│  │ Opening Book  │───────▶│  AI Engine     |
│  │               │        │                 │           │
│  │ • Polyglot    │        │ • Minimax       │           │
│  │ • .bin files  │        │ • Alpha-Beta    │           │
│  └───────────────┘        │ • Evaluation    │           │
│                           │ • Threading     │           │
│                           └─────────────────┘           │
│                                    │                    │
│                                    ▼                    │
│                           ┌─────────────────┐           │
│                           │ C++ Engine      │           │
│                           │ (Optional)      │           │
│                           │                 │           │
│                           │ • Bitboards     │           │
│                           │ • Fast search   │           │
│                           │ • Transposition │           │
│                           └─────────────────┘           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 🔄 Component Interaction Flow

```
┌──────────────────────────────────────────────────────────┐
│                     USER ACTION                           │
│              (Click, Drag, Button press)                  │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                    EVENT HANDLING                           │
│                 (main_window_v2.py)                         │
│                                                             │
│  • pygame events → handle_event()                           │
│  • UI events → handle_button_press()                        │
│  • Mouse events → widget.handle_mouse_*()                   │
└────────────────────────┬───────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ BoardWidget │  │ ChessClock  │  │ ControlPanel│
│             │  │             │  │             │
│ • Validate  │  │ • Update    │  │ • Execute   │
│ • Move      │  │ • Switch    │  │ • Action    │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       │                │                │
       ▼                ▼                ▼
┌──────────────────────────────────────────────┐
│           GAME STATE UPDATE                   │
│                                               │
│  • board.push(move)                           │
│  • clock.switch_player()                      │
│  • Check game over                            │
│  • Update widgets                             │
└────────────────────┬──────────────────────────┘
                     │
                     ▼
      ┌──────────────┴──────────────┐
      │                              │
      ▼                              ▼
┌───────────┐              ┌──────────────────┐
│ Player    │              │ AI Turn?         │
│ Turn      │              │                  │
│ Continue  │              │ • ai_move_thread │
└───────────┘              │ • Background     │
                           │ • Queue result   │
                           └──────────────────┘
```

## 🎨 GUI Component Tree

```
ChessGame (Main Class)
│
├── pygame_gui.UIManager
│   ├── Home Buttons
│   │   ├── Title Label
│   │   ├── Play Button
│   │   ├── Settings Button
│   │   └── About Button
│   │
│   ├── ChessClock
│   │   ├── White Clock Label
│   │   └── Black Clock Label
│   │
│   └── ControlPanel
│       ├── Resign Button
│       ├── Draw Button
│       ├── Analysis Button
│       ├── Rematch Button
│       └── Home Button
│
├── BoardWidget
│   ├── Board State (chess.Board)
│   ├── Selected Square
│   ├── Legal Moves
│   ├── Dragging State
│   ├── Arrows
│   └── Highlights
│
├── CapturedPiecesWidget
│   ├── Captured White Pieces
│   ├── Captured Black Pieces
│   └── Material Difference
│
└── MoveHistoryWidget
    ├── Move Stack
    └── SAN Notation
```

## 🔄 Game Loop Flow

```
┌─────────────────────────────────────────┐
│         MAIN GAME LOOP                  │
│         (60 FPS)                        │
└────────────────┬────────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ Event Handling │
        │ • pygame.event │
        │ • UI events    │
        └────────┬───────┘
                 │
                 ▼
        ┌────────────────┐
        │     Update     │
        │ • Clock update │
        │ • AI check     │
        │ • UI update    │
        └────────┬───────┘
                 │
                 ▼
        ┌────────────────┐
        │      Draw      │
        │ • Board        │
        │ • Widgets      │
        │ • UI overlay   │
        └────────┬───────┘
                 │
                 ▼
        ┌────────────────┐
        │ Display Flip   │
        │ (60 FPS)       │
        └────────┬───────┘
                 │
                 └──────► Loop back
```

## 🧵 AI Threading Model

```
┌────────────────────────────────────────────┐
│            MAIN THREAD                      │
│            (GUI Thread)                     │
│                                             │
│  ┌──────────────────────────────┐          │
│  │ Player makes move            │          │
│  └─────────────┬────────────────┘          │
│                │                            │
│                ▼                            │
│  ┌──────────────────────────────┐          │
│  │ Check if AI turn             │          │
│  └─────────────┬────────────────┘          │
│                │                            │
│                ▼                            │
│  ┌──────────────────────────────┐          │
│  │ Spawn AI Thread              │◄─────────┼─────┐
│  │ clock.pause()                │          │     │
│  └─────────────┬────────────────┘          │     │
│                │                            │     │
│                │          ┌─────────────────┼─────┘
│                │          │                 │
│                │          ▼                 │
│  ┌─────────────▼──────────────────┐        │
│  │ Continue GUI Loop              │        │
│  │ (Responsive, no lag)           │        │
│  └─────────────┬──────────────────┘        │
│                │                            │
│                ▼                            │
│  ┌──────────────────────────────┐          │
│  │ Check AI queue               │◄─────┐   │
│  │ ai_move_queue.get()          │      │   │
│  └─────────────┬────────────────┘      │   │
│                │                        │   │
│                ▼                        │   │
│  ┌──────────────────────────────┐      │   │
│  │ AI move ready?               │──No──┘   │
│  └─────────────┬────────────────┘          │
│                │ Yes                        │
│                ▼                            │
│  ┌──────────────────────────────┐          │
│  │ Apply move                   │          │
│  │ clock.resume()               │          │
│  └──────────────────────────────┘          │
│                                             │
└─────────────────────────────────────────────┘
                                  │
                                  │
        ┌─────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────┐
│           AI THREAD                         │
│         (Background)                        │
│                                             │
│  ┌──────────────────────────────┐          │
│  │ Check opening book           │          │
│  └─────────────┬────────────────┘          │
│                │                            │
│         Found? ├─Yes─┐                      │
│                │     ▼                      │
│                │  Use book move             │
│                │     │                      │
│         No     │     │                      │
│                ▼     │                      │
│  ┌──────────────┐   │                      │
│  │ Run Minimax  │   │                      │
│  │ • Alpha-Beta │   │                      │
│  │ • Evaluation │   │                      │
│  │ • Depth N    │   │                      │
│  └─────┬────────┘   │                      │
│        │            │                      │
│        └────────┬───┘                      │
│                 ▼                           │
│  ┌──────────────────────────────┐          │
│  │ Put move in queue            │          │
│  │ ai_move_queue.put(move)      │          │
│  └──────────────────────────────┘          │
│                                             │
└─────────────────────────────────────────────┘
```

## 📦 Data Flow

```
User Input
    │
    ▼
BoardWidget.handle_mouse_up()
    │
    ▼
chess.Board.push(move)
    │
    ├──▶ BoardWidget.last_move = move
    │
    ├──▶ CapturedPiecesWidget.track_capture(move)
    │
    ├──▶ ChessClock.switch_player()
    │
    └──▶ Check Game Over
            │
            ├─ Checkmate ──▶ end_game()
            ├─ Stalemate ──▶ end_game()
            └─ Continue ───▶ AI turn?
                                │
                                ▼
                           ai_move_threaded()
                                │
                                ▼
                           [Background processing]
                                │
                                ▼
                           ai_move_queue.put(move)
                                │
                                ▼
                           Main loop checks queue
                                │
                                ▼
                           Apply AI move
                                │
                                └──▶ Back to User Input
```

## 🎯 Component Responsibilities

| Component                | Responsibility                                     |
| ------------------------ | -------------------------------------------------- |
| **ChessGame**            | Main coordinator, game loop, state management      |
| **BoardWidget**          | Board rendering, user interaction, move validation |
| **ChessClock**           | Time management, countdown, increment              |
| **CapturedPiecesWidget** | Display captured pieces, material count            |
| **MoveHistoryWidget**    | Display move history, SAN notation                 |
| **ControlPanel**         | Game control buttons, UI state                     |
| **chess.Board**          | Game rules, move generation, validation            |
| **AI Module**            | Move calculation, opening book, evaluation         |

## 🔧 Extensibility Points

Want to add features? Easy extension points:

1. **New Widget**: Add to `src/gui/components/`
2. **New Theme**: Edit `theme_improved.json`
3. **New AI Level**: Add to `ai_levels` dict
4. **New Time Control**: Add to `time_controls` dict
5. **New Screen**: Add to `current_screen` states
6. **Sound Effects**: Add to assets, hook into events

## 📈 Scalability

The modular design allows easy scaling:

- **Add multiplayer**: Create `NetworkManager` component
- **Add analysis**: Create `AnalysisWidget` component
- **Add database**: Create `GameDatabase` component
- **Add puzzles**: Create `PuzzleManager` component
- **Add tournaments**: Create `TournamentManager` component

Each feature is a new component, doesn't affect existing code!

---

**Architecture Design**: Clean, Modular, Scalable, Maintainable
